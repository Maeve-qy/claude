#!/usr/bin/env python3
"""Sổ QC ngữ nghĩa (qc/ledger.json).

Mỗi phần (section) được QC ngữ nghĩa theo HASH NỘI DUNG CHỮ (chữ trên trang + chữ trong hình SVG, sau khi
ghép số liệu). Đổi layout (CSS, vị trí hình, cỡ chữ, màu) không đổi hash -> phần đó giữ trạng thái "đạt",
không phải QC lại. Chỉ khi chữ/số liệu đổi thì hash đổi và phần đó bị đánh dấu cần QC lại.

  python3 tools/qc.py status                         # phần nào cần QC
  python3 tools/qc.py pass 51_m2 52_m3 --note "..."  # ghi nhận đạt (dùng hash của lần build gần nhất)
  python3 tools/qc.py pass all --note "..."
"""
import sys, json, argparse, datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
LEDGER = ROOT / 'qc' / 'ledger.json'
STATE = ROOT / 'build' / 'build_state.json'


def load():
    return json.loads(LEDGER.read_text(encoding='utf-8')) if LEDGER.exists() else {}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('cmd', choices=['status', 'pass'])
    ap.add_argument('sections', nargs='*')
    ap.add_argument('--note', default='')
    a = ap.parse_args()
    st = json.loads(STATE.read_text(encoding='utf-8'))
    led = load()
    shas = st['text_sha']
    if a.cmd == 'status':
        for n, h in shas.items():
            e = led.get(n, {})
            ok = e.get('status') == 'passed' and e.get('text_sha') == h
            print(f'{n:16s} {"ĐẠT (giữ nguyên)" if ok else "CẦN QC"}  {e.get("date", "")}  {e.get("note", "")[:60]}')
        return
    names = list(shas) if a.sections == ['all'] else a.sections
    today = datetime.date.today().isoformat()
    for n in names:
        led[n] = {'status': 'passed', 'text_sha': shas[n], 'spec_sha': st['spec_sha'], 'date': today, 'note': a.note}
    LEDGER.parent.mkdir(exist_ok=True)
    LEDGER.write_text(json.dumps(led, ensure_ascii=False, indent=1), encoding='utf-8')
    print('đã ghi', len(names), 'phần vào', LEDGER.relative_to(ROOT))


if __name__ == '__main__':
    main()
