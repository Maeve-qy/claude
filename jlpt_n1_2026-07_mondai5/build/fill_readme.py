# -*- coding: utf-8 -*-
"""Fill README.md from README.template.md with real numbers (chapters, sizes, SHA-256).
usage: python fill_readme.py <folder> <segments.json> <video_name>"""
import sys, os, json, hashlib, subprocess
folder, segs, video = sys.argv[1:4]
tpl = open(os.path.join(folder, "build", "README.template.md"), encoding="utf-8").read()
S = json.load(open(segs, encoding="utf-8"))


def mmss(t):
    t = int(round(t)); return f"{t // 60:02d}:{t % 60:02d}"


chapters = "\n".join(f"| {mmss(a)} | {title} |" for title, a, b in S)
vp = os.path.join(folder, video)
dur = float(subprocess.check_output(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", vp]).decode())
rows = []
for fn in (video, "2026.07.vi.ass", "2026.07.vi-ja-study.ass"):
    raw = open(os.path.join(folder, fn), "rb").read()
    rows.append(f"| `{fn}` | {len(raw):,} | `{hashlib.sha256(raw).hexdigest()}` |")
out = (tpl.replace("{VIDEO_NAME}", video).replace("{VIDEO_DUR}", f"{int(dur // 60)} phút {int(round(dur % 60))} giây")
          .replace("{VIDEO_MB}", f"{os.path.getsize(vp) / 1e6:.1f}").replace("{CHAPTERS}", chapters).replace("{HASHES}", "\n".join(rows)))
assert "{" not in out.split("## Dựng lại")[0].replace("{\\", ""), "unfilled placeholder"
open(os.path.join(folder, "README.md"), "w", encoding="utf-8").write(out)
print(out[:600])
