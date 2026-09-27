#!/usr/bin/env python3
"""Sinh <defs> dùng chung: họa tiết vải (pattern) + đầu mũi tên. Mọi pattern dùng userSpaceOnUse
để render.py có thể đổi thành vector (Chromium mặc định raster hóa pattern khi in PDF)."""


def _p(pid, w, h, body):
    return f'<pattern id="p-{pid}" width="{w}" height="{h}" patternUnits="userSpaceOnUse">{body}</pattern>'


def gingham(pid, c, base='#FFFFFF', t=12, op=.42):
    h = t / 2
    return _p(pid, t, t, f'<rect width="{t}" height="{t}" fill="{base}"/><rect width="{h}" height="{t}" fill="{c}" fill-opacity="{op}"/>'
                         f'<rect width="{t}" height="{h}" fill="{c}" fill-opacity="{op}"/>')


def plaid(pid, base, c1, c2, line='#FFFFFF', t=28):
    b = (f'<rect width="{t}" height="{t}" fill="{base}"/>'
         f'<rect x="0" width="10" height="{t}" fill="{c1}" fill-opacity=".55"/><rect y="0" width="{t}" height="10" fill="{c1}" fill-opacity=".55"/>'
         f'<rect x="15" width="3" height="{t}" fill="{c2}" fill-opacity=".7"/><rect y="15" width="{t}" height="3" fill="{c2}" fill-opacity=".7"/>'
         f'<rect x="22" width="1.2" height="{t}" fill="{line}" fill-opacity=".7"/><rect y="22" width="{t}" height="1.2" fill="{line}" fill-opacity=".7"/>')
    return _p(pid, t, t, b)


def denim(pid, base, hi='#FFFFFF', op=.16, t=12):
    lines = '<path d="' + ''.join(f'M{x} {t} L{x + t} 0 ' for x in (-t, -t / 2, 0, t / 2)) + f'" stroke="{hi}" stroke-opacity="{op}" stroke-width="1.3"/>'
    speck = f'<rect x="2" y="7" width="1.2" height="1.2" fill="{hi}" fill-opacity="{op * 1.4:.2f}"/><rect x="8" y="2" width="1" height="1" fill="#000" fill-opacity=".08"/>'
    return _p(pid, t, t, f'<rect width="{t}" height="{t}" fill="{base}"/>{lines}{speck}')


def terry(pid, base, dark, t=12):
    # 1 path gồm nhiều vòng nhỏ (ít đối tượng hơn -> PDF nhẹ hơn)
    pts = [(3, 3), (9, 3), (6, 8.5), (0, 8.5), (12, 8.5), (3, 14), (9, 14), (3, -3), (9, -3)]
    d = ''.join(f'M{x - 1.7} {y} a1.7 1.7 0 1 0 3.4 0 a1.7 1.7 0 1 0 -3.4 0 ' for x, y in pts)
    return _p(pid, t, 11, f'<rect width="{t}" height="11" fill="{base}"/><path d="{d}" fill="none" stroke="{dark}" stroke-opacity=".28" stroke-width=".9"/>')


def jersey(pid, base, dark, t=16):
    d = ''.join(f'M{x + .6} {y + .5} L{x + 2} {y + 3.2} L{x + 3.4} {y + .5} ' for x in (0, 4, 8, 12) for y in (0, 4, 8, 12))
    return _p(pid, t, t, f'<rect width="{t}" height="{t}" fill="{base}"/><path d="{d}" fill="none" stroke="{dark}" stroke-opacity=".2" stroke-width=".8"/>')


def linen(pid, base, dark, t=24):
    b = f'<rect width="{t}" height="{t}" fill="{base}"/>'
    for y, o, w in ((2, .16, .9), (6.5, .09, .6), (10, .2, 1.1), (15, .1, .6), (19.5, .17, .8)):
        b += f'<rect x="0" y="{y}" width="{t}" height="{w}" fill="{dark}" fill-opacity="{o}"/>'
    for x, o, w in ((4, .1, .7), (11, .16, .9), (17.5, .08, .6), (21, .13, .7)):
        b += f'<rect x="{x}" y="0" width="{w}" height="{t}" fill="{dark}" fill-opacity="{o}"/>'
    b += f'<rect x="6" y="9.7" width="7" height="1.6" rx=".8" fill="{dark}" fill-opacity=".14"/>'
    return _p(pid, t, t, b)


def fleece(pid, base, hi, t=12):
    pts = [(2, 3, 1.6), (8, 1.5, 1.2), (5, 8, 1.8), (10.5, 9, 1.3), (1, 10.5, 1)]
    d = ''.join(f'<circle cx="{x}" cy="{y}" r="{r}" fill="{hi}" fill-opacity=".22"/>' for x, y, r in pts)
    return _p(pid, t, t, f'<rect width="{t}" height="{t}" fill="{base}"/>{d}')


def micro(pid, base, dark, t=12):
    d = ''.join(f'M{x - .7} {y} a.7 .7 0 1 0 1.4 0 a.7 .7 0 1 0 -1.4 0 ' for x in (1.5, 7.5) for y in (1.5, 7.5)) + ''.join(f'M{x - .7} {y} a.7 .7 0 1 0 1.4 0 a.7 .7 0 1 0 -1.4 0 ' for x in (4.5, 10.5) for y in (4.5, 10.5))
    return _p(pid, t, t, f'<rect width="{t}" height="{t}" fill="{base}"/><path d="{d}" fill="{dark}" fill-opacity=".18"/>')


def floral(pid, base, petal, center='#F4D58D', leaf='#7FA37A', t=26):
    def fl(cx, cy, r, pc):
        s = ''
        for k in range(5):
            import math
            a = math.radians(k * 72 - 90)
            s += f'<circle cx="{cx + math.cos(a) * r:.2f}" cy="{cy + math.sin(a) * r:.2f}" r="{r * .72:.2f}" fill="{pc}"/>'
        return s + f'<circle cx="{cx}" cy="{cy}" r="{r * .55:.2f}" fill="{center}"/>'
    b = f'<rect width="{t}" height="{t}" fill="{base}"/>'
    b += f'<ellipse cx="11" cy="12.5" rx="2.6" ry="1.1" fill="{leaf}" transform="rotate(35 11 12.5)"/>'
    b += fl(7, 7, 2.6, petal) + fl(19.5, 19, 2.1, petal)
    b += f'<circle cx="20" cy="5" r="1" fill="{leaf}"/><circle cx="4" cy="20" r="1" fill="{center}"/>'
    return _p(pid, t, t, b)


def dots(pid, base, c, t=12, r=2):
    return _p(pid, t, t, f'<rect width="{t}" height="{t}" fill="{base}"/><circle cx="3" cy="3" r="{r}" fill="{c}"/><circle cx="9" cy="9" r="{r}" fill="{c}"/>')


def stripes(pid, base, c, t=10, w=4, vertical=True):
    r = f'<rect x="0" width="{w}" height="{t}" fill="{c}"/>' if vertical else f'<rect y="0" width="{t}" height="{w}" fill="{c}"/>'
    return _p(pid, t, t, f'<rect width="{t}" height="{t}" fill="{base}"/>{r}')


def purl(pid, base, dark, t=8):
    b = f'<rect width="{t}" height="{t}" fill="{base}"/>'
    b += f'<path d="M0 2 q1 -1.6 2 0 q1 1.6 2 0 q1 -1.6 2 0 q1 1.6 2 0" fill="none" stroke="{dark}" stroke-opacity=".3" stroke-width=".9"/>'
    b += f'<path d="M0 6 q1 1.6 2 0 q1 -1.6 2 0 q1 1.6 2 0 q1 -1.6 2 0" fill="none" stroke="{dark}" stroke-opacity=".3" stroke-width=".9"/>'
    return _p(pid, t, t, b)


def overlay(pid, kind, c='#FFFFFF', op=.55):
    if kind == 'dots':
        return _p(pid, 10, 10, f'<circle cx="2.5" cy="2.5" r="1.4" fill="{c}" fill-opacity="{op}"/><circle cx="7.5" cy="7.5" r="1.4" fill="{c}" fill-opacity="{op}"/>')
    if kind == 'stripe':
        return _p(pid, 8, 8, f'<rect width="2.4" height="8" fill="{c}" fill-opacity="{op}"/>')
    if kind == 'check':
        return _p(pid, 12, 12, f'<rect width="6" height="12" fill="{c}" fill-opacity="{op * .6:.2f}"/><rect width="12" height="6" fill="{c}" fill-opacity="{op * .6:.2f}"/>')
    if kind == 'floral':
        import math
        fl = ''.join(f'<circle cx="{6 + 2.2 * math.cos(math.radians(k * 72)):.2f}" cy="{6 + 2.2 * math.sin(math.radians(k * 72)):.2f}" r="1.5" fill="{c}" fill-opacity="{op}"/>' for k in range(5))
        return _p(pid, 16, 16, fl + f'<circle cx="13" cy="13" r="1" fill="{c}" fill-opacity="{op}"/>')
    if kind == 'grid':
        return _p(pid, 10, 10, f'<path d="M0 .5 H10 M.5 0 V10" stroke="{c}" stroke-opacity="{op}" stroke-width="1"/>')


def hatch(pid, c='#9AA5AB', t=7):
    return _p(pid, t, t, f'<rect width="{t}" height="{t}" fill="#F3F1EC"/><path d="M-1 {t + 1} L{t + 1} -1 M-1 1 L1 -1 M{t - 1} {t + 1} L{t + 1} {t - 1}" stroke="{c}" stroke-width="1"/>')


FABRICS = [
    gingham('gingham-blue', '#3E74B8'), gingham('gingham-red', '#C2452D'), gingham('gingham-green', '#4F9A57'),
    gingham('gingham-navy', '#22385C', op=.38), gingham('gingham-terra', '#C8643B', op=.4), gingham('gingham-mint', '#3C9D8E', op=.35),
    gingham('gingham-pink', '#E07F8A', op=.38), gingham('gingham-olive', '#4E6B3A', op=.36), gingham('gingham-sky', '#6FA2D6', op=.4),
    plaid('flannel-red', '#B8392E', '#3A2A2A', '#F2C14E'), plaid('flannel-blue', '#2B4C74', '#16263D', '#E3B23C'),
    plaid('flannel-green', '#4E6B3A', '#23331A', '#C9DDA0'), plaid('flannel-terra', '#C8643B', '#6B4331', '#E8D5B5'),
    denim('denim', '#3B5F8A'), denim('denim-dark', '#22385C', op=.14), denim('denim-light', '#9DB4CF', hi='#FFFFFF', op=.35),
    denim('chambray', '#7C9CC0', op=.28),
    terry('terry-white', '#FAF8F2', '#8C8A80'), terry('terry-sage', '#BFD6BA', '#4F7349'), terry('terry-peach', '#F4C9B0', '#A8482A'),
    terry('terry-sky', '#BCD4EC', '#2B4C74'), terry('terry-mustard', '#F2D78E', '#9C7212'), terry('terry-grey', '#C9CDCF', '#4B5A63'),
    terry('terry-mint', '#A8DCD1', '#2F7D70'), terry('terry-brown', '#8A6A55', '#3B2A20'),
    jersey('jersey-heather', '#B9BEC2', '#23313A'), jersey('jersey-navy', '#2B3F5E', '#000000'), jersey('jersey-pink', '#F2A7A0', '#8A3A33'),
    jersey('jersey-white', '#F7F5F0', '#6F7F88'), jersey('jersey-mustard', '#E3B23C', '#6B4B08'), jersey('jersey-teal', '#3C9D8E', '#12423B'),
    jersey('jersey-olive', '#8DB255', '#2C3E14'), jersey('jersey-sky', '#A9CBEA', '#23466E'), jersey('jersey-terra', '#D96F43', '#5A2410'),
    linen('linen', '#E8DCC6', '#8C7A5C'), linen('linen-sage', '#C9D8C0', '#4F7349'), linen('linen-white', '#F6F1E6', '#9C8F76'),
    fleece('fleece-green', '#5E8F63', '#FFFFFF'), fleece('fleece-grey', '#8E979C', '#FFFFFF'),
    micro('micro-yellow', '#F2C94C', '#6B4B08'), micro('micro-blue', '#5B8FD0', '#0D2A52'),
    floral('floral-cream', '#FAF3E3', '#E89A6B'), floral('floral-mint', '#CFEBE1', '#F2A7A0', center='#F4D58D'),
    floral('floral-navy', '#22385C', '#F4EEE1', center='#E3B23C', leaf='#8DB255'),
    dots('dots-mustard', '#E3B23C', '#FFFFFF'), dots('dots-terra', '#FCEEE6', '#D96F43', r=1.6), dots('dots-navy', '#22385C', '#F4EEE1', r=1.5),
    stripes('stripe-navy', '#FFFFFF', '#22385C', t=10, w=3), stripes('stripe-red', '#FFFFFF', '#C2452D', t=8, w=2.4),
    stripes('stripe-sage', '#F5F1E3', '#7FA37A', t=12, w=5), stripes('stripe-denim', '#E9F0F8', '#3E6A9E', t=9, w=2),
    stripes('stripe-terra-h', '#FBEDE5', '#C8643B', t=10, w=3.4, vertical=False),
    purl('purl-teal', '#6DB5A9', '#12423B'), denim('denim-back', '#C9D6E6', hi='#3B5F8A', op=.35),
    overlay('ov-dots', 'dots'), overlay('ov-stripe', 'stripe'), overlay('ov-check', 'check'), overlay('ov-floral', 'floral'), overlay('ov-grid', 'grid'),
    overlay('ov-dots-d', 'dots', '#23313A', .35), overlay('ov-stripe-d', 'stripe', '#23313A', .25), overlay('ov-floral-d', 'floral', '#23313A', .3),
    hatch('hatch'),
]

MARKERS = '''
<marker id="arr" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse"><path d="M0 1.2 L9.4 5 L0 8.8 z" fill="#2B6CB0"/></marker>
<marker id="arr-flow" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="5.5" markerHeight="5.5" orient="auto-start-reverse"><path d="M0 0 L10 5 L0 10 z" fill="#2B4C74"/></marker>
<marker id="arr-terra" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="5.5" markerHeight="5.5" orient="auto-start-reverse"><path d="M0 0 L10 5 L0 10 z" fill="#C4592F"/></marker>
<marker id="arr-grain" viewBox="0 0 10 10" refX="8.5" refY="5" markerWidth="8" markerHeight="8" orient="auto-start-reverse"><path d="M0 1.5 L9 5 L0 8.5" fill="none" stroke="#23313A" stroke-width="1.6"/></marker>
'''


def defs_svg():
    return ('<svg width="0" height="0" style="position:absolute;width:0;height:0" aria-hidden="true"><defs>'
            + MARKERS + ''.join(FABRICS) + '</defs></svg>')


FABRIC_IDS = [f.split('id="p-')[1].split('"')[0] for f in FABRICS]

if __name__ == '__main__':
    print(len(FABRIC_IDS), 'patterns')
