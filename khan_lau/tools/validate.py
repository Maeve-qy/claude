#!/usr/bin/env python3
"""Kiểm tra tất định cho dữ liệu: schema JSON + các bất biến công thức + sơ đồ xếp mẫu.

Thoát mã 1 nếu có lỗi. Chạy: python3 tools/validate.py
"""
import json, sys, math
from pathlib import Path
import jsonschema

sys.path.insert(0, str(Path(__file__).resolve().parent))
import calc

ROOT = Path(__file__).resolve().parents[1]


def close(a, b, eps=1e-6):
    return abs(a - b) < eps


def get_ref(d, ref):
    cur = d
    for k in ref.split('.'):
        cur = cur[int(k)] if isinstance(cur, list) else cur[k]
    return cur


def check(spec, d):
    errs, notes = [], []
    E = errs.append
    sa = spec['meta']['seam_allowance']
    # --- bất biến công thức ---
    m2 = d['m2']
    if m2['cut'] != [m2['fin'][0] + 2 * sa, m2['fin'][1] + 2 * sa]: E('M2: cắt ≠ TP + 2×ĐM')
    if m2['opening'] >= m2['fin'][0] / 2: E('M2: khe lộn quá dài')
    m3 = d['m3']
    if m3['g1'] > m3['g2']: E('M3: lần gấp 1 phải ≤ lần gấp 2 để mép thô được giấu')
    if m3['cut'] != [m3['fin'][0] + 2 * (m3['g1'] + m3['g2']), m3['fin'][1] + 2 * (m3['g1'] + m3['g2'])]: E('M3: công thức gấp mép đôi')
    if m3['loop_visible'] < 4: E('M3: quai treo quá ngắn để móc')
    m4 = d['m4']
    for o in m4['options']:
        if not close(o['n'] * o['sq_fin'], m4['fin'][0]): E(f"M4: {o['n']}×ô TP ≠ TP")
        if not close(o['row_len'], m4['fin'][0] + 2 * sa): E(f"M4 n={o['n']}: hàng ghép {o['row_len']} ≠ TP+2ĐM")
    if m4['top'] != m4['back']: E('M4: mặt ghép khác lớp sau')
    if m4['strip_min_fin'] < 1.5: E('M4: dải ghép quá hẹp')
    m5 = d['m5']
    if m5['binding_w'] < 6 * m5['b'] + 2 * m5['t']: E('M5: dải bo viền hẹp hơn 6b + 2t')
    if m5['bind_long'][1] < m5['fin'][1]: E('M5: dải cạnh dài ngắn hơn cạnh')
    if m5['bind_short'][1] < m5['fin'][0] + 2 * 1.5: E('M5: dải cạnh ngắn không đủ đuôi bọc đầu')
    if m5['bind_total'] < m5['perimeter']: E('M5: tổng dải < chu vi')
    if not close((m5['jeans_n'] * m5['jeans_strip'][0]) - (m5['jeans_n'] - 1) * 2 * sa, m5['fin'][0]): E('M5: ghép dải jeans không ra đúng bề ngang')
    if m5['fin'][0] % m5['grid'] or m5['fin'][1] % m5['grid']: notes.append('M5: lưới chần không chia hết khăn')
    for ex in [d['m6']] + d['m6']['examples']:
        tag = f"M6 {ex['L']}×{ex['W']}"
        if ex['free_margin'] < 2: E(f'{tag}: không đủ chỗ cho khe lộn giữa 2 túi')
        if ex['P'] < spec['products']['m6']['pocket_min']: E(f'{tag}: túi nông')
        if ex['Lp'] <= ex['L'] or ex['Wp'] <= ex['W']: E(f'{tag}: không có độ dư')
        if ex['cut_pocket'][0] != ex['cut_main'][1]: E(f'{tag}: túi không bằng bề rộng thân')
    # --- palette / mã màu ---
    for p in spec['palettes']:
        if len({c[1].lower() for c in p['colors']}) != 4: E(f"Palette {p['id']}: trùng màu")
    fab_ids = {f['id'] for f in spec['fabrics']}
    for pid, p in spec['products'].items():
        for f in p['fabrics']:
            if f not in fab_ids: E(f'{pid}: vải lạ {f}')
    for g in spec['garments']:
        if g['fabric'] not in fab_ids: E(f"{g['id']}: vải lạ")
    # --- sơ đồ xếp mẫu: trong biên, không chồng, đúng kích thước tham chiếu ---
    gar = {g['id']: {p['id']: p for p in g['pieces']} for g in spec['garments']}
    for L in spec['layouts']:
        pc = gar[L['garment']][L['piece']]
        its = L['items']
        used = 0
        for i, it in enumerate(its):
            if it['x'] < 0 or it['y'] < 0 or it['x'] + it['w'] > pc['w'] + 1e-9 or it['y'] + it['h'] > pc['h'] + 1e-9:
                E(f"{L['id']}: '{it['label']}' vượt ra ngoài mảnh {pc['w']}×{pc['h']}")
            ref = get_ref(d, it['ref'])
            dims = sorted(ref) if isinstance(ref, list) else None
            if dims is None:  # bề rộng dải
                if not (close(it['h'], ref) or close(it['w'], ref)): E(f"{L['id']}: '{it['label']}' không khớp {it['ref']}={ref}")
            elif sorted([it['w'], it['h']]) != dims:
                E(f"{L['id']}: '{it['label']}' {it['w']}×{it['h']} ≠ {it['ref']}={ref}")
            used += it['w'] * it['h']
            for j in range(i + 1, len(its)):
                o = its[j]
                if it['x'] < o['x'] + o['w'] and o['x'] < it['x'] + it['w'] and it['y'] < o['y'] + o['h'] and o['y'] < it['y'] + it['h']:
                    E(f"{L['id']}: '{it['label']}' chồng lên '{o['label']}'")
        notes.append(f"{L['id']}: dùng {used / (pc['w'] * pc['h']) * 100:.0f}% diện tích")
    return errs, notes


def main():
    spec = json.loads((ROOT / 'data' / 'spec.json').read_text(encoding='utf-8'))
    schema = json.loads((ROOT / 'data' / 'spec.schema.json').read_text(encoding='utf-8'))
    v = jsonschema.Draft202012Validator(schema)
    serr = sorted(v.iter_errors(spec), key=lambda e: list(e.path))
    for e in serr:
        print('SCHEMA:', '/'.join(map(str, e.path)), e.message)
    d = calc.main()
    errs, notes = check(spec, d)
    for n in notes:
        print('  ·', n)
    for e in errs:
        print('LỖI:', e)
    ok = not serr and not errs
    print('KẾT QUẢ:', 'ĐẠT' if ok else f'{len(serr)} lỗi schema, {len(errs)} lỗi bất biến')
    return 0 if ok else 1


if __name__ == '__main__':
    sys.exit(main())
