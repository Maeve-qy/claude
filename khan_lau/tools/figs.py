"""Hình minh họa & sơ đồ kỹ thuật. Mỗi hàm nhận ctx (ctx.d = số liệu dẫn xuất, ctx.spec = dữ liệu gốc) và trả về SVG."""
from art import *  # noqa


# ================================================================ BÌA

def cover_art(ctx):
    W, H = 700, 560
    s = ''
    # nền: tấm vải lanh lớn + bóng mềm
    s += '<ellipse cx="350" cy="515" rx="330" ry="30" fill="#23313A" opacity=".08"/>'
    # rổ mây với khăn cuộn
    s += basket(380, 330, 250, 150)
    for cx, cy, r, pid in ((420, 318, 34, 'gingham-blue'), (486, 305, 38, 'terry-peach'), (556, 318, 34, 'denim'),
                           (452, 262, 30, 'floral-cream'), (522, 258, 31, 'jersey-teal'), (590, 282, 26, 'stripe-sage')):
        s += rolled(cx, cy, r, pid)
    s += basket(380, 330, 250, 150).split('<rect x=')[0]  # vẽ lại mặt trước rổ đè lên khăn cuộn
    # vẽ lại viền miệng rổ
    s += f'<rect x="373" y="325" width="264" height="10" rx="5" fill="#8A6A45"/><rect x="375" y="326" width="260" height="3" rx="1.5" fill="#fff" opacity=".25"/>'
    # chồng khăn gấp bên trái
    s += stack_side(36, 290, 250, [('terry-sage', 6), ('gingham-red', -4), ('denim-light', 10), ('floral-mint', 0),
                                   ('jersey-mustard', 8), ('linen', -2), ('flannel-blue', 5), ('terry-white', 0), ('dots-terra', 7)], t=21)
    # thanh treo gỗ + 3 khăn bếp
    s += '<path d="M60 44 H430" stroke="#8A6A55" stroke-width="9" stroke-linecap="round"/><path d="M62 41 H428" stroke="#fff" stroke-opacity=".25" stroke-width="2"/>'
    s += '<circle cx="60" cy="44" r="9" fill="#6B4331"/><circle cx="430" cy="44" r="9" fill="#6B4331"/>'
    for cx in (148, 272, 376):
        s += f'<path d="M{cx} 47 v12 q0 8 -7 8" stroke="#7D8A91" stroke-width="3" fill="none" stroke-linecap="round"/>'
    s += hanging_towel(95, 84, 105, 165, 'gingham-terra', stripe='#C8643B', loop='#2B4C74', hook=False)
    s += hanging_towel(212, 84, 120, 190, 'linen-white', stripe='#2B4C74', loop='#D96F43', hook=False)
    s += hanging_towel(336, 84, 80, 140, 'gingham-green', stripe='#4E6B3A', loop='#E3B23C', hook=False)
    # khăn lau bàn trải phẳng, hơi xoay, phía trước
    s += folded(415, 470, 150, 70, 'gingham-green', rot=-6, tone='#FFFFFF')
    s += folded(210, 478, 170, 64, 'terry-sky', rot=4)
    # kéo + cuộn chỉ + thước dây
    s += big_scissors(90, 520, s_=1.0, rot=-18)
    s += spool(655, 470, '#D96F43', 1.2) + spool(630, 505, '#2B4C74', 1.0)
    s += tape_measure(470, 205, s_=.85, rot=-8)
    return svg(W, H, s)


# ================================================================ 6 MẪU (ảnh đại diện)

def _prod(ctx, k, W=210, H=150):
    if k == 'm1':
        b = jersey_rag(40, 38, 104, 96, 'jersey-pink', rot=-9) + jersey_rag(62, 30, 104, 96, 'jersey-sky', rot=4) + jersey_rag(84, 40, 96, 92, 'jersey-heather', rot=12)
    elif k == 'm2':
        b = cloth_flip(52, 14, 120, 120, 'gingham-blue', 'terry-white', stitch='#FFFFFF', quilt=[(0, 0, 1, 1), (1, 0, 0, 1)])
    elif k == 'm3':
        b = hanging_towel(66, 34, 82, 108, 'linen-white', stripe='#2B4C74', loop='#D96F43')
    elif k == 'm4':
        pids = ['floral-cream', 'gingham-terra', 'dots-terra', 'gingham-terra', 'linen', 'flannel-terra', 'dots-terra', 'flannel-terra', 'floral-cream']
        b = cloth_flip(52, 14, 120, 120, patch_front(pids, 3), 'terry-peach', stitch='#FFFFFF')
    elif k == 'm5':
        b = cloth_flip(56, 8, 104, 136, 'terry-sky', 'denim', binding=('jersey-terra', 9),
                       quilt=([(1/3, 0, 1/3, 1), (2/3, 0, 2/3, 1), (0, .25, 1, .25), (0, .5, 1, .5), (0, .75, 1, .75)], '#2B4C74'))
    else:
        b = mop(52, 112, 130, pid_face='terry-mint', pid_back='denim')
    return svg(W, H, b)


def prod_m1(ctx): return _prod(ctx, 'm1')
def prod_m2(ctx): return _prod(ctx, 'm2')
def prod_m3(ctx): return _prod(ctx, 'm3')
def prod_m4(ctx): return _prod(ctx, 'm4')
def prod_m5(ctx): return _prod(ctx, 'm5')
def prod_m6(ctx): return _prod(ctx, 'm6')


# ================================================================ QUY ƯỚC NÉT VẼ

LEGEND = [
    ('cut', 'Đường cắt', 'Mép vải; cắt đúng theo nét này'),
    ('seam', 'Đường may ráp', 'Cách mép 1 cm (phần chừa 1 cm)'),
    ('top', 'Đường diễu / chần', 'May ở mặt phải, thấy được'),
    ('fold', 'Nếp gấp', 'Gấp vải theo nét này, không cắt'),
    ('mark', 'Nét phấn đánh dấu', 'Vẽ bằng phấn / bút bay màu'),
    ('zig', 'Mũi zigzag / vắt sổ', 'Khóa mép cho vải không tưa'),
    ('gap', 'Khe lộn (không may)', 'Chừa hở để lộn khăn'),
    ('grain', 'Canh sợi dọc', 'Mũi tên song song biên vải'),
    ('dim', 'Kích thước', 'Đơn vị cm; ghi ngang × dọc'),
    ('rs', 'Mặt phải vải', 'Màu đậm, rõ họa tiết'),
    ('ws', 'Mặt trái vải', 'Màu nhạt'),
    ('clip', 'Cắt bỏ', 'Phần vải thừa cắt đi'),
]


def legend_sample(kind):
    W, H = 62, 22
    y = H / 2
    if kind == 'cut':
        b = line(4, y, W - 4, y, cls='s-cut')
    elif kind == 'seam':
        b = line(4, y, W - 4, y, cls='s-seam')
    elif kind == 'top':
        b = line(4, y, W - 4, y, cls='s-top')
    elif kind == 'fold':
        b = line(4, y, W - 4, y, cls='s-fold')
    elif kind == 'mark':
        b = line(4, y, W - 4, y, cls='s-mark')
    elif kind == 'zig':
        b = zig(4, y, W - 4, y, amp=4)
    elif kind == 'gap':
        b = gap_band(12, y, W - 12, y, t=8) + line(2, y, 12, y, cls='s-seam') + line(W - 12, y, W - 2, y, cls='s-seam') + \
            line(12, y - 4, 12, y + 4, extra='stroke="#D6336C" stroke-width="2.2"') + line(W - 12, y - 4, W - 12, y + 4, extra='stroke="#D6336C" stroke-width="2.2"')
    elif kind == 'grain':
        b = line(6, y, W - 6, y, cls='s-grain')
    elif kind == 'dim':
        b = line(5, y + 3, W - 5, y + 3, cls='s-dim') + txt(W / 2, y - 1, '32', 't-dim t-mid')
    elif kind == 'rs':
        b = rect(6, 2, W - 12, H - 4, fill=fab('gingham-blue'), rx=2) + rect(6, 2, W - 12, H - 4, cls='s-edge', rx=2)
    elif kind == 'ws':
        b = rect(6, 2, W - 12, H - 4, fill=fab('gingham-blue'), rx=2) + rect(6, 2, W - 12, H - 4, fill='#fff', rx=2, extra='opacity=".58"') + rect(6, 2, W - 12, H - 4, cls='s-edge', rx=2)
    else:
        b = rect(6, 2, W - 12, H - 4, cls='f-discard', rx=2) + rect(6, 2, W - 12, H - 4, cls='s-edge', rx=2)
    return svg(W, H, b)


def legend_grid(ctx):
    cells = ''.join(f'<div class="lg"><div class="lgs">{legend_sample(k)}</div><div><b>{n}</b><span>{m}</span></div></div>' for k, n, m in LEGEND)
    return f'<div class="lgrid">{cells}</div>'


# ================================================================ CẤU TẠO KHĂN MAY LỘN (mặt cắt)

def anatomy_bag(ctx):
    W, H = 640, 190
    b = ''
    # --- nhìn từ trên (trái)
    b += cloth_flip(18, 22, 140, 140, 'gingham-blue', 'terry-white', stitch='#0E8C8C', quilt=([(0, 0, 1, 1), (1, 0, 0, 1)], '#0E8C8C'), c=46)
    b += txt(88, 182, 'Nhìn từ trên', 't-lbl t-mid t-bold')
    # khung phóng to
    b += rect(128, 70, 34, 34, extra='fill="none" stroke="#C4592F" stroke-width="1.6" stroke-dasharray="4 3" rx="4"')
    b += path('M162 87 C 190 87 196 87 214 87', cls='s-move')
    # --- mặt cắt (phải): 1 cm = 64 px
    u = 64
    E = 566            # mép khăn (đường may ráp)
    yA, yB = 74, 126
    x0 = 236
    ym = (yA + yB) / 2
    cA, cB = '#6FA2D6', '#E6D9BF'
    for (yy, col, tw, sgn, ec) in ((yA, cA, 8, -1, '#2B4C74'), (yB, cB, 12, 1, '#8C7A5C')):
        d = f'M{x0} {yy} H{E - 18} Q{E + 4} {yy} {E + 4} {ym + sgn * 9} Q{E + 3} {ym + sgn * 6} {E - 6} {ym + sgn * 6} H{E - u}'
        b += path(d, extra=f'fill="none" stroke="{ec}" stroke-width="{tw + 2}" stroke-linejoin="round" stroke-linecap="butt"')
        b += path(d, extra=f'fill="none" stroke="{col}" stroke-width="{tw}" stroke-linejoin="round" stroke-linecap="butt"')
    # đường may ráp (chỉ đỏ xuyên 2 lớp tại mép)
    b += line(E + 1, ym - 13, E + 1, ym + 13, extra='stroke="#D6336C" stroke-width="3.4" stroke-linecap="round"')
    # đường diễu 0,5 cm + đường chần
    xt = E - u * 0.5
    xq = x0 + 74
    for xx in (xt, xq):
        b += line(xx, yA - 10, xx, yB + 12, extra='stroke="#0E8C8C" stroke-width="2.6" stroke-dasharray="5 3"')
    # kích thước
    b += line(xt, yA - 30, xt, yA - 10, cls='s-ext') + line(E + 1, yA - 30, E + 1, ym - 14, cls='s-ext')
    b += dim_h(xt, E + 1, yA - 26, '0,5 cm')
    b += line(E - u, ym + 10, E - u, yB + 30, cls='s-ext') + line(E + 1, ym + 14, E + 1, yB + 30, cls='s-ext')
    b += dim_h(E - u, E + 1, yB + 26, '1 cm', above=False, dy=14)
    # nhãn
    b += txt(x0, yA - 12, 'Lớp A (mặt lau)', 't-lbl t-bold')
    b += txt(x0, yB + 24, 'Lớp B', 't-lbl t-bold')
    b += txt(xt - 8, yA - 22, 'Đường diễu kẹp chặt phần chừa', 't-lbl t-top t-end t-sm t-bold')
    b += txt(xq, yB + 25, 'Đường chần', 't-lbl t-top t-mid t-sm t-bold')
    b += txt(E - u - 6, ym + 4, 'Phần chừa 1 cm nằm kín giữa 2 lớp', 't-lbl t-end t-sm')
    b += txt(E + 12, ym - 3, 'Mép khăn =', 't-lbl t-seam t-bold t-sm')
    b += txt(E + 12, ym + 9, 'đường may ráp', 't-lbl t-seam t-bold t-sm')
    b += txt(400, 182, 'Mặt cắt ngang mép khăn (phóng to)', 't-lbl t-mid t-bold')
    return svg(W, H, b)


# ================================================================ QUẦN ÁO CŨ -> MẢNH PHẲNG

def _piece(ctx, gid, pid_):
    for gg in ctx.spec['garments']:
        if gg['id'] == gid:
            for p in gg['pieces']:
                if p['id'] == pid_:
                    return p


def garment_shirt(ctx):
    W, H = 330, 205
    m = CM(165 - 28 * 2.35, 14, 2.35)
    b = shirt_front(m)
    b += scissors(m.P(-9, 40)[0], m.P(-9, 40)[1], s=1.1, rot=60)
    return svg(W, H, b)


def pieces_shirt(ctx):
    """các mảnh phẳng lấy từ áo sơ mi, vẽ đúng tỉ lệ + kích thước từ spec"""
    s_ = 2.9
    W, H = 360, 300
    b = ''
    back = _piece(ctx, 'somi', 'than_sau'); front = _piece(ctx, 'somi', 'vat_truoc'); sl = _piece(ctx, 'somi', 'tay')
    m = CM(10, 30, s_)
    # thân sau (có cầu vai bị bỏ)
    b += piece(10, 30 - 8 * s_, (back['w'] + 6) * s_, 8 * s_, 'gingham-sky', shadow=False)
    b += rect(10, 30 - 8 * s_, (back['w'] + 6) * s_, 8 * s_, cls='f-discard', extra='opacity=".85"')
    b += txt(10 + (back['w'] + 6) * s_ / 2, 30 - 2.2 * s_, 'cầu vai (bỏ)', 't-lbl t-mid t-sm')
    b += piece(10, 30, (back['w'] + 6) * s_, (back['h'] + 5) * s_, 'gingham-sky')
    b += zone(m, 3, 1, back['w'], back['h'], 'Thân sau', dims(back['w'], back['h']))
    # 2 vạt trước
    x2 = 10 + (back['w'] + 6) * s_ + 14
    for i in range(2):
        xx = x2 + i * (front['w'] + 3) * s_
        m2 = CM(xx, 30, s_)
        b += piece(xx, 30, (front['w'] + 2) * s_, (front['h'] + 6) * s_, 'gingham-sky')
        b += zone(m2, 1, 3, front['w'], front['h'], 'Vạt ' + ('trái' if i == 0 else 'phải'), dims(front['w'], front['h']))
    # 2 tay
    y3 = 30 + (back['h'] + 5) * s_ + 16
    for i in range(2):
        xx = 10 + i * (sl['h'] + 8) * s_
        m3 = CM(xx, y3, s_)
        # tay mở phẳng: hình thang nằm ngang
        tr = [('M', (0, -3)), ('L', (sl['h'] + 4, 0)), ('L', (sl['h'] + 4, sl['w'])), ('L', (0, sl['w'] + 3)), ('Z',)]
        b += garment_shape(m3.d(tr), 'gingham-sky')
        b += zone(m3, 1.5, 0.3, sl['h'], sl['w'] - 0.6, None)
        cx, cy = m3.P(1.5 + sl['h'] / 2, sl['w'] / 2)
        b += txt(cx, cy - 3, 'Tay áo', 't-lbl t-mid t-bold') + txt(cx, cy + 11, dims(sl['w'], sl['h']), 't-dim t-mid')
    return svg(W, H, b)


PROD_COL = {'m1': '#7FA37A', 'm2': '#D96F43', 'm3': '#2B4C74', 'm4': '#E3B23C', 'm5': '#3C9D8E', 'm6': '#7C4DFF'}
GAR_FAB = {'somi': 'gingham-sky', 'aothun': 'jersey-teal', 'jeans': 'denim', 'khantam': 'terry-peach', 'vogoi': 'floral-mint'}


def layout_svg(ctx, lid, s_=3.0, W=None, H=None, show_title=False):
    L = next(x for x in ctx.spec['layouts'] if x['id'] == lid)
    pc = _piece(ctx, L['garment'], L['piece'])
    pad = 30
    W = W or pc['w'] * s_ + pad + 12
    H = H or pc['h'] * s_ + pad + 8
    ox, oy = pad, 22
    b = piece(ox, oy, pc['w'] * s_, pc['h'] * s_, GAR_FAB[L['garment']])
    b += rect(ox, oy, pc['w'] * s_, pc['h'] * s_, fill='#fff', extra='opacity=".35"')
    b += dim_h(ox, ox + pc['w'] * s_, oy - 7, dims(pc['w'], 0).split(' ×')[0])
    b += dim_v(ox - 8, oy, oy + pc['h'] * s_, art_vn(pc['h']))
    for it in L['items']:
        col = PROD_COL[it['ref'].split('.')[0]]
        x, y, w, h = ox + it['x'] * s_, oy + it['y'] * s_, it['w'] * s_, it['h'] * s_
        b += rect(x, y, w, h, fill=fab(GAR_FAB[L['garment']]))
        b += rect(x, y, w, h, fill=col, extra='opacity=".30"')
        b += rect(x + .8, y + .8, w - 1.6, h - 1.6, extra=f'fill="none" stroke="{col}" stroke-width="1.6"')
        cx, cy = x + w / 2, y + h / 2
        code = 'M' + it['ref'][1]
        dd = dims(max(it['w'], it['h']), min(it['w'], it['h'])) if it['ref'].startswith('m6') else dims(it['w'], it['h'])
        tw = len(dd) * 6.2
        if h >= 30 and w >= max(tw, 26):
            b += txt(cx, cy - 2, code, 't-lbl t-mid t-bold')
            b += txt(cx, cy + 11, dd, 't-dim t-mid')
        elif w >= tw + 22 and h >= 14:
            b += txt(cx, cy + 4, code + '  ' + dd, 't-dim t-mid')
        elif h >= tw + 22 and w >= 14:
            b += f'<text x="{f(cx + 4)}" y="{f(cy)}" class="t-dim t-mid" transform="rotate(-90 {f(cx + 4)} {f(cy)})">{code}  {dd}</text>'
        elif w >= 26 and h >= 16:
            b += txt(cx, cy + 4, code, 't-lbl t-mid t-bold t-sm')
    return svg(W, H, b)


def art_vn(x):
    from art import vn as _vn
    return _vn(x)


def lay_somi_back(ctx): return layout_svg(ctx, 'somi_back', 3.3)
def lay_somi_back_m3(ctx): return layout_svg(ctx, 'somi_back_m3', 3.3)
def lay_thun_front(ctx): return layout_svg(ctx, 'thun_front', 3.2)
def lay_jeans_leg(ctx): return layout_svg(ctx, 'jeans_leg', 2.6)
def lay_towel(ctx): return layout_svg(ctx, 'towel', 2.05)


# ================================================================ PHẦN 1 — CHỌN VẢI

SWATCH = {'gingham_blue': 'gingham-blue', 'jersey_heather': 'jersey-heather', 'terry_white': 'terry-white', 'denim': 'denim',
          'linen': 'linen', 'flannel_red': 'flannel-red', 'fleece_green': 'fleece-green', 'microfiber_yellow': 'micro-yellow'}


def swatch_svg(pid, w=46, h=40, fray=0):
    b = rect(2, 3, w - 4, h - 4, fill='#23313A', rx=5, extra='opacity=".12"')
    b += rect(0, 0, w - 4, h - 4, fill=fab(pid), rx=5)
    # mép tưa minh họa ở cạnh dưới
    if fray:
        for k in range(4, int(w) - 6, 3):
            ln = 2 + (k * 7 % 5) * fray / 2
            b += line(k, h - 4, k + (k % 2), h - 4 + ln, extra='stroke="#6F7F88" stroke-width=".8" opacity=".75"')
    b += rect(0, 0, w - 4, h - 4, rx=5, extra='fill="none" stroke="#23313A" stroke-opacity=".25"')
    return svg(w, h + 4, b)


def _okbar(ok, W):
    col = '#46693F' if ok else '#A8482A'
    t = 'ĐẠT' if ok else 'KHÔNG ĐẠT'
    return rect(W / 2 - 34, 66, 68, 15, fill=col, rx=7.5) + txt(W / 2, 77, t, 't-lbl t-mid t-bold t-white t-sm')


def _drop_panel(ok):
    W, H = 96, 84
    b = rect(4, 34, 88, 26, fill=fab('gingham-blue' if ok else 'stripe-red'), rx=4)
    b += rect(4, 34, 88, 26, rx=4, extra='fill="none" stroke="#23313A" stroke-opacity=".25"')
    if ok:
        b += '<ellipse cx="48" cy="47" rx="26" ry="8.5" fill="#1C3553" opacity=".32"/><ellipse cx="48" cy="47" rx="16" ry="5" fill="#1C3553" opacity=".22"/>'
        b += txt(48, 12, '≤ 5 giây', 't-lbl t-mid t-bold')
    else:
        b += '<ellipse cx="48" cy="46" rx="11" ry="3" fill="#23313A" opacity=".18"/>'
        b += '<path d="M37 44 C37 33 59 33 59 44 C59 47.5 37 47.5 37 44 Z" fill="#BCD4EC" stroke="#2B6CB0" stroke-width="1.2"/>'
        b += '<ellipse cx="43" cy="38.5" rx="3" ry="1.6" fill="#fff" opacity=".9"/>'
        b += txt(48, 12, 'sau 30 giây', 't-lbl t-mid t-bold')
    b += '<path d="M48 16 v7" stroke="#9AA5AB" stroke-width="5" stroke-linecap="round"/><path d="M48 23 v4" stroke="#9AA5AB" stroke-width="2"/>'
    return svg(W, H, b + _okbar(ok, W))


def test_drop_ok(ctx): return _drop_panel(True)
def test_drop_bad(ctx): return _drop_panel(False)


def _bleed_panel(ok):
    W, H = 96, 84
    b = rect(6, 6, 84, 54, fill='#FFFFFF', rx=3, extra='stroke="#C9CDCF"')
    b += rect(24, 16, 48, 30, fill=fab('flannel-red'), rx=4, extra='transform="rotate(-6 48 31)"')
    if not ok:
        b += '<ellipse cx="76" cy="44" rx="12" ry="9" fill="#C2452D" opacity=".38"/><ellipse cx="18" cy="24" rx="9" ry="7" fill="#C2452D" opacity=".3"/>'
    return svg(W, H, b + _okbar(ok, W))


def test_bleed_ok(ctx): return _bleed_panel(True)
def test_bleed_bad(ctx): return _bleed_panel(False)


def _fray_panel(ok):
    W, H = 96, 84
    pid = 'jersey-teal' if ok else 'linen'
    b = rect(8, 6, 80, 36, fill=fab(pid), rx=2)
    b += rect(8, 6, 80, 36, rx=2, extra='fill="none" stroke="#23313A" stroke-opacity=".25"')
    if ok:
        b += rect(8, 39, 80, 3, fill='#23313A', extra='opacity=".18"')
    else:
        for k in range(10, 87, 2):
            ln = 6 + (k * 13 % 11)
            b += f'<path d="M{k} 42 q{(k % 3) - 1} {ln / 2} {(k % 5) - 2} {ln}" stroke="#8C7A5C" stroke-width=".9" fill="none" opacity=".85"/>'
    return svg(W, H, b + _okbar(ok, W))


def test_fray_ok(ctx): return _fray_panel(True)
def test_fray_bad(ctx): return _fray_panel(False)


def _wet_panel(ok):
    W, H = 96, 84
    pid = 'gingham-blue' if ok else 'floral-mint'
    b = ''
    if ok:
        b += rect(14, 22, 68, 22, fill=fab(pid), rx=2) + rect(14, 22, 68, 22, rx=2, extra='fill="none" stroke="#23313A" stroke-opacity=".3"')
    else:
        b += poly([(10, 22), (44, 22), (40, 28), (46, 33), (41, 38), (45, 44), (10, 44)], fill=fab(pid))
        b += poly([(52, 22), (86, 22), (86, 44), (51, 44), (55, 38), (50, 33), (56, 28)], fill=fab(pid))
        b += poly([(10, 22), (44, 22), (40, 28), (46, 33), (41, 38), (45, 44), (10, 44)], extra='fill="none" stroke="#23313A" stroke-opacity=".3"')
        b += poly([(52, 22), (86, 22), (86, 44), (51, 44), (55, 38), (50, 33), (56, 28)], extra='fill="none" stroke="#23313A" stroke-opacity=".3"')
    b += path('M12 33 H2', cls='s-move') + path('M84 33 H94', cls='s-move')
    b += '<path d="M30 12 q3 -5 6 0 q-3 4 -6 0" fill="#BCD4EC" stroke="#2B6CB0"/><path d="M60 12 q3 -5 6 0 q-3 4 -6 0" fill="#BCD4EC" stroke="#2B6CB0"/>'
    return svg(W, H, b + _okbar(ok, W))


def test_wet_ok(ctx): return _wet_panel(True)
def test_wet_bad(ctx): return _wet_panel(False)


def garment_tshirt(ctx):
    W, H = 300, 210
    m = CM(150 - 25 * 2.6, 16, 2.6)
    b = tshirt_front(m)
    b += scissors(m.P(52, 23)[0] + 12, m.P(52, 23)[1] - 2, s=1.1, rot=180)
    cx, cy = m.P(25, 14)
    b += txt(cx, cy - 18, 'hình in: bỏ', 't-lbl t-mid t-sm t-bold')
    b += zone(m, 1, 23.5, 48, 45, 'Thân trước', dims(48, 45))
    return svg(W, H, b)


def garment_jeans(ctx):
    W, H = 200, 304
    m = CM(100 - 20 * 2.55, 14, 2.55)
    b = jeans_front(m)
    for x0 in (-1.5, 20.5):
        b += zone(m, x0, 31, 19 if x0 < 0 else 19, 70)
    for xx in (8, 31):
        cx, cy = m.P(xx, 66)
        b += f'<text x="{f(cx)}" y="{f(cy)}" class="t-lbl t-mid t-bold t-sm" transform="rotate(-90 {f(cx)} {f(cy)})">Ống trước 20 × 70</text>'
    b += txt(100, 296, '(2 ống sau ở mặt kia)', 't-lbl t-mid t-sm')
    return svg(W, H, b)


def garment_towel(ctx):
    W, H = 190, 328
    m = CM(95 - 35 * 2.1, 24, 2.1)
    b = bath_towel(m)
    b += zone(m, 2, 11, 66, 118, 'Phần dùng được', '66 × 125')
    cx, cy = m.P(35, -2)
    b += txt(cx, cy, 'viền dệt 2 đầu: bỏ', 't-lbl t-mid t-bold', extra='style="font-size:12px"')
    return svg(W, H, b)


def _box(x, y, w, h, scraps, label, sub):
    s = ''
    # hộp giấy mở nắp
    s += poly([(x + 6, y), (x + w - 6, y), (x + w, y + 10), (x, y + 10)], fill='#C9A77C')
    for sx, sy, sw, sh, pid, rot in scraps:
        s += g(rect(x + sx, y + sy, sw, sh, fill=fab(pid), rx=1.5) + rect(x + sx, y + sy, sw, sh, rx=1.5, extra='fill="none" stroke="#23313A" stroke-opacity=".25"'),
               tr=f'rotate({rot} {f(x + sx + sw / 2)} {f(y + sy + sh / 2)})')
    s += rect(x + 3, y + h * .38 + 3, w, h * .62, fill='#23313A', extra='opacity=".12"')
    s += rect(x, y + h * .38, w, h * .62, fill='#D8B98F')
    s += rect(x, y + h * .38, w, 5, fill='#8A6A45', extra='opacity=".35"')
    s += rect(x + w * .2, y + h * .55, w * .6, h * .3, fill='#FFFCF6', rx=3)
    s += txt(x + w / 2, y + h * .55 + 14, label, 't-lbl t-mid t-bold t-nost')
    for i, ln in enumerate(sub if isinstance(sub, list) else [sub]):
        s += txt(x + w / 2, y + h + 16 + i * 12, ln, 't-lbl t-mid t-sm')
    return s


def scrap_bins(ctx):
    d = ctx.d
    W, H = 660, 160
    bw, bh, gap = 118, 110, 16
    xs = [6 + i * (bw + gap) for i in range(5)]
    b = ''
    b += _box(xs[0], 10, bw, bh, [(8, -26, 60, 44, 'gingham-blue', -8), (44, -30, 62, 46, 'terry-sage', 7)], f'≥ {art_vn(d["m2"]["cut"][0])} cm', ['Khăn lau bàn,', 'lau nhà, khăn bếp'])
    b += _box(xs[1], 10, bw, bh, [(10, -14, 40, 34, 'floral-cream', -10), (50, -18, 44, 36, 'jersey-teal', 9), (32, -8, 30, 26, 'denim-light', 2)], f'{art_vn(d["m4"]["options"][0]["sq_cut"])}–{art_vn(d["m2"]["cut"][0])} cm', ['Giẻ rửa chén, giẻ thun,', 'túi vỏ bàn lau, ô 17'])
    b += _box(xs[2], 10, bw, bh, [(8, -6, 22, 22, 'dots-terra', -12), (30, -10, 24, 24, 'gingham-red', 6), (56, -6, 22, 22, 'flannel-blue', -4), (78, -8, 22, 22, 'linen', 10)], f'{art_vn(d["m4"]["options"][3]["sq_cut"])}–{art_vn(d["m4"]["options"][0]["sq_cut"])} cm', ['Ô ghép 12 · 9,5 · 8 cm', 'lớp ruột nhỏ'])
    b += _box(xs[3], 10, bw, bh, [(6, -2, 104, 9, 'stripe-navy', -6), (8, 6, 100, 8, 'jersey-mustard', 4), (10, -12, 96, 10, 'gingham-green', -2)], f'Dải {art_vn(d["m4"]["strip_min"])}–{art_vn(d["m5"]["binding_w"])} cm', ['Ghép dải, dải bo viền,', 'quai treo'])
    b += _box(xs[4], 10, bw, bh, [(14, 8, 12, 10, 'floral-mint', 20), (30, 4, 14, 9, 'denim', -14), (48, 8, 10, 12, 'terry-peach', 8), (62, 3, 13, 10, 'gingham-terra', -6), (80, 7, 11, 11, 'jersey-pink', 15)], f'< {art_vn(d["m4"]["options"][3]["sq_cut"])} cm', ['Nhồi đệm lót nồi,', 'gối kê chân'])
    return svg(W, H, b)


def grain_woven(ctx):
    W, H = 300, 200
    x0, y0, w, h = 30, 12, 186, 156
    b = rect(x0 + 3, y0 + 4, w, h, fill='#23313A', extra='opacity=".12"')
    b += rect(x0, y0, w, h, fill='#F3EBDD')
    for k in range(0, int(w), 6):
        b += line(x0 + k + 3, y0, x0 + k + 3, y0 + h, extra='stroke="#2B4C74" stroke-opacity=".3" stroke-width="1.6"')
    for k in range(0, int(h), 6):
        b += line(x0, y0 + k + 3, x0 + w, y0 + k + 3, extra='stroke="#C4592F" stroke-opacity=".26" stroke-width="1.6"')
    b += rect(x0, y0, 9, h, fill='#E6D9BF') + ''.join(line(x0 + 2 + i * 2.2, y0, x0 + 2 + i * 2.2, y0 + h, extra='stroke="#8C7A5C" stroke-opacity=".5" stroke-width=".8"') for i in range(4))
    b += rect(x0, y0, w, h, cls='s-edge')
    b += f'<text x="{x0 - 8}" y="{y0 + h / 2}" class="t-lbl t-mid t-sm t-bold" transform="rotate(-90 {x0 - 8} {y0 + h / 2})">Biên vải</text>'
    cx = x0 + 150
    b += line(cx, y0 + 12, cx, y0 + h - 12, cls='s-grain', extra='style="stroke-width:2.4"')
    b += txt(x0 + w + 8, y0 + 50, 'Canh dọc', 't-lbl t-bold')
    b += txt(x0 + w + 8, y0 + 63, 'ít giãn', 't-lbl t-sm')
    b += txt(x0 + w + 8, y0 + 75, 'nhất', 't-lbl t-sm')
    b += line(cx + 4, y0 + 58, x0 + w + 5, y0 + 58, extra='stroke="#23313A" stroke-width=".8"')
    yh = y0 + h - 22
    b += line(x0 + 22, yh, x0 + w - 12, yh, extra='stroke="#C4592F" stroke-width="2.4" marker-start="url(#arr-terra)" marker-end="url(#arr-terra)"')
    b += txt(x0 + w / 2, y0 + h + 16, 'Canh ngang: giãn nhẹ', 't-lbl t-mid t-bold t-terra')
    b += line(x0 + 24, y0 + 16, x0 + 100, y0 + 92, extra='stroke="#7C4DFF" stroke-width="2.4" stroke-dasharray="5 3"')
    b += txt(x0 + 22, y0 + 108, 'Canh xéo 45°', 't-lbl t-bold t-mark')
    b += txt(x0 + 22, y0 + 121, 'giãn nhiều', 't-lbl t-sm t-mark')
    return svg(W, H, b)


def off_grain(ctx):
    W, H = 330, 146
    b = ''
    b += piece(14, 16, 84, 84, 'gingham-green')
    b += txt(56, 120, 'Cắt đúng canh', 't-lbl t-mid t-bold') + txt(56, 133, 'giặt xong vẫn vuông', 't-lbl t-mid t-sm')
    b += '<g transform="translate(124 16)"><clipPath id="og1"><rect width="84" height="84"/></clipPath><rect x="2.5" y="3" width="84" height="84" fill="#23313A" opacity=".12"/><g clip-path="url(#og1)"><g transform="rotate(12 42 42)"><rect x="-40" y="-40" width="170" height="170" fill="url(#p-gingham-green)"/></g></g><rect width="84" height="84" class="s-edge"/></g>'
    b += txt(166, 120, 'Cắt lệch canh', 't-lbl t-mid t-bold t-terra') + txt(166, 133, 'sọc caro chạy xiên', 't-lbl t-mid t-sm')
    b += path('M214 58 H238', cls='s-move')
    sk = [(248, 22), (316, 12), (324, 94), (256, 104)]
    b += '<clipPath id="og2">' + poly(sk) + '</clipPath>'
    b += poly([(x + 2.5, y + 3) for x, y in sk], fill='#23313A', extra='opacity=".12"')
    b += '<g clip-path="url(#og2)"><g transform="rotate(4 286 58)"><rect x="220" y="-10" width="140" height="140" fill="url(#p-gingham-green)"/></g></g>'
    b += poly(sk, cls='s-edge')
    b += txt(286, 120, 'Sau khi giặt', 't-lbl t-mid t-bold t-terra') + txt(286, 133, 'khăn méo, vặn', 't-lbl t-mid t-sm')
    return svg(W, H, b)


def pull_thread(ctx):
    W, H = 300, 150
    x0, y0, w, h = 20, 18, 220, 110
    b = rect(x0 + 3, y0 + 4, w, h, fill='#23313A', extra='opacity=".12"') + rect(x0, y0, w, h, fill=fab('linen'))
    b += rect(x0, y0, w, h, cls='s-edge')
    yy = y0 + 46
    # sợi bị rút: vải nhăn dọc theo đường
    b += line(x0, yy, x0 + 150, yy, extra='stroke="#FFFCF6" stroke-width="3"')
    b += zig(x0 + 150, yy, x0 + w, yy, amp=1.6, step=3.6, cls='').replace('/>', ' fill="none" stroke="#8C7A5C" stroke-width="1"/>')
    b += path(f'M{x0 + 150} {yy} Q{x0 + 190} {yy - 2} {x0 + w + 22} {yy - 26}', extra='fill="none" stroke="#8C7A5C" stroke-width="1.6"')
    b += path(f'M{x0 + w + 30} {yy - 32} q -6 -2 -8 6', extra='stroke="#C4592F" stroke-width="2" fill="none"')
    b += txt(x0 + w + 20, yy - 36, 'kéo', 't-lbl t-mid t-sm t-bold t-terra')
    b += scissors(x0 + 60, yy + 16, s=1.0, rot=0)
    b += line(x0 + 76, yy + 1, x0 + 140, yy + 1, extra='stroke="#C4592F" stroke-width="1.6" stroke-dasharray="4 3"')
    b += txt(x0 + 8, yy + 50, 'Khe hở do rút sợi = đường cắt thẳng canh', 't-lbl t-sm t-bold')
    return svg(W, H, b)


def right_wrong(ctx):
    W, H = 330, 112
    b = ''
    items = [('jersey-teal', 'Thun · mặt phải', 'cột chữ V dọc'), ('purl-teal', 'Thun · mặt trái', 'gợn vòng ngang'),
             ('denim', 'Jeans · mặt phải', 'đậm, vân chéo'), ('denim-back', 'Jeans · mặt trái', 'nhạt, sợi trắng')]
    for i, (pid, t1, t2) in enumerate(items):
        x = 6 + i * 81
        b += piece(x, 6, 70, 62, pid, rx=5)
        b += txt(x + 35, 86, t1, 't-lbl t-mid t-sm t-bold')
        b += txt(x + 35, 99, t2, 't-lbl t-mid t-sm')
    return svg(W, H, b)


def square_up_scrap(ctx):
    W, H = 330, 150
    b = ''
    shape = [(18, 30), (70, 14), (150, 20), (196, 44), (188, 96), (206, 128), (120, 138), (60, 132), (28, 110), (10, 70)]
    b += poly([(x + 3, y + 4) for x, y in shape], fill='#23313A', extra='opacity=".12"')
    b += poly(shape, fill=fab('floral-cream'))
    b += poly(shape, cls='s-edge')
    rx0, ry0, rw, rh = 48, 30, 88, 88
    b += rect(rx0, ry0, rw, rh, extra='fill="#fff" opacity=".35"')
    for i, (x1, y1, x2, y2) in enumerate([(rx0, ry0 - 16, rx0, ry0 + rh + 14), (rx0 - 14, ry0 + rh, rx0 + rw + 16, ry0 + rh),
                                          (rx0 + rw, ry0 + rh + 14, rx0 + rw, ry0 - 16), (rx0 + rw + 14, ry0, rx0 - 16, ry0)], 1):
        b += line(x1, y1, x2, y2, extra='stroke="#C4592F" stroke-width="1.8" stroke-dasharray="7 4"')
    for i, (x, y) in enumerate([(rx0 - 10, ry0 + 20), (rx0 + 30, ry0 + rh + 10), (rx0 + rw + 10, ry0 + rh - 20), (rx0 + rw - 30, ry0 - 10)], 1):
        b += badge(x, y, i, r=8)
    b += line(rx0 + rw - 14, ry0 + 12, rx0 + rw - 14, ry0 + rh - 12, cls='s-grain')
    b += txt(rx0 + rw / 2 - 6, ry0 + rh / 2 + 4, 'miếng vuông', 't-lbl t-mid t-bold')
    # ê-ke
    b += poly([(236, 40), (236, 128), (318, 128)], fill='#F2D78E', extra='opacity=".9"') + poly([(250, 70), (250, 114), (294, 114)], fill='#FFFCF6')
    b += poly([(236, 40), (236, 128), (318, 128)], extra='fill="none" stroke="#9C7212" stroke-width="1.2"')
    for k in range(0, 80, 8):
        b += line(236, 128 - k, 241, 128 - k, extra='stroke="#9C7212" stroke-width="1"')
    b += txt(277, 144, 'ê-ke / góc bìa', 't-lbl t-mid t-sm t-bold')
    return svg(W, H, b)


# ================================================================ PHẦN 2 — PHỐI MÀU
import math as _math

WHEEL = [('Vàng', '#F2C94C'), ('Vàng cam', '#F2A541'), ('Cam', '#EE8434'), ('Cam đỏ', '#E2603A'), ('Đỏ', '#C8453A'), ('Đỏ tím', '#B0457A'),
         ('Tím', '#7B4F9D'), ('Tím lam', '#5561A8'), ('Lam', '#3E74B8'), ('Lam lục', '#2F9C95'), ('Lục', '#5BA35B'), ('Vàng lục', '#A6C45A')]


def _seg(cx, cy, r0, r1, i, n=12, gap=1.2):
    a0 = _math.radians(i * 360 / n - 90 - 180 / n + gap / 2)
    a1 = _math.radians((i + 1) * 360 / n - 90 - 180 / n - gap / 2)
    p = lambda r, a: (cx + r * _math.cos(a), cy + r * _math.sin(a))
    x0, y0 = p(r1, a0); x1, y1 = p(r1, a1); x2, y2 = p(r0, a1); x3, y3 = p(r0, a0)
    return f'M{x0:.2f} {y0:.2f} A{r1} {r1} 0 0 1 {x1:.2f} {y1:.2f} L{x2:.2f} {y2:.2f} A{r0} {r0} 0 0 0 {x3:.2f} {y3:.2f} Z'


def mix(hex_, t, to='#FFFFFF'):
    a = [int(hex_[i:i + 2], 16) for i in (1, 3, 5)]
    b_ = [int(to[i:i + 2], 16) for i in (1, 3, 5)]
    return '#' + ''.join(f'{round(x + (y - x) * t):02X}' for x, y in zip(a, b_))


def luminance(hex_):
    def lin(c):
        c = c / 255
        return c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4
    r, g_, b_ = (int(hex_[i:i + 2], 16) for i in (1, 3, 5))
    return 0.2126 * lin(r) + 0.7152 * lin(g_) + 0.0722 * lin(b_)


def grey_of(hex_):
    y = luminance(hex_)
    v = 1.055 * y ** (1 / 2.4) - 0.055 if y > 0.0031308 else 12.92 * y
    k = round(max(0, min(1, v)) * 255)
    return f'#{k:02X}{k:02X}{k:02X}'


def color_wheel(ctx):
    W, H = 300, 260
    cx, cy = 150, 128
    b = f'<circle cx="{cx + 3}" cy="{cy + 4}" r="100" fill="#23313A" opacity=".1"/>'
    for i, (n, c) in enumerate(WHEEL):
        b += f'<path d="{_seg(cx, cy, 52, 100, i)}" fill="{c}"/>'
        b += f'<path d="{_seg(cx, cy, 36, 51, i)}" fill="{mix(c, .5)}"/>'
    b += f'<circle cx="{cx}" cy="{cy}" r="34" fill="#FFFCF6"/>'
    b += txt(cx, cy - 2, 'Vòng', 't-lbl t-mid t-bold t-nost') + txt(cx, cy + 12, '12 màu', 't-lbl t-mid t-bold t-nost')
    for i, (n, c) in enumerate(WHEEL):
        a = _math.radians(i * 30 - 90)
        tx, ty = cx + 113 * _math.cos(a), cy + 113 * _math.sin(a) + 4
        anc = 't-mid' if abs(_math.cos(a)) < .3 else ('' if _math.cos(a) > 0 else 't-end')
        b += txt(tx, ty, n, f't-lbl t-sm {anc}')
    # nửa nóng / lạnh
    b += txt(262, 20, 'Màu nóng', 't-lbl t-bold t-terra') + txt(4, 250, 'Màu lạnh', 't-lbl t-bold t-denim')
    return svg(W, H, b)


def _mini_wheel(sel, tints=False):
    W, H = 96, 96
    cx, cy = 48, 48
    b = ''
    for i, (n, c) in enumerate(WHEEL):
        on = i in sel
        b += f'<path d="{_seg(cx, cy, 20, 44 if on else 38, i)}" fill="{c}" opacity="{1 if on else .22}"/>'
    if tints:
        c = WHEEL[sel[0]][1]
        for k, t in enumerate((.35, .6)):
            b += f'<path d="{_seg(cx, cy, 8 + k * 6, 13 + k * 6, sel[0])}" fill="{mix(c, t)}"/>'
    for i in sel:
        a = _math.radians(i * 30 - 90)
        b += f'<circle cx="{cx + 50 * _math.cos(a):.1f}" cy="{cy + 50 * _math.sin(a):.1f}" r="3" fill="#23313A"/>'
    return svg(W, H, b)


def _mini_patch(cols, ovs, n=3, size=84):
    b = ''
    cw = size / n
    b += rect(3, 4, size, size, fill='#23313A', extra='opacity=".12"')
    for r in range(n):
        for c in range(n):
            k = (r * n + c)
            col = cols[k % len(cols)]
            ov = ovs[k % len(ovs)]
            b += rect(c * cw, r * cw, cw + .3, cw + .3, fill=col)
            if ov:
                b += rect(c * cw, r * cw, cw + .3, cw + .3, fill=fab(ov))
    b += rect(0, 0, size, size, extra='fill="none" stroke="#23313A" stroke-opacity=".25"')
    return svg(size + 4, size + 5, b)


SCHEMES = [
    ('Đơn sắc', 'Một màu, nhiều độ đậm nhạt. Dễ nhất, luôn hài hòa.', [10], True,
     ['#3F7F3F', '#8DC08A', '#5BA35B', '#C9E3C6', '#3F7F3F', '#8DC08A', '#5BA35B', '#C9E3C6', '#3F7F3F'], ['ov-dots', None, 'ov-stripe', None, 'ov-floral', None, 'ov-check', None, 'ov-dots']),
    ('Tương đồng', '2–3 màu đứng cạnh nhau trên vòng. Ấm áp, êm mắt.', [1, 2, 3], False,
     ['#F2A541', '#EE8434', '#E2603A', '#EE8434', '#F2A541', '#E2603A', '#E2603A', '#F2A541', '#EE8434'], [None, 'ov-dots', 'ov-stripe', 'ov-check', None, 'ov-dots', None, 'ov-floral', None]),
    ('Bổ túc', '2 màu đối diện. Nổi bật: 1 màu làm chính, màu kia chỉ điểm xuyết.', [8, 2], False,
     ['#3E74B8', '#3E74B8', '#9DB7D5', '#3E74B8', '#EE8434', '#3E74B8', '#9DB7D5', '#3E74B8', '#3E74B8'], ['ov-check', None, 'ov-dots', None, None, 'ov-stripe', 'ov-dots', None, 'ov-check']),
    ('Bộ ba', '3 màu cách đều nhau. Vui mắt; nên dùng bản nhạt (pastel).', [0, 4, 8], False,
     ['#F6DE92', '#E8A19B', '#A9C3E3', '#E8A19B', '#FFFFFF', '#F6DE92', '#A9C3E3', '#F6DE92', '#E8A19B'], ['ov-dots-d', None, 'ov-stripe', None, 'ov-floral-d', 'ov-check', None, 'ov-dots-d', None]),
]


def scheme_cards(ctx):
    out = ''
    for name, desc, sel, tints, cols, ovs in SCHEMES:
        out += f'<div class="sch"><div class="scha">{_mini_wheel(sel, tints)}{_mini_patch(cols, ovs)}</div><b>{name}</b><span>{desc}</span></div>'
    return f'<div class="schs">{out}</div>'


def rule_603010(ctx):
    n = 9
    shares = [('chính', .6, '#2B4C74', 'ov-check'), ('phụ', .3, '#E8DCC6', 'ov-stripe-d'), ('nhấn', .1, '#D96F43', 'ov-dots')]
    raw = [n * p for _, p, _, _ in shares]
    cnt = [int(x) for x in raw]
    for i in sorted(range(3), key=lambda i: raw[i] - cnt[i], reverse=True)[: n - sum(cnt)]:
        cnt[i] += 1
    assert sum(cnt) == n
    ctx.d['r603010'] = cnt
    order = [0, 1, 0, 1, 2, 1, 0, 0, 0]  # chỉ số màu cho 9 ô: nhấn ở giữa
    assert [order.count(i) for i in range(3)] == cnt, (order, cnt)
    W, H = 300, 120
    b = ''
    size, cw = 96, 32
    b += rect(3, 14, size, size, fill='#23313A', extra='opacity=".12"')
    for k, ci in enumerate(order):
        r, c = divmod(k, 3)
        _, _, col, ov = shares[ci]
        b += rect(c * cw, 10 + r * cw, cw + .3, cw + .3, fill=col) + rect(c * cw, 10 + r * cw, cw + .3, cw + .3, fill=fab(ov))
    for k in (1, 2):
        b += line(k * cw, 10, k * cw, 10 + size, extra='stroke="#fff" stroke-width="1.4"') + line(0, 10 + k * cw, size, 10 + k * cw, extra='stroke="#fff" stroke-width="1.4"')
    b += rect(0, 10, size, size, extra='fill="none" stroke="#23313A" stroke-opacity=".3"')
    x = 112
    for i, (nm, p, col, ov) in enumerate(shares):
        wbar = 80 * p
        y = 18 + i * 32
        b += rect(x, y, wbar, 18, fill=col, rx=3) + rect(x, y, wbar, 18, fill=fab(ov), rx=3)
        b += txt(x + wbar + 6, y + 13, f'{int(p * 100)}% màu {nm} = {cnt[i]} ô', 't-lbl t-sm t-bold')
    return svg(W, H, b)


def value_check(ctx):
    pairs = [(('Đỏ gạch', '#C2452D'), ('Xanh lá', '#3A7C50')), (('Navy', '#22385C'), ('Vàng bơ', '#F4D58D'))]
    dl = [abs(luminance(a[1]) - luminance(b_[1])) for a, b_ in pairs]
    assert dl[0] < 0.05 and dl[1] > 0.4, dl  # cặp 1 gần cùng độ sáng, cặp 2 tương phản mạnh
    W, H = 300, 136
    b = txt(0, 26, 'Ảnh', 't-lbl t-sm t-bold') + txt(0, 38, 'màu', 't-lbl t-sm t-bold') + txt(0, 78, 'Ảnh đen', 't-lbl t-sm t-bold') + txt(0, 90, 'trắng', 't-lbl t-sm t-bold')
    for k, (a, b2) in enumerate(pairs):
        x0 = 60 + k * 122
        for j, (nm, col) in enumerate((a, b2)):
            b += rect(x0 + j * 56, 8, 52, 42, fill=col, rx=4)
            b += rect(x0 + j * 56, 60, 52, 42, fill=grey_of(col), rx=4)
            b += txt(x0 + j * 56 + 26, 116, nm, 't-lbl t-mid t-sm')
        b += txt(x0 + 54, 131, 'Nhòe vào nhau' if k == 0 else 'Tách bạch rõ', f't-lbl t-mid t-bold t-sm {"t-terra" if k == 0 else "t-sage"}')
    return svg(W, H, b)


def palette_card_art(ctx, pid):
    P = next(p for p in ctx.spec['palettes'] if p['id'] == pid)
    cols = [c for _, c in P['colors']]
    light = lambda c: luminance(c) > .45
    ov = lambda c, k: (['ov-dots-d', 'ov-stripe-d', 'ov-floral-d', None][k % 4] if light(c) else ['ov-dots', 'ov-check', 'ov-floral', None][k % 4])
    W, H = 250, 104
    b = ''
    # khăn ghép 3×3
    order = [0, 2, 1, 2, 3, 2, 1, 2, 0]
    size, cw = 88, 88 / 3
    b += rect(8 + 3, 8 + 4, size, size, fill='#23313A', extra='opacity=".12"')
    for k, ci in enumerate(order):
        r, c = divmod(k, 3)
        col = cols[ci]
        b += rect(8 + c * cw, 8 + r * cw, cw + .3, cw + .3, fill=col)
        o = ov(col, k)
        if o:
            b += rect(8 + c * cw, 8 + r * cw, cw + .3, cw + .3, fill=fab(o))
    b += rect(8, 8, size, size, extra='fill="none" stroke="#23313A" stroke-opacity=".3"')
    # chồng 3 khăn gấp
    for i, ci in enumerate([3, 1, 0, 2]):
        y = 18 + i * 19
        col = cols[ci]
        b += rect(118 + 3, y + 3, 120, 17, rx=8, fill='#23313A', extra='opacity=".12"')
        b += rect(118 + (i % 2) * 4, y, 120, 17, rx=8, fill=col)
        o = ov(col, i + 1)
        if o:
            b += rect(118 + (i % 2) * 4, y, 120, 17, rx=8, fill=fab(o))
        b += rect(118 + (i % 2) * 4, y + 9, 120, 8, rx=5, fill='#23313A', extra='opacity=".1"')
        b += line(126 + (i % 2) * 4, y + 8.5, 226 + (i % 2) * 4, y + 8.5, extra=f'stroke="{"#23313A" if light(col) else "#FFFFFF"}" stroke-opacity=".6" stroke-width="1" stroke-dasharray="3 2"')
        b += rect(118 + (i % 2) * 4, y, 120, 17, rx=8, extra='fill="none" stroke="#23313A" stroke-opacity=".25"')
    return svg(W, H, b)


def pattern_mix(ctx):
    W, H = 320, 128
    b = ''
    ok = [('flannel-terra', 'Lớn'), ('dots-terra', 'Nhỏ'), (None, 'Trơn')]
    bad = [('flannel-red', 'Lớn'), ('flannel-blue', 'Lớn'), ('floral-mint', 'Lớn')]
    for k, (sets, title, good) in enumerate(((ok, 'Nên: lớn + nhỏ + trơn', True), (bad, 'Tránh: 3 họa tiết lớn', False))):
        x0 = 6 + k * 160
        for j, (pid, lb) in enumerate(sets):
            x = x0 + j * 50
            b += rect(x + 2, 22, 44, 62, fill='#23313A', rx=4, extra='opacity=".12"')
            b += rect(x, 18, 44, 62, fill=fab(pid) if pid else '#E8D5B5', rx=4)
            b += rect(x, 18, 44, 62, rx=4, extra='fill="none" stroke="#23313A" stroke-opacity=".25"')
            b += txt(x + 22, 98, lb, 't-lbl t-mid t-sm')
        b += txt(x0 + 72, 12, title, f't-lbl t-mid t-bold {"t-sage" if good else "t-terra"}')
        b += f'<circle cx="{x0 + 72}" cy="116" r="8" fill="{"#46693F" if good else "#C4592F"}"/>' + (path(f'M{x0 + 68} 116 l3 3 l5 -6', extra='stroke="#fff" stroke-width="2" fill="none" stroke-linecap="round"') if good else path(f'M{x0 + 69} 113 l6 6 M{x0 + 75} 113 l-6 6', extra='stroke="#fff" stroke-width="2" stroke-linecap="round"'))
    return svg(W, H, b)


def pick_from_print(ctx):
    W, H = 640, 150
    b = ''
    b += rect(8 + 3, 18 + 4, 150, 110, fill='#23313A', rx=6, extra='opacity=".12"') + rect(8, 18, 150, 110, fill=fab('floral-cream'), rx=6)
    b += rect(8, 18, 150, 110, rx=6, extra='fill="none" stroke="#23313A" stroke-opacity=".25"')
    b += txt(83, 144, '1. Mảnh chủ đạo (bạn thích nhất)', 't-lbl t-mid t-sm t-bold')
    picks = [('#E89A6B', 'cánh hoa'), ('#7FA37A', 'lá'), ('#F4D58D', 'nhụy')]
    for i, (c, n) in enumerate(picks):
        y = 30 + i * 36
        b += path(f'M166 {73} C 200 {73} 206 {y + 12} 236 {y + 12}', extra='fill="none" stroke="#9AA5AB" stroke-width="1.4" stroke-dasharray="4 3"')
        b += f'<circle cx="252" cy="{y + 12}" r="13" fill="{c}" stroke="#fff" stroke-width="2.5"/>'
        b += txt(272, y + 16, n, 't-lbl t-sm')
    b += txt(262, 144, '2. Rút 3 màu', 't-lbl t-mid t-sm t-bold')
    sw = [('gingham-terra', 'caro đất nung'), ('jersey-olive', 'thun xanh lá'), ('dots-mustard', 'chấm bi vàng')]
    for i, (pid, n) in enumerate(sw):
        x = 340 + i * 78
        b += rect(x + 2, 32, 66, 80, fill='#23313A', rx=5, extra='opacity=".12"') + rect(x, 28, 66, 80, fill=fab(pid), rx=5)
        b += rect(x, 28, 66, 80, rx=5, extra='fill="none" stroke="#23313A" stroke-opacity=".25"')
        b += txt(x + 33, 124, n, 't-lbl t-mid t-sm')
    b += txt(456, 144, '3. Tìm vải trơn / họa tiết nhỏ cùng màu', 't-lbl t-mid t-sm t-bold')
    b += rect(582, 46, 44, 44, fill='#2B4C74', rx=5) + rect(582, 46, 44, 44, fill=fab('ov-dots'), rx=5)
    b += txt(604, 124, 'navy', 't-lbl t-mid t-sm')
    b += txt(604, 144, '4. + 1 màu nhấn', 't-lbl t-mid t-sm t-bold')
    b += path('M318 73 H332', cls='s-flow') + path('M562 68 H576', cls='s-flow')
    return svg(W, H, b)


# ================================================================ PHẦN 3 — KỸ THUẬT CƠ BẢN

def template_trace(ctx):
    W, H = 300, 170
    b = piece(10, 20, 170, 130, 'gingham-blue')
    b += rect(38, 36, 104, 104, fill='#23313A', extra='opacity=".15" transform="translate(3 4)"')
    b += rect(38, 36, 104, 104, fill='#D8B98F', rx=2, extra='stroke="#8A6A45" stroke-width="1.2"')
    b += txt(90, 84, 'Rập bìa', 't-lbl t-mid t-bold t-nost') + txt(90, 98, dims(*ctx.d['m2']['cut']), 't-dim t-mid')
    b += rect(36, 34, 108, 108, cls='s-mark')
    b += '<g transform="translate(148 30) rotate(35)"><rect x="0" y="-5" width="46" height="10" rx="3" fill="#7C4DFF"/><path d="M46 -5 L55 0 L46 5 Z" fill="#E3D9FF"/></g>'
    b += txt(158, 20, 'vẽ quanh rập', 't-lbl t-sm t-mark t-bold')
    b += path('M188 90 H214', cls='s-flow')
    b += piece(222, 52, 70, 70, 'gingham-blue')
    b += scissors(222, 48, s=1, rot=0)
    b += txt(257, 140, 'cắt đúng nét phấn', 't-lbl t-mid t-sm t-bold')
    return svg(W, H, b)


def diag_check(ctx):
    a, c = ctx.d['m2']['cut']
    dg = ctx.d['m2']['diag']
    W, H = 300, 160
    b = piece(16, 18, 116, 116, 'linen-white')
    b += line(16, 18, 132, 134, extra='stroke="#2B6CB0" stroke-width="1.4" stroke-dasharray="5 3"')
    b += line(132, 18, 16, 134, extra='stroke="#2B6CB0" stroke-width="1.4" stroke-dasharray="5 3"')
    b += txt(74, 64, f'{art_vn(dg)}', 't-dim t-mid') + txt(74, 100, f'{art_vn(dg)}', 't-dim t-mid')
    b += txt(74, 152, 'Hai đường chéo bằng nhau: vuông', 't-lbl t-mid t-sm t-bold t-sage')
    sk = [(176, 26), (292, 18), (284, 134), (168, 126)]
    b += poly([(x + 2.5, y + 3) for x, y in sk], fill='#23313A', extra='opacity=".12"') + poly(sk, fill=fab('linen-white')) + poly(sk, cls='s-edge')
    b += line(176, 26, 284, 134, extra='stroke="#C4592F" stroke-width="1.4" stroke-dasharray="5 3"')
    b += line(292, 18, 168, 126, extra='stroke="#C4592F" stroke-width="1.4" stroke-dasharray="5 3"')
    b += txt(230, 152, 'Lệch nhau: cắt lại cho vuông', 't-lbl t-mid t-sm t-bold t-terra')
    return svg(W, H, b)


def seam_guide(ctx):
    W, H = 300, 172
    b = rect(0, 0, 300, 172, fill='#DDE2E5', rx=10)
    b += rect(0, 0, 300, 172, rx=10, extra='fill="none" stroke="#8A9499"')
    b += rect(120, 12, 150, 150, fill='#C7CED2', rx=6, extra='stroke="#8A9499"')
    for k, lab in enumerate(['0,5', '1', '1,5']):
        x = 150 + (k + 1) * 19.2
        b += line(x, 18, x, 150, extra='stroke="#6F7F88" stroke-width="1.2"')
        b += txt(x, 168, lab, 't-lbl t-mid t-sm t-bold')
    b += rect(188.4, 14, 16, 146, fill='#F2D78E', extra='opacity=".9"')
    # vải chạy từ trước ra sau (dọc), mép phải chạm băng keo
    b += rect(14, 8, 174.4, 160, fill=fab('floral-cream'))
    b += rect(14, 8, 174.4, 160, cls='s-edge')
    b += line(150, 12, 150, 164, cls='s-seam')
    b += rect(122, 56, 56, 58, fill='#EEF1F3', rx=8, extra='stroke="#6F7F88" stroke-width="1.2" opacity=".95"')
    b += '<circle cx="150" cy="85" r="3.2" fill="#23313A"/>'
    b += txt(150, 50, 'kim', 't-lbl t-mid t-sm t-bold')
    b += dim_h(150, 188.4, 134, '1 cm', dy=-4)
    b += txt(246, 86, 'băng keo', 't-lbl t-mid t-sm t-bold') + txt(246, 99, 'cách kim 1 cm', 't-lbl t-mid t-sm')
    b += path('M60 150 V120', cls='s-flow') + txt(66, 158, 'vải chạy vào máy', 't-lbl t-sm t-bold')
    b += txt(60, 40, 'mép vải', 't-lbl t-mid t-sm t-bold') + txt(60, 53, 'chạm băng keo →', 't-lbl t-mid t-sm')
    return svg(W, H, b)


def pivot_corner(ctx):
    W, H = 300, 170
    b = piece(14, 44, 170, 116, 'dots-terra', side='wrong')
    b += txt(20, 154, 'mặt trái', 't-lbl t-sm t-bold')
    sx, sy = 184 - 16, 44 + 16
    b += line(18, sy, sx, sy, cls='s-seam') + line(sx, sy, sx, 160, extra='class="s-seam" opacity=".35"')
    b += f'<circle cx="{sx}" cy="{sy}" r="5" fill="none" stroke="#23313A" stroke-width="1.6"/><circle cx="{sx}" cy="{sy}" r="1.8" fill="#23313A"/>'
    b += line(sx, 20, sx, sy - 6, cls='s-ext') + line(184, 20, 184, 44, cls='s-ext')
    b += dim_h(sx, 184, 24, '1 cm')
    b += line(186, sy, 200, sy, cls='s-ext') + dim_v(196, 44, sy, '1 cm', side='right')
    b += hand_arrow_turn(sx - 26, sy + 30, 22, 200, 320, cls='s-move')
    b += txt(sx - 52, sy + 60, 'xoay 90°', 't-lbl t-sm t-bold t-terra t-end')
    lines_ = ['1. Dừng máy,', 'kim cắm xuống', '2. Nâng chân vịt', '3. Xoay vải 90°', '4. Hạ chân vịt,', 'may tiếp']
    b += txt_lines(214, 92, lines_, 't-lbl t-sm', lh=14)
    return svg(W, H, b)


def corner_clip(ctx):
    W, H = 640, 176
    b = ''
    titles = [('Không cắt góc', 'góc cộm, tròn', False), ('Cắt xéo cách đường may 2–3 mm', 'góc vuông, gọn', True), ('Cắt vào sát đường may', 'thủng góc khi lộn', False)]
    for i, (t1, t2, ok) in enumerate(titles):
        x0 = 10 + i * 212
        X, Y, S = x0, 14, 116
        b += piece(X, Y, S, S, 'gingham-blue', side='wrong', shadow=True)
        b += line(X, Y + 22, X + S - 22, Y + 22, cls='s-seam') + line(X + S - 22, Y + 22, X + S - 22, Y + S, cls='s-seam')
        cx, cy = X + S - 22, Y + 22  # góc đường may
        if i == 1:
            tri = [(X + S - 14, Y), (X + S, Y), (X + S, Y + 14)]
            b += poly([(X + S - 22 + 5, Y), (X + S, Y), (X + S, Y + 22 - 5)], cls='f-discard')
            b += line(X + S - 22 + 5, Y, X + S, Y + 22 - 5, extra='stroke="#C4592F" stroke-width="1.8"')
            b += scissors(X + S + 10, Y + 2, s=.9, rot=135)
        if i == 2:
            b += poly([(cx - 2, Y), (X + S, Y), (X + S, cy + 2), (cx + 1, cy - 1)], cls='f-discard')
            b += path(f'M{cx - 2} {Y} L{cx + 1} {cy - 1} L{X + S} {cy + 2}', extra='stroke="#C4592F" stroke-width="1.8" fill="none"')
            b += f'<circle cx="{cx}" cy="{cy}" r="7" fill="none" stroke="#C4592F" stroke-width="1.6"/>'
        # kết quả sau khi lộn
        rx, ry = x0 + 138, 50
        if i == 0:
            b += path(f'M{rx} {ry + 60} V{ry + 10} Q{rx} {ry} {rx + 10} {ry} H{rx + 60}', extra='fill="none" stroke="#3E74B8" stroke-width="10" stroke-linecap="butt"')
            b += f'<circle cx="{rx + 6}" cy="{ry + 6}" r="9" fill="#3E74B8"/>'
        else:
            b += path(f'M{rx} {ry + 60} V{ry} H{rx + 60}', extra='fill="none" stroke="#3E74B8" stroke-width="8" stroke-linejoin="miter"')
            if i == 2:
                b += f'<circle cx="{rx}" cy="{ry}" r="5" fill="#FFFCF6" stroke="#C4592F" stroke-width="1.4"/>'
        b += txt(rx + 30, ry + 80, 'sau khi lộn', 't-lbl t-mid t-sm t-muted')
        b += txt(x0 + 100, 158, t1, f't-lbl t-mid t-bold t-sm {"t-sage" if ok else "t-terra"}')
        b += txt(x0 + 100, 171, t2, 't-lbl t-mid t-sm')
    return svg(W, H, b)


def grading(ctx):
    W, H = 300, 112
    u = 70
    S = 176  # vị trí đường may
    b = txt(4, 12, 'Mặt cắt trước khi lộn', 't-lbl t-sm t-bold')
    b += txt(4, 47, 'vải mỏng', 't-lbl t-sm t-bold') + txt(4, 71, 'khăn bông', 't-lbl t-sm t-bold')
    b += line(64, 44, S + u, 44, extra='stroke="#6FA2D6" stroke-width="7"')
    b += line(64, 58, S + u * .5, 58, extra='stroke="#E6D9BF" stroke-width="12"')
    b += line(S + u * .5, 58, S + u, 58, extra='stroke="#E6D9BF" stroke-width="12" stroke-dasharray="3 3" opacity=".45"')
    b += line(S, 36, S, 68, extra='stroke="#D6336C" stroke-width="3"')
    b += txt(S - 6, 30, 'đường may', 't-lbl t-sm t-seam t-bold t-end')
    b += dim_h(S, S + u, 30, '1 cm')
    b += line(S + u * .5, 66, S + u * .5, 84, cls='s-ext') + line(S, 70, S, 84, cls='s-ext')
    b += dim_h(S, S + u * .5, 80, '0,5 cm', above=False, dy=14)
    b += txt(S + u * .5 + 4, 104, 'phần tỉa bỏ', 't-lbl t-sm t-muted')
    return svg(W, H, b)


def push_corner(ctx):
    W, H = 300, 118
    b = ''
    X, Y = 30, 16
    b += piece(X, Y, 150, 84, 'gingham-blue')
    b += line(X + 60, Y + 84, X + 144, Y + 6, extra='stroke="#C9A77C" stroke-width="7" stroke-linecap="round" stroke-dasharray="10 5" opacity=".9"')
    b += '<circle cx="176" cy="20" r="10" fill="none" stroke="#C4592F" stroke-width="1.6" stroke-dasharray="3 2"/>'
    b += pin(206, 10, rot=160) + txt(200, 42, 'ghim khều nhẹ', 't-lbl t-sm t-bold') + txt(200, 55, 'góc từ bên ngoài', 't-lbl t-sm')
    b += txt(200, 76, 'que đầu tù đẩy', 't-lbl t-sm t-bold') + txt(200, 89, 'từ bên trong', 't-lbl t-sm')
    b += txt(150, 114, 'Không dùng kéo nhọn — dễ đâm thủng góc', 't-lbl t-mid t-sm t-terra t-bold')
    return svg(W, H, b)


def press_edge(ctx):
    W, H = 300, 120
    b = ''
    for k, ok in enumerate((True, False)):
        x0 = 10 + k * 150
        y = 40
        if ok:
            b += path(f'M{x0} {y} H{x0 + 100} Q{x0 + 112} {y} {x0 + 112} {y + 10} Q{x0 + 112} {y + 20} {x0 + 100} {y + 20} H{x0}', extra='fill="none" stroke="#6FA2D6" stroke-width="6"')
            b += path(f'M{x0 + 112} {y + 10} v0', extra='')
            b += line(x0 + 112, y + 4, x0 + 112, y + 16, extra='stroke="#D6336C" stroke-width="3"')
            b += path(f'M{x0} {y + 20} H{x0 + 100}', extra='stroke="#E6D9BF" stroke-width="6"')
        else:
            b += path(f'M{x0} {y} H{x0 + 112}', extra='stroke="#6FA2D6" stroke-width="6"')
            b += path(f'M{x0} {y + 20} H{x0 + 100} Q{x0 + 116} {y + 20} {x0 + 116} {y + 10} Q{x0 + 116} {y + 2} {x0 + 108} {y}', extra='fill="none" stroke="#E6D9BF" stroke-width="6"')
            b += line(x0 + 106, y - 5, x0 + 110, y + 5, extra='stroke="#D6336C" stroke-width="3"')
        b += txt(x0 + 56, 90, 'Đường may nằm đúng mép' if ok else 'Lớp dưới lộ lên mặt trên', f't-lbl t-mid t-sm t-bold {"t-sage" if ok else "t-terra"}')
    b += txt(150, 112, 'Lăn đường may giữa 2 ngón tay cho ra đúng mép rồi mới ủi', 't-lbl t-mid t-sm')
    return svg(W, H, b)


def quilt_patterns(ctx):
    W, H = 640, 128
    b = ''
    opts = [('Chéo chữ X', [(0, 0, 1, 1), (1, 0, 0, 1)], 'gingham-blue'), ('Lưới ô 10 cm', [(1/3, 0, 1/3, 1), (2/3, 0, 2/3, 1), (0, 1/3, 1, 1/3), (0, 2/3, 1, 2/3)], 'linen'),
            ('Sọc song song', [(k / 6, 0, k / 6, 1) for k in range(1, 6)], 'terry-sage'), ('Lọt khe đường ghép', 'patch', None)]
    for i, (nm, segs, pid) in enumerate(opts):
        x0 = 20 + i * 158
        if segs == 'patch':
            pf = patch_front(['floral-cream', 'gingham-terra', 'dots-terra', 'linen', 'flannel-terra', 'gingham-terra', 'dots-terra', 'linen', 'floral-cream'], 3)
            b += cloth_flip(x0 + 8, 6, 96, 96, pf, 'terry-peach', stitch='#0E8C8C', quilt=([(1/3, 0, 1/3, 1), (2/3, 0, 2/3, 1), (0, 1/3, 1, 1/3), (0, 2/3, 1, 2/3)], '#0E8C8C'), c=0.1, shadow=True)
        else:
            b += cloth_flip(x0 + 8, 6, 96, 96, pid, 'terry-white', stitch='#0E8C8C', quilt=(segs, '#0E8C8C'), c=0.1)
        b += txt(x0 + 56, 122, nm, 't-lbl t-mid t-bold')
    return svg(W, H, b)


def double_hem_xsec(ctx):
    g1, g2 = ctx.d['m3']['g1'], ctx.d['m3']['g2']
    u = 44  # px / cm
    W, H = 640, 150
    b = ''
    steps = ['1. Mép thô', f'2. Gấp {art_vn(g1)} cm, ủi', f'3. Gấp tiếp {art_vn(g2)} cm, ủi', '4. May sát mép gấp trong']
    for i, t in enumerate(steps):
        x0 = 14 + i * 158
        y = 70
        E = x0 + 128  # mép ngoài sau cùng
        col = '#6FA2D6'
        if i == 0:
            b += line(x0, y, E, y, extra=f'stroke="{col}" stroke-width="6"')
            b += dim_h(E - (g1 + g2) * u, E, y - 14, f'{art_vn(g1 + g2)} cm dành cho gấu', dy=-2)
            b += line(E - (g1 + g2) * u, y - 10, E - (g1 + g2) * u, y - 3, cls='s-ext') + line(E, y - 10, E, y - 3, cls='s-ext')
        elif i == 1:
            e1 = E - g2 * u  # sau gấp 1: mép gấp nằm ở vị trí này
            b += path(f'M{x0} {y} H{e1} Q{e1 + 5} {y} {e1 + 5} {y - 5} Q{e1 + 5} {y - 10} {e1} {y - 10} H{e1 - g1 * u + 4}', extra=f'fill="none" stroke="{col}" stroke-width="5"')
            b += dim_h(e1 - g1 * u + 4, e1 + 5, y - 22, f'{art_vn(g1)} cm')
        elif i == 2:
            b += path(f'M{x0} {y} H{E} Q{E + 6} {y} {E + 6} {y - 6} Q{E + 6} {y - 12} {E} {y - 12} H{E - g2 * u + 6} Q{E - g2 * u} {y - 12} {E - g2 * u} {y - 17} Q{E - g2 * u} {y - 22} {E - g2 * u + 6} {y - 22} H{E - 4}', extra=f'fill="none" stroke="{col}" stroke-width="4.5"')
            b += dim_h(E - g2 * u, E + 6, y + 18, f'{art_vn(g2)} cm', above=False, dy=14)
        else:
            b += path(f'M{x0} {y} H{E} Q{E + 6} {y} {E + 6} {y - 6} Q{E + 6} {y - 12} {E} {y - 12} H{E - g2 * u + 6} Q{E - g2 * u} {y - 12} {E - g2 * u} {y - 17} Q{E - g2 * u} {y - 22} {E - g2 * u + 6} {y - 22} H{E - 4}', extra=f'fill="none" stroke="{col}" stroke-width="4.5"')
            xs = E - g2 * u + 0.2 * u + 2
            b += line(xs, y - 30, xs, y + 8, extra='stroke="#0E8C8C" stroke-width="2.6" stroke-dasharray="5 3"')
            b += dim_h(xs, E + 6, y + 22, f'{art_vn(ctx.d["m3"]["stitch_from_edge"])} cm', above=False, dy=14)
        b += txt(x0 + 64, 136, t, 't-lbl t-mid t-bold t-sm')
    b += txt(320, 12, 'Mặt cắt ngang mép khăn (mặt trái ở trên)', 't-lbl t-mid t-sm t-muted')
    return svg(W, H, b)


def _edge_tile(kind):
    W, H = 138, 98
    b = ''
    X, Y, w, h = 10, 6, 118, 62
    E = X + w  # mép phải
    if kind == 'overlock':
        b += rect(X, Y, w, h, fill=fab('linen'))
        b += line(E - 12, Y, E - 12, Y + h, extra='stroke="#2B4C74" stroke-width="1.2"') + line(E - 7, Y, E - 7, Y + h, extra='stroke="#2B4C74" stroke-width="1.2"')
        for k in range(0, int(h), 5):
            b += path(f'M{E - 12} {Y + k} C{E + 4} {Y + k} {E + 4} {Y + k + 5} {E - 7} {Y + k + 5}', extra='fill="none" stroke="#D96F43" stroke-width="1"')
        t1, t2 = 'Vắt sổ máy 3–4 chỉ', 'Tốt nhất, nhanh nhất'
    elif kind == 'zig_edge':
        b += rect(X, Y, w, h, fill=fab('linen'))
        b += zig(E - 5, Y, E - 5, Y + h, amp=5, step=3.6)
        t1, t2 = 'Zigzag sát mép', 'Mũi phải rơi ra ngoài mép'
    elif kind == 'zig_trim':
        b += rect(X, Y, w - 8, h, fill=fab('linen'))
        b += rect(E - 8, Y, 8, h, cls='f-discard')
        b += zig(E - 14, Y, E - 14, Y + h, amp=4, step=3.6)
        b += line(E - 8, Y - 4, E - 8, Y + h + 4, extra='stroke="#C4592F" stroke-width="1.4" stroke-dasharray="4 3"')
        t1, t2 = 'Zigzag cách mép, tỉa', 'Tỉa sát mũi, không cắt chỉ'
    elif kind == 'pinking':
        pts = [(X, Y)]
        for k in range(0, int(h) + 1, 6):
            pts += [(E - (4 if (k // 6) % 2 else 0), Y + k)]
        pts += [(E, Y + h), (X, Y + h)]
        b += poly(pts, fill=fab('floral-cream'))
        b += poly(pts[1:-1], close=False, extra='fill="none" stroke="#A8482A" stroke-width="1.6" stroke-linejoin="miter"')
        t1, t2 = 'Kéo răng cưa', 'Chỉ giảm tưa, vải ít tưa'
    elif kind == 'double':
        b += rect(X, Y, w, h, fill=fab('gingham-blue'))
        b += rect(E - 18, Y, 18, h, fill='#23313A', extra='opacity=".12"')
        b += line(E - 18, Y, E - 18, Y + h, extra='stroke="#23313A" stroke-opacity=".35"')
        b += line(E - 15, Y, E - 15, Y + h, cls='s-top')
        t1, t2 = 'Gấp mép đôi', 'Mép thô cuộn kín bên trong'
    elif kind == 'bag':
        b += rect(X, Y, w, h, fill=fab('gingham-blue'))
        b += line(E - 7, Y, E - 7, Y + h, cls='s-top')
        b += rect(E - 2, Y, 2, h, fill='#E6D9BF')
        t1, t2 = 'May lộn + diễu', 'Mép thô nằm giữa 2 lớp'
    elif kind == 'bind':
        b += rect(X, Y, w, h, fill=fab('terry-sky'))
        b += rect(E - 16, Y, 16, h, fill=fab('jersey-terra'))
        b += line(E - 16, Y, E - 16, Y + h, extra='stroke="#23313A" stroke-opacity=".3"')
        b += line(E - 13, Y, E - 13, Y + h, cls='s-top')
        t1, t2 = 'Bo viền', 'Dải vải bọc kín mép'
    else:  # raw
        b += rect(X, Y, w, h, fill=fab('jersey-teal'))
        b += rect(E - 3, Y, 3, h, fill='#23313A', extra='opacity=".2"')
        t1, t2 = 'Để mép cắt', 'Thun, nỉ: không tưa'
    if kind != 'pinking':
        b += rect(X, Y, w, h, extra='fill="none" stroke="#23313A" stroke-opacity=".2"')
    b += txt(W / 2, 84, t1, 't-lbl t-mid t-bold t-sm') + txt(W / 2, 96, t2, 't-lbl t-mid t-sm')
    return svg(W, H, b)


def edge_finishes(ctx):
    kinds = ['overlock', 'zig_edge', 'zig_trim', 'pinking', 'bag', 'double', 'bind', 'raw']
    return '<div class="edges">' + ''.join(f'<div class="edge">{_edge_tile(k)}</div>' for k in kinds) + '</div>'


def overlock_flow(ctx):
    W, H = 640, 214
    b = ''

    def node(x, y, w, h, lines_, kind):
        fill = {'q': '#FFFFFF', 'no': '#EDF4EA', 'yes': '#FCEEE6', 'opt': '#FCF5E1'}[kind]
        st = {'q': '#2B4C74', 'no': '#46693F', 'yes': '#C4592F', 'opt': '#9C7212'}[kind]
        s = rect(x + 2, y + 3, w, h, fill='#23313A', rx=10, extra='opacity=".1"') + rect(x, y, w, h, fill=fill, rx=10, extra=f'stroke="{st}" stroke-width="1.6"')
        n = len(lines_)
        for i, (t, bold) in enumerate(lines_):
            s += txt(x + w / 2, y + h / 2 + (i - (n - 1) / 2) * 13 + 4, t, f't-lbl t-mid t-nost {"t-bold" if bold else "t-sm"}')
        return s
    b += node(200, 8, 240, 48, [('Mép vải có được giấu kín?', True), ('may lộn · gấp mép đôi · bo viền', False)], 'q')
    b += node(8, 92, 200, 66, [('KHÔNG cần vắt sổ', True), ('Mẫu 2, 3, 4, 5, 6', False), ('(đường diễu / may mép giữ chặt)', False)], 'no')
    b += node(262, 92, 160, 48, [('Vải có tưa sợi?', True), ('phép thử số 3', False)], 'q')
    b += node(238, 156, 190, 56, [('Không cần', True), ('thun, nỉ · Mẫu 1', False), ('zigzag nếu muốn mép đẹp', False)], 'opt')
    b += node(452, 146, 180, 66, [('CẦN vắt sổ', True), ('hoặc zigzag khóa mép', False), ('khăn bông: 2 lượt zigzag', False)], 'yes')
    b += path('M260 56 C 200 70 150 76 120 90', cls='s-flow') + txt(170, 76, 'Có', 't-lbl t-bold t-sage')
    b += path('M360 56 V88', cls='s-flow') + txt(368, 80, 'Không', 't-lbl t-bold t-terra')
    b += path('M333 140 V151', cls='s-flow') + txt(326, 151, 'Không', 't-lbl t-bold t-end')
    b += path('M422 124 C 480 124 526 128 536 142', cls='s-flow') + txt(478, 118, 'Có', 't-lbl t-bold t-terra')
    return svg(W, H, b)


def backtack(ctx):
    W, H = 300, 106
    b = piece(10, 20, 280, 60, 'linen-white')
    y = 50
    b += path(f'M40 {y - 4} H70', extra='stroke="#D6336C" stroke-width="2" marker-end="url(#arr-terra)" fill="none"')
    b += path(f'M70 {y} H42', extra='stroke="#D6336C" stroke-width="2" marker-end="url(#arr-terra)" fill="none"')
    b += path(f'M42 {y + 4} H250', extra='stroke="#D6336C" stroke-width="2" stroke-dasharray="6 3" fill="none"')
    b += path(f'M222 {y + 8} H250', extra='stroke="#D6336C" stroke-width="2" fill="none"') + path(f'M250 {y + 12} H222', extra='stroke="#D6336C" stroke-width="2" marker-end="url(#arr-terra)" fill="none"')
    b += txt(56, 36, 'tới 3 mũi', 't-lbl t-sm t-mid t-bold') + txt(56, 72, 'lùi 3 mũi', 't-lbl t-sm t-mid t-bold')
    b += txt(236, 78, 'cuối: lùi 3 mũi', 't-lbl t-sm t-mid t-bold')
    b += txt(150, 100, 'Lại mũi ở đầu và cuối mọi đường may', 't-lbl t-mid t-sm t-bold')
    return svg(W, H, b)


def pin_clip(ctx):
    W, H = 300, 106
    b = piece(10, 22, 280, 60, 'terry-sage') + piece(10, 18, 280, 60, 'gingham-blue', shadow=False)
    for x in (40, 110, 180, 250):
        b += clip(x, 78, rot=0, c='#E3B23C')
    b += pin(70, 8, rot=90) + pin(150, 8, rot=90, head='#3E74B8')
    b += txt(150, 100, 'Kẹp mỗi 8–10 cm; ghim vuông góc mép, đầu ghim ra ngoài', 't-lbl t-mid t-sm t-bold')
    return svg(W, H, b)


def f_bag(ctx):
    d = ctx.d['m2']
    W, H = 170, 150
    s_ = 3.4
    cw = d['cut'][0] * s_
    X, Y = 26, 18
    b = piece(X, Y, cw, cw, 'gingham-blue')
    b += rect(X + s_, Y + s_, cw - 2 * s_, cw - 2 * s_, cls='s-seam')
    b += dim_h(X, X + cw, Y - 6, f'cắt {art_vn(d["cut"][0])}')
    b += dim_h(X + s_, X + cw - s_, Y + cw / 2, f'TP {art_vn(d["fin"][0])}', dy=-4)
    b += txt(X + cw + 6, Y + 12, '1', 't-dim') + txt(X + cw + 6, Y + 24, 'cm', 't-dim')
    return svg(W, H, b)


def f_hem(ctx):
    d = ctx.d['m3']
    W, H = 170, 150
    X, Y, w, h = 20, 18, 110, 120
    b = piece(X, Y, w, h, 'linen-white')
    g = 8
    b += rect(X + g, Y + g, w - 2 * g, h - 2 * g, cls='s-fold')
    b += rect(X + 2 * g, Y + 2 * g, w - 4 * g, h - 4 * g, cls='s-fold')
    b += dim_h(X, X + w, Y - 6, f'cắt {art_vn(d["cut"][0])}')
    b += dim_h(X + 2 * g, X + w - 2 * g, Y + h / 2, f'TP {art_vn(d["fin"][0])}', dy=-4)
    b += txt(X + w + 6, Y + 14, f'{art_vn(d["g1"])}+{art_vn(d["g2"])}', 't-dim')
    return svg(W, H, b)


def f_patch(ctx):
    d = ctx.d['m4']
    W, H = 170, 150
    n = d['n']
    sq = 34
    X, Y = 16, 22
    b = ''
    pids = ['floral-cream', 'gingham-terra', 'dots-terra']
    for k in range(n):
        x = X + k * (sq - 7)
        b += piece(x, Y, sq, sq, pids[k % 3], shadow=False) + rect(x, Y, sq, sq, cls='s-edge')
    b += dim_h(X, X + sq, Y - 6, f'{art_vn(d["sq_cut"])}')
    tot = sq + (n - 1) * (sq - 7)
    b += dim_h(X, X + tot, Y + sq + 16, f'{n} × {art_vn(d["sq_cut"])} − {n - 1} × 2 = {art_vn(d["row_len"])}', above=False, dy=14)
    b += txt(X, Y + sq + 56, 'mỗi đường ghép “ăn” 2 cm', 't-lbl')
    for k in range(1, n):
        x = X + k * (sq - 7)
        b += line(x + 3.5, Y - 2, x + 3.5, Y + sq + 2, cls='s-seam')
    return svg(W, H, b)


def f_bind(ctx):
    d = ctx.d['m5']
    W, H = 170, 150
    u = 13
    b = ''
    y0 = 40
    # khăn dày t, dải bọc
    b += rect(10, y0, 100, d['t'] * u * 2, fill=fab('terry-sky'))
    x = 110
    bw = d['b'] * u
    b += path(f'M{x - bw} {y0 - 3} H{x + 3} Q{x + 9} {y0 - 3} {x + 9} {y0 + 4} V{y0 + d["t"] * u * 2 - 4} Q{x + 9} {y0 + d["t"] * u * 2 + 3} {x + 3} {y0 + d["t"] * u * 2 + 3} H{x - bw}', extra='fill="none" stroke="#D96F43" stroke-width="5"')
    b += dim_h(x - bw, x + 9, y0 - 12, 'b')
    b += dim_v(x + 22, y0, y0 + d['t'] * u * 2, 't', side='right')
    b += txt(10, 100, f'b = bề rộng viền nhìn thấy', 't-lbl')
    b += txt(10, 114, f't = độ dày khăn', 't-lbl')
    b += rect(10, 124, 150, 16, fill=fab('jersey-terra'), rx=2)
    b += txt(85, 136, f'dải {art_vn(d["binding_w"])} cm', 't-lbl t-mid t-bold t-white')
    return svg(W, H, b)


def f_mop(ctx):
    d = ctx.d['m6']
    W, H = 170, 150
    s_ = 3.2
    X, Y = 12, 36
    L = d['cut_main'][0] * s_
    Wd = d['cut_main'][1] * s_
    b = piece(X, Y, L, Wd, 'terry-mint')
    Pp = d['P'] * s_
    for x0 in (X + s_, X + L - s_ - Pp):
        b += rect(x0, Y + s_, Pp, Wd - 2 * s_, fill=fab('denim'))
        b += line(x0 + (Pp if x0 < X + 20 else 0), Y + s_, x0 + (Pp if x0 < X + 20 else 0), Y + Wd - s_, extra='stroke="#fff" stroke-width="1.4" stroke-dasharray="3 2"')
    b += dim_h(X, X + L, Y - 6, f'{art_vn(d["cut_main"][0])}')
    b += dim_h(X + s_, X + s_ + Pp, Y + Wd + 14, f'P {art_vn(d["P"])}', above=False, dy=12)
    b += txt(X, Y + Wd + 44, 'túi: vải gấp đôi', 't-lbl')
    return svg(W, H, b)


def f_loop(ctx):
    d = ctx.d['m3']
    W, H = 170, 150
    b = ''
    s_ = 7
    L = d['loop'][1] * s_ * .9
    b += rect(12, 16, L, d['loop'][0] * s_, fill=fab('jersey-terra'), rx=2)
    for k in (1, 2, 3):
        b += line(12, 16 + k * d['loop'][0] * s_ / 4, 12 + L, 16 + k * d['loop'][0] * s_ / 4, cls='s-fold')
    b += dim_h(12, 12 + L, 12, f'{art_vn(d["loop"][1])}')
    b += dim_v(12 + L + 8, 16, 16 + d['loop'][0] * s_, f'{art_vn(d["loop"][0])}', side='right')
    # quai thành phẩm
    b += path('M50 142 V100 Q50 76 72 76 Q94 76 94 100 V142', extra='fill="none" stroke="#D96F43" stroke-width="8.8"')
    b += rect(30, 124, 84, 18, fill=fab('linen-white'), extra='stroke="#23313A" stroke-opacity=".3"')
    b += dim_v(112, 76, 124, f'{art_vn(d["loop_visible"])}', side='right')
    b += txt(20, 70, f'rộng {art_vn(d["loop_quarter"])}', 't-lbl t-bold')
    return svg(W, H, b)


def f_gap(ctx):
    d = ctx.d['m2']
    W, H = 170, 150
    X, Y, S = 26, 22, 110
    b = piece(X, Y, S, S, 'floral-cream', side='wrong')
    g1, g2 = S / 2 - d['opening'] * 1.9, S / 2 + d['opening'] * 1.9
    b += gap_band(X + g1, Y + S - 6, X + g2, Y + S - 6)
    b += seam_rect(X + 6, Y + 6, S - 12, S - 12, gap=('b', g1 - 6, g2 - 6))
    b += dim_h(X + g1, X + g2, Y + S + 16, f'{art_vn(d["opening"])}–{art_vn(d["opening_thick"])} cm', above=False, dy=12)
    return svg(W, H, b)


# ================================================================ MẪU 2 — KHĂN LAU BÀN (và các bước may lộn dùng chung)

def bag_step(ctx, k, A='gingham-blue', B='terry-white', cut=None, opening=None, W=300, H=212, s_=None, quilt='X', label_A='A', label_B='B', qlabel=None):
    d = ctx.d
    cut = cut or d['m2']['cut']
    opening = opening or d['m2']['opening']
    sa = d['sa']
    s_ = s_ or (118 if k == 'cut' else 156) / max(cut)
    w, h = cut[0] * s_, cut[1] * s_
    X, Y = (W - w) / 2, 22
    u = s_  # 1 cm
    b = ''

    def piece(x, y, w_, h_, pid, side='right', **kw):  # noqa: F811 — hỗ trợ mặt ghép (hàm vẽ)
        from art import piece as _piece
        if callable(pid):
            if side == 'wrong':
                out = _piece(x, y, w_, h_, 'linen-white', side='wrong', **kw)
                n = getattr(pid, 'n', 3)
                for kk in range(1, n):
                    out += line(x + w_ * kk / n, y, x + w_ * kk / n, y + h_, extra='stroke="#23313A" stroke-opacity=".25" stroke-dasharray="2 2"')
                    out += line(x, y + h_ * kk / n, x + w_, y + h_ * kk / n, extra='stroke="#23313A" stroke-opacity=".25" stroke-dasharray="2 2"')
                return out
            return rect(x + 2.5, y + 3, w_, h_, fill='#23313A', extra='opacity=".12"') + pid(x, y, w_, h_) + rect(x, y, w_, h_, cls='s-edge')
        return _piece(x, y, w_, h_, pid, side=side, **kw)
    if k == 'cut':
        X1, X2 = W / 2 - w - 2, W / 2 + 26
        b += piece(X1, Y, w, h, A) + piece(X2, Y, w, h, B)
        b += grain(X1 + w - 10, Y + 12, Y + h - 12) + grain(X2 + w - 10, Y + 12, Y + h - 12)
        b += dim_h(X1, X1 + w, Y - 6, art_vn(cut[0])) + dim_v(X1 - 6, Y, Y + h, art_vn(cut[1]))
        b += txt(X1 + w / 2, Y + h + 16, f'Lớp {label_A} (mặt phải)', 't-lbl t-mid t-sm t-bold') + txt(X2 + w / 2, Y + h + 16, f'Lớp {label_B} (mặt phải)', 't-lbl t-mid t-sm t-bold')
    elif k == 'stack':
        b += piece(X + 6, Y + 6, w, h, B)
        b += piece(X - 2, Y - 2, w, h, A, side='wrong')
        b += clips_around(X - 2, Y - 2, w, h)
        b += txt(X - 2 + w / 2, Y + h / 2 + 2, f'{label_A}: mặt trái', 't-lbl t-mid t-bold')
        b += txt(X + w + 16, Y + h - 4, f'{label_B} bên dưới:', 't-lbl t-sm') + txt(X + w + 16, Y + h + 9, 'mặt phải lên', 't-lbl t-sm')
        b += txt(W / 2, Y + h + 22, '2 mặt phải úp vào nhau', 't-lbl t-mid t-sm t-bold t-terra')
    elif k == 'sew':
        b += piece(X, Y, w, h, A, side='wrong')
        g1 = w / 2 - opening / 2 * u
        g2 = w / 2 + opening / 2 * u
        b += gap_band(X + g1, Y + h - u, X + g2, Y + h - u, t=8)
        b += seam_rect(X + u, Y + u, w - 2 * u, h - 2 * u, gap=('b', g1 - u, g2 - u))
        for cx, cy in ((X + u, Y + u), (X + w - u, Y + u), (X + u, Y + h - u), (X + w - u, Y + h - u)):
            b += f'<circle cx="{f(cx)}" cy="{f(cy)}" r="3" fill="#23313A"/>'
        b += dim_h(X + g1, X + g2, Y + h + 22, f'khe {art_vn(opening)} cm', above=False, dy=12)
        b += dim_v(X + w + 8, Y, Y + u, '1 cm', side='right')
        b += path(f'M{f(X + g2)} {f(Y + h - u)} h22', cls='s-move')
        b += txt(X + g2 + 4, Y + h + 12, 'bắt đầu', 't-lbl t-sm t-terra t-bold')
        b += txt(X + g1 - 4, Y + h + 12, 'kết thúc', 't-lbl t-sm t-terra t-bold t-end')
    elif k == 'clip':
        b += piece(X, Y, w, h, A, side='wrong')
        g1 = w / 2 - opening / 2 * u
        g2 = w / 2 + opening / 2 * u
        b += seam_rect(X + u, Y + u, w - 2 * u, h - 2 * u, gap=('b', g1 - u, g2 - u))
        b += corner_clips(X, Y, w, h, u)
        b += scissors(X + w + 14, Y - 2, s=1, rot=135)
        b += txt(X + w / 2, Y + h + 16, 'cắt xéo, cách điểm xoay góc 2–3 mm', 't-lbl t-mid t-sm t-bold')
    elif k == 'turn':
        # nửa đã lộn: hình chữ nhật với khe mở, mặt phải trồi ra
        b += piece(X, Y, w, h, A, side='wrong')
        g1 = w / 2 - opening / 2 * u
        g2 = w / 2 + opening / 2 * u
        b += f'<path d="M{f(X + g1 - 4)} {f(Y + h)} C{f(X + g1 - 40)} {f(Y + h + 34)} {f(X + g2 + 40)} {f(Y + h + 34)} {f(X + g2 + 4)} {f(Y + h)} Z" fill="{fab(A)}" stroke="#23313A" stroke-opacity=".35"/>'
        b += path(f'M{f(X + w / 2)} {f(Y + h * .3)} C{f(X + w / 2 + 30)} {f(Y + h * .6)} {f(X + w / 2 + 10)} {f(Y + h + 6)} {f(X + w / 2)} {f(Y + h + 24)}', cls='s-move')
        b += txt(X - 8, Y + h - 16, 'mặt phải', 't-lbl t-sm t-bold t-end') + txt(X - 8, Y + h - 3, 'trồi ra', 't-lbl t-sm t-end')
        b += stick(X + w - 3, Y + 3, X + w + 26, Y + h - 30)
        b += txt(X + w + 10, Y + h - 14, 'đẩy góc', 't-lbl t-sm t-bold')
    elif k == 'press':
        b += piece(X, Y, w, h, A)
        g1 = w / 2 - opening / 2 * u
        g2 = w / 2 + opening / 2 * u
        b += line(X + g1, Y + h - 1, X + g2, Y + h - 1, extra='stroke="#FFE16A" stroke-width="3"')
        b += clip(X + w / 2, Y + h, rot=0)
        b += iron(X + w + 40, Y + 40, s_=.9)
        b += txt(X + w / 2, Y + h + 22, 'mép khe gấp vào 1 cm, ủi, kẹp', 't-lbl t-mid t-sm t-bold')
    elif k == 'top':
        b += piece(X, Y, w, h, A)
        b += topstitch_rect(X, Y, w, h, d['ts'] * u)
        b += dim_v(X + w + 8, Y, Y + d['ts'] * u, f'{art_vn(d["ts"])} cm', side='right')
        b += path(f'M{f(X + w / 2 - 20)} {f(Y + d["ts"] * u + 10)} h30', cls='s-move')
        b += txt(X + w / 2, Y + h + 16, 'diễu quanh — đóng luôn khe lộn', 't-lbl t-mid t-sm t-bold')
    elif k == 'quilt':
        b += piece(X, Y, w, h, A)
        b += topstitch_rect(X, Y, w, h, d['ts'] * u)
        if quilt == 'X':
            b += line(X + 6, Y + 6, X + w - 6, Y + h - 6, cls='s-top') + line(X + w - 6, Y + 6, X + 6, Y + h - 6, cls='s-top')
        else:
            for t in (1 / 3, 2 / 3):
                b += line(X + w * t, Y + 4, X + w * t, Y + h - 4, cls='s-top') + line(X + 4, Y + h * t, X + w - 4, Y + h * t, cls='s-top')
        b += txt(W / 2, Y + h + 16, qlabel or ('chần chữ X (hoặc lưới 10 cm)' if quilt == 'X' else 'chần lưới — may từ giữa ra'), 't-lbl t-mid t-sm t-bold')
    return svg(W, H, b)


def m2_cut(ctx):
    d = ctx.d['m2']
    W, H = 330, 200
    s_ = 4.6
    w = d['cut'][0] * s_
    X, Y = 36, 26
    b = piece(X, Y, w, w, 'gingham-blue')
    b += rect(X + s_, Y + s_, w - 2 * s_, w - 2 * s_, cls='s-seam')
    g1 = w / 2 - d['opening'] / 2 * s_
    b += gap_band(X + g1, Y + w - s_, X + g1 + d['opening'] * s_, Y + w - s_, t=8)
    b += dim_h(X, X + w, Y - 8, f'{art_vn(d["cut"][0])} cm')
    b += dim_v(X - 8, Y, Y + w, f'{art_vn(d["cut"][1])}')
    b += dim_h(X + s_, X + w - s_, Y + w / 2 - 12, f'thành phẩm {art_vn(d["fin"][0])}', dy=-4)
    b += line(X, Y, X + w, Y + w, extra='stroke="#2B6CB0" stroke-width="1" stroke-dasharray="4 3" opacity=".8"')
    b += grain(X + w - 20, Y + 20, Y + w - 30)
    b += txt(X + w + 14, Y + 20, '× 2 miếng', 't-lbl t-bold t-lg')
    b += txt(X + w + 14, Y + 38, '1 lớp A', 't-lbl t-sm') + txt(X + w + 14, Y + 51, '1 lớp B', 't-lbl t-sm')
    b += txt(X + w + 14, Y + 80, 'đường may', 't-lbl t-sm t-seam t-bold') + txt(X + w + 14, Y + 93, f'cách mép {art_vn(ctx.d["sa"])} cm', 't-lbl t-sm')
    b += txt(X + w + 14, Y + 122, 'khe lộn', 't-lbl t-sm t-bold') + txt(X + w + 14, Y + 135, f'{art_vn(d["opening"])} cm', 't-lbl t-sm')
    b += txt(X + w + 14, Y + 160, 'đường chéo', 't-lbl t-sm t-bold') + txt(X + w + 14, Y + 173, f'{art_vn(d["diag"])} cm', 't-dim')
    return svg(W, H, b)


def m2_hero(ctx):
    W, H = 300, 200
    b = cloth_flip(40, 18, 170, 170, 'gingham-blue', 'terry-white', stitch='#FFFFFF', quilt=[(0, 0, 1, 1), (1, 0, 0, 1)], c=64)
    b += folded(200, 120, 90, 60, 'gingham-red', rot=8)
    return svg(W, H, b)


def m2_s1(ctx): return bag_step(ctx, 'cut')
def m2_s2(ctx): return bag_step(ctx, 'stack')
def m2_s3(ctx): return bag_step(ctx, 'sew')
def m2_s4(ctx): return bag_step(ctx, 'clip')
def m2_s5(ctx): return bag_step(ctx, 'turn')
def m2_s6(ctx): return bag_step(ctx, 'press')
def m2_s7(ctx): return bag_step(ctx, 'top')
def m2_s8(ctx): return bag_step(ctx, 'quilt')


# ================================================================ MẪU 1 — GIẺ ÁO THUN

def m1_s1(ctx):
    W, H = 300, 184
    m = CM(150 - 25 * 2.45, 8, 2.45)
    b = tshirt_front(m, cuts=False)
    b += cutline(m.d([('M', (-8, 23)), ('L', (58, 23))]))
    b += scissors(m.P(60, 23)[0] + 6, m.P(60, 23)[1], s=1.0, rot=180)
    b += txt(150, 180, 'Cắt ngang ngay dưới nách, bỏ phần trên', 't-lbl t-mid t-sm t-bold')
    return svg(W, H, b)


def m1_s2(ctx):
    W, H = 300, 184
    s_ = 2.6
    b = ''
    for i, x0 in enumerate((20, 160)):
        b += piece(x0, 34, 48 * s_ * .95, 45 * s_ * .95, 'jersey-teal')
        b += line(x0 + 2, 34 + 45 * s_ * .95 - 5, x0 + 48 * s_ * .95 - 2, 34 + 45 * s_ * .95 - 5, extra='stroke="#fff" stroke-opacity=".8" stroke-width="1.1" stroke-dasharray="3 2"')
        b += txt(x0 + 48 * s_ * .95 / 2, 24, 'Thân trước' if i == 0 else 'Thân sau', 't-lbl t-mid t-bold')
    b += dim_h(20, 20 + 48 * s_ * .95, 164, '48 cm', above=False, dy=14)
    b += txt(150, 196, '', 't-lbl')
    b += txt(20 + 24 * s_ * .95, 34 + 45 * s_ * .95 + 14, 'mép gấu áo', 't-lbl t-mid t-sm t-bold')
    return svg(W, H, b)


def m1_s3(ctx):
    d = ctx.d['m1']
    W, H = 300, 184
    s_ = 3.0
    X, Y = 44, 14
    b = piece(X, Y, 48 * s_, 45 * s_, 'jersey-teal')
    c = d['cut'][0] * s_
    b += line(X + c, Y, X + c, Y + 45 * s_, cls='s-mark')
    b += line(X, Y + 45 * s_ - c, X + 48 * s_, Y + 45 * s_ - c, cls='s-mark')
    b += rect(X, Y, 48 * s_, 45 * s_ - c, fill='#fff', extra='opacity=".45"')
    b += txt(X + 24 * s_, Y + (45 * s_ - c) / 2 + 4, 'phần dư: dải bo viền', 't-lbl t-mid t-sm t-bold')
    b += dim_h(X, X + c, Y + 45 * s_ + 12, art_vn(d['cut'][0]), above=False, dy=12)
    b += dim_h(X + c, X + 2 * c, Y + 45 * s_ + 12, art_vn(d['cut'][0]), above=False, dy=12)
    b += dim_v(X + 48 * s_ + 8, Y + 45 * s_ - c, Y + 45 * s_, art_vn(d['cut'][1]), side='right')
    b += txt(X + c, Y + 45 * s_ - 8, 'gấu áo = cạnh chuẩn', 't-lbl t-mid t-sm t-bold')
    return svg(W, H, b)


def m1_s4(ctx):
    W, H = 300, 184
    b = jersey_rag(40, 40, 100, 100, 'jersey-teal', rot=-6) + jersey_rag(160, 44, 100, 100, 'jersey-teal', rot=5)
    b += txt(150, 30, 'Kéo nhẹ 2 mép cắt → mép tự cuộn gọn', 't-lbl t-mid t-sm t-bold')
    return svg(W, H, b)


def m1_hero(ctx):
    W, H = 300, 116
    b = jersey_rag(24, 22, 76, 76, 'jersey-pink', rot=-10) + jersey_rag(80, 16, 76, 76, 'jersey-sky', rot=3) + jersey_rag(138, 24, 76, 76, 'jersey-heather', rot=12)
    b += rolled(256, 70, 28, 'jersey-mustard')
    return svg(W, H, b)


# ================================================================ MẪU 3 — KHĂN BẾP TREO

def m3_hero(ctx):
    W, H = 300, 210
    b = f'<path d="M40 22 H270" stroke="#8A6A55" stroke-width="8" stroke-linecap="round"/>'
    b += hanging_towel(64, 52, 104, 144, 'linen-white', stripe='#2B4C74', loop='#D96F43', hook=False)
    b += hanging_towel(188, 52, 88, 120, 'gingham-navy', stripe='#C8643B', loop='#E3B23C', hook=False)
    for cx in (116, 232):
        b += f'<path d="M{cx} 25 v12 q0 8 -7 8" stroke="#7D8A91" stroke-width="3" fill="none" stroke-linecap="round"/>'
    return svg(W, H, b)


def m3_cut(ctx):
    d = ctx.d['m3']
    W, H = 330, 262
    s_ = 4.3
    X, Y = 34, 22
    w, h = d['cut'][0] * s_, d['cut'][1] * s_
    b = piece(X, Y, w, h, 'linen-white')
    for k in (d['g1'], d['g1'] + d['g2']):
        b += rect(X + k * s_, Y + k * s_, w - 2 * k * s_, h - 2 * k * s_, extra='fill="none" stroke="#4B5A63" stroke-width="1.3" stroke-dasharray="9 3 2 3"')
    b += dim_h(X, X + w, Y - 8, f'{art_vn(d["cut"][0])} cm')
    b += dim_v(X - 8, Y, Y + h, art_vn(d['cut'][1]))
    c = (d['g1'] + d['g2']) * s_
    b += dim_h(X + c, X + w - c, Y + h * .28, f'TP {art_vn(d["fin"][0])}')
    b += line(X + w * .62, Y + c, X + w * .62, Y + h - c, cls='s-dim')
    b += f'<text x="{f(X + w * .62 - 6)}" y="{f(Y + h * .6)}" class="t-dim t-mid" transform="rotate(-90 {f(X + w * .62 - 6)} {f(Y + h * .6)})">TP {art_vn(d["fin"][1])}</text>'
    b += grain(X + w * .3, Y + h * .4, Y + h - 30)
    b += txt(X + w * .3 + 8, Y + h * .4 + 14, 'canh dọc', 't-lbl t-sm')
    lx, ly = X + w + 30, Y + 10
    lw, lh = d['loop'][0] * s_, d['loop'][1] * s_
    b += piece(lx, ly, lw, lh, 'jersey-terra')
    for k in (1, 2, 3):
        b += line(lx + lw * k / 4, ly, lx + lw * k / 4, ly + lh, cls='s-fold')
    b += dim_h(lx, lx + lw, ly - 6, art_vn(d['loop'][0])) + dim_v(lx + lw + 6, ly, ly + lh, art_vn(d['loop'][1]), side='right')
    b += txt(lx + lw / 2, ly + lh + 16, 'dải quai', 't-lbl t-mid t-sm t-bold')
    b += line(lx - 6, ly + lh + 44, lx + 40, ly + lh + 44, extra='stroke="#4B5A63" stroke-width="1.3" stroke-dasharray="9 3 2 3"')
    b += txt(lx - 6, ly + lh + 36, 'nếp gấp', 't-lbl t-sm')
    b += txt(lx - 6, ly + lh + 60, 'cách mép', 't-lbl t-sm') + txt(lx - 6, ly + lh + 74, '1 cm và 2 cm', 't-dim')
    return svg(W, H, b)


def m3_loop(ctx):
    d = ctx.d['m3']
    W, H = 300, 150
    u = 11  # px / cm theo bề ngang dải
    b = ''
    lw = d['loop'][0] * u
    col = '#D96F43'
    steps = [('Gấp đôi,|ủi, mở ra', 0), ('Gấp 2 mép|vào giữa', 1), ('Gấp đôi|lại', 2), ('Diễu|mép mở', 3)]
    for i, (t, k) in enumerate(steps):
        x0 = 8 + i * 74
        y0 = 30
        if k == 0:
            b += line(x0, y0 + 20, x0 + lw, y0 + 20, extra=f'stroke="{col}" stroke-width="4"')
            b += line(x0 + lw / 2, y0 + 12, x0 + lw / 2, y0 + 28, cls='s-fold')
        elif k == 1:
            b += path(f'M{x0 + lw / 2 - 2} {y0 + 14} H{x0 + 4} Q{x0} {y0 + 14} {x0} {y0 + 18} Q{x0} {y0 + 22} {x0 + 4} {y0 + 22} H{x0 + lw - 4} Q{x0 + lw} {y0 + 22} {x0 + lw} {y0 + 18} Q{x0 + lw} {y0 + 14} {x0 + lw - 4} {y0 + 14} H{x0 + lw / 2 + 2}', extra=f'fill="none" stroke="{col}" stroke-width="3.2"')
        else:
            q = lw / 4
            b += path(f'M{x0 + 6} {y0 + 8} H{x0 + q + 2} Q{x0 + q + 6} {y0 + 8} {x0 + q + 6} {y0 + 12} V{y0 + 28} Q{x0 + q + 6} {y0 + 32} {x0 + q + 2} {y0 + 32} H{x0 + 6}', extra=f'fill="none" stroke="{col}" stroke-width="3"')
            b += path(f'M{x0 + 6} {y0 + 14} H{x0 + q} M{x0 + 6} {y0 + 26} H{x0 + q}', extra=f'fill="none" stroke="{col}" stroke-width="3"')
            if k == 3:
                b += line(x0 + 9, y0 + 2, x0 + 9, y0 + 38, extra='stroke="#0E8C8C" stroke-width="2.4" stroke-dasharray="4 2.4"')
            b += dim_h(x0 + 6, x0 + q + 8, y0 + 50, art_vn(d['loop_quarter']), above=False, dy=12)
        b += badge(x0 + 8, 12, i + 1, r=8)
        t1, t2 = t.split('|')
        b += txt(x0 + 30, 104, t1, 't-lbl t-mid t-sm t-bold') + txt(x0 + 30, 117, t2, 't-lbl t-mid t-sm')
    b += txt(150, 142, f'mặt cắt ngang dải {art_vn(d["loop"][0])} cm → quai 4 lớp rộng {art_vn(d["loop_quarter"])} cm', 't-lbl t-mid t-sm')
    return svg(W, H, b)


def m3_press(ctx):
    d = ctx.d['m3']
    W, H = 300, 150
    s_ = 7
    X, Y = 20, 16
    b = piece(X, Y, 180, 120, 'linen-white', side='wrong')
    # dải gấp 2 lớp ở cạnh phải và cạnh dưới
    c = (d['g1'] + d['g2']) * s_
    b += rect(X + 180 - c, Y, c, 120, fill=fab('linen-white')) + rect(X, Y + 120 - c, 180, c, fill=fab('linen-white'))
    b += line(X + 180 - c, Y, X + 180 - c, Y + 120 - c, extra='stroke="#23313A" stroke-opacity=".35"') + line(X, Y + 120 - c, X + 180 - c, Y + 120 - c, extra='stroke="#23313A" stroke-opacity=".35"')
    b += line(X + 180 - c / 2, Y, X + 180 - c / 2, Y + 120, cls='s-fold') + line(X, Y + 120 - c / 2, X + 180, Y + 120 - c / 2, cls='s-fold')
    b += iron(X + 210, Y + 60, s_=.8)
    b += dim_h(X + 180 - c, X + 180, Y - 6, f'{art_vn(d["g1"])} + {art_vn(d["g2"])}')
    b += txt(X + 70, Y + 60, 'mặt trái', 't-lbl t-mid t-sm t-muted')
    return svg(W, H, b)


def m3_miter(ctx):
    d = ctx.d['m3']
    g1, g2 = d['g1'], d['g2']
    c = g1 + g2
    tr = d['miter_trim']
    u = 21
    R = 7.2  # cm hiển thị
    W, H = 640, 222
    b = ''
    import math as m_

    def P(x0, y0, x, y):  # cm (góc thô tại 0,0; vải ở x<=0,y<=0) -> px
        return (x0 + (x + R) * u, y0 + (y + R) * u)

    def pg(x0, y0, pts, **kw):
        return poly([P(x0, y0, *p) for p in pts], **kw)
    titles = ['Ủi gấp 1 + gấp 2, mở nếp 2', 'Gấp chéo góc qua điểm P', f'Mở ra, cắt góc chừa {art_vn(tr)} cm', 'Gấp lại theo nếp → góc 45°']
    for i, t in enumerate(titles):
        x0, y0 = 4 + i * 160, 18
        L = -R + .2
        if i in (0, 2):
            b += pg(x0, y0, [(L, L), (-g1, L), (-g1, -g1), (L, -g1)], fill=fab('gingham-sky'))
            b += pg(x0, y0, [(L, L), (-g1, L), (-g1, -g1), (L, -g1)], fill='#fff', extra='opacity=".55"')
            b += pg(x0, y0, [(-2 * g1, L), (-g1, L), (-g1, -g1), (-2 * g1, -g1)], fill=fab('gingham-sky'))
            b += pg(x0, y0, [(L, -2 * g1), (-g1, -2 * g1), (-g1, -g1), (L, -g1)], fill=fab('gingham-sky'))
            b += pg(x0, y0, [(-2 * g1, L), (-2 * g1, -2 * g1), (L, -2 * g1)], cls='s-edge', close=False)
            b += line(*P(x0, y0, -c, L), *P(x0, y0, -c, -g1), extra='stroke="#1C3553" stroke-width="1.7" stroke-dasharray="9 3 2 3" fill="none"') + line(*P(x0, y0, L, -c), *P(x0, y0, -g1, -c), extra='stroke="#1C3553" stroke-width="1.7" stroke-dasharray="9 3 2 3" fill="none"')
            if i == 2:
                k = -2 * c
                b += line(*P(x0, y0, k + g1, -g1), *P(x0, y0, -g1, k + g1), extra='stroke="#1C3553" stroke-width="1.7" stroke-dasharray="9 3 2 3" fill="none"')
                kc = k + tr * m_.sqrt(2)
                a1, a2 = P(x0, y0, kc + g1, -g1), P(x0, y0, -g1, kc + g1)
                b += poly([a1, P(x0, y0, -g1, -g1), a2], cls='f-discard')
                b += line(*a1, *a2, extra='stroke="#C4592F" stroke-width="1.8"')
                b += scissors(a2[0] + 14, a2[1] - 4, s=.8, rot=135)
        elif i == 1:
            F1, F2 = (-(g1 + 2 * g2), -g1), (-g1, -(g1 + 2 * g2))
            Rr = (-(g1 + 2 * g2), -(g1 + 2 * g2))
            body = [(L, L), (-g1, L), F2, F1, (L, -g1)]
            b += pg(x0, y0, body, fill=fab('gingham-sky')) + pg(x0, y0, body, fill='#fff', extra='opacity=".55"')
            b += pg(x0, y0, [(-2 * g1, L), (-g1, L), F2, (-2 * g1, -2 * g1 - (0))], fill=fab('gingham-sky'))
            b += pg(x0, y0, [(L, -2 * g1), (L, -g1), F1, (-2 * g1, -2 * g1)], fill=fab('gingham-sky'))
            b += line(*P(x0, y0, -c, L), *P(x0, y0, -c, -c), extra='stroke="#1C3553" stroke-width="1.7" stroke-dasharray="9 3 2 3" fill="none"') + line(*P(x0, y0, L, -c), *P(x0, y0, -c, -c), extra='stroke="#1C3553" stroke-width="1.7" stroke-dasharray="9 3 2 3" fill="none"')
            b += pg(x0, y0, [F1, F2, Rr], fill='#23313A', extra='opacity=".15" transform="translate(2 3)"')
            b += pg(x0, y0, [F1, F2, Rr], fill=fab('gingham-sky'))
            b += pg(x0, y0, [F1, F2, Rr], extra='fill="none" stroke="#23313A" stroke-opacity=".4"')
            b += line(*P(x0, y0, *F1), *P(x0, y0, *F2), extra='stroke="#C4592F" stroke-width="1.8"')
        else:
            M = (-(c + g2), -(c + g2))
            b += pg(x0, y0, [(L, L), (-c, L), (-c, -c), (L, -c)], fill=fab('gingham-sky')) + pg(x0, y0, [(L, L), (-c, L), (-c, -c), (L, -c)], fill='#fff', extra='opacity=".55"')
            b += pg(x0, y0, [(-c - g2, L), (-c, L), (-c, -c), M], fill=fab('gingham-sky'))
            b += pg(x0, y0, [(L, -c - g2), M, (-c, -c), (L, -c)], fill=fab('gingham-sky'))
            b += pg(x0, y0, [(-c - g2, L), M, (L, -c - g2)], cls='s-edge', close=False)
            b += line(*P(x0, y0, *M), *P(x0, y0, -c, -c), extra='stroke="#23313A" stroke-width="1.6"')
            st = -c - g2 + .2
            b += pg(x0, y0, [(st, L), (st, st), (L, st)], cls='s-top', close=False)
            b += txt(*P(x0, y0, -c - g2 - .2, -c + .9), '45°', 't-lbl t-sm t-bold t-end')
        # điểm P
        px, py = P(x0, y0, -c, -c)
        b += f'<circle cx="{f(px)}" cy="{f(py)}" r="4.2" fill="#C4592F" stroke="#fff" stroke-width="1.4"/>'
        b += txt(px + 7, py - 6, 'P', 't-lbl t-bold t-terra')
        b += badge(x0 + 10, y0 - 6, i + 1, r=8)
        b += txt(x0 + 78, 190, t, 't-lbl t-mid t-sm t-bold')
    b += txt(320, 215, 'P = giao điểm 2 nếp gấp lần 2 = góc khăn khi may xong (nhìn từ mặt trái)', 't-lbl t-mid t-sm')
    return svg(W, H, b)


def m3_loop_attach(ctx):
    d = ctx.d['m3']
    W, H = 300, 190
    s_ = 7
    X, Y = 10, 40
    b = piece(X, Y, 280, 130, 'linen-white', side='wrong')
    hem = d['g2'] * s_
    b += rect(X, Y, 280, hem * 2, fill=fab('linen-white'))
    b += line(X, Y + hem * 2, X + 280, Y + hem * 2, extra='stroke="#23313A" stroke-opacity=".35"')
    lw = d['loop_quarter'] * s_
    cx = X + 140
    # quai chữ U, 2 đầu luồn dưới gấu, vòng quay xuống
    for sx in (-1, 1):
        b += rect(cx + sx * 12 - lw / 2, Y + 2, lw, 28, fill='#D96F43')
    b += path(f'M{cx - 12} {Y + 30} V{Y + 70} Q{cx - 12} {Y + 92} {cx} {Y + 92} Q{cx + 12} {Y + 92} {cx + 12} {Y + 70} V{Y + 30}', extra=f'fill="none" stroke="#D96F43" stroke-width="{lw}"')
    b += rect(X, Y, 280, hem * 2, fill='#fff', extra='opacity=".35"')
    b += line(X, Y + hem * 2 - .2 * s_, X + 280, Y + hem * 2 - .2 * s_, cls='s-top')
    b += txt(cx + 26, Y + 70, 'quai quay xuống', 't-lbl t-sm t-bold') + txt(cx + 26, Y + 83, 'khi may gấu', 't-lbl t-sm')
    b += dim_v(cx - 30, Y, Y + hem * 2, '1 cm', side='left')
    b += txt(150, 22, 'Mép trên khăn (mặt trái) · 2 đầu quai giấu dưới gấu', 't-lbl t-mid t-sm t-bold')
    return svg(W, H, b)


def m3_loop_up(ctx):
    W, H = 300, 190
    X, Y = 10, 92
    b = piece(X, Y, 280, 90, 'linen-white')
    cx = X + 140
    b += path(f'M{cx - 12} {Y + 12} V{Y - 22} Q{cx - 12} {Y - 46} {cx} {Y - 46} Q{cx + 12} {Y - 46} {cx + 12} {Y - 22} V{Y + 12}', extra='fill="none" stroke="#D96F43" stroke-width="8.8"')
    b += line(cx - 26, Y + 3, cx + 26, Y + 3, extra='stroke="#0E8C8C" stroke-width="2.4" stroke-dasharray="4 2.4"')
    b += line(X, Y + 12, X + 280, Y + 12, cls='s-top')
    b += hand_arrow_turn(cx + 44, Y + 10, 26, 90, -60, cls='s-move')
    b += txt(cx + 74, Y - 30, 'lật quai lên', 't-lbl t-sm t-bold t-terra')
    b += txt(cx - 40, Y - 26, 'may chặn cách', 't-lbl t-sm t-bold t-top t-end') + txt(cx - 40, Y - 13, 'mép 0,3 cm', 't-lbl t-sm t-end')
    b += line(cx - 38, Y - 12, cx - 24, Y + 1, extra='stroke="#0E8C8C" stroke-width="1"')
    b += txt(150, 20, 'Mặt phải khăn', 't-lbl t-mid t-sm t-bold')
    return svg(W, H, b)


def m3_sew(ctx):
    d = ctx.d['m3']
    W, H = 300, 194
    s_ = 3.3
    w, h = d['fin'][0] * s_, d['fin'][1] * s_
    X, Y = 96, 12
    b = piece(X, Y, w, h, 'linen-white', side='wrong')
    hem = d['g2'] * s_ * 1.6
    b += path(f'M{X} {Y} H{X + w} V{Y + h} H{X} Z M{X + hem} {Y + hem} V{Y + h - hem} H{X + w - hem} V{Y + hem} Z', fill=fab('linen-white'), extra='fill-rule="evenodd"')
    b += rect(X + hem, Y + hem, w - 2 * hem, h - 2 * hem, extra='fill="none" stroke="#23313A" stroke-opacity=".35"')
    b += rect(X + hem - 1.6, Y + hem - 1.6, w - 2 * hem + 3.2, h - 2 * hem + 3.2, cls='s-top')
    b += line(X + w, Y + h * .25, X + w + 16, Y + h * .25, cls='s-ext') + line(X + w - hem, Y + h * .25, X + w + 16, Y + h * .25, cls='s-ext')
    b += txt(X + w + 10, Y + h * .25 - 6, f'{art_vn(d["stitch_from_edge"])} cm', 't-dim')
    b += path(f'M{X + hem / 2} {Y + h / 2 + 22} v-30', cls='s-move')
    b += txt(X - 8, Y + h / 2 + 4, 'bắt đầu', 't-lbl t-sm t-bold t-terra t-end') + txt(X - 8, Y + h / 2 + 17, 'giữa cạnh dài', 't-lbl t-sm t-end')
    b += rect(X + w / 2 - 8, Y - 2, 16, hem + 4, fill='#D96F43', rx=2)
    b += txt(X + w + 8, Y + h - 4, 'mặt trái', 't-lbl t-sm t-muted')
    return svg(W, H, b)



def m3_stripe(ctx):
    W, H = 300, 170
    b = f'<path d="M20 16 H280" stroke="#8A6A55" stroke-width="6" stroke-linecap="round"/>'
    b += hanging_towel(40, 40, 70, 112, 'linen-white', stripe='#FFFFFF', loop='#2B4C74', hook=False)
    b += rect(38, 118, 74, 7, fill=fab('gingham-terra'))
    b += hanging_towel(132, 40, 70, 112, 'linen', stripe='#FFFFFF', loop='#D96F43', hook=False)
    b += rect(130, 112, 74, 6, fill='#2B4C74') + rect(130, 122, 74, 3, fill='#2B4C74')
    b += hanging_towel(224, 40, 62, 112, 'gingham-sky', stripe='#FFFFFF', loop='#E3B23C', hook=False)
    b += rect(222, 124, 66, 8, fill=fab('floral-cream'))
    return svg(W, H, b)



# ================================================================ MẪU 4 — KHĂN GHÉP MẢNH

M4_PIDS = ['floral-cream', 'gingham-terra', 'dots-terra', 'gingham-terra', 'flannel-terra', 'gingham-terra', 'dots-terra', 'gingham-terra', 'floral-cream']


def _m4_front():
    fn = patch_front(M4_PIDS, 3)
    fn.n = 3
    return fn


def m4_hero(ctx):
    W, H = 300, 200
    b = cloth_flip(46, 16, 170, 170, _m4_front(), 'terry-peach', stitch='#FFFFFF', quilt=([(1/3, 0, 1/3, 1), (2/3, 0, 2/3, 1), (0, 1/3, 1, 1/3), (0, 2/3, 1, 2/3)], '#FFFFFF'), c=60)
    b += stack_side(206, 150, 84, [('dots-terra', 0), ('gingham-terra', 4), ('floral-cream', -2)], t=14)
    return svg(W, H, b)


def m4_cut(ctx):
    d = ctx.d['m4']
    W, H = 330, 190
    s_ = 3.6
    q = d['sq_cut'] * s_
    b = ''
    X, Y = 16, 26
    for k, pid in enumerate(M4_PIDS):
        r, c = divmod(k, 3)
        b += piece(X + c * (q + 6), Y + r * (q + 6), q, q, pid)
    b += dim_h(X, X + q, Y - 7, art_vn(d['sq_cut']))
    b += dim_v(X + 3 * (q + 6) + 2, Y, Y + q, art_vn(d['sq_cut']), side='right')
    b += txt(X + 1.5 * (q + 6), Y + 3 * (q + 6) + 12, f'{d["count"]} ô × {dims(*d["square"])}', 't-lbl t-mid t-bold')
    bx = X + 3 * (q + 6) + 34
    bw = d['back'][0] * s_ * .62
    b += piece(bx, Y, bw, bw, 'terry-peach')
    b += dim_h(bx, bx + bw, Y - 7, art_vn(d['back'][0]))
    b += txt(bx + bw / 2, Y + bw + 16, f'Lớp sau {dims(*d["back"])}', 't-lbl t-mid t-bold')
    b += txt(bx + bw / 2, Y + bw + 30, '(vẽ thu nhỏ)', 't-lbl t-mid t-sm t-muted')
    return svg(W, H, b)


def m4_layouts(ctx):
    W, H = 330, 130
    A, B, C = '#C8643B', '#F3E1CF', '#2B4C74'
    lays = [('Bàn cờ', [A, B, A, B, A, B, A, B, A], '5 + 4'), ('Chữ thập', [B, A, B, A, A, A, B, A, B], '5 + 4'),
            ('60 – 30 – 10', [A, B, A, B, C, B, A, A, A], '5 + 3 + 1')]
    b = ''
    for i, (nm, cols, cnt) in enumerate(lays):
        x0 = 14 + i * 108
        q = 26
        b += rect(x0 + 3, 12, 3 * q, 3 * q, fill='#23313A', extra='opacity=".12"')
        for k, col in enumerate(cols):
            r, c = divmod(k, 3)
            b += rect(x0 + c * q, 8 + r * q, q, q, fill=col, extra='stroke="#fff" stroke-width="1.2"')
        b += txt(x0 + 39, 104, nm, 't-lbl t-mid t-bold') + txt(x0 + 39, 118, cnt + ' ô', 't-lbl t-mid t-sm')
    return svg(W, H, b)


def m4_rows(ctx):
    d = ctx.d['m4']
    W, H = 300, 228
    b = ''
    s1 = 6.0
    q = d['sq_cut'] * s1
    sa = ctx.d['sa'] * s1
    X, Y = 8, 52
    b += piece(X, Y, q, q, M4_PIDS[1]) + piece(X + 5, Y + 5, q, q, M4_PIDS[0], side='wrong')
    b += line(X + 5 + q - sa, Y + 5, X + 5 + q - sa, Y + 5 + q, cls='s-seam')
    b += dim_h(X + 5 + q - sa, X + 5 + q, Y + q + 18, '1 cm', above=False, dy=12)
    b += txt(X + q / 2 + 4, Y - 18, '1. úp 2 mặt phải,', 't-lbl t-mid t-sm t-bold') + txt(X + q / 2 + 4, Y - 6, 'may cách mép 1 cm', 't-lbl t-mid t-sm')
    s2 = 4.9
    q2 = d['sq_cut'] * s2
    sa2 = ctx.d['sa'] * s2
    X2, Y2 = 106, 82
    step = q2 - 2 * sa2
    for k in range(3):
        b += rect(X2 + k * step, Y2, q2 if k == 2 else step, q2, fill=fab(M4_PIDS[k]))
    b += rect(X2 + 2.5, Y2 + 3, 2 * step + q2, q2, fill='#23313A', extra='opacity=".1"')
    for k in range(3):
        b += rect(X2 + k * step, Y2, q2 if k == 2 else step, q2, fill=fab(M4_PIDS[k]))
    for k in (1, 2):
        b += line(X2 + k * step, Y2, X2 + k * step, Y2 + q2, extra='stroke="#23313A" stroke-opacity=".45" stroke-width="1.2"')
    tot = 2 * step + q2
    b += rect(X2, Y2, tot, q2, cls='s-edge')
    b += dim_h(X2, X2 + tot, Y2 + q2 + 18, f'{art_vn(d["row_len"])} cm', above=False, dy=12)
    b += txt(X2 + tot / 2, Y2 - 24, '2. thêm ô thứ 3', 't-lbl t-mid t-sm t-bold') + txt(X2 + tot / 2, Y2 - 12, '→ 1 hàng 3 ô', 't-lbl t-mid t-sm')
    return svg(W, H, b)


def m4_press(ctx):
    W, H = 300, 228
    s_ = 3.8
    q = 12 * s_
    sa = s_
    step = q - 2 * sa
    b = ''
    X, Y = 14, 12
    dirs = [-1, 1, -1]
    for r in range(3):
        yy = Y + r * (q + 8)
        for c in range(3):
            b += rect(X + c * step, yy, q if c == 2 else step, q, fill=fab(M4_PIDS[r * 3 + c]))
        b += rect(X, yy, 2 * step + q, q, fill='#fff', extra='opacity=".45"')
        for c in (1, 2):
            xx = X + c * step
            # phần chừa ủi lệch về 1 phía (dải tối 2 cm)
            fx = xx - 2 * sa if dirs[r] < 0 else xx
            b += rect(fx, yy, 2 * sa, q, fill='#23313A', extra='opacity=".16"')
            b += line(xx, yy, xx, yy + q, extra='stroke="#D6336C" stroke-width="1.4" stroke-dasharray="4 2.4"')
        mid = X + (2 * step + q) / 2
        b += path(f'M{mid - 16 * dirs[r]} {yy + q / 2} H{mid + 16 * dirs[r]}', cls='s-move')
        b += txt(X + 2 * step + q + 10, yy + q / 2 + 4, f'hàng {r + 1}: ủi về {"trái" if dirs[r] < 0 else "phải"}', 't-lbl t-sm t-bold')
    b += txt(150, 222, 'mặt trái · dải tối = phần chừa đã ủi lệch', 't-lbl t-mid t-sm')
    return svg(W, H, b)


def m4_join(ctx):
    d = ctx.d['m4']
    W, H = 300, 228
    s_ = 5.4
    q = d['sq_cut'] * s_
    sa = ctx.d['sa'] * s_
    step = q - 2 * sa
    tot = 2 * step + q
    X, Y = (W - tot) / 2, 40
    b = ''
    for r, op in ((1, 1), (0, .8)):
        yy = Y + r * 30
        for c in range(3):
            b += rect(X + c * step, yy, q if c == 2 else step, q, fill=fab(M4_PIDS[r * 3 + c]))
        if r == 0:
            b += rect(X, yy, tot, q, fill='#fff', extra='opacity=".45"')
        b += rect(X, yy, tot, q, cls='s-edge')
        for c in (1, 2):
            b += line(X + c * step, yy, X + c * step, yy + q, extra='stroke="#23313A" stroke-opacity=".45" stroke-width="1.2"')
    b += line(X, Y + q - sa, X + tot, Y + q - sa, cls='s-seam')
    for c in (1, 2):
        b += pin(X + c * step, Y + q - sa, rot=-90)
    b += txt(W / 2, Y - 12, 'hàng 1 (mặt trái) úp lên hàng 2', 't-lbl t-mid t-sm t-bold')
    b += txt(W / 2, Y + q + 42, 'ghim đúng giao điểm, may 1 cm', 't-lbl t-mid t-sm t-bold')
    return svg(W, H, b)


def m4_check(ctx):
    d = ctx.d['m4']
    W, H = 300, 228
    s_ = 5.6
    t = d['top'][0] * s_
    X, Y = 30, 24
    b = rect(X + 3, Y + 4, t, t, fill='#23313A', extra='opacity=".12"') + _m4_front()(X, Y, t, t) + rect(X, Y, t, t, cls='s-edge')
    b += dim_h(X, X + t, Y - 7, f'{art_vn(d["top"][0])} cm')
    b += dim_v(X + t + 8, Y, Y + t, f'{art_vn(d["top"][1])}', side='right')
    b += txt(X + t / 2, Y + t + 18, f'= đúng bằng lớp sau {dims(*d["back"])}', 't-lbl t-mid t-sm t-bold')
    return svg(W, H, b)


def m4_strips(ctx):
    W, H = 300, 180
    widths = [6, 9, 5, 7, 10, 8]
    pids = ['gingham-terra', 'floral-cream', 'dots-terra', 'linen', 'flannel-terra', 'stripe-terra-h']
    b = ''
    X, Y, s_ = 14, 16, 3.3
    x = X
    for w_, pid in zip(widths, pids):
        b += rect(x, Y, w_ * s_, 40 * s_, fill=fab(pid)) + rect(x, Y, w_ * s_, 40 * s_, cls='s-edge')
        x += (w_ - 2) * s_
    tot = x - X + 2 * s_
    b += rect(X + (tot - 32 * s_) / 2, Y + 4 * s_, 32 * s_, 32 * s_, extra='fill="none" stroke="#7C4DFF" stroke-width="2" stroke-dasharray="6 3"')
    b += txt(X + tot + 12, Y + 60, 'cắt lại', 't-lbl t-sm t-bold t-mark') + txt(X + tot + 12, Y + 73, '32 × 32', 't-dim')
    return svg(W, H, b)


def m4_s5(ctx): return bag_step(ctx, 'stack', A=_m4_front(), B='terry-peach', cut=ctx.d['m4']['back'], label_A='ghép')
def m4_s6(ctx): return bag_step(ctx, 'sew', A=_m4_front(), B='terry-peach', cut=ctx.d['m4']['back'])
def m4_s7(ctx): return bag_step(ctx, 'top', A=_m4_front(), B='terry-peach', cut=ctx.d['m4']['back'])
def m4_s8(ctx): return bag_step(ctx, 'quilt', A=_m4_front(), B='terry-peach', cut=ctx.d['m4']['back'], quilt='grid', qlabel='chần lọt khe theo 4 đường ghép')


# ================================================================ MẪU 5 — KHĂN LAU NHÀ BO VIỀN

def m5_hero(ctx):
    W, H = 300, 200
    b = cloth_flip(40, 10, 140, 186, 'terry-sky', 'denim', binding=('jersey-terra', 11),
                   quilt=([(1/3, 0, 1/3, 1), (2/3, 0, 2/3, 1), (0, .25, 1, .25), (0, .5, 1, .5), (0, .75, 1, .75)], '#2B4C74'), c=56)
    # xô nước
    b += '<path d="M206 120 L276 120 L268 190 L214 190 Z" fill="#9DB7D5" stroke="#2B4C74" stroke-width="1.4"/>'
    b += '<ellipse cx="241" cy="120" rx="35" ry="8" fill="#BCD4EC" stroke="#2B4C74" stroke-width="1.4"/>'
    b += '<path d="M208 118 Q241 70 274 118" fill="none" stroke="#6F7F88" stroke-width="3"/>'
    return svg(W, H, b)


def m5_cut(ctx):
    d = ctx.d['m5']
    W, H = 640, 214
    s_ = 3.6
    b = ''
    X, Y = 30, 24
    w, h = d['fin'][0] * s_, d['fin'][1] * s_
    items = [('A · khăn bông', 'terry-sky', 'mặt thấm'), ('C · thun cotton', 'jersey-heather', 'lớp ruột')]
    for i, (nm, pid, sub) in enumerate(items):
        x = X + i * (w + 26)
        b += piece(x, Y, w, h, pid)
        b += txt(x + w / 2, Y + h / 2 - 2, nm, 't-lbl t-mid t-bold') + txt(x + w / 2, Y + h / 2 + 12, sub, 't-lbl t-mid t-sm')
        b += grain(x + w - 12, Y + 14, Y + h - 14)
    b += dim_h(X, X + w, Y - 8, art_vn(d['fin'][0])) + dim_v(X - 8, Y, Y + h, art_vn(d['fin'][1]))
    # jeans 2 dải
    x = X + 2 * (w + 26)
    jw = d['jeans_strip'][0] * s_
    for k in range(2):
        b += piece(x + k * (jw + 6), Y, jw, h, 'denim')
    b += txt(x + jw + 3, Y + h + 30, f'B · jeans: {d["jeans_n"]} dải', 't-lbl t-mid t-bold')
    b += dim_h(x, x + jw, Y - 8, art_vn(d['jeans_strip'][0]))
    # dải bo
    bx = x + 2 * jw + 34
    bw = d['binding_w'] * s_
    lens = [('dài', d['bind_long'][1]), ('dài', d['bind_long'][1]), ('ngắn', d['bind_short'][1]), ('ngắn', d['bind_short'][1])]
    for k, (nm, L) in enumerate(lens):
        b += piece(bx + k * (bw + 8), Y, bw, L * s_ * .98, 'jersey-terra')
    b += dim_h(bx, bx + bw, Y - 8, art_vn(d['binding_w']))
    for k, (nm, L) in enumerate(lens):
        b += txt(bx + k * (bw + 8) + bw / 2, Y + L * s_ * .98 + 14, art_vn(L), 't-dim t-mid')
    b += txt(bx + 2 * (bw + 8) - 4, Y + h + 30, '4 dải bo viền', 't-lbl t-mid t-bold')
    return svg(W, H, b)


def m5_join(ctx):
    d = ctx.d['m5']
    W, H = 300, 210
    s_ = 4.2
    jw = d['jeans_strip'][0] * s_
    h = 40 * s_ * .9
    X, Y = 40, 24
    sa = ctx.d['sa'] * s_
    b = piece(X, Y, jw, h, 'denim') + piece(X + jw - 2 * sa, Y, jw, h, 'denim')
    b += line(X + jw - sa, Y, X + jw - sa, Y + h, extra='stroke="#fff" stroke-width="1.6" stroke-dasharray="4 2.4"')
    tot = 2 * jw - 2 * sa
    b += dim_h(X, X + tot, Y - 8, f'{art_vn(d["fin"][0])} cm')
    b += dim_h(X, X + jw, Y + h + 16, art_vn(d['jeans_strip'][0]), above=False, dy=12)
    b += txt(X + tot + 12, Y + 40, 'may nối', 't-lbl t-sm t-bold') + txt(X + tot + 12, Y + 53, 'ĐM 1 cm,', 't-lbl t-sm') + txt(X + tot + 12, Y + 66, 'ủi rẽ', 't-lbl t-sm')
    return svg(W, H, b)


def m5_stack(ctx):
    W, H = 300, 210
    b = ''
    w, h = 118, 150
    b += piece(40, 44, w, h, 'denim', side='wrong') + txt(40 + w / 2, 44 + h + 12, '', 't-lbl')
    b += piece(64, 30, w, h, 'jersey-heather')
    b += piece(88, 16, w, h, 'terry-sky')
    b += txt(94, 30, '', 't-lbl')
    b += txt(214, 30, 'A · khăn bông', 't-lbl t-sm t-bold') + txt(214, 43, 'mặt phải lên', 't-lbl t-sm')
    b += txt(190, 188, 'C · thun', 't-lbl t-sm t-bold')
    b += txt(34, 205, 'B · jeans (mặt phải úp xuống)', 't-lbl t-sm t-bold')
    b += path('M242 60 V120', cls='s-flow') + path('M242 120 V60', cls='s-flow')
    b += txt(250, 94, 'dưới', 't-lbl t-sm') + txt(250, 70, 'trên', 't-lbl t-sm')
    return svg(W, H, b)


def m5_zig(ctx):
    d = ctx.d['m5']
    W, H = 300, 210
    s_ = 4.4
    w, h = d['fin'][0] * s_, d['fin'][1] * s_ * .95
    X, Y = 60, 12
    b = piece(X, Y, w, h, 'terry-sky')
    i = 0.5 * s_
    b += zig(X + i, Y + i, X + w - i, Y + i, amp=2.6) + zig(X + w - i, Y + i, X + w - i, Y + h - i, amp=2.6)
    b += zig(X + w - i, Y + h - i, X + i, Y + h - i, amp=2.6) + zig(X + i, Y + h - i, X + i, Y + i, amp=2.6)
    b += clips_around(X, Y, w, h)
    b += txt(X - 10, Y + h / 2, 'zigzag', 't-lbl t-sm t-bold t-end', extra='style="fill:#C2185B"') + txt(X - 10, Y + h / 2 + 13, 'cách mép', 't-lbl t-sm t-end') + txt(X - 10, Y + h / 2 + 26, '0,5 cm', 't-lbl t-sm t-end')
    return svg(W, H, b)


def m5_quilt(ctx):
    d = ctx.d['m5']
    W, H = 300, 210
    s_ = 4.4
    w, h = d['fin'][0] * s_, d['fin'][1] * s_ * .95
    X, Y = 60, 12
    b = piece(X, Y, w, h, 'terry-sky')
    sy = h / d['fin'][1]
    order = []
    ys = d['grid_y']
    mid = ys[len(ys) // 2]
    seq = [('h', mid)] + [('v', x) for x in d['grid_x']] + [('h', y) for y in ys if y != mid]
    for n, (o, v) in enumerate(seq, 1):
        if o == 'h':
            yy = Y + v * sy
            b += line(X + 4, yy, X + w - 4, yy, extra='stroke="#2B4C74" stroke-width="1.8" stroke-dasharray="4 2.6"')
            b += badge(X + w + 12, yy, n, r=8)
        else:
            xx = X + v * s_
            b += line(xx, Y + 4, xx, Y + h - 4, extra='stroke="#2B4C74" stroke-width="1.8" stroke-dasharray="4 2.6"')
            b += badge(xx, Y - 2 + 0, n, r=8)
    b += dim_h(X, X + d['grid'] * s_, Y + h + 14, f'{art_vn(d["grid"])} cm', above=False, dy=12)
    b += txt(X - 8, Y + h / 2, 'thứ tự', 't-lbl t-sm t-bold t-end') + txt(X - 8, Y + h / 2 + 13, 'may', 't-lbl t-sm t-end')
    return svg(W, H, b)


def _bind_xsec(stage):
    """mặt cắt mép khăn + dải bo (stage 1: may vào mặt A; 2: lật sang mặt B và may)"""
    W, H = 300, 150
    u = 30  # px / cm
    b = ''
    E = 196
    yA, yB = 64, 82
    b += rect(10, yA, E - 10, yB - yA, fill=fab('terry-sky'))
    b += rect(10, yA + 6, E - 10, 6, fill=fab('jersey-heather'))
    b += rect(10, yB - 4, E - 10, 4, fill='#3B5F8A')
    b += txt(12, yA - 8, 'mặt A', 't-lbl t-sm t-bold') + txt(12, yB + 16, 'mặt B', 't-lbl t-sm t-bold')
    col = '#D96F43'
    if stage == 1:
        x1 = E - 3.5 * u
        b += path(f'M{E} {yA - 3} H{x1} Q{x1 - 6} {yA - 6.5} {x1} {yA - 10} H{E}', extra=f'fill="none" stroke="{col}" stroke-width="3.2"')
        b += line(E - u, yA - 16, E - u, yA + 2, extra='stroke="#D6336C" stroke-width="3"')
        b += txt((x1 + E) / 2 - 16, yA - 20, 'dải gấp đôi', 't-lbl t-sm t-bold t-mid t-terra')
        b += line(E - u, yB + 4, E - u, yB + 26, cls='s-ext') + line(E, yB + 4, E, yB + 26, cls='s-ext')
        b += dim_h(E - u, E, yB + 22, '1 cm', above=False, dy=14)
        b += txt(E + 8, yA - 2, 'mép thô dải', 't-lbl t-sm') + txt(E + 8, yA + 11, '= mép khăn', 't-lbl t-sm')
        b += txt(E - u + 4, yA - 30, 'may', 't-lbl t-sm t-seam t-bold')
    else:
        b += path(f'M{E - u} {yA - 7} H{E - 4} Q{E + 12} {yA - 7} {E + 12} {(yA + yB) / 2} Q{E + 12} {yB + 7} {E - 4} {yB + 7} H{E - u - 8}', extra=f'fill="none" stroke="{col}" stroke-width="6"')
        b += line(E - u, yA - 12, E - u, yA + 2, extra='stroke="#D6336C" stroke-width="3"')
        b += line(E - u - 2, yB - 2, E - u - 2, yB + 16, extra='stroke="#0E8C8C" stroke-width="3" stroke-dasharray="3 2"')
        b += txt(12, yB + 44, 'may từ mặt B, sát mép gấp 2 mm', 't-lbl t-sm t-bold t-top')
        b += line(E - u - 2, yB + 18, E - u - 2, yB + 32, extra='stroke="#0E8C8C" stroke-width="1"')
        b += dim_h(E - u, E + 12, yA - 20, '≈ 1 cm')
        b += path(f'M{E + 26} {yA - 12} C {E + 62} {yA} {E + 62} {yB} {E + 26} {yB + 16}', cls='s-move')
        b += txt(E + 50, yA - 22, 'lật dải', 't-lbl t-sm t-bold t-terra')
    return svg(W, H, b)


def m5_fold(ctx):
    d = ctx.d['m5']
    W, H = 300, 150
    s_ = 7
    b = piece(20, 30, 236, d['binding_w'] * s_ * .9, 'jersey-terra')
    b += line(20, 30 + d['binding_w'] * s_ * .45, 256, 30 + d['binding_w'] * s_ * .45, cls='s-fold')
    b += dim_v(264, 30, 30 + d['binding_w'] * s_ * .9, f'{art_vn(d["binding_w"])}', side='right')
    b += path('M140 108 v18', cls='s-flow')
    b += piece(20, 132 - 6, 236, d['binding_half'] * s_ * .5, 'jersey-terra', shadow=False)
    b += txt(150, 20, f'gấp đôi theo chiều dài (mặt trái vào trong), ủi → {art_vn(d["binding_half"])} cm', 't-lbl t-mid t-sm t-bold')
    return svg(W, H, b)


def m5_s6(ctx): return _bind_xsec(1)
def m5_s7(ctx): return _bind_xsec(2)


def m5_short(ctx):
    d = ctx.d['m5']
    W, H = 300, 160
    b = ''
    X, Y, w = 40, 52, 200
    b += rect(X, Y, w, 96, fill=fab('terry-sky'))
    for x0 in (X, X + w - 16):
        b += rect(x0, Y, 16, 96, fill=fab('jersey-terra')) + rect(x0, Y, 16, 96, cls='s-edge')
    b += txt(X + w / 2, Y + 60, 'khăn: 2 cạnh dài đã bo xong', 't-lbl t-mid t-sm')
    t = d['tail'] * 11
    b += rect(X - t, Y - 18, w + 2 * t, 18, fill=fab('jersey-terra')) + rect(X - t, Y - 18, w + 2 * t, 18, cls='s-edge')
    b += txt(X + w / 2, Y - 24, f'dải cạnh ngắn {art_vn(d["bind_short"][1])} cm', 't-lbl t-mid t-sm t-bold')
    for sx, x0 in ((-1, X), (1, X + w)):
        b += line(x0, Y - 22, x0, Y + 4, cls='s-ext')
        b += path(f'M{x0 + sx * (t + 6)} {Y - 6} C{x0 + sx * (t + 20)} {Y + 8} {x0 + sx * 12} {Y + 26} {x0 + sx * 2} {Y + 20}', cls='s-move')
    b += dim_h(X + w, X + w + t, Y - 44, f'{art_vn(d["tail"])} cm', dy=14)
    b += txt(X + w / 2, Y + 84, 'gấp 2 đuôi bọc kín đầu mép, rồi lật dải', 't-lbl t-mid t-sm t-bold t-terra')
    return svg(W, H, b)


def m6_measure(ctx):
    d = ctx.d['m6']
    W, H = 330, 200
    s_ = 6
    L, Wd = d['L'] * s_, d['W'] * s_
    X, Y = 30, 40
    b = rect(X + 3, Y + 4, L, Wd, fill='#23313A', rx=8, extra='opacity=".12"')
    b += rect(X, Y, L, Wd, fill='#B8C0C4', rx=8, extra='stroke="#6F7F88" stroke-width="1.4"')
    b += ''.join(rect(X + 10 + k * 14, Y + 8, 6, Wd - 16, fill='#9AA5AB', rx=2) for k in range(int((L - 20) / 14)))
    b += rect(X + L / 2 - 14, Y + Wd / 2 - 10, 28, 20, fill='#6F7F88', rx=4)
    b += line(X + L / 2, Y - 4, X + L / 2, Y + Wd + 4, extra='stroke="#23313A" stroke-width="1.2" stroke-dasharray="3 2"')
    b += txt(X + L / 2, Y - 10, 'khớp gập (nếu có)', 't-lbl t-mid t-sm')
    b += dim_h(X, X + L, Y + Wd + 18, f'L = {art_vn(d["L"])} cm', above=False, dy=14)
    b += dim_v(X + L + 10, Y, Y + Wd, f'W = {art_vn(d["W"])}', side='right')
    # nhìn nghiêng
    y2 = Y + Wd + 56
    b += rect(X, y2, L, d['h'] * s_ * 1.6, fill='#B8C0C4', rx=3, extra='stroke="#6F7F88"')
    b += dim_v(X + L + 10, y2, y2 + d['h'] * s_ * 1.6, f'h = {art_vn(d["h"])}', side='right')
    b += txt(X, y2 + 26, 'nhìn nghiêng: đo độ dày h', 't-lbl t-sm')
    return svg(W, H, b)


def m6_pieces(ctx):
    d = ctx.d['m6']
    W, H = 640, 200
    s_ = 4.6
    L, Wd = d['cut_main'][0] * s_, d['cut_main'][1] * s_
    X, Y = 30, 24
    b = piece(X, Y, L, Wd, 'terry-mint') + txt(X + L / 2, Y + Wd / 2 + 4, 'A · mặt lau (khăn bông)', 't-lbl t-mid t-bold')
    b += piece(X, Y + Wd + 26, L, Wd, 'denim') + txt(X + L / 2, Y + Wd * 1.5 + 30, 'B · lưng (jeans, cotton dày)', 't-lbl t-mid t-bold')
    b += dim_h(X, X + L, Y - 7, f'{art_vn(d["cut_main"][0])} cm') + dim_v(X - 7, Y, Y + Wd, art_vn(d['cut_main'][1]))
    b += line(X + 14, Y + Wd - 10, X + 80, Y + Wd - 10, cls='s-grain') + line(X + 14, Y + 2 * Wd + 16, X + 80, Y + 2 * Wd + 16, cls='s-grain')
    px = X + L + 40
    pw, ph = d['cut_pocket'][0] * s_, d['cut_pocket'][1] * s_
    for k in range(2):
        xx = px + k * (pw + 20)
        b += piece(xx, Y, pw, ph, 'denim')
        b += line(xx - 4, Y + ph / 2, xx + pw + 4, Y + ph / 2, cls='s-fold')
        b += txt(xx + pw / 2, Y + ph + 16, f'túi {k + 1}', 't-lbl t-mid t-bold')
    b += dim_h(px, px + pw, Y - 7, art_vn(d['cut_pocket'][0])) + dim_v(px + 2 * pw + 30, Y, Y + ph, art_vn(d['cut_pocket'][1]), side='right')
    b += txt(px + pw + 10, Y + ph + 34, f'gấp đôi → {dims(*d["pocket_folded"])}', 't-lbl t-mid t-sm t-bold')
    return svg(W, H, b)


def _mop_base(ctx, s_=6.0):
    d = ctx.d['m6']
    return d, s_, d['cut_main'][0] * s_, d['cut_main'][1] * s_


def m6_s3(ctx):
    d, s_, L, Wd = _mop_base(ctx)
    W, H = 300, 186
    X, Y = 18, 40
    b = piece(X, Y, L, Wd, 'denim-back') + txt(X + L / 2, Y + Wd + 16, 'B · mặt phải lên', 't-lbl t-mid t-sm t-bold')
    P = d['pocket_folded'][1] * s_
    for x0, fold_x in ((X, X + P), (X + L - P, X + L - P)):
        b += rect(x0, Y, P, Wd, fill=fab('denim'))
        b += line(fold_x, Y, fold_x, Y + Wd, extra='stroke="#fff" stroke-width="2"')
        b += rect(x0, Y, P, Wd, cls='s-edge')
    b += rect(X + 2.5, Y + 2.5, L - 5, Wd - 5, extra='fill="none" stroke="#D6336C" stroke-width="1.2" stroke-dasharray="2 2"')
    b += txt(X + P / 2, Y - 8, 'túi', 't-lbl t-mid t-sm t-bold') + txt(X + L - P / 2, Y - 8, 'túi', 't-lbl t-mid t-sm t-bold')
    b += dim_h(X, X + P, Y + Wd + 30, f'{art_vn(d["P"] + ctx.d["sa"])}', above=False, dy=12)
    b += txt(X + L / 2, Y - 8, 'mép gấp quay vào giữa', 't-lbl t-mid t-sm')
    return svg(W, H, b)


def m6_s4(ctx):
    d, s_, L, Wd = _mop_base(ctx)
    W, H = 300, 186
    X, Y = 18, 40
    b = piece(X + 4, Y + 4, L, Wd, 'denim')
    b += piece(X - 2, Y - 2, L, Wd, 'terry-mint', side='wrong')
    b += clips_around(X - 2, Y - 2, L, Wd, n_side=2)
    g1 = L / 2 - d['opening'] / 2 * s_
    b += gap_band(X - 2 + g1, Y - 2 + Wd - s_, X - 2 + g1 + d['opening'] * s_, Y - 2 + Wd - s_, t=7)
    b += seam_rect(X - 2 + s_, Y - 2 + s_, L - 2 * s_, Wd - 2 * s_, gap=('b', g1 - s_, g1 - s_ + d['opening'] * s_))
    b += dim_h(X - 2 + g1, X - 2 + g1 + d['opening'] * s_, Y + Wd + 22, f'khe {art_vn(d["opening"])} cm', above=False, dy=12)
    b += txt(X + L / 2, Y - 14, 'A úp xuống (mặt trái lên), may quanh 1 cm', 't-lbl t-mid t-sm t-bold')
    return svg(W, H, b)


def m6_s6(ctx):
    d, s_, L, Wd = _mop_base(ctx)
    W, H = 300, 186
    X, Y = 18, 36
    b = piece(X, Y, L, Wd, 'denim-back')
    P = d['P'] * s_
    for x0, fx in ((X, X + P), (X + L - P, X + L - P)):
        b += rect(x0, Y, P, Wd, fill=fab('denim')) + rect(x0, Y, P, Wd, cls='s-edge')
        b += line(fx, Y, fx, Y + Wd, extra='stroke="#fff" stroke-width="2"')
    b += topstitch_rect(X, Y, L, Wd, d['ts'] if False else ctx.d['ts'] * s_)
    b += txt(X + L / 2, Y + Wd + 18, 'mặt lưng sau khi lộn: 2 túi ở 2 đầu', 't-lbl t-mid t-sm t-bold')
    b += dim_h(X, X + P, Y - 7, f'túi sâu {art_vn(d["P"])}')
    return svg(W, H, b)


def m6_s8(ctx):
    W, H = 300, 170
    b = ''
    # bàn lau gập chữ V + mũi tên
    b += '<g transform="translate(30 30)">'
    b += '<path d="M0 60 L80 20 L160 60" fill="none" stroke="#9AA5AB" stroke-width="8" stroke-linejoin="round"/>'
    b += '<circle cx="80" cy="20" r="6" fill="#6F7F88"/><path d="M80 20 L110 -20" stroke="#B8C0C4" stroke-width="5"/>'
    b += '</g>'
    b += rect(20, 100, 180, 30, fill=fab('terry-mint'), rx=3) + rect(20, 100, 36, 30, fill=fab('denim')) + rect(164, 100, 36, 30, fill=fab('denim'))
    b += rect(20, 100, 180, 30, cls='s-edge')
    b += path('M40 90 C 40 96 40 98 40 100', cls='s-move') + path('M180 90 C 180 96 180 98 180 100', cls='s-move')
    b += txt(110, 150, '1. gập bàn lau, nhét 2 đầu vào 2 túi', 't-lbl t-mid t-sm t-bold')
    b += txt(110, 164, '2. duỗi thẳng — vỏ căng tự giữ', 't-lbl t-mid t-sm')
    b += mop(214, 118, 70, pid_face='terry-mint', pid_back='denim')
    return svg(W, H, b)


def m6_s2(ctx):
    d = ctx.d['m6']
    W, H = 300, 170
    s_ = 4.8
    pw, ph = d['cut_pocket'][0] * s_, d['cut_pocket'][1] * s_
    X, Y = 26, 20
    b = piece(X, Y, pw, ph, 'denim', side='wrong') + line(X - 4, Y + ph / 2, X + pw + 4, Y + ph / 2, cls='s-fold')
    b += path(f'M{X + pw + 14} {Y + ph / 2} H{X + pw + 44}', cls='s-flow')
    X2 = X + pw + 56
    b += piece(X2, Y + ph / 4, pw, ph / 2, 'denim')
    b += line(X2, Y + ph / 4 + 3, X2 + pw, Y + ph / 4 + 3, extra='stroke="#fff" stroke-width="1.4" stroke-dasharray="3 2"')
    b += txt(X2 + pw / 2, Y + ph / 4 - 6, 'mép gấp', 't-lbl t-mid t-sm t-bold')
    b += txt(X2 + pw / 2, Y + ph * .75 + 16, 'mép thô 2 lớp', 't-lbl t-mid t-sm')
    b += dim_v(X2 + pw + 8, Y + ph / 4, Y + ph * .75, art_vn(d['pocket_folded'][1]), side='right')
    return svg(W, H, b)


def m6_s5(ctx):
    d, s_, L, Wd = _mop_base(ctx)
    W, H = 300, 186
    X, Y = 18, 40
    b = piece(X, Y, L, Wd, 'terry-mint', side='wrong')
    g1 = L / 2 - d['opening'] / 2 * s_
    b += seam_rect(X + s_, Y + s_, L - 2 * s_, Wd - 2 * s_, gap=('b', g1 - s_, g1 - s_ + d['opening'] * s_))
    b += corner_clips(X, Y, L, Wd, s_)
    b += txt(X + L / 2, Y - 12, 'cắt 4 góc; tỉa khăn bông còn 0,5 cm', 't-lbl t-mid t-sm t-bold')
    b += txt(X + L / 2, Y + Wd + 20, 'rồi lộn qua khe, đẩy góc', 't-lbl t-mid t-sm')
    return svg(W, H, b)


def m6_gallery(ctx):
    W, H = 640, 180
    b = ''
    s_ = 4.2
    d = ctx.d['m6']
    L, Wd = d['fin'][0] * s_, d['fin'][1] * s_
    P = d['P'] * s_
    items = [('terry-mint', 'denim', 'khăn bông · lau ướt'), ('flannel-red', 'denim-dark', 'flannel · lau bụi khô'), ('micro-blue', 'gingham-navy', 'microfiber · lau kính, gạch')]
    for i, (face, back, lab) in enumerate(items):
        x, y = 16 + i * 206, 24
        b += piece(x, y, L, Wd, back) + rect(x, y, P, Wd, fill='#fff', extra='opacity=".18"') + rect(x + L - P, y, P, Wd, fill='#fff', extra='opacity=".18"')
        b += line(x + P, y, x + P, y + Wd, extra='stroke="#fff" stroke-width="1.6"') + line(x + L - P, y, x + L - P, y + Wd, extra='stroke="#fff" stroke-width="1.6"')
        b += piece(x + 8, y + Wd + 14, L, Wd, face)
        b += topstitch_rect(x + 8, y + Wd + 14, L, Wd, 2.2, cls='s-top-light')
        b += txt(x + L / 2 + 4, y + 2 * Wd + 32, lab, 't-lbl t-mid t-sm t-bold')
    return svg(W, H, b)


def storage_basket(ctx):
    W, H = 320, 166
    b = basket(40, 70, 240, 72)
    cols = [('#4F9A57', 'gingham-green'), ('#3E74B8', 'gingham-sky'), ('#E8B931', 'terry-mustard'), ('#CF3F37', 'gingham-red'), ('#5B6167', 'denim-dark')]
    for i, (c, pid) in enumerate(cols):
        cx = 72 + i * 44
        b += rolled(cx, 58, 21, pid)
        b += f'<circle cx="{cx}" cy="58" r="21" fill="none" stroke="{c}" stroke-width="3.2"/>'
    b += '<rect x="33" y="65" width="254" height="10" rx="5" fill="#8A6A45"/>'
    b += txt(160, 162, 'Cuộn tròn, xếp theo mã màu của từng khu vực', 't-lbl t-mid t-sm')
    return svg(W, H, b)


def m6_xsec(ctx):
    d = ctx.d['m6']
    W, H = 640, 150
    u = 14
    pw, ph = d['W'] * u, d['h'] * u
    cx, cy = 200, 76
    x0, x1 = cx - pw / 2, cx + pw / 2
    y0, y1 = cy - ph / 2, cy + ph / 2
    b = rect(x0, y0, pw, ph, fill='#B8C0C4', rx=3, extra='stroke="#6F7F88"')
    b += txt(cx, cy + 4, f'bàn lau {art_vn(d["W"])} × {art_vn(d["h"])}', 't-lbl t-mid t-sm t-bold t-nost')
    g = 5
    # thân (dưới) + túi (trên), nối ở 2 mép, có đường diễu 0,5 cm
    for sgn, col in ((1, '#6FC0AE'), (-1, '#3B5F8A')):
        yy = y1 + g if sgn > 0 else y0 - g
        b += path(f'M{x0 - 16} {cy} Q{x0 - 16} {yy} {x0 + 6} {yy} H{x1 - 6} Q{x1 + 16} {yy} {x1 + 16} {cy}', extra=f'fill="none" stroke="{col}" stroke-width="5"')
    for xx in (x0 - 16, x1 + 16):
        b += line(xx, cy - 5, xx, cy + 5, extra='stroke="#D6336C" stroke-width="3"')
        b += line(xx + (6 if xx < cx else -6), cy - 9, xx + (6 if xx < cx else -6), cy + 9, extra='stroke="#0E8C8C" stroke-width="2.4" stroke-dasharray="3 2"')
    b += txt(x0 - 22, cy - 12, 'mép vỏ', 't-lbl t-sm t-end')
    b += txt(cx, y0 - g - 10, 'túi (jeans)', 't-lbl t-mid t-sm t-bold') + txt(cx, y1 + g + 20, 'mặt lau (khăn bông)', 't-lbl t-mid t-sm t-bold')
    tx = 400
    b += txt(tx, 40, f'Chu vi túi sau khi diễu = 2 × ({art_vn(d["Wp"])} − 1) = {art_vn(d["perim_pocket"])} cm', 't-lbl t-bold')
    b += txt(tx, 62, f'Chu vi bàn lau = 2 × ({art_vn(d["W"])} + {art_vn(d["h"])}) = {art_vn(d["perim_plate"])} cm', 't-lbl t-bold')
    b += txt(tx, 88, 'Phần dư còn lại cho bề dày 2 lớp vải.', 't-lbl t-sm')
    b += txt(tx, 104, 'Nếu chỉ cộng W + 2 (bỏ quên h), túi hụt', 't-lbl t-sm')
    b += txt(tx, 118, 'và không lồng được bàn lau vào.', 't-lbl t-sm')
    return svg(W, H, b)
