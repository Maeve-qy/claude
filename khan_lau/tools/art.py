"""Thư viện vẽ SVG: nét kỹ thuật (đường may, kích thước, khe lộn...) + minh họa (khăn, quần áo, dụng cụ).
Quy ước: 1 đơn vị = 1 px CSS. Mọi hàm trả về chuỗi SVG (không có thẻ <svg> bọc ngoài, trừ svg())."""
import math
from html import escape

# ---------------------------------------------------------------- khung

def svg(w, h, body, cls='', style=''):
    st = f' style="{style}"' if style else ''
    return f'<svg class="{cls}" width="{w}" height="{h}" viewBox="0 0 {w} {h}" xmlns="http://www.w3.org/2000/svg"{st}>{body}</svg>'


def g(body, tr='', op=None, cls=''):
    a = f' transform="{tr}"' if tr else ''
    a += f' opacity="{op}"' if op is not None else ''
    a += f' class="{cls}"' if cls else ''
    return f'<g{a}>{body}</g>'


def f(v):
    """số gọn cho SVG"""
    return f'{v:.2f}'.rstrip('0').rstrip('.') if isinstance(v, float) else str(v)


def vn(x):
    """số kiểu Việt Nam: 0,5 ; 45,3 ; 12"""
    if isinstance(x, float) and x.is_integer():
        x = int(x)
    s = f'{x}' if isinstance(x, int) else f'{x:.2f}'.rstrip('0').rstrip('.')
    return s.replace('.', ',')


def dims(a, b):
    return f'{vn(a)} × {vn(b)}'

# ---------------------------------------------------------------- vải & nét kỹ thuật

def fab(pid):
    return f'url(#p-{pid})'


def rect(x, y, w, h, fill='none', cls='', rx=0, extra=''):
    c = f' class="{cls}"' if cls else ''
    r = f' rx="{f(rx)}"' if rx else ''
    fl = f' fill="{fill}"' if fill else ''
    return f'<rect x="{f(x)}" y="{f(y)}" width="{f(w)}" height="{f(h)}"{r}{fl}{c} {extra}/>'


def piece(x, y, w, h, pid, side='right', rx=2, shadow=True, edge=True, label=None, lcls='t-lbl t-mid'):
    """Một mảnh vải phẳng. side='wrong' = mặt trái (nhạt, có chữ nhỏ)."""
    s = ''
    if shadow:
        s += rect(x + 2.5, y + 3, w, h, fill='#23313A', rx=rx, extra='opacity=".12"')
    s += rect(x, y, w, h, fill=fab(pid), rx=rx)
    if side == 'wrong':
        s += rect(x, y, w, h, fill='#FFFFFF', rx=rx, extra='opacity=".58"')
    if edge:
        s += rect(x, y, w, h, cls='s-edge', rx=rx)
    if label:
        s += txt(x + w / 2, y + h / 2 + 4, label, lcls)
    return s


def poly(pts, cls='', fill=None, close=True, extra=''):
    d = 'M' + ' L'.join(f'{f(px)} {f(py)}' for px, py in pts) + (' Z' if close else '')
    fl = f' fill="{fill}"' if fill else ''
    c = f' class="{cls}"' if cls else ''
    return f'<path d="{d}"{fl}{c} {extra}/>'


def path(d, cls='', fill=None, extra=''):
    fl = f' fill="{fill}"' if fill else ''
    c = f' class="{cls}"' if cls else ''
    return f'<path d="{d}"{fl}{c} {extra}/>'


def line(x1, y1, x2, y2, cls='', extra=''):
    c = f' class="{cls}"' if cls else ''
    return f'<line x1="{f(x1)}" y1="{f(y1)}" x2="{f(x2)}" y2="{f(y2)}"{c} {extra}/>'


def txt(x, y, s, cls='t-lbl', extra=''):
    return f'<text x="{f(x)}" y="{f(y)}" class="{cls}" {extra}>{escape(str(s))}</text>'


def txt_lines(x, y, lines, cls='t-lbl', lh=13):
    return ''.join(txt(x, y + i * lh, s, cls) for i, s in enumerate(lines))


def seam_rect(x, y, w, h, gap=None, cls='s-seam', ticks=True):
    """Đường may chữ nhật. gap=(cạnh 'b'|'t'|'l'|'r', vị trí đầu, vị trí cuối) tính từ góc trái/trên của cạnh đó (px).
    Đường may bắt đầu ở mép cuối khe và chạy vòng tới mép đầu khe."""
    if not gap:
        return rect(x, y, w, h, cls=cls)
    side, a, b = gap
    # các góc theo chiều kim đồng hồ bắt đầu từ trái-trên
    if side == 'b':
        start, end = (x + a, y + h), (x + b, y + h)
        pts = [end, (x + w, y + h), (x + w, y), (x, y), (x, y + h), start]
    elif side == 't':
        start, end = (x + a, y), (x + b, y)
        pts = [end, (x + w, y), (x + w, y + h), (x, y + h), (x, y), start]
    elif side == 'r':
        start, end = (x + w, y + a), (x + w, y + b)
        pts = [end, (x + w, y + h), (x, y + h), (x, y), (x + w, y), start]
    else:
        start, end = (x, y + a), (x, y + b)
        pts = [end, (x, y + h), (x + w, y + h), (x + w, y), (x, y), start]
    s = poly(pts, cls=cls, close=False)
    if ticks:
        for (px, py) in (start, end):
            if side in 'bt':
                s += line(px, py - 4, px, py + 4, extra='stroke="#D6336C" stroke-width="2.2"')
            else:
                s += line(px - 4, py, px + 4, py, extra='stroke="#D6336C" stroke-width="2.2"')
    return s


def gap_band(x1, y1, x2, y2, t=7):
    """dải vàng đánh dấu khe lộn (ngang hoặc dọc)"""
    if abs(y1 - y2) < 1e-6:
        return rect(min(x1, x2), y1 - t / 2, abs(x2 - x1), t, cls='f-gap', rx=2)
    return rect(x1 - t / 2, min(y1, y2), t, abs(y2 - y1), cls='f-gap', rx=2)


def zig(x1, y1, x2, y2, amp=3.2, step=4.2, cls='s-zig'):
    L = math.hypot(x2 - x1, y2 - y1)
    n = max(2, int(L / step))
    ux, uy = (x2 - x1) / L, (y2 - y1) / L
    nx, ny = -uy, ux
    pts = []
    for i in range(n + 1):
        t = i * L / n
        s = amp if i % 2 else -amp
        pts.append((x1 + ux * t + nx * s, y1 + uy * t + ny * s))
    return poly(pts, cls=cls, close=False)


def dim_h(x1, x2, y, label, ext=None, cls='t-dim t-mid', above=True, dy=None):
    s = ''
    if ext is not None:
        for xx in (x1, x2):
            s += line(xx, ext, xx, y + (-3 if ext > y else 3), cls='s-ext')
    s += line(x1, y, x2, y, cls='s-dim')
    ty = y - 4 if above else y + 12
    if dy is not None:
        ty = y + dy
    s += txt((x1 + x2) / 2, ty, label, cls)
    return s


def dim_v(x, y1, y2, label, ext=None, side='left', cls='t-dim', rot=False):
    s = ''
    if ext is not None:
        for yy in (y1, y2):
            s += line(ext, yy, x + (3 if ext < x else -3), yy, cls='s-ext')
    s += line(x, y1, x, y2, cls='s-dim')
    my = (y1 + y2) / 2
    if rot:
        s += f'<text x="{f(x - 5 if side == "left" else x + 13)}" y="{f(my)}" class="{cls} t-mid" transform="rotate(-90 {f(x - 5 if side == "left" else x + 13)} {f(my)})">{escape(label)}</text>'
    elif side == 'left':
        s += txt(x - 5, my + 4, label, cls + ' t-end')
    else:
        s += txt(x + 5, my + 4, label, cls)
    return s


def badge(x, y, n, r=9, fill=None):
    fl = f' style="fill:{fill}"' if fill else ''
    return f'<circle cx="{f(x)}" cy="{f(y)}" r="{r}" class="n-circle"{fl}/><text x="{f(x)}" y="{f(y + .5)}" class="n-txt">{n}</text>'


def arrow(d, cls='s-flow'):
    return f'<path d="{d}" class="{cls}"/>'


def grain(x, y1, y2):
    return line(x, y1, x, y2, cls='s-grain')


def scissors(x, y, s=1.0, rot=0, c='#C4592F'):
    """kéo nhỏ (biểu tượng cắt)"""
    b = (f'<circle cx="-7" cy="5" r="4.2" fill="none" stroke="{c}" stroke-width="2"/>'
         f'<circle cx="-7" cy="-5" r="4.2" fill="none" stroke="{c}" stroke-width="2"/>'
         f'<path d="M-3.5 3.2 L13 -3 M-3.5 -3.2 L13 3" stroke="#4B5A63" stroke-width="2.2" stroke-linecap="round"/>'
         f'<circle cx="2.8" cy="0" r="1.2" fill="#4B5A63"/>')
    return g(b, tr=f'translate({f(x)} {f(y)}) rotate({rot}) scale({s})')


def pin(x, y, rot=0, head='#D96F43'):
    b = f'<line x1="0" y1="0" x2="20" y2="0" stroke="#8A9499" stroke-width="1.3" stroke-linecap="round"/><circle cx="0" cy="0" r="3.2" fill="{head}"/><circle cx="-1" cy="-1" r="1" fill="#fff" opacity=".7"/>'
    return g(b, tr=f'translate({f(x)} {f(y)}) rotate({rot})')


def clip(x, y, rot=0, c='#E3B23C'):
    """kẹp vải"""
    b = (f'<rect x="-5" y="-8" width="10" height="16" rx="2.5" fill="{c}"/>'
         f'<rect x="-5" y="-8" width="10" height="5" rx="2" fill="#000" opacity=".12"/>'
         f'<rect x="-2" y="2" width="4" height="4" rx="1" fill="#fff" opacity=".5"/>')
    return g(b, tr=f'translate({f(x)} {f(y)}) rotate({rot})')


def needle_foot(x, y, s=1.0):
    """chân vịt + kim nhìn từ trên (biểu tượng máy may đang may)"""
    b = ('<rect x="-9" y="-16" width="18" height="30" rx="4" fill="#B8C0C4" stroke="#6F7F88" stroke-width="1"/>'
         '<rect x="-2" y="-14" width="4" height="22" rx="1.5" fill="#6F7F88"/>'
         '<circle cx="0" cy="0" r="2" fill="#23313A"/>')
    return g(b, tr=f'translate({f(x)} {f(y)}) scale({s})')


def hand_arrow_turn(cx, cy, r, a0, a1, cls='s-move'):
    """mũi tên vòng cung (xoay/lộn)"""
    x0, y0 = cx + r * math.cos(math.radians(a0)), cy + r * math.sin(math.radians(a0))
    x1, y1 = cx + r * math.cos(math.radians(a1)), cy + r * math.sin(math.radians(a1))
    large = 1 if abs(a1 - a0) > 180 else 0
    sweep = 1 if a1 > a0 else 0
    return f'<path d="M{f(x0)} {f(y0)} A{r} {r} 0 {large} {sweep} {f(x1)} {f(y1)}" class="{cls}"/>'

# ---------------------------------------------------------------- minh họa

def folded(x, y, w, h, pid, rx=5, stitch=True, flap=0.34, tone='#FFFFFF', rot=0, shadow=True, tag=None):
    """Khăn gấp nhìn từ trên (dạng nằm): thân + nếp gấp phía dưới có bóng đổ nhẹ + đường diễu."""
    s = ''
    if shadow:
        s += f'<rect x="{f(x + 4)}" y="{f(y + 6)}" width="{f(w)}" height="{f(h)}" rx="{rx}" fill="#23313A" opacity=".13"/>'
    s += f'<rect x="{f(x)}" y="{f(y)}" width="{f(w)}" height="{f(h)}" rx="{rx}" fill="{fab(pid)}"/>'
    fy = y + h * (1 - flap)
    # nếp gấp: dải tối nhẹ + viền sáng
    s += f'<rect x="{f(x)}" y="{f(fy)}" width="{f(w)}" height="{f(h - (fy - y))}" rx="{rx}" fill="#23313A" opacity=".08"/>'
    s += f'<path d="M{f(x + 1)} {f(fy)} Q{f(x + w / 2)} {f(fy + 3)} {f(x + w - 1)} {f(fy)}" stroke="#FFFFFF" stroke-opacity=".75" stroke-width="1.6" fill="none"/>'
    s += f'<path d="M{f(x + 1)} {f(fy + 2)} Q{f(x + w / 2)} {f(fy + 5)} {f(x + w - 1)} {f(fy + 2)}" stroke="#23313A" stroke-opacity=".14" stroke-width="1.4" fill="none"/>'
    if stitch:
        i = 5
        s += f'<rect x="{f(x + i)}" y="{f(y + i)}" width="{f(w - 2 * i)}" height="{f(h - 2 * i)}" rx="{max(rx - 2, 1)}" fill="none" stroke="{tone}" stroke-opacity=".85" stroke-width="1.2" stroke-dasharray="3 2.4"/>'
    s += f'<rect x="{f(x)}" y="{f(y)}" width="{f(w)}" height="{f(h)}" rx="{rx}" fill="none" stroke="#23313A" stroke-opacity=".22" stroke-width="1"/>'
    if tag:
        s += f'<rect x="{f(x + w - 16)}" y="{f(y - 3)}" width="9" height="14" rx="1.5" fill="{tag}"/>'
    return g(s, tr=f'rotate({rot} {f(x + w / 2)} {f(y + h / 2)})') if rot else s


def stack_side(x, y, w, layers, t=17, rx=8):
    """Chồng khăn gấp nhìn ngang: mỗi lớp là 1 khối bo tròn đầu phải (nếp gấp), lệch nhẹ."""
    s = ''
    cy = y
    for i, (pid, dx) in enumerate(layers):
        xx = x + dx
        s += f'<rect x="{f(xx + 3)}" y="{f(cy + 4)}" width="{f(w)}" height="{t}" rx="{rx}" fill="#23313A" opacity=".12"/>'
        s += f'<rect x="{f(xx)}" y="{f(cy)}" width="{f(w)}" height="{t}" rx="{rx}" fill="{fab(pid)}"/>'
        # bóng dưới + ánh sáng trên → khối tròn
        s += f'<rect x="{f(xx)}" y="{f(cy + t * .55)}" width="{f(w)}" height="{f(t * .45)}" rx="{rx * .6}" fill="#23313A" opacity=".13"/>'
        s += f'<path d="M{f(xx + rx)} {f(cy + 2.2)} H{f(xx + w - rx)}" stroke="#fff" stroke-opacity=".7" stroke-width="1.6" stroke-linecap="round"/>'
        # đường diễu
        s += f'<path d="M{f(xx + 7)} {f(cy + t / 2)} H{f(xx + w - 11)}" stroke="#fff" stroke-opacity=".8" stroke-width="1.1" stroke-dasharray="3 2.2"/>'
        s += f'<rect x="{f(xx)}" y="{f(cy)}" width="{f(w)}" height="{t}" rx="{rx}" fill="none" stroke="#23313A" stroke-opacity=".25"/>'
        cy += t - 1
    return s


def rolled(cx, cy, r, pid, length=0, rot=0):
    """Khăn cuộn tròn nhìn đầu: vòng xoắn."""
    s = f'<circle cx="{f(cx + 2)}" cy="{f(cy + 3)}" r="{r}" fill="#23313A" opacity=".14"/>'
    s += f'<circle cx="{f(cx)}" cy="{f(cy)}" r="{r}" fill="{fab(pid)}"/>'
    # xoắn ốc
    pts = []
    for i in range(0, 330):
        a = math.radians(i * 3)
        rr = r * 0.12 + (r * 0.8) * (i / 330)
        pts.append((cx + rr * math.cos(a), cy + rr * math.sin(a)))
    d = 'M' + ' L'.join(f'{f(px)} {f(py)}' for px, py in pts)
    s += f'<path d="{d}" fill="none" stroke="#23313A" stroke-opacity=".28" stroke-width="1.3"/>'
    s += f'<circle cx="{f(cx)}" cy="{f(cy)}" r="{r}" fill="none" stroke="#23313A" stroke-opacity=".3"/>'
    s += f'<path d="M{f(cx - r * .7)} {f(cy - r * .72)} A{r} {r} 0 0 1 {f(cx + r * .5)} {f(cy - r * .86)}" stroke="#fff" stroke-opacity=".6" stroke-width="2" fill="none" stroke-linecap="round"/>'
    return g(s, tr=f'rotate({rot} {f(cx)} {f(cy)})') if rot else s


def hanging_towel(x, y, w, h, pid, stripe='#22385C', loop='#C4592F', hook=True):
    """Khăn bếp treo trên móc: có quai, 2 sọc ngang kiểu khăn bếp, gấu gấp mép."""
    s = ''
    cx = x + w / 2
    if hook:
        s += f'<path d="M{f(cx - 20)} {f(y - 30)} H{f(cx + 20)}" stroke="#8A6A55" stroke-width="7" stroke-linecap="round"/>'
        s += f'<path d="M{f(cx)} {f(y - 27)} v10 q0 8 -7 8" stroke="#7D8A91" stroke-width="3" fill="none" stroke-linecap="round"/>'
    s += f'<path d="M{f(cx - 6)} {f(y + 2)} C{f(cx - 7)} {f(y - 16)} {f(cx + 7)} {f(y - 16)} {f(cx + 6)} {f(y + 2)}" stroke="{loop}" stroke-width="4.5" fill="none"/>'
    # thân khăn hơi loe gợn
    d = (f'M{f(x)} {f(y)} H{f(x + w)} L{f(x + w + 3)} {f(y + h)} '
         f'Q{f(x + w * .75)} {f(y + h + 5)} {f(x + w / 2)} {f(y + h)} Q{f(x + w * .25)} {f(y + h - 4)} {f(x - 3)} {f(y + h)} Z')
    s += f'<path d="{d}" transform="translate(4 6)" fill="#23313A" opacity=".12"/>'
    s += f'<path d="{d}" fill="{fab(pid)}"/>'
    for yy in (y + h * .72, y + h * .80):
        s += f'<path d="M{f(x - 1)} {f(yy)} H{f(x + w + 2)}" stroke="{stripe}" stroke-width="{h * .035:.1f}"/>'
    # nếp vải dọc
    for k, o in ((.3, .1), (.62, .08)):
        s += f'<path d="M{f(x + w * k)} {f(y + 6)} Q{f(x + w * k + 4)} {f(y + h * .5)} {f(x + w * k - 2)} {f(y + h - 4)}" stroke="#23313A" stroke-opacity="{o}" stroke-width="5" fill="none"/>'
    s += f'<path d="M{f(x + 5)} {f(y + 5)} H{f(x + w - 5)}" stroke="#fff" stroke-opacity=".8" stroke-width="1.1" stroke-dasharray="3 2.2"/>'
    s += f'<path d="M{f(x + 2)} {f(y + h - 7)} Q{f(x + w / 2)} {f(y + h - 9)} {f(x + w + 1)} {f(y + h - 6)}" stroke="#fff" stroke-opacity=".8" stroke-width="1.1" stroke-dasharray="3 2.2" fill="none"/>'
    s += f'<path d="{d}" fill="none" stroke="#23313A" stroke-opacity=".25"/>'
    return s


def mop(x, y, w, pid_face='terry-sky', pid_back='denim', handle=True, s_=1.0):
    """Cây lau nhà dẹt có vỏ bọc (nhìn nghiêng 3/4)."""
    h = w * .2
    b = ''
    if handle:
        b += f'<path d="M{f(x + w * .5)} {f(y - 4)} L{f(x + w * .78)} {f(y - w * 1.05)}" stroke="#B8C0C4" stroke-width="7" stroke-linecap="round"/>'
        b += f'<path d="M{f(x + w * .5)} {f(y - 4)} L{f(x + w * .78)} {f(y - w * 1.05)}" stroke="#fff" stroke-opacity=".6" stroke-width="2" stroke-linecap="round"/>'
        b += f'<path d="M{f(x + w * .74)} {f(y - w * .95)} L{f(x + w * .79)} {f(y - w * 1.07)}" stroke="#2B4C74" stroke-width="10" stroke-linecap="round"/>'
        b += f'<circle cx="{f(x + w * .5)}" cy="{f(y - 2)}" r="7" fill="#6F7F88"/>'
    # đế: hình bình hành (mặt trên) + dày
    top = [(x, y), (x + w, y), (x + w - w * .12, y + h), (x - w * .12, y + h)]
    b += poly([(px + 5, py + 8) for px, py in top], fill='#23313A', extra='opacity=".14"')
    b += poly([(x - w * .12, y + h), (x + w - w * .12, y + h), (x + w - w * .12, y + h + 9), (x - w * .12, y + h + 9)], fill=fab(pid_face))
    b += poly([(x - w * .12, y + h), (x + w - w * .12, y + h), (x + w - w * .12, y + h + 9), (x - w * .12, y + h + 9)], fill='#23313A', extra='opacity=".12"')
    b += poly(top, fill=fab(pid_back))
    # 2 túi ở 2 đầu
    pw = w * .24
    for x0 in (x, x + w - pw):
        b += poly([(x0, y), (x0 + pw, y), (x0 + pw - w * .12, y + h), (x0 - w * .12, y + h)], fill=fab(pid_back))
        b += poly([(x0, y), (x0 + pw, y), (x0 + pw - w * .12, y + h), (x0 - w * .12, y + h)], fill='#fff', extra='opacity=".12"')
    b += f'<path d="M{f(x + pw)} {f(y)} L{f(x + pw - w * .12)} {f(y + h)} M{f(x + w - pw)} {f(y)} L{f(x + w - pw - w * .12)} {f(y + h)}" stroke="#fff" stroke-opacity=".85" stroke-width="1.3" stroke-dasharray="3 2"/>'
    b += poly(top, cls='s-edge')
    return b


def basket(x, y, w, h, fill='#C9A77C', dark='#8A6A45'):
    s = f'<path d="M{f(x - 4)} {f(y)} H{f(x + w + 4)} L{f(x + w - 8)} {f(y + h)} H{f(x + 8)} Z" transform="translate(4 6)" fill="#23313A" opacity=".13"/>'
    s += f'<path d="M{f(x - 4)} {f(y)} H{f(x + w + 4)} L{f(x + w - 8)} {f(y + h)} H{f(x + 8)} Z" fill="{fill}"/>'
    for i in range(1, 5):
        yy = y + h * i / 5
        s += f'<path d="M{f(x - 4 + 12 * i / 5)} {f(yy)} H{f(x + w + 4 - 12 * i / 5)}" stroke="{dark}" stroke-opacity=".45" stroke-width="1.4"/>'
    for i in range(1, 12):
        xx = x + w * i / 12
        s += f'<path d="M{f(xx)} {f(y)} L{f(xx + (x + w / 2 - xx) * .1)} {f(y + h)}" stroke="{dark}" stroke-opacity=".3" stroke-width="1.2"/>'
    s += f'<rect x="{f(x - 7)}" y="{f(y - 5)}" width="{f(w + 14)}" height="10" rx="5" fill="{dark}"/>'
    s += f'<rect x="{f(x - 5)}" y="{f(y - 4)}" width="{f(w + 10)}" height="3" rx="1.5" fill="#fff" opacity=".25"/>'
    return s


def spool(x, y, c='#C4592F', s_=1.0):
    b = (f'<rect x="-9" y="-15" width="18" height="4" rx="1.5" fill="#C9A77C"/><rect x="-9" y="11" width="18" height="4" rx="1.5" fill="#C9A77C"/>'
         f'<rect x="-7" y="-11" width="14" height="22" fill="{c}"/>'
         + ''.join(f'<path d="M-7 {v} H7" stroke="#000" stroke-opacity=".12" stroke-width="1"/>' for v in range(-9, 11, 3))
         + '<rect x="-7" y="-11" width="4" height="22" fill="#fff" opacity=".2"/>')
    return g(b, tr=f'translate({f(x)} {f(y)}) scale({s_})')


def big_scissors(x, y, s_=1.0, rot=0, handle='#C4592F'):
    """kéo cắt vải: 2 lưỡi thép hé mở + 2 tay cầm vòng."""
    b = (f'<path d="M-2 -2 L84 -13 Q88 -12.5 85 -10 L4 4 Z" fill="#DDE2E5" stroke="#8A9499" stroke-width=".8"/>'
         f'<path d="M-2 2 L84 11 Q88 11 85 8.5 L4 -4 Z" fill="#C7CED2" stroke="#8A9499" stroke-width=".8"/>'
         f'<path d="M6 -2.2 L80 -11" stroke="#fff" stroke-opacity=".8" stroke-width="1"/>'
         f'<circle cx="2" cy="0" r="3.2" fill="#6F7F88"/><circle cx="2" cy="0" r="1.2" fill="#C7CED2"/>'
         f'<path d="M-1 -3 C-10 -8 -18 -18 -30 -17 C-42 -16 -44 -4 -34 -2 C-24 0 -12 -1 -1 -3 Z" fill="{handle}"/>'
         f'<path d="M-1 3 C-10 8 -18 20 -32 20 C-46 20 -46 6 -36 3 C-24 0 -12 1 -1 3 Z" fill="{handle}" opacity=".88"/>'
         f'<ellipse cx="-31" cy="-9" rx="7" ry="4.2" fill="#FFFCF6"/><ellipse cx="-33" cy="11" rx="8" ry="4.6" fill="#FFFCF6"/>')
    return g(b, tr=f'translate({f(x)} {f(y)}) rotate({rot}) scale({s_})')


def tape_measure(x, y, s_=1.0, rot=0):
    b = '<path d="M0 0 C 30 -10 60 12 110 0 C 140 -8 160 6 190 2" stroke="#E3B23C" stroke-width="11" fill="none" stroke-linecap="butt"/>'
    for i in range(0, 19):
        t = i / 18
        b += f'<path d="M{f(t * 186 + 2)} {f(-3 + 4 * math.sin(t * 6))} v5" stroke="#6B4B08" stroke-width=".9" opacity=".7"/>'
    return g(b, tr=f'translate({f(x)} {f(y)}) rotate({rot}) scale({s_})')


# ---------------------------------------------------------------- quần áo phẳng (để vẽ vùng cắt)

def shirt_outline(x, y, s):
    """Áo sơ mi nhìn sau, trải phẳng. Trả về (path_d, các mốc). s = px/cm. Thân rộng 56 cm, dài 76 cm."""
    W, L = 56 * s, 76 * s
    sh = 8 * s   # vai xuôi
    arm = 24 * s  # sâu nách
    sl = 60 * s  # dài tay
    x0, x1 = x, x + W
    d = (f'M{f(x0 + 18 * s)} {f(y)} Q{f(x + W / 2)} {f(y + 2.2 * s)} {f(x1 - 18 * s)} {f(y)} '  # cổ
         f'L{f(x1)} {f(y + 3.5 * s)} '  # vai phải
         f'L{f(x1 + sl * .82)} {f(y + sl * .55)} L{f(x1 + sl * .72)} {f(y + sl * .68)} '  # tay phải
         f'L{f(x1)} {f(y + arm)} '
         f'L{f(x1)} {f(y + L - 6 * s)} Q{f(x1 - 4 * s)} {f(y + L - 11 * s)} {f(x1 - 12 * s)} {f(y + L - 2 * s)} '
         f'Q{f(x + W / 2)} {f(y + L + 2 * s)} {f(x0 + 12 * s)} {f(y + L - 2 * s)} Q{f(x0 + 4 * s)} {f(y + L - 11 * s)} {f(x0)} {f(y + L - 6 * s)} '
         f'L{f(x0)} {f(y + arm)} L{f(x0 - sl * .72)} {f(y + sl * .68)} L{f(x0 - sl * .82)} {f(y + sl * .55)} L{f(x0)} {f(y + 3.5 * s)} Z')
    return d


_uid = [0]


def uid(p='u'):
    _uid[0] += 1
    return f'{p}{_uid[0]}'


def cloth_flip(x, y, w, h, front, back, c=None, rx=3, stitch=None, quilt=None, binding=None, shadow=True, back_wrong=False):
    """Khăn trải phẳng, góc dưới-phải lật lên để thấy mặt kia.
    front: pattern id hoặc hàm(x,y,w,h)->svg (vd. mặt ghép mảnh); back: pattern id của mặt sau.
    stitch: màu đường diễu quanh mép; quilt: list đoạn [(x1,y1,x2,y2)] theo tỉ lệ 0..1; binding: (pattern, bề rộng px)."""
    c = c if c is not None else min(w, h) * .32
    A = (x + w, y + h - c)
    B = (x + w - c, y + h)
    C2 = (x + w - c, y + h - c)
    body = [(x, y), (x + w, y), A, B, (x, y + h)]
    cid = uid('cf')
    s = ''
    if shadow:
        s += poly([(px + 3, py + 4) for px, py in body], fill='#23313A', extra='opacity=".13"')
    s += f'<clipPath id="{cid}">{poly(body)}</clipPath>'
    inner = ''
    if binding:
        bp, bw = binding
        inner += rect(x, y, w, h, fill=fab(bp))
        inner += rect(x + bw, y + bw, w - 2 * bw, h - 2 * bw, fill=fab(front) if isinstance(front, str) else 'none')
        if not isinstance(front, str):
            inner += front(x + bw, y + bw, w - 2 * bw, h - 2 * bw)
        inner += rect(x + bw, y + bw, w - 2 * bw, h - 2 * bw, extra='fill="none" stroke="#23313A" stroke-opacity=".18"')
        inner += rect(x + bw - 2.2, y + bw - 2.2, w - 2 * bw + 4.4, h - 2 * bw + 4.4, extra='fill="none" stroke="#fff" stroke-opacity=".85" stroke-width="1.1" stroke-dasharray="3 2.2"')
    else:
        inner += rect(x, y, w, h, fill=fab(front)) if isinstance(front, str) else front(x, y, w, h)
    if quilt:
        qc = quilt[1] if isinstance(quilt, tuple) and isinstance(quilt[1], str) else '#FFFFFF'
        segs = quilt[0] if isinstance(quilt, tuple) and isinstance(quilt[1], str) else quilt
        for (a1, b1, a2, b2) in segs:
            inner += line(x + a1 * w, y + b1 * h, x + a2 * w, y + b2 * h, extra=f'stroke="{qc}" stroke-opacity=".9" stroke-width="1.2" stroke-dasharray="3 2.2"')
    if stitch:
        i = 6
        inner += rect(x + i, y + i, w - 2 * i, h - 2 * i, extra=f'fill="none" stroke="{stitch}" stroke-opacity=".9" stroke-width="1.2" stroke-dasharray="3 2.2"')
    s += f'<g clip-path="url(#{cid})">{inner}</g>'
    s += poly(body, extra='fill="none" stroke="#23313A" stroke-opacity=".28"')
    # mép lật
    flap = [A, B, C2]
    s += poly([(A[0] - 2, A[1] + 3), (B[0] + 2, B[1] + 2), (C2[0] + 3, C2[1] + 4)], fill='#23313A', extra='opacity=".18"')
    s += poly(flap, fill=fab(back))
    if back_wrong:
        s += poly(flap, fill='#fff', extra='opacity=".5"')
    s += poly(flap, fill='#23313A', extra='opacity=".06"')
    s += line(A[0], A[1], B[0], B[1], extra='stroke="#fff" stroke-opacity=".8" stroke-width="1.6"')
    s += poly(flap, extra='fill="none" stroke="#23313A" stroke-opacity=".3"')
    return s


def patch_front(pids, n):
    """trả về hàm vẽ mặt ghép n×n ô với danh sách pattern (lặp lại nếu thiếu)"""
    def draw(x, y, w, h):
        s = ''
        cw, ch = w / n, h / n
        for r in range(n):
            for c in range(n):
                pid = pids[(r * n + c) % len(pids)]
                s += rect(x + c * cw, y + r * ch, cw + .3, ch + .3, fill=fab(pid))
        for k in range(1, n):
            s += line(x + k * cw, y, x + k * cw, y + h, extra='stroke="#23313A" stroke-opacity=".22" stroke-width="1"')
            s += line(x, y + k * ch, x + w, y + k * ch, extra='stroke="#23313A" stroke-opacity=".22" stroke-width="1"')
        return s
    return draw


def jersey_rag(x, y, w, h, pid, rot=0):
    """giẻ áo thun: mép cắt hơi cuộn (không may)"""
    s = rect(x + 3, y + 4, w, h, fill='#23313A', rx=2, extra='opacity=".12"')
    s += rect(x, y, w, h, fill=fab(pid), rx=2)
    # mép cuộn: viền tối nhẹ 2 cạnh cắt (trái/phải) + gấu may sẵn (dưới)
    s += rect(x, y, 3.2, h, fill='#23313A', extra='opacity=".14"') + rect(x + w - 3.2, y, 3.2, h, fill='#23313A', extra='opacity=".14"')
    s += line(x + 3, y + h - 7, x + w - 3, y + h - 7, extra='stroke="#fff" stroke-opacity=".75" stroke-width="1.1" stroke-dasharray="2.6 2"')
    s += line(x + 3, y + h - 4.5, x + w - 3, y + h - 4.5, extra='stroke="#fff" stroke-opacity=".75" stroke-width="1.1" stroke-dasharray="2.6 2"')
    s += rect(x, y, w, h, rx=2, extra='fill="none" stroke="#23313A" stroke-opacity=".22"')
    return g(s, tr=f'rotate({rot} {f(x + w / 2)} {f(y + h / 2)})') if rot else s


# ---------------------------------------------------------------- biểu tượng nhỏ (34×34)
ICONS = {
 'shirt': '<path d="M11 6 L6 9 L3 16 L8 18 L10 14 V29 H24 V14 L26 18 L31 16 L28 9 L23 6 Q17 10 11 6 Z" fill="#9DB7D5" stroke="#2B4C74" stroke-width="1.5" stroke-linejoin="round"/><path d="M17 10 V29" stroke="#2B4C74" stroke-width="1" stroke-dasharray="2 1.6"/>',
 'palette': '<path d="M17 4 C8 4 3 10 3 17 C3 25 9 30 16 30 C19 30 19 27 18 25 C17 23 18 21 21 21 H25 C29 21 31 18 31 15 C31 9 25 4 17 4 Z" fill="#F8F2E6" stroke="#2B4C74" stroke-width="1.5"/><circle cx="10" cy="15" r="2.6" fill="#D96F43"/><circle cx="14" cy="9.5" r="2.6" fill="#E3B23C"/><circle cx="21" cy="9.5" r="2.6" fill="#7FA37A"/><circle cx="25.5" cy="14.5" r="2.4" fill="#3E6A9E"/>',
 'tools': '<rect x="4" y="21" width="26" height="7" rx="1.5" fill="#F2D78E" stroke="#9C7212" stroke-width="1.2"/><path d="M8 21 v3 M12 21 v4 M16 21 v3 M20 21 v4 M24 21 v3" stroke="#9C7212" stroke-width="1"/><circle cx="9" cy="8" r="3.4" fill="none" stroke="#C4592F" stroke-width="1.8"/><circle cx="9" cy="16" r="3.4" fill="none" stroke="#C4592F" stroke-width="1.8"/><path d="M12 10 L28 5 M12 14 L28 17" stroke="#4B5A63" stroke-width="1.8" stroke-linecap="round"/>',
 'formula': '<rect x="4" y="4" width="26" height="26" rx="4" fill="#E9F0F8" stroke="#2B6CB0" stroke-width="1.4"/><path d="M9 12 h7 M12.5 8.5 v7 M19 12 h6 M9 22 h6 M19 20 h6 M19 24 h6" stroke="#2B6CB0" stroke-width="1.8" stroke-linecap="round"/>',
 'needle': '<path d="M6 28 L26 6" stroke="#6F7F88" stroke-width="2" stroke-linecap="round"/><ellipse cx="24.5" cy="7.5" rx="1.2" ry="2.6" transform="rotate(42 24.5 7.5)" fill="#fff" stroke="#6F7F88"/><path d="M25 7 C31 14 20 18 26 26 C28 29 22 31 18 28" fill="none" stroke="#D96F43" stroke-width="1.6" stroke-linecap="round"/><path d="M4 30 h8" stroke="#D6336C" stroke-width="1.6" stroke-dasharray="2.4 1.6"/>',
 'wash': '<path d="M17 4 C17 4 7 15 7 21 C7 26.5 11.5 30 17 30 C22.5 30 27 26.5 27 21 C27 15 17 4 17 4 Z" fill="#BCD4EC" stroke="#2B4C74" stroke-width="1.5"/><path d="M12 21 C12 24 14 26 17 26" stroke="#fff" stroke-width="2" fill="none" stroke-linecap="round"/>',
 'zig': '<rect x="4" y="6" width="26" height="22" rx="3" fill="#F8F2E6" stroke="#8A9499" stroke-width="1"/><path d="M6 12 L9 20 L12 12 L15 20 L18 12 L21 20 L24 12 L27 20" fill="none" stroke="#C2185B" stroke-width="1.7" stroke-linejoin="round"/>',
 'check': '<rect x="5" y="4" width="24" height="27" rx="3" fill="#fff" stroke="#46693F" stroke-width="1.5"/><path d="M10 12 l2.5 2.5 L17 10 M10 21 l2.5 2.5 L17 19" stroke="#46693F" stroke-width="1.8" fill="none" stroke-linecap="round" stroke-linejoin="round"/><path d="M20 12.5 h5 M20 21.5 h5" stroke="#7D8A91" stroke-width="1.6" stroke-linecap="round"/>',
}


def icon(name, size=34):
    return f'<svg width="{size}" height="{size}" viewBox="0 0 34 34" xmlns="http://www.w3.org/2000/svg">{ICONS[name]}</svg>'


# ---------------------------------------------------------------- quần áo trải phẳng (tọa độ cm -> px)

class CM:
    """ánh xạ tọa độ cm -> px: X(x), Y(y)"""
    def __init__(self, ox, oy, s):
        self.ox, self.oy, self.s = ox, oy, s

    def P(self, x, y):
        return (self.ox + x * self.s, self.oy + y * self.s)

    def d(self, cmds):
        """cmds: list ('M'|'L'|'Q'|'C'|'Z', pts...) theo cm"""
        out = ''
        for c in cmds:
            op, pts = c[0], c[1:]
            out += op + ' '.join(f'{f(self.ox + px * self.s)} {f(self.oy + py * self.s)}' for px, py in pts) + ' '
        return out.strip()

    def rect(self, x, y, w, h, **kw):
        return rect(self.ox + x * self.s, self.oy + y * self.s, w * self.s, h * self.s, **kw)


def garment_shape(dpath, pid, shadow=True):
    s = ''
    if shadow:
        s += f'<path d="{dpath}" transform="translate(3 5)" fill="#23313A" opacity=".12"/>'
    s += f'<path d="{dpath}" fill="{fab(pid)}"/>'
    s += f'<path d="{dpath}" fill="none" stroke="#23313A" stroke-opacity=".45" stroke-width="1.1" stroke-linejoin="round"/>'
    return s


def cutline(dpath):
    """đường cắt tháo (cam, nét đứt dài)"""
    return f'<path d="{dpath}" fill="none" stroke="#C4592F" stroke-width="2" stroke-dasharray="7 4" stroke-linecap="round"/>'


def zone(m, x, y, w, h, label=None, sub=None, col='#FFFFFF'):
    """vùng vải dùng được: khung trắng đậm + nền trắng mờ"""
    s = m.rect(x, y, w, h, fill=col, extra='opacity=".42"')
    s += m.rect(x, y, w, h, extra='fill="none" stroke="#FFFFFF" stroke-width="2.4"')
    s += m.rect(x, y, w, h, extra='fill="none" stroke="#1C3553" stroke-width="1.2" stroke-dasharray="5 3"')
    if label:
        cx, cy = m.P(x + w / 2, y + h / 2)
        s += txt(cx, cy - (3 if sub else -4), label, 't-lbl t-mid t-bold')
        if sub:
            s += txt(cx, cy + 11, sub, 't-dim t-mid')
    return s


def shirt_front(m, pid='gingham-sky', cuts=True):
    """áo sơ mi nam trải phẳng (mặt trước), thân 56 × 76 cm, tay 60 cm"""
    import math as _m
    body = [('M', (20, 0)), ('Q', (28, 3.5), (36, 0)), ('L', (56, 4)), ('L', (56, 24)), ('L', (56, 68)),
            ('Q', (52, 66), (46, 72)), ('Q', (28, 80), (10, 72)), ('Q', (4, 66), (0, 68)), ('L', (0, 24)), ('L', (0, 4)), ('Z',)]
    s = ''
    # tay áo (vẽ trước để thân đè lên)
    for side in (-1, 1):
        ang = _m.radians(56)
        dx, dy = side * _m.cos(ang), _m.sin(ang)
        nx, ny = dy, -dx  # vuông góc
        bx = 0 if side < 0 else 56
        S, U = (bx, 4), (bx, 24)
        mid = (bx, 14)
        cen = (mid[0] + dx * 54, mid[1] + dy * 54)
        hw = 7
        c1 = (cen[0] - side * nx * hw * -1, cen[1] - side * ny * hw * -1)
        c2 = (cen[0] + side * nx * hw * -1, cen[1] + side * ny * hw * -1)
        # chọn c_up gần S hơn
        c_up, c_dn = (c1, c2) if _m.dist(c1, S) < _m.dist(c2, S) else (c2, c1)
        sl = [('M', S), ('L', c_up), ('L', c_dn), ('L', U), ('Z',)]
        s += garment_shape(m.d(sl), pid)
        cf1 = (c_up[0] + dx * 6, c_up[1] + dy * 6)
        cf2 = (c_dn[0] + dx * 6, c_dn[1] + dy * 6)
        s += garment_shape(m.d([('M', c_up), ('L', cf1), ('L', cf2), ('L', c_dn), ('Z',)]), pid)
        s += f'<path d="{m.d([("M", c_up), ("L", cf1), ("L", cf2), ("L", c_dn), ("Z",)])}" fill="#fff" opacity=".25"/>'
        if cuts:
            s += cutline(m.d([('M', U), ('L', c_dn)]))
            s += cutline(m.d([('M', c_up), ('L', c_dn)]))
    s += garment_shape(m.d(body), pid)
    # cổ áo
    collar = [('M', (19, -1)), ('Q', (28, 2), (37, -1)), ('L', (38, 3)), ('L', (30, 9)), ('L', (28, 7)), ('L', (26, 9)), ('L', (18, 3)), ('Z',)]
    s += garment_shape(m.d(collar), pid, shadow=False)
    s += f'<path d="{m.d(collar)}" fill="#fff" opacity=".35"/>'
    # nẹp cúc + cúc
    s += m.rect(26.3, 7, 3.4, 69, fill='#fff', extra='opacity=".35"')
    s += m.rect(26.3, 7, 3.4, 69, extra='fill="none" stroke="#23313A" stroke-opacity=".35"')
    for yy in (13, 22, 31, 40, 49, 58, 67):
        cx, cy = m.P(28, yy)
        s += f'<circle cx="{f(cx)}" cy="{f(cy)}" r="{f(.75 * m.s)}" fill="#F8F2E6" stroke="#7D8A91" stroke-width=".8"/>'
    # túi ngực
    s += m.rect(33, 14, 11, 12, fill='#fff', extra='opacity=".28"') + m.rect(33, 14, 11, 12, extra='fill="none" stroke="#23313A" stroke-opacity=".35" stroke-dasharray="2 1.5"')
    if cuts:
        # đường cắt tháo: sườn áo, vòng nách, dọc nẹp, dưới cầu vai (ở thân sau)
        s += cutline(m.d([('M', (0, 4)), ('L', (0, 68))]))
        s += cutline(m.d([('M', (56, 4)), ('L', (56, 68))]))
        s += cutline(m.d([('M', (25.8, 8)), ('L', (25.8, 76))]))
        s += cutline(m.d([('M', (30.2, 8)), ('L', (30.2, 76))]))
        s += cutline(m.d([('M', (0, 4)), ('L', (20, 1.2))]))
        s += cutline(m.d([('M', (56, 4)), ('L', (36, 1.2))]))
    return s


def tshirt_front(m, pid='jersey-teal', cuts=True):
    """áo thun cổ tròn trải phẳng, thân 50 × 70"""
    body = [('M', (16, 0)), ('Q', (25, 8), (34, 0)), ('L', (50, 5)), ('L', (67, 14)), ('L', (59, 30)), ('L', (50, 23)),
            ('L', (50, 70)), ('L', (0, 70)), ('L', (0, 23)), ('L', (-9, 30)), ('L', (-17, 14)), ('L', (0, 5)), ('Z',)]
    s = garment_shape(m.d(body), pid)
    # bo cổ
    s += f'<path d="{m.d([("M", (16, 0)), ("Q", (25, 8), (34, 0))])}" fill="none" stroke="#fff" stroke-opacity=".55" stroke-width="{f(1.6 * m.s)}"/>'
    # gấu tay, gấu áo (đường may kép)
    for seg in ([('M', (-17, 14)), ('L', (-9, 30))], [('M', (67, 14)), ('L', (59, 30))]):
        s += f'<path d="{m.d(seg)}" fill="none" stroke="#fff" stroke-opacity=".6" stroke-width="1" stroke-dasharray="2.4 1.8" transform="translate(0 0)"/>'
    for yy in (68, 68.8):
        s += f'<path d="{m.d([("M", (1, yy)), ("L", (49, yy))])}" stroke="#fff" stroke-opacity=".7" stroke-width="1" stroke-dasharray="2.4 1.8"/>'
    # hình in ngực (nên cắt bỏ)
    cx, cy = m.P(25, 14)
    s += f'<circle cx="{f(cx)}" cy="{f(cy)}" r="{f(5.5 * m.s)}" fill="#F2D78E" opacity=".95"/><circle cx="{f(cx)}" cy="{f(cy)}" r="{f(3 * m.s)}" fill="#D96F43" opacity=".85"/>'
    if cuts:
        s += cutline(m.d([('M', (-1, 23)), ('L', (51, 23))]))
        s += cutline(m.d([('M', (0, 23)), ('L', (0, 70))]))
        s += cutline(m.d([('M', (50, 23)), ('L', (50, 70))]))
    return s


def jeans_front(m, pid='denim', cuts=True):
    """quần jeans trải phẳng, eo 40, dài 106"""
    body = [('M', (0, 0)), ('L', (40, 0)), ('L', (44, 20)), ('L', (42, 106)), ('L', (22, 106)), ('L', (20, 33)),
            ('L', (18, 106)), ('L', (-2, 106)), ('L', (-4, 20)), ('Z',)]
    s = garment_shape(m.d(body), pid)
    s += f'<path d="{m.d(body)}" fill="none" stroke="#E3B23C" stroke-opacity=".9" stroke-width="1" stroke-dasharray="3 2" transform="translate(0 0)"/>'
    # lưng quần + đỉa + cúc
    s += m.rect(-.3, 0, 40.6, 4, fill='#fff', extra='opacity=".18"')
    s += f'<path d="{m.d([("M", (0, 4)), ("L", (40, 4))])}" stroke="#E3B23C" stroke-width="1" stroke-dasharray="3 2"/>'
    for xx in (4, 13, 27, 36):
        s += m.rect(xx, -.4, 1.4, 5.2, fill=fab(pid), extra='stroke="#1C3553" stroke-opacity=".4"')
    cx, cy = m.P(20.8, 2)
    s += f'<circle cx="{f(cx)}" cy="{f(cy)}" r="{f(1.2 * m.s)}" fill="#C9A77C" stroke="#8A6A45"/>'
    # túi trước + đường khóa
    for sd in (0, 1):
        pts = [('M', (4, 4)), ('Q', (10, 12), (14, 11))] if not sd else [('M', (36, 4)), ('Q', (30, 12), (26, 11))]
        s += f'<path d="{m.d(pts)}" fill="none" stroke="#E3B23C" stroke-width="1.1" stroke-dasharray="3 2"/>'
    s += f'<path d="{m.d([("M", (20, 4)), ("L", (20, 22)), ("Q", (20, 26), (23, 24)), ("L", (23, 4))])}" fill="none" stroke="#E3B23C" stroke-width="1.1" stroke-dasharray="3 2"/>'
    # đầu gối bạc màu
    for kx in (8, 32):
        cx, cy = m.P(kx, 64)
        s += f'<ellipse cx="{f(cx)}" cy="{f(cy)}" rx="{f(6 * m.s)}" ry="{f(5 * m.s)}" fill="#fff" opacity=".22"/>'
    if cuts:
        s += cutline(m.d([('M', (-4, 30)), ('L', (44, 30))]))
        s += cutline(m.d([('M', (-4.2, 30)), ('L', (-2, 106))]))
        s += cutline(m.d([('M', (20, 33)), ('L', (18, 106))]))
        s += cutline(m.d([('M', (20, 33)), ('L', (22, 106))]))
        s += cutline(m.d([('M', (44.2, 30)), ('L', (42, 106))]))
        s += cutline(m.d([('M', (-2.2, 102)), ('L', (18.2, 102))]))
        s += cutline(m.d([('M', (21.8, 102)), ('L', (42.2, 102))]))
    return s


def bath_towel(m, w=70, h=140, pid='terry-peach', band='#C8643B', cuts=True):
    s = m.rect(0, 0, w, h, fill='#23313A', extra='opacity=".12" transform="translate(3 5)"')
    s += m.rect(0, 0, w, h, fill=fab(pid))
    for y0 in (4, h - 10):
        s += m.rect(0, y0, w, 6, fill=band, extra='opacity=".85"')
        for k in range(0, int(w), 3):
            s += m.rect(k, y0 + 1.5, 1.5, 3, fill='#fff', extra='opacity=".35"')
    s += m.rect(0, 0, w, h, extra='fill="none" stroke="#23313A" stroke-opacity=".4"')
    # mép biên dệt 2 bên
    s += m.rect(0, 0, 1.2, h, fill='#fff', extra='opacity=".35"') + m.rect(w - 1.2, 0, 1.2, h, fill='#fff', extra='opacity=".35"')
    if cuts:
        s += cutline(m.d([('M', (-2, 11)), ('L', (w + 2, 11))])) + cutline(m.d([('M', (-2, h - 11)), ('L', (w + 2, h - 11))]))
        s += cutline(m.d([('M', (2, 11)), ('L', (2, h - 11))])) + cutline(m.d([('M', (w - 2, 11)), ('L', (w - 2, h - 11))]))
    return s


# ---------------------------------------------------------------- dụng cụ (khung 110 × 70)

def tool_art(name):
    W, H = 110, 70
    b = ''
    if name == 'keo':
        b = big_scissors(52, 36, s_=.95, rot=-12)
    elif name == 'keobam':
        b = ('<path d="M20 50 L78 30 L86 34 L26 56 Z" fill="#C7CED2" stroke="#6F7F88"/><path d="M20 40 L78 30 L86 26 L24 34 Z" fill="#DDE2E5" stroke="#6F7F88"/>'
             '<path d="M20 34 Q6 44 20 56" fill="none" stroke="#D96F43" stroke-width="7" stroke-linecap="round"/>')
    elif name == 'daoxoay':
        b = rect(6, 40, 98, 26, fill='#4F9A57', rx=3) + ''.join(line(6 + k * 10, 40, 6 + k * 10, 66, extra='stroke="#fff" stroke-opacity=".45" stroke-width=".8"') for k in range(1, 10))
        b += line(6, 53, 104, 53, extra='stroke="#fff" stroke-opacity=".45" stroke-width=".8"')
        b += '<g transform="rotate(-30 56 30)"><rect x="26" y="22" width="58" height="14" rx="7" fill="#E3B23C"/><rect x="28" y="24" width="30" height="4" rx="2" fill="#fff" opacity=".4"/></g>'
        b += '<circle cx="36" cy="44" r="14" fill="#DDE2E5" stroke="#8A9499" stroke-width="1.4"/><circle cx="36" cy="44" r="3" fill="#6F7F88"/>'
    elif name == 'thuoc':
        b = '<g transform="rotate(-8 55 35)">' + rect(8, 18, 94, 34, fill='#E9F0F8', rx=2, extra='opacity=".9" stroke="#8A9499"')
        for k in range(0, 95, 6):
            b += line(8 + k, 18, 8 + k, 18 + (9 if k % 30 == 0 else 5), extra='stroke="#23313A" stroke-width=".8"')
            b += line(8 + k, 18, 8 + k, 52, extra='stroke="#2B6CB0" stroke-opacity=".2" stroke-width=".6"')
        for k in range(0, 35, 6):
            b += line(8, 18 + k, 102, 18 + k, extra='stroke="#2B6CB0" stroke-opacity=".2" stroke-width=".6"')
        b += line(8, 35, 102, 35, extra='stroke="#D6336C" stroke-width="1.1"') + '</g>'
    elif name == 'thuocday':
        b = '<circle cx="34" cy="38" r="24" fill="#E3B23C"/><circle cx="34" cy="38" r="16" fill="#F2D78E"/><circle cx="34" cy="38" r="6" fill="#C9951C"/>'
        b += '<path d="M56 30 L104 22 L106 32 L58 42 Z" fill="#F2D78E" stroke="#9C7212" stroke-width=".8"/>'
        b += ''.join(line(60 + k * 5, 29 - k * .8, 60 + k * 5, 33 - k * .8, extra='stroke="#6B4B08" stroke-width=".8"') for k in range(9))
    elif name == 'phan':
        b = '<path d="M14 54 L40 14 L66 54 Z" fill="#9DB7D5" stroke="#2B4C74" stroke-width="1.2" stroke-linejoin="round"/>'
        b += '<g transform="rotate(-35 80 36)"><rect x="56" y="30" width="50" height="11" rx="3" fill="#7C4DFF"/><path d="M106 30 L114 35.5 L106 41 Z" fill="#E3D9FF"/><rect x="58" y="31" width="14" height="9" rx="2" fill="#5B35D5"/></g>'
    elif name == 'kep':
        b = clip(24, 36, rot=-15) + clip(44, 32, rot=8, c='#D96F43') + clip(64, 38, rot=-4, c='#7FA37A')
        b += pin(78, 22, rot=30) + pin(84, 34, rot=20, head='#3E74B8') + pin(80, 48, rot=8, head='#E3B23C')
    elif name == 'maymay':
        b = ('<rect x="6" y="54" width="98" height="10" rx="3" fill="#C9CDCF"/>'
             '<path d="M16 54 V22 Q16 12 26 12 H86 Q96 12 96 22 V34 H80 V26 H34 V54 Z" fill="#F8F2E6" stroke="#8A9499" stroke-width="1.4"/>'
             '<rect x="80" y="34" width="14" height="20" fill="#F8F2E6" stroke="#8A9499" stroke-width="1.4"/>'
             '<rect x="84" y="40" width="6" height="14" fill="#6F7F88"/><line x1="87" y1="54" x2="87" y2="60" stroke="#23313A" stroke-width="1.2"/>'
             '<circle cx="24" cy="30" r="6" fill="#D96F43"/><rect x="40" y="16" width="30" height="6" rx="3" fill="#9DB7D5"/>'
             '<rect x="54" y="4" width="8" height="10" fill="#2B4C74"/>')
    elif name == 'kim':
        for i, (sz, x) in enumerate((('80/12', 22), ('90/14', 54), ('100/16', 86))):
            b += f'<path d="M{x} 10 v8 h3 v-8 z" fill="#8A9499"/><path d="M{x + 1.5} 18 L{x + 1.5} 52" stroke="#8A9499" stroke-width="{1.4 + i * .5}"/><path d="M{x + 1.5} 52 l0 5" stroke="#8A9499" stroke-width="1"/>'
    elif name == 'chi':
        b = spool(30, 36, '#2B4C74', 1.4) + spool(58, 36, '#E8D5B5', 1.4) + spool(86, 36, '#D96F43', 1.4)
    elif name == 'banui':
        b = ('<path d="M14 50 Q20 22 60 20 H96 V50 Z" fill="#9DB7D5" stroke="#2B4C74" stroke-width="1.4"/>'
             '<path d="M10 50 H100 V56 H10 Z" fill="#C7CED2" stroke="#8A9499"/>'
             '<path d="M58 20 Q60 6 76 6 H92 Q98 6 98 14 V20" fill="none" stroke="#2B4C74" stroke-width="6" stroke-linecap="round"/>'
             '<circle cx="46" cy="38" r="5" fill="#D96F43"/>')
    elif name == 'que':
        b = '<g transform="rotate(-20 55 35)"><rect x="10" y="30" width="90" height="7" rx="3.5" fill="#C9A77C"/><path d="M100 30 L108 33.5 L100 37 Z" fill="#C9A77C"/></g>'
        b += '<g transform="rotate(10 55 45)"><path d="M14 44 H80 L96 48 L80 52 H14 Z" fill="#E3B23C" stroke="#9C7212"/></g>'
    elif name == 'bia':
        b = rect(12, 10, 70, 52, fill='#D8B98F', rx=2, extra='stroke="#8A6A45"') + rect(30, 20, 70, 44, fill='#E9CFA6', rx=2, extra='stroke="#8A6A45"')
        b += txt(65, 48, '32 × 32', 't-dim t-mid', extra='style="font-size:15px"')
    elif name == 'kimtay':
        b = '<path d="M14 56 L92 16" stroke="#8A9499" stroke-width="2" stroke-linecap="round"/><ellipse cx="89" cy="17.5" rx="1.2" ry="3" transform="rotate(63 89 17.5)" fill="#fff" stroke="#8A9499"/>'
        b += '<path d="M90 17 C 104 30 70 36 86 52 C 92 58 76 64 66 58" fill="none" stroke="#D96F43" stroke-width="1.6"/>'
        b += '<circle cx="30" cy="30" r="14" fill="#E3B23C" opacity=".9"/><circle cx="30" cy="30" r="9" fill="#F2D78E"/>'
    elif name == 'keoraxang':
        b = big_scissors(52, 36, s_=.95, rot=-12, handle='#7FA37A')
        b += ''.join(f'<path d="M{58 + k * 6} {28 - k * 1.3} l3 -3 l3 3" fill="none" stroke="#6F7F88" stroke-width="1"/>' for k in range(6))
    return svg(W, H, b)


# ---------------------------------------------------------------- trợ giúp vẽ bước may

def clips_around(x, y, w, h, n_side=1, c='#E3B23C'):
    s = ''
    pts = [(x, y), (x + w, y), (x, y + h), (x + w, y + h)]
    for k in range(1, n_side + 1):
        t = k / (n_side + 1)
        pts += [(x + w * t, y), (x + w * t, y + h), (x, y + h * t), (x + w, y + h * t)]
    for px, py in pts:
        rot = 0 if (abs(py - y) < 1e-6 or abs(py - y - h) < 1e-6) else 90
        s += clip(px, py, rot=rot, c=c)
    return s


def corner_clips(x, y, w, h, inset, gap=2.5):
    """4 tam giác cắt góc (gạch) — inset = khoảng đường may (px)"""
    s = ''
    for cx, cy, sx, sy in ((x, y, 1, 1), (x + w, y, -1, 1), (x, y + h, 1, -1), (x + w, y + h, -1, -1)):
        a = inset - gap
        tri = [(cx, cy), (cx + sx * (inset + a), cy), (cx, cy + sy * (inset + a))]
        s += poly(tri, cls='f-discard')
        s += line(cx + sx * (inset + a), cy, cx, cy + sy * (inset + a), extra='stroke="#C4592F" stroke-width="1.6"')
    return s


def topstitch_rect(x, y, w, h, inset, cls='s-top'):
    return rect(x + inset, y + inset, w - 2 * inset, h - 2 * inset, cls=cls)


def iron(x, y, s_=1.0, rot=0):
    b = ('<path d="M-30 12 Q-26 -8 2 -10 H26 V12 Z" fill="#9DB7D5" stroke="#2B4C74" stroke-width="1.3"/>'
         '<path d="M-33 12 H29 V16 H-33 Z" fill="#C7CED2" stroke="#8A9499" stroke-width=".8"/>'
         '<path d="M0 -10 Q2 -20 12 -20 H22 Q26 -20 26 -15 V-10" fill="none" stroke="#2B4C74" stroke-width="4" stroke-linecap="round"/>')
    return g(b, tr=f'translate({f(x)} {f(y)}) rotate({rot}) scale({s_})')


def stick(x1, y1, x2, y2):
    return line(x1, y1, x2, y2, extra='stroke="#C9A77C" stroke-width="6" stroke-linecap="round"') + line(x1, y1, x2, y2, extra='stroke="#fff" stroke-opacity=".35" stroke-width="1.5" stroke-linecap="round"')
