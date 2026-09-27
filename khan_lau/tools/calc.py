#!/usr/bin/env python3
"""Tính mọi số liệu dẫn xuất từ data/spec.json -> build/derived.json.

Nguyên tắc: không có con số dẫn xuất nào được gõ tay trong bài. Kích thước cắt, đường chéo kiểm tra,
dải bo viền, số miếng cắt được từ mỗi món đồ ... đều tính ở đây, rồi được chèn vào HTML qua {{...}}.
"""
import json, math
from functools import lru_cache
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def rhu(x):
    """Làm tròn nửa lên (10,5 -> 11), khác round() của Python (làm tròn về số chẵn)."""
    return int(math.floor(x + 0.5))


def ceil_half(x):
    return math.ceil(x * 2 - 1e-9) / 2


def diag(w, h):
    return round(math.hypot(w, h), 1)


def pack(W, H, w, h):
    """Số miếng w×h (được xoay) tối đa cắt được từ tấm W×H bằng các nhát cắt thẳng xuyên tấm (guillotine)."""
    W, H, w, h = (int(round(v * 2)) for v in (W, H, w, h))  # đơn vị 0,5 cm

    @lru_cache(maxsize=None)
    def f(a, b):
        if a <= 0 or b <= 0:
            return 0
        best = 0
        for pw, ph in ((w, h), (h, w)):
            if pw <= a and ph <= b:
                best = max(best, (a // pw) * (b // ph))
        # các vị trí cắt hợp lý: tổ hợp i*w + j*h
        cuts = set()
        for i in range(0, a // min(w, h) + 1):
            for j in range(0, a // min(w, h) + 1):
                c = i * w + j * h
                if 0 < c < a:
                    cuts.add(('v', c))
                c2 = i * w + j * h
                if 0 < c2 < b:
                    cuts.add(('h', c2))
        for d, c in cuts:
            if d == 'v':
                best = max(best, f(c, b) + f(a - c, b))
            else:
                best = max(best, f(a, c) + f(a, b - c))
        return best

    return f(W, H)


def derive(spec):
    sa = spec['meta']['seam_allowance']
    ts = spec['meta']['topstitch']
    P = spec['products']
    d = {'sa': sa, 'ts': ts, 'sa2': 2 * sa}

    # M1 — cắt, không may
    m1 = P['m1']
    d['m1'] = {'fin': m1['finished'], 'cut': m1['finished'], 'diag': diag(*m1['finished'])}

    # M2 — may lộn 2 lớp: cắt = TP + 2×ĐM
    m2 = P['m2']
    fin = m2['finished']
    cut = [fin[0] + 2 * sa, fin[1] + 2 * sa]
    d['m2'] = {'fin': fin, 'cut': cut, 'diag': diag(*cut), 'opening': m2['opening'], 'opening_thick': m2['opening_thick'],
               'variants': [{'fin': [v, v], 'cut': [v + 2 * sa, v + 2 * sa], 'diag': diag(v + 2 * sa, v + 2 * sa)} for v in m2['variants']],
               'quilt_third': round(fin[0] / 3, 1)}
    d['m2']['v20'] = [20 + 2 * sa, 20 + 2 * sa]

    # M3 — gấp mép đôi: cắt = TP + 2×(g1+g2)
    m3 = P['m3']
    g1, g2 = m3['hem']
    fin = m3['finished']
    add = 2 * (g1 + g2)
    cut = [fin[0] + add, fin[1] + add]
    ls = m3['loop_strip']
    d['m3'] = {'fin': fin, 'cut': cut, 'diag': diag(*cut), 'g1': g1, 'g2': g2, 'hem_total': g1 + g2, 'add': add,
               'loop': ls, 'loop_half': ls[0] / 2, 'loop_quarter': ls[0] / 4, 'loop_tuck': m3['loop_tuck'],
               'loop_visible': (ls[1] - 2 * m3['loop_tuck']) / 2, 'stitch_from_edge': g2 - 0.2,
               'miter_trim': 0.6}

    # M4 — ghép mảnh n×n: ô cắt = ô TP + 2×ĐM
    m4 = P['m4']
    fin = m4['finished']
    n = m4['grid']

    def patch(nn):
        sq_fin = fin[0] / nn
        sq_cut = sq_fin + 2 * sa
        top = nn * sq_cut - (nn - 1) * 2 * sa
        return {'n': nn, 'count': nn * nn, 'sq_fin': sq_fin, 'sq_cut': sq_cut, 'square': [sq_cut, sq_cut],
                'row_len': top, 'top': [top, top], 'diag_sq': diag(sq_cut, sq_cut)}

    base = patch(n)
    d['m4'] = dict(base)
    d['m4'].update({'fin': fin, 'back': [fin[0] + 2 * sa, fin[1] + 2 * sa], 'opening': m4['opening'],
                    'options': [patch(k) for k in m4['grid_options']], 'strip_min': m4['strip_min'],
                    'strip_min_fin': m4['strip_min'] - 2 * sa})

    # M5 — 3 lớp bo viền kiểu Pháp: cắt = TP; dải = 6b + 2t (làm tròn lên 0,5 cm)
    m5 = P['m5']
    fin = m5['finished']
    b, t = m5['binding_b'], m5['thickness']
    bw_raw = 6 * b + 2 * t + m5.get('binding_extra', 0)
    bw = ceil_half(bw_raw)
    tail = m5['binding_tail']
    long_len = fin[1] + 2 * sa           # dư 1 cm mỗi đầu, xén sau
    short_len = fin[0] + 2 * tail        # dư 2 cm mỗi đầu để gấp bọc đầu
    js = m5['jeans_strips']
    jw = (fin[0] + (js - 1) * 2 * sa) / js
    g = m5['quilt_grid']
    d['m5'] = {'fin': fin, 'cut_A': fin, 'cut_B': fin, 'cut_C': fin, 'b': b, 't': t, 'binding_w_raw': bw_raw,
               'binding_w': bw, 'binding_half': bw / 2, 'bind_long': [bw, long_len], 'bind_short': [bw, short_len],
               'tail': tail, 'bind_total': 2 * long_len + 2 * short_len, 'perimeter': 2 * (fin[0] + fin[1]),
               'jeans_strip': [jw if jw != int(jw) else int(jw), fin[1]], 'jeans_n': js,
               'grid': g, 'grid_x': [x for x in range(g, fin[0], g)], 'grid_y': [y for y in range(g, fin[1], g)],
               'cells': (fin[0] // g) * (fin[1] // g), 'thin_example_w': ceil_half(6 * b + 2 * 0.2 + m5.get('binding_extra', 0)),
               'extra': m5.get('binding_extra', 0), 'one_strip': 2 * (fin[0] + fin[1]) + 20}
    d['m5']['n_lines'] = len(d['m5']['grid_x']) + len(d['m5']['grid_y'])

    # M6 — vỏ bàn lau có 2 túi, tính theo số đo bàn lau
    m6 = P['m6']

    def mop(L, W, h):
        # túi phải ôm được cả độ dày h của bàn lau; đường diễu 0,5 cm 2 bên ăn mất 1 cm -> cộng thêm 'ease'
        Lp = ceil_half(L + h + m6['ease'])
        Wp = ceil_half(W + h + m6['ease'])
        Lp = int(Lp) if float(Lp).is_integer() else Lp
        Wp = int(Wp) if float(Wp).is_integer() else Wp
        Pk = max(m6['pocket_min'], rhu(L * m6['pocket_ratio']))
        return {'L': L, 'W': W, 'h': h, 'Lp': Lp, 'Wp': Wp, 'P': Pk, 'fin': [Lp, Wp],
                'cut_main': [Lp + 2 * sa, Wp + 2 * sa], 'cut_pocket': [Wp + 2 * sa, 2 * Pk + 2 * sa],
                'pocket_folded': [Wp + 2 * sa, Pk + sa], 'free_len': Lp - 2 * Pk,
                'free_margin': (Lp - 2 * Pk - m6['opening']) / 2,
                'perim_pocket': 2 * (Wp - 2 * ts), 'perim_plate': 2 * (W + h)}

    ex = mop(*m6['plate'], m6['plate_thick'])
    d['m6'] = dict(ex)
    d['m6'].update({'opening': m6['opening'], 'examples': [mop(*e) for e in m6['plate_examples']],
                    'ease': m6['ease'], 'pocket_min': m6['pocket_min'], 'pocket_pct': int(m6['pocket_ratio'] * 100)})

    cut32 = d['m2']['cut'][0]
    d['shrink'] = {'pct': 5, 'cut': cut32, 'after': round(cut32 * (1 - 0.05), 1), 'loss': round(cut32 * 0.05, 1)}

    # Hiệu suất cắt: mỗi món đồ cắt được bao nhiêu miếng
    targets = [('m1', 'Giẻ áo thun', d['m1']['cut'], ['thun_cotton']),
               ('m2', 'Khăn lau bàn (1 lớp)', d['m2']['cut'], ['cotton_det_thoi', 'khan_bong', 'thun_cotton', 'flannel']),
               ('m3', 'Khăn bếp treo', d['m3']['cut'], ['cotton_det_thoi', 'lanh']),
               ('m4', 'Ô ghép', d['m4']['square'], ['cotton_det_thoi', 'lanh', 'flannel']),
               ('m5', 'Lớp khăn lau nhà', d['m5']['cut_A'], ['khan_bong', 'thun_cotton']),
               ('m6', 'Lớp vỏ bàn lau', d['m6']['cut_main'], ['khan_bong', 'microfiber', 'jeans'])]
    yields = []
    for g_ in spec['garments']:
        row = {'garment': g_['id'], 'name': g_['name'], 'fabric': g_['fabric'], 'cells': []}
        for pid, label, size, ok in targets:
            total = sum(pc['qty'] * pack(pc['w'], pc['h'], size[0], size[1]) for pc in g_['pieces'])
            cell = {'pid': pid, 'label': label, 'size': size, 'n': total, 'suitable': g_['fabric'] in ok}
            if pid == 'm5' and g_['fabric'] == 'jeans':  # mặt chà B ghép từ dải jeans
                strips = sum(pc['qty'] * pack(pc['w'], pc['h'], *d['m5']['jeans_strip']) for pc in g_['pieces'])
                cell.update({'n': strips // d['m5']['jeans_n'], 'suitable': True, 'note': 'jeans'})
            row['cells'].append(cell)
        yields.append(row)
    d['yields'] = yields
    # Tổ hợp thực tế cho câu chữ: 1 áo sơ mi = 1 mặt khăn lau bàn (thân sau) + các ô ghép còn lại
    lay = {L['id']: L for L in spec['layouts']}
    somi = {p['id']: p for p in next(g_ for g_ in spec['garments'] if g_['id'] == 'somi')['pieces']}
    sq = d['m4']['square']
    o_back = sum(1 for it in lay['somi_back']['items'] if it['ref'] == 'm4.square')
    o_rest = sum(pc['qty'] * pack(pc['w'], pc['h'], *sq) for k, pc in somi.items() if k != 'than_sau')
    ytab = {r['garment']: {c['pid']: c['n'] for c in r['cells']} for r in yields}
    thun = next(g_ for g_ in spec['garments'] if g_['id'] == 'aothun')['pieces'][0]
    strips_per_panel = int((thun['h'] - d['m1']['cut'][1]) // d['m5']['binding_w'])
    d['combo_thun'] = {'strips_panel': strips_per_panel, 'strips_total': 2 * strips_per_panel, 'strip_len': thun['w'],
                       'binding_ok': 2 * strips_per_panel >= 4 and thun['w'] >= d['m5']['bind_long'][1]}
    d['combo'] = {'somi_o': o_back + o_rest, 'somi_o_back': o_back, 'somi_khan_ghep': (o_back + o_rest) // d['m4']['count'],
                  'khantam_m5': ytab['khantam']['m5'], 'somi_o_rest': o_rest, 'thun_m1': ytab['aothun']['m1'], 'somi_o_all': ytab['somi']['m4']}
    d['yield_targets'] = [{'pid': p, 'label': l, 'size': s} for p, l, s, _ in targets]
    return d


def main():
    spec = json.loads((ROOT / 'data' / 'spec.json').read_text(encoding='utf-8'))
    d = derive(spec)
    out = ROOT / 'build'
    out.mkdir(exist_ok=True)
    (out / 'derived.json').write_text(json.dumps(d, ensure_ascii=False, indent=1), encoding='utf-8')
    print('derived.json:', len(json.dumps(d)), 'bytes')
    return d


if __name__ == '__main__':
    main()
