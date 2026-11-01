# -*- coding: utf-8 -*-
"""Append the QC Comment (gate status, counts, tools, unverified scope) to the study ASS without touching the
render payload; prints payload hash (Script Info + Styles + Dialogue) and full-file SHA-256.
usage: python finalize_m5.py <dir_with_ass> <qc_report.json>"""
import sys, os, json, hashlib
ADIR, REP = sys.argv[1], sys.argv[2]
study = os.path.join(ADIR, "2026.07.vi-ja-study.ass")
R = json.load(open(REP, encoding="utf-8"))
raw = open(study, encoding="utf-8-sig").read()
lines = raw.split("\n")
lines = [l for l in lines if ",META.QC," not in l]          # idempotent


def payload(ls):
    return hashlib.sha256("\n".join(l for l in ls if not l.startswith("Comment:")).encode("utf-8")).hexdigest()


c = R["counts"]
qc = dict(kind="QC", scope="VIDEO_VERIFIED (ASR-assisted, no human listening) — 問題5 only (2160.80–2539.45 s)",
          gates=R["gates"], G2="PASS (scope: this source; names/relations locked in ENTITY/RELATION)",
          G8="see README (size/SHA-256 computed after this line was written)",
          counts=dict(pairs=c["N_pairs"], ja_events=c["N_JA"], vi_events=c["N_VI"], missing_JA=c["missing_JA_ids"],
                      missing_VI=c["missing_VI_ids"], mismatched=c["mismatched_pair_ids"], items_required=c["items_expected"],
                      items_complete=c["items_serialized_complete"], vocab=c["vocab_required"], grammar=c["grammar_required"],
                      kanji_items=c["kanji_items"], kana_only_items=c["kana_only_items"], excluded_candidates=c["ledger_excluded_rows"],
                      collisions=len(c["collisions"]), protected_zone_hits=len(c["protected_zone_hits"])),
          visual_review="120 composited 1080p shots (83 pairs + 37 panels) on source frames, 14 contact sheets reviewed",
          tools=["ffmpeg 6.1.1 (libass 0.17.1, HarfBuzz 8.3.0)", "faster-whisper 1.2.1 + Whisper small CTranslate2 int8",
                 "jamdict-data 1.5 (JMdict, KANJIDIC2)", "Unihan 17.0 kVietnamese", "fonts: Noto Sans CJK JP 2.004, Noto Sans 2.004"],
          not_verified=["no human listening pass", "hvdic.thivien.net / mazii.net not reachable from the build environment",
                        "render verified with libass 0.17.1 only; other players may differ", "word-level timing not claimed (ANCHOR_PRECISION=CUE)"],
          warnings=R["warnings"], payload_sha256=payload(lines))
qline = "Comment: 0,0:00:00.00,0:00:00.00,JA,META.QC,0,0,0,," + json.dumps(qc, ensure_ascii=False, separators=(",", ":"))
# insert after the last META comment
idx = max(i for i, l in enumerate(lines) if l.startswith("Comment:"))
lines.insert(idx + 1, qline)
with open(study, "w", encoding="utf-8-sig", newline="\n") as f:
    f.write("\n".join(lines))
for fn in ("2026.07.vi.ass", "2026.07.vi-ja-study.ass"):
    b = open(os.path.join(ADIR, fn), "rb").read()
    print(fn, len(b), hashlib.sha256(b).hexdigest())
print("payload_sha256", qc["payload_sha256"])
