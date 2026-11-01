# -*- coding: utf-8 -*-
"""Independent QC: re-parse both ASS files from disk, check structure/identity/manifests/timing,
then re-render every pair and every item with libass (ctypes) and check geometry on real rasters.
usage: python qc_m5.py <dir_with_ass> <report.json>"""
import sys, os, re, json, math, hashlib
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import numpy as np
import data_m5 as D
from assr import Renderer

ADIR, REPORT = sys.argv[1], sys.argv[2]
BASIC = os.path.join(ADIR, "2026.07.vi.ass")
STUDY = os.path.join(ADIR, "2026.07.vi-ja-study.ass")
Q_LIMIT = math.floor(D.SOURCE["duration"] * 100) / 100
R = {"gates": {}, "errors": [], "warnings": [], "counts": {}}


def err(gate, msg):
    R["errors"].append(f"{gate}: {msg}")


def parse(path):
    raw = open(path, "rb").read()
    assert raw.startswith(b"\xef\xbb\xbf"), "no UTF-8 BOM"
    assert b"\r\n" not in raw, "CRLF found"
    txt = raw[3:].decode("utf-8")
    sections, cur = {}, None
    for line in txt.split("\n"):
        if line.startswith("[") and line.endswith("]"):
            cur = line; sections[cur] = []; continue
        if cur and line:
            sections[cur].append(line)
    fmt = [x.strip() for x in sections["[Events]"][0].split(":", 1)[1].split(",")]
    assert fmt == ["Layer", "Start", "End", "Style", "Name", "MarginL", "MarginR", "MarginV", "Effect", "Text"], fmt
    evs = []
    for line in sections["[Events]"][1:]:
        kind, rest = line.split(": ", 1)
        parts = rest.split(",", 9)
        ev = dict(zip(fmt, parts)); ev["kind"] = kind; ev["raw"] = line
        evs.append(ev)
    return txt, sections, evs


def tsec(s):
    h, m, rest = s.split(":")
    return int(h) * 3600 + int(m) * 60 + float(rest)


tb, sb, eb = parse(BASIC)
tst, ss, es = parse(STUDY)

# ---------------- G6 structure / identity
same_info = sb["[Script Info]"] == ss["[Script Info]"] and sb["[V4+ Styles]"] == ss["[V4+ Styles]"]
CAP_STYLES = {"SubBox", "SpkBox", "Spk", "JA", "VI"}
cap_b = [e["raw"] for e in eb if e["kind"] == "Dialogue" and e["Style"] in CAP_STYLES]
cap_s = [e["raw"] for e in es if e["kind"] == "Dialogue" and e["Style"] in CAP_STYLES]
identical_caps = cap_b == cap_s
card_in_basic = [e for e in eb if e["kind"] == "Dialogue" and e["Style"] not in CAP_STYLES]
if not same_info: err("G6", "Script Info / Styles differ")
if not identical_caps: err("G6", "caption events differ between files")
if card_in_basic: err("G6", "card events present in basic file")
for e in eb + es:
    if e["kind"] != "Dialogue":
        continue
    a, b = tsec(e["Start"]), tsec(e["End"])
    if not (0 <= a < b <= Q_LIMIT + 1e-9):
        err("G6", f"bad timing {e['Name']} {a} {b}")
    t = e["Text"]
    if t.strip() == "" or re.search(r"\\[1-4]?a(lpha)?&HFF", t, re.I):
        err("G6", f"empty/transparent event {e['Name']}")
    body = re.sub(r"\{[^}]*\}", "", t)
    if "\\" in body.replace("\\N", ""):
        err("G6", f"stray backslash in visible text {e['Name']}")
    if "\\p1" in t and not t.endswith("{\\p0}"):
        err("G6", f"drawing not closed {e['Name']}")
    for tag in re.findall(r"\\[a-z]+", t):
        pass
meta = {}
for e in es:
    if e["kind"] == "Comment":
        obj = json.loads(e["Text"])
        meta.setdefault(obj.get("kind"), []).append(obj)
R["counts"]["comment_kinds"] = {k: len(v) for k, v in meta.items()}

# ---------------- G1 pairs: one JA + one VI per pair, same timing, spans rebuild VERIFIED_SOURCE
def by_name(evs, style):
    return {e["Name"].rsplit(".", 1)[0]: e for e in evs if e["kind"] == "Dialogue" and e["Style"] == style}


def visible_text(e):
    return re.sub(r"\{[^}]*\}", "", e["Text"])


ja_s, vi_s = by_name(es, "JA"), by_name(es, "VI")
ja_b, vi_b = by_name(eb, "JA"), by_name(eb, "VI")
expected = [p[0] for p in D.PAIRS]
missing_ja = [p for p in expected if p not in ja_s or p not in ja_b]
missing_vi = [p for p in expected if p not in vi_s or p not in vi_b]
mismatched = []
for pid, uid, ja, vi in D.PAIRS:
    for jj, vv in ((ja_s, vi_s), (ja_b, vi_b)):
        if pid in jj and pid in vv:
            if (jj[pid]["Start"], jj[pid]["End"]) != (vv[pid]["Start"], vv[pid]["End"]):
                mismatched.append(pid)
            if visible_text(jj[pid]) != ja:
                mismatched.append(pid + ":JAtext")
            if visible_text(vv[pid]).replace("\\N", " ") != vi.replace(" | ", " "):
                mismatched.append(pid + ":VItext")
rebuild = {}
for pid in expected:
    uid = next(p[1] for p in D.PAIRS if p[0] == pid)
    rebuild[uid] = rebuild.get(uid, "") + visible_text(ja_s[pid]).replace("\\N", "")
bad_rebuild = [u[0] for u in D.UTTS if rebuild.get(u[0]) != u[4]]
order_ok = [e["Name"].rsplit(".", 1)[0] for e in es if e["kind"] == "Dialogue" and e["Style"] == "JA"] == expected
seq = [(tsec(ja_s[p]["Start"]), tsec(ja_s[p]["End"]), p) for p in expected]
overlaps = [(a[2], b[2]) for a, b in zip(seq, seq[1:]) if a[1] > b[0] + 1e-9]
R["counts"].update(N_pairs=len(expected), N_JA=len(ja_s), N_VI=len(vi_s), N_JA_basic=len(ja_b), N_VI_basic=len(vi_b))
for name, lst in [("missing_JA_ids", missing_ja), ("missing_VI_ids", missing_vi), ("mismatched_pair_ids", mismatched),
                  ("utterances_not_rebuilt", bad_rebuild), ("caption_time_overlaps", overlaps)]:
    R["counts"][name] = lst
    if lst: err("G1/G5", f"{name}: {lst}")
if not order_ok: err("G1", "JA order differs from pair order")

# ---------------- G3/G4/G5 items vs manifest
items = {it["id"]: it for it in D.ITEMS}
mani = {m["item_id"]: m for m in meta.get("MANIFEST", [])}
card_evs = [e for e in es if e["kind"] == "Dialogue" and e["Style"] not in CAP_STYLES]
by_item = {}
for e in card_evs:
    key = e["Name"].split(".")[0]
    by_item.setdefault(key, []).append(e)
panel_evs = {e["Name"].split(".")[0]: e for e in card_evs if e["Style"] == "Panel"}
serialized_complete, item_problems = [], []
pair_start = {p: tsec(ja_s[p]["Start"]) for p in expected}
for iid, it in items.items():
    evs = {e["Name"]: e for e in by_item.get(iid, [])}
    need = [f"{iid}.BAR", f"{iid}.TAG", f"{iid}.HV", f"{iid}.MEAN"]
    for k, seg in enumerate(it["ruby"]):
        need.append(f"{iid}.B{k + 1}")
        if seg["ruby"]:
            need.append(f"{iid}.R{k + 1}")
    probs = [n for n in need if n not in evs]
    extra = [n for n in evs if n not in need]
    if extra: probs.append(f"unexpected {extra}")
    if not probs:
        times = {(e["Start"], e["End"]) for e in evs.values()}
        if len(times) != 1: probs.append("components with different timing")
        st, en = tsec(next(iter(times))[0]), tsec(next(iter(times))[1])
        if abs(st - pair_start[it["pair"]]) > 0.005: probs.append(f"start {st} != anchor cue start {pair_start[it['pair']]}")
        if en - st - 0.4 < 4.0 - 1e-6: probs.append(f"reading floor {en - st - 0.4:.2f}")
        for k, seg in enumerate(it["ruby"]):
            if visible_text(evs[f"{iid}.B{k + 1}"]) != seg["base"]: probs.append(f"B{k + 1} text")
            if seg["ruby"] and visible_text(evs[f"{iid}.R{k + 1}"]) != seg["ruby"]: probs.append(f"R{k + 1} text")
        hv = visible_text(evs[f"{iid}.HV"])
        has_kanji = any("\u4e00" <= c <= "\u9fff" for c in it["disp"])
        if has_kanji:
            if not (it.get("hv") and hv == f"[{it['hv']}]"): probs.append("HV missing for kanji item")
            if hv != hv.upper(): probs.append("HV not uppercase")
            kanji_runs = [seg for seg in it["ruby"] if any("\u4e00" <= c <= "\u9fff" for c in seg["base"])]
            if any(not seg["ruby"] for seg in kanji_runs): probs.append("kanji run without ruby")
        else:
            if hv != "CHỈ KANA": probs.append("kana-only notice wrong")
        if re.search(r"ÂHV|ÄHV|HV:", hv): probs.append("forbidden HV label")
        if iid not in mani: probs.append("no manifest")
        # panel covering the item
        pn = mani.get(iid, {}).get("panel")
        if pn not in panel_evs: probs.append("no panel")
        else:
            pa, pb = tsec(panel_evs[pn]["Start"]), tsec(panel_evs[pn]["End"])
            if not (pa <= st + 1e-9 and pb >= en - 1e-9): probs.append("panel does not cover item")
    if probs: item_problems.append((iid, probs))
    else: serialized_complete.append(iid)
R["counts"]["items_expected"] = len(items)
R["counts"]["items_serialized_complete"] = len(serialized_complete)
R["counts"]["item_problems"] = item_problems
if item_problems: err("G3/G4", f"item problems: {item_problems}")
R["counts"]["vocab_required"] = sum(1 for i in items.values() if i["cat"] == "V")
R["counts"]["grammar_required"] = sum(1 for i in items.values() if i["cat"] == "G")
R["counts"]["kanji_items"] = sum(1 for i in items.values() if any("\u4e00" <= c <= "\u9fff" for c in i["disp"]))
R["counts"]["kana_only_items"] = sum(1 for i in items.values() if not any("\u4e00" <= c <= "\u9fff" for c in i["disp"]))
R["counts"]["ledger_excluded_rows"] = len(meta.get("LEDGER_EXCLUDED", []))

# ---------------- G7 render checks with libass on the real 1920x1080 canvas
RD = Renderer(1920, 1080)
head = tst.split("[Events]")[0] + "[Events]\nFormat: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text\n"


def render_events(evlist, t):
    return RD.render(head + "\n".join(e["raw"] for e in evlist) + "\n", int(round(t * 1000)))


def nz_bbox(mask, thr=0.04):
    ys, xs = np.where(mask > thr)
    if len(xs) == 0: return None
    return (int(xs.min()), int(ys.min()), int(xs.max()) + 1, int(ys.max()) + 1)


cap_by_pair = {}
for e in es:
    if e["kind"] == "Dialogue" and e["Style"] in CAP_STYLES:
        cap_by_pair.setdefault(e["Name"].split(".")[0], []).append(e)
geo_pairs, gap_fail, clip_fail = {}, [], []
for pid in expected:
    st, en = tsec(ja_s[pid]["Start"]), tsec(ja_s[pid]["End"])
    t = (st + en) / 2
    bja, mja = render_events([ja_s[pid]], t)
    bvi, mvi = render_events([vi_s[pid]], t)
    ball, mall = render_events(cap_by_pair[pid], t)
    geo_pairs[pid] = dict(ja=bja, vi=bvi, all=ball, t=t)
    if bja is None or bvi is None: err("G7", f"{pid} not visible"); continue
    if bja[3] + 10 > bvi[1]: gap_fail.append((pid, bja[3], bvi[1]))
    for b in (bja, bvi, ball):
        if b[0] < 20 or b[1] < 20 or b[2] > 1900 or b[3] > 1076: clip_fail.append((pid, b))
    # composite check: JA/VI rendered together keep their individual boxes (no collision displacement)
    bboth, _ = render_events([ja_s[pid], vi_s[pid]], t)
    if bboth != (min(bja[0], bvi[0]), min(bja[1], bvi[1]), max(bja[2], bvi[2]), max(bja[3], bvi[3])):
        err("G7", f"{pid} composite bbox differs (collision shift?)")
R["counts"]["pairs_rendered"] = len(geo_pairs)
if gap_fail: err("G7", f"JA/VI gap < 10px: {gap_fail}")
if clip_fail: err("G7", f"caption near/over frame edge: {clip_fail}")

# items: every component visible, inside its panel, ruby above + centred on base, no component overlaps
lay_panels = {}
for e in card_evs:
    if e["Style"] == "Panel":
        m = re.search(r"\\pos\(([\d.]+),([\d.]+)\)", e["Text"])
        lay_panels[e["Name"].split(".")[0]] = e
item_fail, ruby_fail, overlap_fail = [], [], []
geo_items = {}
for iid, it in items.items():
    evs = {e["Name"]: e for e in by_item[iid]}
    pn = mani[iid]["panel"]
    st, en = tsec(evs[f"{iid}.BAR"]["Start"]), tsec(evs[f"{iid}.BAR"]["End"])
    t = st + 0.6
    pb, _ = render_events([panel_evs[pn]], t)
    comps = {}
    for name, e in evs.items():
        b, m = render_events([e], t)
        if b is None: item_fail.append((iid, name, "invisible")); continue
        comps[name] = (b, m)
        if not (pb[0] <= b[0] and pb[1] <= b[1] and b[2] <= pb[2] and b[3] <= pb[3]):
            item_fail.append((iid, name, "outside panel", b, pb))
    for k, seg in enumerate(it["ruby"]):
        if seg["ruby"]:
            rb, bb = comps.get(f"{iid}.R{k + 1}"), comps.get(f"{iid}.B{k + 1}")
            if rb and bb:
                rb, bb = rb[0], bb[0]
                if rb[3] > bb[1] - 1: ruby_fail.append((iid, k + 1, "not above", rb, bb))
                cr, cb = (rb[0] + rb[2]) / 2, (bb[0] + bb[2]) / 2
                if abs(cr - cb) > 2.5: ruby_fail.append((iid, k + 1, "not centred", round(cr - cb, 1)))
    # pairwise overlap of text components (bar excluded)
    names = [n for n in comps if not n.endswith(".BAR")]
    for i in range(len(names)):
        for j in range(i + 1, len(names)):
            a, b = comps[names[i]][1], comps[names[j]][1]
            inter = float(np.minimum(a, b).sum())
            if inter > 3.0: overlap_fail.append((iid, names[i], names[j], round(inter, 1)))
    # ruby runs must not overlap neighbouring base kana beyond 3 px (checked as bbox overlap with other base runs)
    for k, seg in enumerate(it["ruby"]):
        if not seg["ruby"]: continue
        rb = comps[f"{iid}.R{k + 1}"][0]
        for k2, seg2 in enumerate(it["ruby"]):
            if k2 == k: continue
            bb = comps[f"{iid}.B{k2 + 1}"][0]
            ov = min(rb[2], bb[2]) - max(rb[0], bb[0])
            if ov > 4 and rb[3] > bb[1] - 1: ruby_fail.append((iid, k + 1, f"over B{k2 + 1}", ov))
    geo_items[iid] = dict(t=t, panel=pb)
R["counts"]["items_rendered"] = len(geo_items)
for nm, lst in [("item_component_fail", item_fail), ("ruby_fail", ruby_fail), ("component_overlap", overlap_fail)]:
    R["counts"][nm] = lst
    if lst: err("G7", f"{nm}: {lst[:6]}")

# collisions over time: caption box vs panels, panel vs panel (rects), panels vs protected slide zones
def rect_of_drawing(e):
    b, _ = render_events([e], (tsec(e["Start"]) + tsec(e["End"])) / 2)
    return b


panel_rects = {k: rect_of_drawing(e) for k, e in panel_evs.items()}
box_rects = {e["Name"].split(".")[0]: rect_of_drawing(e) for e in es if e["kind"] == "Dialogue" and e["Style"] == "SubBox"}
chip_rects = {e["Name"].split(".")[0]: rect_of_drawing(e) for e in es if e["kind"] == "Dialogue" and e["Style"] == "SpkBox"}


def inter(a, b, pad=0):
    return not (a[2] + pad <= b[0] or b[2] + pad <= a[0] or a[3] + pad <= b[1] or b[3] + pad <= a[1])


coll = []
for pk, pe in panel_evs.items():
    pa, pb_ = tsec(pe["Start"]), tsec(pe["End"])
    for pid in expected:
        ca, cb = tsec(ja_s[pid]["Start"]), tsec(ja_s[pid]["End"])
        if ca < pb_ and cb > pa:
            if inter(panel_rects[pk], box_rects[pid], 6): coll.append((pk, pid, "box"))
            if pid in chip_rects and inter(panel_rects[pk], chip_rects[pid], 6): coll.append((pk, pid, "chip"))
    for qk, qe_ in panel_evs.items():
        if qk <= pk: continue
        qa, qb = tsec(qe_["Start"]), tsec(qe_["End"])
        if qa < pb_ and qb > pa and inter(panel_rects[pk], panel_rects[qk], 4): coll.append((pk, qk, "panel"))
# protected slide zones (from 1080p frames of the source): header pill, question number, 1番 digits row, 2番 options (question part)
ZONES = [("header", (530, 100, 1420, 210), 2197.7, 2545), ("q-number", (195, 140, 395, 270), 2197.7, 2545),
         ("instr-title", (100, 120, 710, 250), 2161.2, 2197.7),
         ("q1-digits", (530, 320, 1400, 440), 2197.7, 2339.8), ("instr-text", (100, 370, 1770, 660), 2161.2, 2197.7),
         ("q2-options", (330, 300, 1560, 900), 2503.0, 2540.2)]
zone_hits = []
for pk, pe in panel_evs.items():
    pa, pb_ = tsec(pe["Start"]), tsec(pe["End"])
    for zn, zr, za, zb in ZONES:
        if pa < zb and pb_ > za and inter(panel_rects[pk], zr): zone_hits.append((pk, zn))
for pid in expected:
    ca, cb = tsec(ja_s[pid]["Start"]), tsec(ja_s[pid]["End"])
    for zn, zr, za, zb in ZONES:
        if ca < zb and cb > za and inter(box_rects[pid], zr): zone_hits.append((pid, zn))
R["counts"]["collisions"] = coll
R["counts"]["protected_zone_hits"] = zone_hits
if coll: err("G7", f"collisions: {coll}")
if zone_hits: err("G7", f"protected slide zones covered: {zone_hits}")
decor = []
MASCOT = (1470, 740, 1810, 1050)
for pk, pe in panel_evs.items():
    if inter(panel_rects[pk], MASCOT): decor.append(pk)
R["warnings"].append(f"decorative mascot partially covered by panels: {decor}")
q2_dialog_cover = [pk for pk, pe in panel_evs.items() if tsec(pe["Start"]) >= 2344.8 and inter(panel_rects[pk], (330, 300, 1560, 900))]
R["warnings"].append(f"2番 printed options covered during the dialogue (not during 質問1/2) by panels: {len(q2_dialog_cover)}")

# ---------------- gates
G = R["gates"]
G["G1"] = "PASS" if not (missing_ja or missing_vi or mismatched or bad_rebuild) else "FAIL"
G["G3"] = "PASS" if not item_problems else "FAIL"
G["G4"] = "PASS" if not item_problems else "FAIL"
G["G5"] = "PASS" if not (overlaps or item_problems) else "FAIL"
G["G6"] = "PASS" if (same_info and identical_caps and not card_in_basic and not any(e.startswith("G6") for e in R["errors"])) else "FAIL"
G["G7_geometry"] = "PASS" if not any(e.startswith("G7") for e in R["errors"]) else "FAIL"
for p in (BASIC, STUDY):
    raw = open(p, "rb").read()
    R.setdefault("files", {})[os.path.basename(p)] = dict(bytes=len(raw), sha256=hashlib.sha256(raw).hexdigest())
json.dump(R, open(REPORT, "w", encoding="utf-8"), ensure_ascii=False, indent=1, default=str)
print(json.dumps(R["gates"], ensure_ascii=False))
print("errors:", len(R["errors"]))
for e in R["errors"][:30]: print("  ", e[:400])
for w in R["warnings"]: print("  WARN", w)
print({k: v for k, v in R["counts"].items() if not isinstance(v, list) or len(v) < 8})
