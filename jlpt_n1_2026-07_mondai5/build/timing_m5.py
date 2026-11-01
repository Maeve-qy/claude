# -*- coding: utf-8 -*-
"""Cue timing for every bilingual pair: forced alignment (Whisper small CT2) + energy-based onset/offset snapping.
usage: python timing_m5.py <model_dir> <wav_16k_from_2155s> <out_json>"""
import sys, os, json, math, wave
import numpy as np
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import data_m5 as D
from fa import FA

OFF = 2155.0
model_dir, wav, out = sys.argv[1], sys.argv[2], sys.argv[3]
fa = FA(model_dir, wav, OFF)
audio = fa.audio
SR = 16000

def energy_db(t0, t1, step=0.01):
    ts = np.arange(t0, t1, step)
    e = []
    for t in ts:
        x = audio[int((t - OFF) * SR): int((t + step - OFF) * SR)]
        e.append(20 * np.log10(np.sqrt((x ** 2).mean()) + 1e-9) if len(x) else -120)
    return ts, np.array(e)

ON_DB = -38.0

def first_voiced(t_from, t_to, run=5):
    ts, e = energy_db(t_from, t_to)
    for i in range(len(ts) - run):
        if np.all(e[i:i + run] > ON_DB):
            return float(ts[i])
    return None

def last_voiced(t_from, t_to, run=5):
    ts, e = energy_db(t_from, t_to)
    for i in range(len(ts) - 1, run - 1, -1):
        if np.all(e[i - run + 1:i + 1] > ON_DB):
            return float(ts[i] + 0.01)
    return None

utt_words = {}
for uid, spk, t0, t1, text in D.UTTS:
    words, lp, nt = fa.align(t0, t1, text)
    joined = "".join(w["w"] for w in words)
    assert joined == text, (uid, joined, text)
    pos = 0
    for w in words:
        w["a"], w["b"] = pos, pos + len(w["w"]); pos += len(w["w"])
    utt_words[uid] = dict(words=words, lp=lp, ntok=nt)

pairs = []
cursor = {}
for pid, uid, ja, vi in D.PAIRS:
    plain = ja.replace("\\N", "")
    text = next(u[4] for u in D.UTTS if u[0] == uid)
    a = cursor.get(uid, 0); b = a + len(plain)
    assert text[a:b] == plain, (pid, text[a:b], plain)
    cursor[uid] = b
    ws = [w for w in utt_words[uid]["words"] if w["b"] > a and w["a"] < b]
    # ignore leading/trailing pure punctuation words for timing
    core = [w for w in ws if w["w"].strip("、。，．？！…　 ") != ""]
    st, en = core[0]["s"], core[-1]["e"]
    pairs.append(dict(pid=pid, uid=uid, a=a, b=b, ws=st, we=en,
                      words=[(w["w"], w["s"], w["e"], w["p"]) for w in ws]))

# snap to the real speech envelope (DTW tends to pull the first word to the window start)
for i, p in enumerate(pairs):
    prev_off = pairs[i - 1]["offset"] if i else p["ws"] - 1.0
    lo = max(p["ws"] - 0.3, prev_off)
    on = first_voiced(lo, min(p["we"], p["ws"] + 1.5))
    p["onset"] = round(on if on is not None else p["ws"], 3)
    p["onset_src"] = "energy" if on is not None else "align"
    nxt_ws = pairs[i + 1]["ws"] if i + 1 < len(pairs) else p["we"] + 0.6
    hi = min(nxt_ws, p["we"] + 0.5)
    off = last_voiced(max(p["onset"] + 0.1, p["we"] - 1.2), hi) if hi > p["onset"] + 0.2 else None
    p["offset"] = round(off if off is not None else p["we"], 3)
    p["offset_src"] = "energy" if off is not None else "align"
    if p["offset"] <= p["onset"]:
        p["offset"] = round(max(p["we"], p["onset"] + 0.3), 3); p["offset_src"] = "align"

# turn boundaries (different utterances): put the cut in the real energy gap if one exists
def quiet_runs(t0, t1, min_frames=3):
    ts, e = energy_db(t0, t1)
    runs, i = [], 0
    while i < len(ts):
        if e[i] < ON_DB:
            j = i
            while j < len(ts) and e[j] < ON_DB: j += 1
            if j - i >= min_frames: runs.append((float(ts[i]), float(ts[j - 1] + 0.01)))
            i = j
        else:
            i += 1
    return runs

for i in range(len(pairs) - 1):
    p, q = pairs[i], pairs[i + 1]
    if p["uid"] == q["uid"]:
        continue
    if q["onset"] - p["offset"] > 0.25:
        continue  # already separated by a clear pause
    runs = quiet_runs(min(p["we"], p["offset"]) - 0.6, max(q["ws"], q["onset"]) + 0.9)
    runs = [r for r in runs if r[0] > p["onset"] + 0.2 and r[1] < q["we"] - 0.2]
    if runs:
        ref = (p["offset"] + q["onset"]) / 2
        r = min(runs, key=lambda r: abs((r[0] + r[1]) / 2 - ref))
        p["offset"], q["onset"] = round(r[0], 3), round(r[1], 3)
        p["offset_src"] = "energy-turn"; q["onset_src"] = "energy-turn"
        p["turn_gap"] = [round(r[0], 3), round(r[1], 3)]

# keep order: each onset >= previous offset - small overlap tolerance (contiguous speech)
for i in range(1, len(pairs)):
    if pairs[i]["onset"] < pairs[i - 1]["offset"]:
        mid = round((pairs[i]["onset"] + pairs[i - 1]["offset"]) / 2, 3)
        pairs[i - 1]["offset"] = mid; pairs[i]["onset"] = mid
        pairs[i - 1]["offset_src"] += "+split"; pairs[i]["onset_src"] += "+split"

LEAD, TAIL, MAXHOLD, GAP = 0.08, 0.30, 1.0, 0.04
for i, p in enumerate(pairs):
    nxt = pairs[i + 1]["onset"] - LEAD if i + 1 < len(pairs) else p["offset"] + 3.0
    prev_end = pairs[i - 1]["end"] if i else 0
    start = max(p["onset"] - LEAD, prev_end)
    nch = len(D.PAIRS[i][2]) + len(D.PAIRS[i][3]) / 2.2
    min_dur = max(1.0, min(4.0, nch * 0.075))
    end = max(p["offset"] + TAIL, start + min_dur)
    end = min(end, p["offset"] + MAXHOLD if start + min_dur <= p["offset"] + MAXHOLD else start + min_dur)
    end = min(end, nxt - GAP)
    p["start"], p["end"] = round(start, 3), round(end, 3)

def qs(t): return math.ceil(round(t * 100, 6)) / 100.0
for p in pairs:
    p["Q_start"], p["Q_end"] = qs(p["start"]), qs(p["end"])
json.dump(dict(utts={k: dict(lp=v["lp"], ntok=v["ntok"], words=[(w["w"], w["s"], w["e"], w["p"]) for w in v["words"]]) for k, v in utt_words.items()},
               pairs=pairs), open(out, "w"), ensure_ascii=False, indent=1)
for p, src in zip(pairs, D.PAIRS):
    print(f'{p["pid"]} {p["Q_start"]:9.2f}-{p["Q_end"]:9.2f} ({p["Q_end"]-p["Q_start"]:4.2f}s) speech {p["onset"]:.2f}-{p["offset"]:.2f} [{p["onset_src"]}/{p["offset_src"]}] {src[2][:28]}')
