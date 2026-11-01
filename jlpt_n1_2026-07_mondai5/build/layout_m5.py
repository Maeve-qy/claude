# -*- coding: utf-8 -*-
"""Layout + ASS writer for 2026.07 問題5.
usage: python layout_m5.py <timing.json> <out_dir>
Writes <out_dir>/2026.07.vi.ass, <out_dir>/2026.07.vi-ja-study.ass and <out_dir>/layout.json.
All text extents are measured with libass itself (assr.py) on an unclipped 3840x1600 canvas (scale 1:1)."""
import sys, os, json, math, hashlib, re
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import data_m5 as D
from assr import Renderer

TIMING, OUTDIR = sys.argv[1], sys.argv[2]
os.makedirs(OUTDIR, exist_ok=True)
T = json.load(open(TIMING, encoding="utf-8"))
PT = {p["pid"]: p for p in T["pairs"]}
PAIRS = D.PAIRS
UTT = {u[0]: u for u in D.UTTS}

PLAY_W, PLAY_H = 1920, 1080
DUR = D.SOURCE["duration"]
Q_LIMIT = math.floor(DUR * 100) / 100


def qs(t):
    return math.ceil(round(t * 100, 6)) / 100.0


def qe(t):
    return min(qs(t), Q_LIMIT)


def ts(t):
    cs = int(round(t * 100))
    return f"{cs // 360000}:{(cs // 6000) % 60:02d}:{(cs // 100) % 60:02d}.{cs % 100:02d}"


# ---------------------------------------------------------------- styles (profile 1080p, sizes >= master floors)
STYLE_FMT = ("Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, "
             "Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, "
             "MarginL, MarginR, MarginV, Encoding")
STYLES = [
    # name, font, size, primary, outline colour, outline, align
    ("SubBox", "Noto Sans", 20, "&H30140F0A", "&H00000000", 0, 7),
    ("SpkBox", "Noto Sans", 20, "&H00FFFFFF", "&H00000000", 0, 7),
    ("Spk", "Noto Sans CJK JP", 32, "&H00161210", "&H00000000", 0, 5),
    ("JA", "Noto Sans CJK JP", 58, "&H00F7F7F7", "&H00141414", 2.5, 2),
    ("VI", "Noto Sans", 64, "&H00B8D4FF", "&H00141414", 3.6, 2),
    ("Panel", "Noto Sans", 20, "&H26140C08", "&H802E2218", 2, 7),
    ("Bar", "Noto Sans", 20, "&H186EC8F5", "&H00000000", 0, 7),
    ("JP_Base", "Noto Sans CJK JP", 50, "&H00F5FAFF", "&H00141414", 1.2, 2),
    ("JP_Ruby", "Noto Sans CJK JP", 28, "&H0090D4F5", "&H00141414", 0.8, 2),
    ("Tag", "Noto Sans CJK JP", 26, "&H0080D8F8", "&H00141414", 0, 4),
    ("HV", "Noto Sans", 34, "&H00F0DCA0", "&H00141414", 0.8, 7),
    ("Mean", "Noto Sans", 36, "&H00DCEEF4", "&H00141414", 0.8, 7),
]
SIZE = {s[0]: s[2] for s in STYLES}


def style_lines():
    out = []
    for name, font, size, prim, outc, outl, align in STYLES:
        out.append(f"Style: {name},{font},{size},{prim},&H000000FF,{outc},&H00000000,0,0,0,0,100,100,0,0,1,"
                   f"{outl:g},0,{align},90,90,40,1")
    return out


def header(playx, playy, title):
    return "\n".join([
        "[Script Info]",
        f"Title: {title}",
        "ScriptType: v4.00+",
        f"PlayResX: {playx}",
        f"PlayResY: {playy}",
        "WrapStyle: 2",
        "ScaledBorderAndShadow: yes",
        "YCbCr Matrix: TV.709",
        "",
        "[V4+ Styles]",
        f"Format: {STYLE_FMT}",
        *style_lines(),
        "",
        "[Events]",
        "Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text",
    ]) + "\n"


# ---------------------------------------------------------------- measurement with libass (unclipped canvas)
MW, MH = 3840, 1600
RM = Renderer(MW, MH)
MHDR = header(MW, MH, "measure")
_mcache = {}


def anchor_x(an):
    return {1: 200, 4: 200, 7: 200, 2: MW // 2, 5: MW // 2, 8: MW // 2}.get(an, MW - 200)


def measure(style, text, an=7, x=None, y=600):
    """ink bbox (x0,y0,x1,y1) of text rendered at \\an{an}\\pos(x,y), absolute coords on the measuring canvas."""
    x = anchor_x(an) if x is None else x
    key = (style, text, an, x, y)
    if key not in _mcache:
        ev = f"Dialogue: 0,0:00:00.00,0:00:05.00,{style},,0,0,0,,{{\\an{an}\\pos({x},{y})}}{text}\n"
        bbox, _ = RM.render(MHDR + ev, 1000)
        assert bbox is not None, (style, text)
        assert 2 < bbox[0] and bbox[2] < MW - 2 and 2 < bbox[1] and bbox[3] < MH - 2, ("touches canvas edge", style, text, bbox)
        _mcache[key] = bbox
    return _mcache[key]


def rel(style, text, an):
    x0, y0, x1, y1 = measure(style, text, an)
    ax = anchor_x(an)
    return x0 - ax, y0 - 600, x1 - ax, y1 - 600


# canvas-clip self test (master 8.5): a deliberately long line must measure wider than the 1920 viewport
_long = "あ" * 60
_b = measure("JA", _long, 7, 100, 300)
assert _b[2] - _b[0] > 1920, "measurement canvas clips"

CJK_ADV = {s: SIZE[s] / 1.448 for s in ("JA", "JP_Base", "JP_Ruby", "Spk", "Tag")}  # Noto Sans CJK JP em = size/1.448


def is_fullwidth(ch):
    o = ord(ch)
    return (0x3000 <= o <= 0x30FF) or (0x4E00 <= o <= 0x9FFF) or (0xFF00 <= o <= 0xFFEF) or o in (0x301C,)


def cjk_width(style, s):
    assert all(is_fullwidth(c) for c in s), ("non full-width char in", s)
    return len(s) * CJK_ADV[style]


# ---------------------------------------------------------------- drawing helpers
def rrect(w, h, r):
    w, h, r = round(w, 1), round(h, 1), min(r, w / 2, h / 2)
    k = round(0.5523 * r, 2)
    f = lambda v: f"{v:g}"
    return (f"m {f(r)} 0 l {f(w - r)} 0 b {f(w - r + k)} 0 {f(w)} {f(r - k)} {f(w)} {f(r)} "
            f"l {f(w)} {f(h - r)} b {f(w)} {f(h - r + k)} {f(w - r + k)} {f(h)} {f(w - r)} {f(h)} "
            f"l {f(r)} {f(h)} b {f(r - k)} {f(h)} 0 {f(h - r + k)} 0 {f(h - r)} "
            f"l 0 {f(r)} b 0 {f(r - k)} {f(r - k)} 0 {f(r)} 0")


def rect(w, h):
    return f"m 0 0 l {w:g} 0 l {w:g} {h:g} l 0 {h:g}"


# ---------------------------------------------------------------- bilingual block layout
VI_MAXW, JA_MAXW = 1720, 1700
GAP = 14                 # bottom(bbox_JA) + GAP <= top(bbox_VI)
PADX, PADT, PADB = 30, 14, 12
VI_INK_BOTTOM = PLAY_H - 34
SPEC_X = {"P041": 330}   # 2番 announced while the source shows the 1番 script frame: keep bottom-left free zone


def wrap_vi(text):
    flat = text.replace(" | ", " ")
    if rel("VI", flat, 7)[2] - rel("VI", flat, 7)[0] <= VI_MAXW:
        return flat
    if " | " in text:   # break by meaning, chosen by the translator
        lines = text.split(" | ")
        assert all(rel("VI", l, 7)[2] - rel("VI", l, 7)[0] <= VI_MAXW for l in lines), ("hinted line too wide", text)
        return "\\N".join(lines)
    text = flat
    words = text.split(" ")
    best = None
    for i in range(1, len(words)):
        a, b = " ".join(words[:i]), " ".join(words[i:])
        wa = rel("VI", a, 7); wb = rel("VI", b, 7)
        m = max(wa[2] - wa[0], wb[2] - wb[0])
        bonus = -60 if a.endswith((",", ";", ":", "–")) else 0
        score = m + bonus
        if m <= VI_MAXW and (best is None or score < best[0]):
            best = (score, a + "\\N" + b)
    assert best, ("cannot wrap", text)
    return best[1]


def layout_pair(pid, ja, vi):
    cx = SPEC_X.get(pid, 960)
    vi_t = wrap_vi(vi)
    for line in ja.split("\\N"):
        w = rel("JA", line, 7); assert w[2] - w[0] <= JA_MAXW, ("JA too wide", pid, line)
    bvi = rel("VI", vi_t, 2)
    vi_y = VI_INK_BOTTOM - bvi[3]
    vi_box = (cx + bvi[0], vi_y + bvi[1], cx + bvi[2], vi_y + bvi[3])
    bja = rel("JA", ja, 2)
    ja_y = (vi_box[1] - GAP) - bja[3]
    ja_box = (cx + bja[0], ja_y + bja[1], cx + bja[2], ja_y + bja[3])
    box = (min(ja_box[0], vi_box[0]) - PADX, ja_box[1] - PADT, max(ja_box[2], vi_box[2]) + PADX, vi_box[3] + PADB)
    return dict(cx=cx, vi_text=vi_t, vi_pos=(cx, vi_y), vi_bbox=vi_box, ja_pos=(cx, ja_y), ja_bbox=ja_box, box=box,
                ja_lines=ja.count("\\N") + 1, vi_lines=vi_t.count("\\N") + 1)


def speaker_chip(spk, box):
    sp = D.SPEAKERS[spk]
    if not sp["ja"]:
        return None
    label = sp["ja"]
    sb = rel("Spk", label, 5)
    tw = sb[2] - sb[0]
    cw, ch = tw + 30, 44
    x = box[0] + 18; y = box[1] - ch + 8   # tab on the top-left edge of the caption box (same place for every speaker)
    mode = "tab"
    return dict(label=label, x=round(x, 1), y=round(y, 1), w=round(cw, 1), h=ch, color=sp["color"], mode=mode,
                bbox=(x, y, x + cw, y + ch))


PL = {}
for pid, uid, ja, vi in PAIRS:
    tm = PT[pid]
    L = layout_pair(pid, ja, vi)
    L.update(pid=pid, uid=uid, spk=UTT[uid][1], ja=ja, vi=vi, start=qs(tm["start"]), end=qe(tm["end"]))
    L["chip"] = speaker_chip(L["spk"], L["box"])
    top = L["box"][1]
    if L["chip"] and L["chip"]["mode"] == "tab":
        top = min(top, L["chip"]["y"])
    L["block_top"] = top
    PL[pid] = L

# ---------------------------------------------------------------- study cards
CTX = [("instr", 2161.2, 2197.7), ("q1", 2197.7, 2339.8), ("script1", 2339.8, 2344.8), ("q2", 2344.8, 2540.2)]
LANES = {
    "instr": [dict(name="R", x=1000, w=790, top=40, bottom=372, relax=372)],
    "q1": [dict(name="L", x=200, w=790, top=448, bottom=1040, relax=1040),
           dict(name="R", x=1010, w=790, top=448, bottom=736, relax=1040)],
    "q2": [dict(name="L", x=200, w=790, top=286, bottom=1040, relax=1040),
           dict(name="R", x=1010, w=790, top=286, bottom=736, relax=1040)],
}
NO_CARDS_AFTER = {"q2": 2503.0}  # 質問1/質問2 + answer pauses: keep the printed options fully visible


def ctx_of(t):
    for name, a, b in CTX:
        if a <= t < b:
            return name, b
    return None, None


PAD_T, PAD_B, ITEM_GAP = 22, 22, 18
TEXT_X, RIGHT_PAD = 40, 30
FADE = 0.20


def hv_display(it):
    if it.get("hv"):
        return f"[{it['hv']}]", False
    return "CHỈ KANA", True


def tag_text(it):
    return "{\\fnNoto Sans CJK JP}" + it["pos"] + "{\\fnNoto Sans} · " + it["label"]


def wrap_mean(text, maxw):
    b = rel("Mean", text, 7)
    if b[2] - b[0] <= maxw:
        return text, 1
    words = text.split(" ")
    best = None
    for i in range(1, len(words)):
        a, c = " ".join(words[:i]), " ".join(words[i:])
        wa, wc = rel("Mean", a, 7), rel("Mean", c, 7)
        m = max(wa[2] - wa[0], wc[2] - wc[0])
        if m <= maxw and (best is None or m < best[0]):
            best = (m, a + "\\N" + c)
    assert best, ("cannot wrap meaning", text)
    return best[1], 2


# per-style vertical ink offsets for \an2 (bottom anchored) and \an7 (top anchored)
OFF_R = rel("JP_Ruby", "きゃく漢", 2)
OFF_B = rel("JP_Base", "漢字かな", 2)
OFF_HV = rel("HV", "[ẶNG VIỄN]", 7)
OFF_M = rel("Mean", "Ặg ẫy", 7)


def item_geometry(it, w):
    """component layout relative to item top-left (x relative to panel x). Returns dict with height and components."""
    inner = w - TEXT_X - RIGHT_PAD
    has_ruby = any(seg["ruby"] for seg in it["ruby"])
    comps = []
    y = 0
    # ruby + base runs: base runs contiguous; each ruby centred on its own base run; gaps inserted only where a
    # ruby would collide with the neighbouring ruby (min 3 px) or overhang a neighbouring kana run by > 3 px.
    segs = []
    for seg in it["ruby"]:
        bw = cjk_width("JP_Base", seg["base"])
        rw = cjk_width("JP_Ruby", seg["ruby"]) if seg["ruby"] else 0.0
        segs.append(dict(base=seg["base"], ruby=seg["ruby"], bw=bw, rw=rw, x=0.0))
    x = 0.0
    for j, sg in enumerate(segs):
        sg["x"] = x
        if j > 0:
            pv = segs[j - 1]
            if sg["rw"]:
                rl = sg["x"] + sg["bw"] / 2 - sg["rw"] / 2
                if pv["rw"]:
                    prr = pv["x"] + pv["bw"] / 2 + pv["rw"] / 2
                    need = prr + 3 - rl
                else:
                    need = (pv["x"] + pv["bw"] - 3) - rl
                if need > 0:
                    sg["x"] += need
            elif pv["rw"]:
                prr = pv["x"] + pv["bw"] / 2 + pv["rw"] / 2
                need = (prr - 3) - sg["x"]
                if need > 0:
                    sg["x"] += need
        x = sg["x"] + sg["bw"]
    # keep the first ruby from sticking out left of the text column
    lead = 0.0
    for sg in segs:
        if sg["rw"]:
            lead = max(lead, -(sg["x"] + sg["bw"] / 2 - sg["rw"] / 2) - 3)
    cells = []
    for sg in segs:
        cells.append(dict(base=sg["base"], ruby=sg["ruby"], x=TEXT_X + lead + sg["x"], w=sg["bw"], bw=sg["bw"], rw=sg["rw"]))
    x = TEXT_X + lead + (segs[-1]["x"] + segs[-1]["bw"])
    base_w = x - TEXT_X
    ruby_ink_h = OFF_R[3] - OFF_R[1]
    base_ink_h = OFF_B[3] - OFF_B[1]
    if has_ruby:
        ruby_ink_top = 0
        base_ink_top = ruby_ink_h + 4
    else:
        ruby_ink_top = None
        base_ink_top = 0
    base_y = base_ink_top - OFF_B[1]  # \an2 y such that ink top = base_ink_top
    ruby_y = (ruby_ink_top - OFF_R[1]) if has_ruby else None
    for i, c in enumerate(cells):
        cxm = c["x"] + c["w"] / 2
        comps.append(dict(role="base", k=i, style="JP_Base", an=2, x=cxm, y=base_y, text=c["base"]))
        if c["ruby"]:
            comps.append(dict(role="ruby", k=i, style="JP_Ruby", an=2, x=cxm, y=ruby_y, text=c["ruby"], base=c["base"]))
    base_ink_bottom = base_ink_top + base_ink_h
    # tag: right of base on the same row if it fits, else own row
    tt = tag_text(it)
    tb = rel("Tag", tt, 4)
    tag_w = tb[2] - tb[0]
    if TEXT_X + base_w + 22 + tag_w <= w - RIGHT_PAD:
        tag_x, tag_y = TEXT_X + base_w + 22, base_ink_top + base_ink_h / 2
        row_bottom = base_ink_bottom
    else:
        tag_x, tag_y = TEXT_X, base_ink_bottom + 8 + (tb[3] - tb[1]) / 2 - (tb[1] + tb[3]) / 2 + (tb[3] - tb[1]) / 2
        row_bottom = base_ink_bottom + 8 + (tb[3] - tb[1])
    comps.append(dict(role="tag", style="Tag", an=4, x=tag_x, y=tag_y, text=tt))
    hv, kana_only = hv_display(it)
    hv_ink_top = row_bottom + 10
    hv_y = hv_ink_top - OFF_HV[1]
    hvb = rel("HV", hv, 7)
    assert hvb[2] - hvb[0] <= inner, ("HV too wide", it["id"])
    comps.append(dict(role="hv", style="HV", an=7, x=TEXT_X, y=hv_y, text=hv, kana_only=kana_only))
    hv_ink_bottom = hv_y + hvb[3]
    mean_t, nlines = wrap_mean(it["mean"], inner)
    m_ink_top = hv_ink_bottom + 8
    m_y = m_ink_top - OFF_M[1]
    mb = rel("Mean", mean_t, 7)
    comps.append(dict(role="mean", style="Mean", an=7, x=TEXT_X, y=m_y, text=mean_t, lines=nlines))
    height = m_y + mb[3]
    return dict(h=math.ceil(height), comps=comps, base_w=base_w, has_ruby=has_ruby, kana_only=kana_only,
                cells=cells, mean_lines=nlines)


def req_visible(it):
    return max(4.0, 1.8 + len(it["mean"]) / 16.0 + len(it.get("hv") or "") / 30.0)


ITEMS = []
for it in D.ITEMS:
    p = PL[it["pair"]]
    d = dict(it)
    d["start"] = p["start"]            # ANCHOR_PRECISION = CUE (start of anchor cue)
    d["source_end"] = p["end"]
    d["req"] = round(req_visible(it), 2)
    d["ctx"], d["ctx_end"] = ctx_of(d["start"])
    ITEMS.append(d)
ITEMS.sort(key=lambda d: (d["start"], d["id"]))

GEO = {}
for it in ITEMS:
    GEO[it["id"]] = item_geometry(it, 790)


def pairs_overlapping(a, b):
    return [p for p in PL.values() if p["start"] < b and p["end"] > a]


def panel_height(items):
    return PAD_T + sum(GEO[i["id"]]["h"] for i in items) + ITEM_GAP * (len(items) - 1) + PAD_B


BASE_SEC = {1: 6.0, 2: 8.0, 3: 10.0}


def panel_end(pn):
    its = pn["items"]
    e = max(pn["start"] + BASE_SEC[len(its)], max(i["source_end"] for i in its),
            max(i["start"] + i["req"] + 2 * FADE for i in its))
    lim = its[0]["ctx_end"] - 0.05
    if its[0]["ctx"] in NO_CARDS_AFTER:
        lim = min(lim, NO_CARDS_AFTER[its[0]["ctx"]])
    return round(min(e, lim, Q_LIMIT), 2)


def fits(pn, lane_bottom):
    h = panel_height(pn["items"])
    bottom = pn["lane"]["top"] + h
    lim = lane_bottom
    for p in pairs_overlapping(pn["start"], pn["end"]):
        lim = min(lim, p["block_top"] - 14)
    return bottom <= lim, bottom, lim


panels, conflicts = [], []
lane_last = {}


def try_place(it, relaxed):
    lanes = LANES[it["ctx"]]
    # 1) join an open panel (same ctx, <=4.0 s spread, <=3 items)
    for pn in panels:
        if pn["ctx"] != it["ctx"] or lane_last.get((pn["ctx"], pn["lane"]["name"])) is not pn:
            continue
        if pn["end"] <= it["start"] or it["start"] - pn["start"] > 4.0 or len(pn["items"]) >= 3:
            continue
        cand = dict(pn, items=pn["items"] + [it])
        cand["end"] = panel_end(cand)
        ok, _, _ = fits(cand, pn["lane"]["relax" if relaxed else "bottom"])
        if ok:
            pn["items"].append(it); pn["end"] = cand["end"]; pn["relaxed"] = pn.get("relaxed") or relaxed
            return True
    # 2) new panel in a free lane (or cut the previous panel if every item keeps its reading floor)
    for lane in lanes:
        key = (it["ctx"], lane["name"])
        last = lane_last.get(key)
        cut_to = None
        if last is not None and last["end"] > it["start"] - 0.02:
            t_cut = round(it["start"] - 0.04, 2)
            if all(t_cut - i["start"] >= i["req"] + 2 * FADE for i in last["items"]) and \
                    all(t_cut >= i["source_end"] for i in last["items"]):
                cut_to = t_cut
            else:
                continue
        pn = dict(id=f"PN{len(panels) + 1:02d}", ctx=it["ctx"], lane=lane, start=it["start"], items=[it])
        pn["end"] = panel_end(pn)
        ok, _, _ = fits(pn, lane["relax" if relaxed else "bottom"])
        if not ok:
            continue
        if cut_to is not None:
            last["end"] = cut_to; last["cut"] = True
        pn["relaxed"] = relaxed
        panels.append(pn); lane_last[key] = pn
        return True
    return False


for it in ITEMS:
    assert it["ctx"] in LANES, ("item outside card contexts", it["id"], it["start"])
    if not try_place(it, False) and not try_place(it, True):
        conflicts.append(dict(item=it["id"], start=it["start"], pair=it["pair"]))

# final verification of lane non-overlap and geometry
for pn in panels:
    pn["h"] = panel_height(pn["items"])
    pn["y"] = pn["lane"]["top"]
    ok, bottom, lim = fits(pn, pn["lane"]["relax"] if pn.get("relaxed") else pn["lane"]["bottom"])
    assert ok, ("panel no longer fits", pn["id"], bottom, lim)
for key in set((p["ctx"], p["lane"]["name"]) for p in panels):
    seq = sorted([p for p in panels if (p["ctx"], p["lane"]["name"]) == key], key=lambda p: p["start"])
    for a, b in zip(seq, seq[1:]):
        assert a["end"] <= b["start"], ("lane overlap", a["id"], b["id"])
for pn in panels:
    for i in pn["items"]:
        vis = pn["end"] - i["start"] - 2 * FADE
        assert vis >= 4.0 - 1e-6, ("reading floor", i["id"], vis)

# ---------------------------------------------------------------- serialize
def dlg(layer, start, end, style, name, text):
    return f"Dialogue: {layer},{ts(start)},{ts(end)},{style},{name},0,0,0,,{text}"


def cmt(name, obj):
    s = json.dumps(obj, ensure_ascii=False, separators=(",", ":"))
    assert "\n" not in s
    return f"Comment: 0,0:00:00.00,0:00:00.00,JA,{name},0,0,0,,{s}"


def f1(v):
    return f"{round(v, 1):g}"


caption_events = []
for pid, uid, ja, vi in PAIRS:
    L = PL[pid]
    st, en = L["start"], L["end"]
    bx = L["box"]
    caption_events.append(dlg(0, st, en, "SubBox", f"{pid}.BOX",
                              f"{{\\an7\\pos({f1(bx[0])},{f1(bx[1])})\\p1}}{rrect(bx[2] - bx[0], bx[3] - bx[1], 16)}{{\\p0}}"))
    ch = L["chip"]
    if ch:
        caption_events.append(dlg(1, st, en, "SpkBox", f"{pid}.SPKBOX",
                                  f"{{\\an7\\pos({f1(ch['x'])},{f1(ch['y'])})\\1c{ch['color']}\\p1}}{rrect(ch['w'], ch['h'], 10)}{{\\p0}}"))
        caption_events.append(dlg(2, st, en, "Spk", f"{pid}.SPK",
                                  f"{{\\an5\\pos({f1(ch['x'] + ch['w'] / 2)},{f1(ch['y'] + ch['h'] / 2)})}}{ch['label']}"))
    caption_events.append(dlg(1, st, en, "JA", f"{pid}.JA", f"{{\\an2\\pos({f1(L['ja_pos'][0])},{f1(L['ja_pos'][1])})}}{ja}"))
    caption_events.append(dlg(1, st, en, "VI", f"{pid}.VI", f"{{\\an2\\pos({f1(L['vi_pos'][0])},{f1(L['vi_pos'][1])})}}{L['vi_text']}"))

card_events, manifest = [], []
for pn in panels:
    lane = pn["lane"]
    px, py = lane["x"], pn["y"]
    card_events.append(dlg(2, pn["start"], pn["end"], "Panel", f"{pn['id']}.PANEL",
                           f"{{\\an7\\pos({px},{py})\\fad(200,200)\\p1}}{rrect(lane['w'], pn['h'], 18)}{{\\p0}}"))
    y = py + PAD_T
    pn["item_y"] = {}
    for it in pn["items"]:
        g = GEO[it["id"]]
        pn["item_y"][it["id"]] = y
        st, en = it["start"], pn["end"]
        ev_ids = []
        name = f"{it['id']}.BAR"
        card_events.append(dlg(3, st, en, "Bar", name,
                               f"{{\\an7\\pos({px + 14},{f1(y)})\\fad(200,200)\\p1}}{rect(6, g['h'])}{{\\p0}}"))
        ev_ids.append(name)
        for c in g["comps"]:
            if c["role"] in ("base", "ruby"):
                name = f"{it['id']}.{'B' if c['role'] == 'base' else 'R'}{c['k'] + 1}"
            else:
                name = f"{it['id']}.{c['role'].upper()}"
            txt = c["text"]
            extra = "\\1c&H00B0B0B0&" if c.get("kana_only") else ""
            card_events.append(dlg(4, st, en, c["style"], name,
                                   f"{{\\an{c['an']}\\pos({f1(px + c['x'])},{f1(y + c['y'])})\\fad(200,200){extra}}}{txt}"))
            ev_ids.append(name)
        manifest.append(dict(item_id=it["id"], panel=pn["id"], lane=lane["name"], ctx=pn["ctx"], start=st, end=en,
                             event_ids=ev_ids,
                             base_run_ids=[e for e in ev_ids if re.search(r"\.B\d+$", e)],
                             ruby_run_ids=[e for e in ev_ids if re.search(r"\.R\d+$", e)],
                             ruby_to_base={f"{it['id']}.R{c['k'] + 1}": f"{it['id']}.B{c['k'] + 1}" for c in g["comps"] if c["role"] == "ruby"},
                             tag_event_ids=[f"{it['id']}.TAG"], hv_event_ids_or_applicability_notice=[f"{it['id']}.HV"],
                             mean_event_ids=[f"{it['id']}.MEAN"]))
        y += g["h"] + ITEM_GAP

# ---------------------------------------------------------------- metadata (study file only)
cursor = {}
bil_meta = []
for pid, uid, ja, vi in PAIRS:
    plain = ja.replace("\\N", "")
    a = cursor.get(uid, 0); cursor[uid] = a + len(plain)
    L = PL[pid]
    bil_meta.append(dict(pair_id=pid, source_cue_ids=[uid], source_spans=[[uid, a, a + len(plain)]], speaker_id=L["spk"],
                         ja_text=ja.replace("\\N", "⏎"), vi_text=L["vi_text"].replace("\\N", "⏎"), start=L["start"], end=L["end"],
                         ja_event_id=f"{pid}.JA", vi_event_id=f"{pid}.VI", ja_lines=L["ja_lines"], vi_lines=L["vi_lines"],
                         ja_bbox=[round(v) for v in L["ja_bbox"]], vi_bbox=[round(v) for v in L["vi_bbox"]],
                         gap_px=round(L["vi_bbox"][1] - L["ja_bbox"][3], 1),
                         timing_evidence=dict(onset=PT[pid]["onset"], offset=PT[pid]["offset"],
                                              onset_src=PT[pid]["onset_src"], offset_src=PT[pid]["offset_src"])))

project = dict(kind="PROJECT", schema_version="1.1", prompt_version="MASTER PROMPT JA–VI ASS v1.1", project_id="jlpt-n1-2026-07-chokai",
               title="JLPT N1 聴解 2026-07 — 問題5", episode_id="問題5", revision="r1", parent_revision=None,
               source_scope="VIDEO_VERIFIED (ASR-assisted; no human listening pass) — scope 問題5 only: "
                            "2160.80–2539.45 s of 2026.07",
               learner_profile="PREVIOUSLY_PASSED_N1_WITH_RECALL_GAPS; goal N1 retake 満点",
               reading_policy="furigana hiragana (katakana kept); Hán Việt from KANJIDIC2/Unihan",
               style_profile="1080p; JA 58 / VI 64 / JP_Base 50 / Ruby 28 / Tag 26 / HV 34 / Mean 36 (>= master floors)",
               dialogue_languages=["JA", "VI"], dialogue_order="JA_ABOVE_VI",
               suffixes={".vi.ass": "bilingual JA+VI, no cards", ".vi-ja-study.ass": "same bilingual + cards"},
               anchor_precision="CUE", level_labels="not displayed (no accessible level source in session)")
entity = dict(kind="ENTITY", name_lock=D.NAME_LOCK)
relation = dict(kind="RELATION", address=[
    {"from": "M (男の学生)", "to": "F (女の学生=山本)", "ja": "山本さん", "vi": "Yamamoto / bạn", "note": "classmates, casual"},
    {"from": "T (先生)", "to": "students", "ja": "皆さん", "vi": "các em"},
    {"from": "F1/F2/M1 (店長)", "to": "each other", "ja": "です・ます", "vi": "trung tính, tránh đại từ"}],
    glossary={"商店街": "khu phố mua sắm", "店長": "cửa hàng trưởng", "コース": "khóa (tự chọn)", "体育大学": "đại học thể thao"})

source_meta = []
for uid, spk, t0, t1, text in D.UTTS:
    pids = [p[0] for p in PAIRS if p[1] == uid]
    source_meta.append(dict(kind="SOURCE", cue_id=uid, speaker_id=spk, source_kind="speech", source_verified=text,
                            start=PL[pids[0]]["start"], end=PL[pids[-1]]["end"], pair_ids=pids,
                            ja_event_ids=[f"{p}.JA" for p in pids], vi_event_ids=[f"{p}.VI" for p in pids],
                            evidence=D.SOURCE_EVIDENCE.get(uid, "ASR (free + forced) agrees with on-screen script"),
                            verification_status="VERIFIED_ASR_ASSISTED"))

item_meta = []
for it in ITEMS:
    item_meta.append(dict(kind="ITEM", item_id=it["id"], category="VOCAB" if it["cat"] == "V" else "GRAMMAR",
                          anchor_cue_id=it["pair"], source_surface=it["src"], display_form=it["disp"],
                          inflection_mapping=it.get("infl"), reading_in_context=it["reading"],
                          ruby_segments=it["ruby"], han_viet=it.get("hv"),
                          han_viet_status="VERIFIED" if it.get("hv") else "NOT_APPLICABLE_KANA_ONLY",
                          han_viet_evidence="KANJIDIC2 vietnam readings (jamdict-data 1.5); Unihan 17.0 kVietnamese cross-check",
                          reading_evidence="JMdict (jamdict-data 1.5) + audio", contextual_pos=it["pos"], label=it["label"],
                          contextual_meaning=it["mean"], status="REQUIRED", start=it["start"], req_visible=it["req"]))
excl_meta = [dict(kind="LEDGER_EXCLUDED", pair=e[0], candidate=e[1], status=e[2], scan=e[3], reason=e[4]) for e in D.EXCLUDED]

# ---------------------------------------------------------------- write files
title = "2026.07 — JLPT N1 聴解 問題5 (JA above / VI below)"
basic_txt = header(PLAY_W, PLAY_H, title)
study_txt = header(PLAY_W, PLAY_H, title)
proj_line = cmt("META.PROJECT", project)
basic_txt += proj_line + "\n" + "\n".join(caption_events) + "\n"
meta_lines = [proj_line, cmt("META.ENTITY", entity), cmt("META.RELATION", relation)]
meta_lines += [cmt(f"META.SOURCE.{m['cue_id']}", m) for m in source_meta]
meta_lines += [cmt(f"META.BILINGUAL.{m['pair_id']}", dict(kind="BILINGUAL", **m)) for m in bil_meta]
meta_lines += [cmt(f"META.ITEM.{m['item_id']}", m) for m in item_meta]
meta_lines += [cmt(f"META.MANIFEST.{m['item_id']}", dict(kind="MANIFEST", **m)) for m in manifest]
meta_lines += [cmt(f"META.LEDGER.X{i + 1:02d}", m) for i, m in enumerate(excl_meta)]
study_txt += "\n".join(meta_lines) + "\n" + "\n".join(caption_events) + "\n" + "\n".join(card_events) + "\n"

for fn, txt in [("2026.07.vi.ass", basic_txt), ("2026.07.vi-ja-study.ass", study_txt)]:
    with open(os.path.join(OUTDIR, fn), "w", encoding="utf-8-sig", newline="\n") as f:
        f.write(txt)

lay = dict(pairs={k: {kk: vv for kk, vv in v.items()} for k, v in PL.items()},
           panels=[dict(id=p["id"], ctx=p["ctx"], lane=p["lane"]["name"], x=p["lane"]["x"], w=p["lane"]["w"], y=p["y"], h=p["h"],
                        start=p["start"], end=p["end"], items=[i["id"] for i in p["items"]], relaxed=p.get("relaxed", False),
                        cut=p.get("cut", False), item_y=p["item_y"]) for p in panels],
           items={it["id"]: dict(start=it["start"], req=it["req"], source_end=it["source_end"], h=GEO[it["id"]]["h"],
                                 mean_lines=GEO[it["id"]]["mean_lines"]) for it in ITEMS},
           conflicts=conflicts, manifest=manifest)
json.dump(lay, open(os.path.join(OUTDIR, "layout.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print("pairs", len(PL), "items", len(ITEMS), "panels", len(panels), "conflicts", conflicts)
for p in panels:
    print(p["id"], p["ctx"], p["lane"]["name"], f"{p['start']:.2f}-{p['end']:.2f}", "h", p["h"], "y", p["y"],
          [i["id"] for i in p["items"]], "RELAXED" if p.get("relaxed") else "", "cut" if p.get("cut") else "")
