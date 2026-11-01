# -*- coding: utf-8 -*-
"""Visual QC sheets: source frame (1080p lanczos) + study ASS rendered by libass, one tile per pair and per panel.
usage: python qc_visual.py <source.mp4> <dir_with_ass> <layout.json> <out_dir>"""
import os, sys, json, subprocess, re
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import numpy as np
from PIL import Image, ImageDraw, ImageFont
from assr import Renderer

SRC, ADIR, LAY, OUT = sys.argv[1:5]
os.makedirs(OUT, exist_ok=True)
lay = json.load(open(LAY, encoding="utf-8"))
study = open(os.path.join(ADIR, "2026.07.vi-ja-study.ass"), encoding="utf-8-sig").read()
R = Renderer(1920, 1080)
shots = []
for pid, p in lay["pairs"].items():
    shots.append((round((p["start"] + p["end"]) / 2, 2), f"{pid} {p['start']:.2f}-{p['end']:.2f}"))
for pn in lay["panels"]:
    starts = [lay["items"][i]["start"] for i in pn["items"]]
    t = min(max(starts) + 0.6, pn["end"] - 0.3)
    shots.append((round(t, 2), f"{pn['id']} {'+'.join(pn['items'])} {pn['start']:.2f}-{pn['end']:.2f}"))
shots.sort()
font = ImageFont.truetype("/usr/share/fonts/truetype/noto/NotoSans-Bold.ttf", 30)
tiles = []
for i, (t, label) in enumerate(shots):
    fp = os.path.join(OUT, f"frame_{t:.2f}.png")
    if not os.path.exists(fp):
        subprocess.run(["ffmpeg", "-v", "error", "-y", "-ss", f"{t}", "-i", SRC, "-frames:v", "1", "-vf",
                        "scale=1920:1080:flags=lanczos", fp], check=True)
    base = np.asarray(Image.open(fp).convert("RGB")).astype(np.float32) / 255.0
    _, _, rgba = R.render(study, int(round(t * 1000)), want_rgba=True)
    a = rgba[..., 3:4]
    comp = rgba[..., :3] * 1.0 + base * (1 - a)  # rgba colour channels are premultiplied-like (colour*cov blend)
    img = Image.fromarray((np.clip(comp, 0, 1) * 255).astype(np.uint8))
    d = ImageDraw.Draw(img)
    d.rectangle([0, 0, 1920, 44], fill=(0, 0, 0))
    d.text((12, 4), f"t={t:.2f}  {label}", fill=(255, 255, 0), font=font)
    tiles.append(img.resize((640, 360), Image.LANCZOS))
per = 9
for s in range(0, len(tiles), per):
    sheet = Image.new("RGB", (1920, 1080), (40, 40, 40))
    for k, tl in enumerate(tiles[s:s + per]):
        sheet.paste(tl, ((k % 3) * 640, (k // 3) * 360))
    sheet.save(os.path.join(OUT, f"sheet_{s // per:02d}.png"))
print("shots", len(shots), "sheets", (len(tiles) + per - 1) // per)
