# -*- coding: utf-8 -*-
"""Assemble the Full HD practice video for 問題5.
usage: python video_m5.py <source.mp4> <dir_with_study_ass> <work_dir> <out.mp4>"""
import os, sys, json, subprocess, re
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import cards_m5 as C
from PIL import Image, ImageDraw

SRC, ADIR, WD, OUT = sys.argv[1:5]
os.makedirs(WD, exist_ok=True)
STUDY = os.path.join(ADIR, "2026.07.vi-ja-study.ass")
FPS = 30


import hashlib


def signature(files, params=""):
    h = hashlib.sha256(params.encode())
    for f in files:
        h.update(open(f, "rb").read())
    return h.hexdigest()


def cached(out, sig):
    return os.path.exists(out) and os.path.exists(out + ".sig") and open(out + ".sig").read() == sig


def mark(out, sig):
    open(out + ".sig", "w").write(sig)


def run(cmd):
    print("$", " ".join(cmd)[:300], flush=True)
    subprocess.run(cmd, check=True)


def esc(p):  # path escaping for ffmpeg filter args
    return p.replace("\\", "\\\\").replace(":", "\\:").replace("'", "\\'")


# ---------------------------------------------------------------- background for generated cards
bg = os.path.join(WD, "bg.png")
im = Image.new("RGB", (1920, 1080))
px = im.load()
for y in range(1080):
    t = y / 1079
    r, g, b = int(16 + (11 - 16) * t), int(24 + (17 - 24) * t), int(38 + (27 - 38) * t)
    for x in range(1920):
        px[x, y] = (r, g, b)
d = ImageDraw.Draw(im)
d.rectangle([0, 0, 10, 1080], fill=(245, 200, 110))
d.line([(110, 1010), (1810, 1010)], fill=(46, 58, 76), width=2)
im.save(bg)

# ---------------------------------------------------------------- generated segments
segs = []


def card_seg(name, fn, chime_from=None):
    ass = os.path.join(WD, f"{name}.ass")
    dur = fn(ass)
    out = os.path.join(WD, f"{name}.mkv")
    sig = signature([ass, bg], f"card|{dur}|{chime_from}")
    if cached(out, sig):
        return out, dur
    vf = f"ass='{esc(ass)}',fade=t=in:st=0:d=0.3,fade=t=out:st={dur - 0.35:.2f}:d=0.35,format=yuv420p"
    cmd = ["ffmpeg", "-v", "error", "-y", "-loop", "1", "-framerate", str(FPS), "-i", bg]
    if chime_from is not None:
        cmd += ["-ss", f"{chime_from}", "-t", "2.5", "-i", SRC]
        af = f"[1:a]aresample=48000,aformat=channel_layouts=stereo,afade=t=out:st=2.1:d=0.4,apad=whole_dur={dur}[a]"
    else:
        cmd += ["-f", "lavfi", "-t", f"{dur}", "-i", "anullsrc=r=48000:cl=stereo"]
        af = "[1:a]aformat=sample_rates=48000:channel_layouts=stereo,apad=whole_dur=" + f"{dur}[a]"
    cmd += ["-filter_complex", f"[0:v]{vf}[v];{af}", "-map", "[v]", "-map", "[a]", "-t", f"{dur}",
            "-c:v", "libx264", "-crf", "12", "-preset", "fast", "-r", str(FPS), "-c:a", "pcm_s16le", out]
    run(cmd)
    mark(out, sig)
    return out, dur


# ---------------------------------------------------------------- base clips from the source
def base_clip(name, seek, t0, t1, freeze_until=None):
    out = os.path.join(WD, f"{name}.mkv")
    if os.path.exists(out) and os.path.getsize(out) > 1000000:   # source-only clip, independent of the ASS
        return out, round(t1 - t0, 3)
    a, b = round(t0 - seek, 3), round(t1 - seek, 3)
    if freeze_until:
        f = round(freeze_until - seek, 3)
        vchain = (f"[0:v]split=2[va][vb];[va]trim=start={f + 0.1}:end={f + 0.134},setpts=PTS-STARTPTS,"
                  f"tpad=stop_mode=clone:stop_duration=2,trim=duration={round(f - a, 3)},setpts=PTS-STARTPTS[h];"
                  f"[vb]trim=start={f}:end={b},setpts=PTS-STARTPTS[m];[h][m]concat=n=2:v=1:a=0,")
    else:
        vchain = f"[0:v]trim=start={a}:end={b},setpts=PTS-STARTPTS,"
    vchain += "scale=1920:1080:flags=lanczos,fps=30,format=yuv420p[v]"
    achain = f"[0:a]atrim=start={a}:end={b},asetpts=PTS-STARTPTS,aresample=48000,aformat=channel_layouts=stereo[a]"
    run(["ffmpeg", "-v", "error", "-y", "-ss", f"{seek}", "-t", f"{t1 - seek + 1}", "-i", SRC,
         "-filter_complex", f"{vchain};{achain}", "-map", "[v]", "-map", "[a]", "-c:v", "libx264", "-crf", "12",
         "-preset", "fast", "-c:a", "pcm_s16le", out])
    return out, round(t1 - t0, 3)


def shift_ass(src_ass, t0, t1, out):
    raw = open(src_ass, encoding="utf-8-sig").read()
    head, ev = raw.split("[Events]\n", 1)
    lines = ev.split("\n")
    fmt, body = lines[0], lines[1:]

    def tsec(s):
        h, m, x = s.split(":"); return int(h) * 3600 + int(m) * 60 + float(x)

    kept = []
    for l in body:
        if not l.startswith("Dialogue: "):
            continue
        parts = l[len("Dialogue: "):].split(",", 9)
        st, en = tsec(parts[1]), tsec(parts[2])
        if en <= t0 or st >= t1:
            continue
        parts[1], parts[2] = C.ts(max(0.0, st - t0)), C.ts(min(t1, en) - t0)
        kept.append("Dialogue: " + ",".join(parts))
    with open(out, "w", encoding="utf-8-sig", newline="\n") as f:
        f.write(head + "[Events]\n" + fmt + "\n" + "\n".join(kept) + "\n")
    return len(kept)


def overlay(name, base, dur, study=None, label=None):
    out = os.path.join(WD, f"{name}.mkv")
    sig = signature([base] if False else [x for x in (study, label) if x], f"overlay|{os.path.basename(base)}|{dur}")
    if cached(out, sig):
        return out, dur
    vf = []
    if study:
        vf.append(f"ass='{esc(study)}'")
    if label:
        vf.append(f"ass='{esc(label)}'")
    vf.append("format=yuv420p")
    run(["ffmpeg", "-v", "error", "-y", "-i", base, "-vf", ",".join(vf), "-c:v", "libx264", "-crf", "12",
         "-preset", "fast", "-c:a", "copy", out])
    mark(out, sig)
    return out, dur


Q1 = (2155.0, 2160.8, 2339.4, 2161.2)   # seek, start, end, slide change (freeze before it)
Q2 = (2340.0, 2343.0, 2539.4, None)
b1, d1 = base_clip("B1", *Q1)
b2, d2 = base_clip("B2", *Q2)
L1 = os.path.join(WD, "label_l1_q1.ass"); C.pass_label(L1, d1, "LƯỢT 1 · NGHE NHƯ THI THẬT", C.AMBER)
L2 = os.path.join(WD, "label_l2_q1.ass"); C.pass_label(L2, d1, "LƯỢT 2 · HỌC KỸ: PHỤ ĐỀ + THẺ HỌC", C.BLUE)
L3 = os.path.join(WD, "label_l1_q2.ass"); C.pass_label(L3, d2, "LƯỢT 1 · NGHE NHƯ THI THẬT", C.AMBER)
L4 = os.path.join(WD, "label_l2_q2.ass"); C.pass_label(L4, d2, "LƯỢT 2 · HỌC KỸ: PHỤ ĐỀ + THẺ HỌC", C.BLUE)
S1 = os.path.join(WD, "study_q1.ass"); n1 = shift_ass(STUDY, Q1[1], Q1[2], S1)
S2 = os.path.join(WD, "study_q2.ass"); n2 = shift_ass(STUDY, Q2[1], Q2[2], S2)
print("study events q1", n1, "q2", n2)

plan = [
    ("Giới thiệu", card_seg("S00_title", C.title_card)),
    ("Chiến lược 問題5", card_seg("S01_strategy", C.strategy_card)),
    ("1番 · Lượt 1 · nghe như thi thật", overlay("S02_q1_exam", b1, d1, label=L1)),
    ("1番 · Đáp án & giải thích", card_seg("S03_q1_answer", C.answer1_card, chime_from=2339.45)),
    ("1番 · Lượt 2 · học kỹ (phụ đề + thẻ)", overlay("S04_q1_study", b1, d1, study=S1, label=L2)),
    ("2番 · Lượt 1 · nghe như thi thật", overlay("S05_q2_exam", b2, d2, label=L3)),
    ("2番 · Đáp án & giải thích", card_seg("S06_q2_answer", C.answer2_card, chime_from=2539.45)),
    ("2番 · Lượt 2 · học kỹ (phụ đề + thẻ)", overlay("S07_q2_study", b2, d2, study=S2, label=L4)),
    ("Tổng kết", card_seg("S08_end", C.end_card)),
]

# chapters
meta = os.path.join(WD, "chapters.txt")
t = 0.0
chap = [";FFMETADATA1", "title=JLPT N1 聴解 2026年7月 — 問題5 (luyện 満点)", "artist=Biên soạn từ video 2026.07 (@LuyendeJLPTcungto)"]
offsets = []
for title, (path, dur) in plan:
    offsets.append((title, round(t, 3), round(t + dur, 3)))
    chap += ["[CHAPTER]", "TIMEBASE=1/1000", f"START={int(round(t * 1000))}", f"END={int(round((t + dur) * 1000))}", f"title={title}"]
    t += dur
open(meta, "w", encoding="utf-8").write("\n".join(chap) + "\n")
json.dump(offsets, open(os.path.join(WD, "segments.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)

inputs, fc = [], ""
for i, (title, (path, dur)) in enumerate(plan):
    inputs += ["-i", path]
    fc += f"[{i}:v][{i}:a]"
fc += f"concat=n={len(plan)}:v=1:a=1[v][a]"
run(["ffmpeg", "-v", "error", "-y", *inputs, "-i", meta, "-filter_complex", fc, "-map", "[v]", "-map", "[a]",
     "-map_metadata", str(len(plan)), "-map_chapters", str(len(plan)),
     "-c:v", "libx264", "-preset", "slow", "-crf", "21", "-tune", "stillimage", "-pix_fmt", "yuv420p",
     "-profile:v", "high", "-level", "4.1", "-r", str(FPS), "-g", "300",
     "-c:a", "aac", "-b:a", "160k", "-ar", "48000", "-movflags", "+faststart", OUT])
print("segments:")
for o in offsets:
    print(f"  {o[1]:8.2f} - {o[2]:8.2f}  {o[0]}")
