"""Khối HTML sinh từ dữ liệu (bảng vải, bảng màu, bảng máy may...). Mỗi hàm nhận ctx, trả về HTML."""
from html import escape
from art import vn, dims  # noqa


def level(n, total=4):
    return '<span class="level">' + ''.join(f'<i class="{"on" if i < n else ""}"></i>' for i in range(total)) + '</span>'


def rating(n, total=5):
    return '<span class="dots">' + ''.join(f'<i class="{"on" if i < n else ""}"></i>' for i in range(total)) + '</span>'


def gallery(ctx):
    import figs
    P = ctx.spec['products']
    fabn = {f['id']: f['name'] for f in ctx.spec['fabrics']}
    lv = {1: 'Rất dễ', 2: 'Dễ', 3: 'Vừa', 4: 'Khó'}
    out = ''
    for i, k in enumerate(['m1', 'm2', 'm3', 'm4', 'm5', 'm6'], 1):
        p = P[k]
        size = dims(*ctx.d[k]['fin']) + ' cm' if k != 'm6' else 'Theo bàn lau'
        art = getattr(figs, f'prod_{k}')(ctx)
        out += f'''<div class="gcard">
  <div class="gart">{art}<span class="gno">Mẫu {i}</span></div>
  <div class="gbody"><h3>{escape(p['name'])}</h3>
  <div class="guse">{escape(p['use'])}</div>
  <div class="gmeta"><span><b>Thành phẩm</b> {size}</span><span><b>Độ khó</b> {level(p['level'])} {lv[p['level']]}</span>
  <span><b>Thời gian</b> {escape(p['time'])}</span><span><b>Vắt sổ</b> {escape(p['overlock'].split(' (')[0])}</span></div></div>
</div>'''
    return f'<div class="gallery">{out}</div>'


def layout_legend(ctx):
    import figs
    P = ctx.spec['products']
    items = ''.join(f'<span><i class="sw" style="background:{figs.PROD_COL[k]};opacity:.75"></i><b>M{k[1]}</b> {escape(P[k]["short"])}</span>' for k in ['m1', 'm2', 'm3', 'm4', 'm5', 'm6'])
    return f'<div class="legend laylg">{items}</div>'


def fabric_table(ctx):
    import figs
    rows = ''
    fray_col = {0: '#46693F', 1: '#46693F', 2: '#9C7212', 3: '#A8482A'}
    for fb in ctx.spec['fabrics']:
        sw = figs.swatch_svg(figs.SWATCH[fb['swatch']], fray=fb['fray_level'])
        rows += (f'<tr><td class="swc">{sw}</td><td><b>{escape(fb["name"])}</b><div class="from">{escape(fb["from"])}</div></td>'
                 f'<td class="c">{rating(fb["absorb"])}</td><td class="c">{rating(fb["durable"])}</td><td class="c">{rating(fb["dry"])}</td>'
                 f'<td style="color:{fray_col[fb["fray_level"]]};font-weight:700">{escape(fb["fray"][0].upper() + fb["fray"][1:])}</td>'
                 f'<td>{escape(fb["best"])}<div class="from">{escape(fb["note"])}</div></td></tr>')
    return (f'<table class="tbl ftbl"><tr><th style="width:15mm">Mẫu vải</th><th style="width:41mm">Loại vải · lấy từ</th><th class="c">Thấm</th><th class="c">Bền</th>'
            f'<th class="c">Khô nhanh</th><th style="width:19mm">Tưa sợi</th><th>Dùng tốt cho</th></tr>{rows}</table>')


def avoid_list(ctx):
    lis = ''.join(f'<li><b>{escape(a["name"])}</b> — {escape(a["why"])}</li>' for a in ctx.spec['avoid'])
    return f'<ul class="no">{lis}</ul>'


def palettes(ctx):
    import figs
    out = ''
    for i, P in enumerate(ctx.spec['palettes'], 1):
        sw = ''.join(f'<span><i class="sw" style="background:{c}"></i>{escape(n)}</span>' for n, c in P['colors'])
        out += f'''<div class="pal"><div class="palart">{figs.palette_card_art(ctx, P["id"])}</div>
<div class="palh"><b>{i}. {escape(P["name"])}</b><em>{escape(P["scheme"])}</em></div>
<div class="palsw">{sw}</div><div class="palsrc"><b>Vải gợi ý:</b> {escape(P["source"])}</div></div>'''
    return f'<div class="pals">{out}</div>'


def color_codes(ctx):
    rows = ''
    for c in ctx.spec['color_codes']:
        rows += (f'<tr><td><span class="cc" style="background:{c["hex"]}"></span><b>{escape(c["color"])}</b></td>'
                 f'<td><b>{escape(c["zone"])}</b></td><td>{escape(c["items"])}</td></tr>')
    return f'<table class="tbl"><tr><th style="width:30mm">Màu mã</th><th style="width:40mm">Khu vực</th><th>Dùng lau</th></tr>{rows}</table>'


TOOLS = [
    ('keo', 'Kéo cắt vải', 'Chỉ dùng để cắt vải cho lưỡi luôn bén.', 'Bắt buộc'),
    ('thuoc', 'Thước kẻ trong 60 cm', 'Có lưới ô: kẻ song song, vuông góc nhanh.', 'Bắt buộc'),
    ('thuocday', 'Thước dây', 'Đo mảnh vải, đo bàn lau nhà.', 'Bắt buộc'),
    ('phan', 'Phấn may / bút bay màu', 'Vẽ đường cắt, đánh dấu khe lộn.', 'Bắt buộc'),
    ('kep', 'Kẹp vải & ghim', 'Kẹp tốt hơn ghim cho khăn bông, jeans, nhiều lớp.', 'Bắt buộc'),
    ('maymay', 'Máy may gia đình', 'Chỉ cần mũi thẳng và zigzag.', 'Bắt buộc'),
    ('kim', 'Kim máy các cỡ', '80/12 vải mỏng · 90/14 khăn bông · 100/16 jeans.', 'Bắt buộc'),
    ('chi', 'Chỉ polyester 40/2', 'Bền, chịu giặt nóng. Chọn màu theo trang Phối màu.', 'Bắt buộc'),
    ('banui', 'Bàn ủi + bình xịt', 'Ủi phẳng, ủi mép — quyết định khăn đẹp hay không.', 'Bắt buộc'),
    ('bia', 'Bìa cứng làm rập', 'Rập đúng cỡ cắt: vẽ nhanh, miếng nào cũng bằng nhau.', 'Nên có'),
    ('que', 'Que đẩy góc', 'Đũa tre đầu tù hoặc dụng cụ đẩy góc bằng nhựa.', 'Nên có'),
    ('daoxoay', 'Dao cắt xoay + thảm cắt', 'Cắt nhanh, thẳng, nhiều lớp cùng lúc.', 'Tùy chọn'),
    ('keobam', 'Kéo bấm chỉ', 'Cắt chỉ thừa sát mặt vải.', 'Nên có'),
    ('keoraxang', 'Kéo răng cưa', 'Cắt mép giảm tưa cho vải ít tưa.', 'Tùy chọn'),
    ('kimtay', 'Kim khâu tay + đê', 'Khâu kín khe lộn, khâu góc bo viền.', 'Nên có'),
]


def tools_grid(ctx):
    from art import tool_art
    cls = {'Bắt buộc': 'terra', 'Nên có': 'denim', 'Tùy chọn': 'sage'}
    out = ''.join(f'<div class="tl"><div class="tla">{tool_art(k)}</div><div><b>{escape(n)}</b><span class="chip {cls[t]}">{t}</span><p>{escape(d)}</p></div></div>' for k, n, d, t in TOOLS)
    return f'<div class="tools">{out}</div>'


def machine_table(ctx):
    rows = ''.join(f'<tr><td><b>{escape(m["job"])}</b></td><td>{escape(m["stitch"])}</td><td class="c">{escape(m["len"])}</td><td class="c">{escape(m["wid"])}</td><td>{escape(m["needle"])}</td></tr>' for m in ctx.spec['machine'])
    return f'<table class="tbl"><tr><th>Việc</th><th>Mũi</th><th class="c">Dài mũi (mm)</th><th class="c">Rộng zigzag (mm)</th><th>Kim</th></tr>{rows}</table>'


def diag_table(ctx):
    d = ctx.d
    from art import vn
    import math
    items = [('Mẫu 1 · giẻ áo thun', d['m1']['cut']), ('Mẫu 2 · khăn lau bàn', d['m2']['cut']), ('Mẫu 3 · khăn bếp treo', d['m3']['cut']),
             ('Mẫu 4 · ô ghép', d['m4']['square']), ('Mẫu 5 · khăn lau nhà', d['m5']['cut_A']), ('Mẫu 6 · thân vỏ bàn lau', d['m6']['cut_main']),
             ('Mẫu 6 · túi vỏ bàn lau', d['m6']['cut_pocket'])]
    cells = ''.join(f'<td><b>{escape(n)}</b><br><span class="dim">cắt {dims(*sz)}</span></td>' for n, sz in items)
    vals = ''.join(f'<td class="c num" style="font-size:14px;color:var(--dim)">{vn(round(math.hypot(*sz), 1))}</td>' for n, sz in items)
    return f'<table class="tbl" style="font-size:10.2px"><tr><th colspan="{len(items)}">Đường chéo đúng của miếng cắt (±0,3 cm là đạt)</th></tr><tr>{cells}</tr><tr>{vals}</tr></table>'


def sizes_table(ctx):
    rows = ''.join(f'<tr><td>{escape(s["item"])}</td><td class="c"><b>{escape(s["range"])}</b></td></tr>' for s in ctx.spec['standard_sizes'])
    return f'<table class="tbl"><tr><th>Loại khăn</th><th class="c">Thành phẩm</th></tr>{rows}</table>'


def m2_variants(ctx):
    d = ctx.d['m2']
    use = {20: 'Giẻ rửa chén', 25: 'Khăn lau nhỏ', 30: 'Khăn lau bàn', 35: 'Khăn đa năng lớn'}
    rows = ''.join(f'<tr><td>{use.get(v["fin"][0], "")}</td><td class="c">{dims(*v["fin"])}</td><td class="c"><b>{dims(*v["cut"])}</b></td><td class="c">{vn(v["diag"])}</td></tr>' for v in d['variants'])
    return f'<table class="tbl"><tr><th>Dùng làm</th><th class="c">Thành phẩm</th><th class="c">Cắt (× 2)</th><th class="c">Chéo</th></tr>{rows}</table>'


def m4_options(ctx):
    d = ctx.d['m4']
    rows = ''.join(f'<tr><td class="c">{o["n"]} × {o["n"]}</td><td class="c">{o["count"]}</td><td class="c">{vn(o["sq_fin"])}</td><td class="c"><b>{vn(o["sq_cut"])} × {vn(o["sq_cut"])}</b></td></tr>' for o in d['options'])
    return f'<table class="tbl"><tr><th class="c">Lưới</th><th class="c">Số ô</th><th class="c">Ô TP</th><th class="c">Ô cắt</th></tr>{rows}</table>'


def yield_table(ctx):
    tg = ctx.d['yield_targets']
    head = ''.join(f'<th>M{t["pid"][1]} · {escape(t["label"])}<br><span style="font-weight:400;opacity:.85">{dims(*t["size"])}</span></th>' for t in tg)
    rows = ''
    for r in ctx.d['yields']:
        cells = ''.join(f'<td class="y">{c["n"]}</td>' if c['suitable'] else '<td class="na">–</td>' for c in r['cells'])
        rows += f'<tr><td><b>{escape(r["name"])}</b></td>{cells}</tr>'
    return f'<table class="tbl ytbl" style="font-size:10.4px"><tr><th>Món đồ</th>{head}</tr>{rows}</table>'


def _spec_bar(ctx, k, cut_txt):
    p = ctx.spec['products'][k]
    lv = {1: 'Rất dễ', 2: 'Dễ', 3: 'Vừa', 4: 'Khó'}
    fin = dims(*ctx.d[k]['fin']) + ' cm' if 'fin' in ctx.d[k] else ''
    return (f'<div class="spec" style="grid-template-columns:1.1fr 1.5fr 1fr .9fr 1fr">'
            f'<div><div class="k">Thành phẩm</div><div class="v">{fin}</div></div>'
            f'<div><div class="k">Cắt</div><div class="v">{cut_txt}</div></div>'
            f'<div><div class="k">Độ khó</div><div class="v">{level(p["level"])} {lv[p["level"]]}</div></div>'
            f'<div><div class="k">Thời gian</div><div class="v">{escape(p["time"])}</div></div>'
            f'<div><div class="k">Vắt sổ</div><div class="v">{escape(p["overlock"].split(" (")[0])}</div></div></div>')


def spec_m1(ctx): return _spec_bar(ctx, 'm1', f'{dims(*ctx.d["m1"]["cut"])} · không may')
def spec_m2(ctx): return _spec_bar(ctx, 'm2', f'2 miếng {dims(*ctx.d["m2"]["cut"])}')
def spec_m3(ctx): return _spec_bar(ctx, 'm3', f'{dims(*ctx.d["m3"]["cut"])} + quai {dims(*ctx.d["m3"]["loop"])}')
def spec_m4(ctx): return _spec_bar(ctx, 'm4', f'{ctx.d["m4"]["count"]} ô {dims(*ctx.d["m4"]["square"])} + 1 × {dims(*ctx.d["m4"]["back"])}')
def spec_m5(ctx): return _spec_bar(ctx, 'm5', f'3 lớp {dims(*ctx.d["m5"]["cut_A"])} + 4 dải bo')
def spec_m6(ctx):
    d = ctx.d['m6']
    return _spec_bar(ctx, 'm6', f'2 × {dims(*d["cut_main"])} + 2 túi {dims(*d["cut_pocket"])}').replace(f'<div class="v"></div>', f'<div class="v">{dims(*d["fin"])} cm*</div>', 1)


def m6_examples(ctx):
    rows = ''
    for e in ctx.d['m6']['examples']:
        rows += (f'<tr><td class="c">{dims(e["L"], e["W"])}</td><td class="c">{vn(e["h"])}</td><td class="c">{dims(*e["fin"])}</td>'
                 f'<td class="c"><b>{dims(*e["cut_main"])}</b></td><td class="c"><b>{dims(*e["cut_pocket"])}</b></td><td class="c">{vn(e["P"])}</td></tr>')
    return ('<table class="tbl" style="font-size:10.6px"><tr><th class="c">Bàn lau L × W</th><th class="c">Dày h</th><th class="c">Vỏ thành phẩm</th>'
            f'<th class="c">Cắt A và B (dài × rộng)</th><th class="c">Cắt 2 túi (rộng × cao)</th><th class="c">Sâu túi P</th></tr>{rows}</table>')


def trouble_table(ctx):
    rows = ''.join(f'<tr><td><b>{escape(t["p"])}</b></td><td>{escape(t["c"])}</td><td>{escape(t["f"])}</td></tr>' for t in ctx.spec['troubleshooting'])
    return f'<table class="tbl terrahead tt"><tr><th style="width:44mm">Hiện tượng</th><th style="width:48mm">Nguyên nhân</th><th>Cách sửa / phòng tránh</th></tr>{rows}</table>'


def cut_summary(ctx):
    d = ctx.d
    P = ctx.spec['products']
    rows = []
    def r(k, part, fab, qty, size, note=''):
        rows.append((k, part, fab, qty, size, note))
    r('m1', 'Giẻ', 'Thun cotton', 'tùy', dims(*d['m1']['cut']), 'không may; zigzag tùy chọn')
    r('m2', 'Lớp A', 'Cotton sơ mi, lanh', 1, dims(*d['m2']['cut']), f'khe lộn {vn(d["m2"]["opening"])} cm')
    r('m2', 'Lớp B', 'Khăn bông, thun, flannel', 1, dims(*d['m2']['cut']), f'khăn bông: khe {vn(d["m2"]["opening_thick"])} cm')
    r('m3', 'Thân khăn', 'Cotton, lanh', 1, dims(*d['m3']['cut']), f'gấp mép {vn(d["m3"]["g1"])} + {vn(d["m3"]["g2"])} cm')
    r('m3', 'Quai treo', 'Cotton mỏng', 1, dims(*d['m3']['loop']), f'gấp 4 → rộng {vn(d["m3"]["loop_quarter"])} cm')
    r('m4', 'Ô ghép', 'Cotton, lanh, flannel', d['m4']['count'], dims(*d['m4']['square']), f'ghép {d["m4"]["n"]} × {d["m4"]["n"]}')
    r('m4', 'Lớp sau', 'Khăn bông, cotton', 1, dims(*d['m4']['back']), f'khe lộn {vn(d["m4"]["opening"])} cm')
    r('m5', 'A mặt thấm', 'Khăn bông', 1, dims(*d['m5']['cut_A']), 'cắt = thành phẩm')
    r('m5', 'C lớp ruột', 'Thun cotton', 1, dims(*d['m5']['cut_C']), '')
    r('m5', 'B mặt chà', 'Jeans', d['m5']['jeans_n'], dims(*d['m5']['jeans_strip']), f'hoặc 1 × {dims(*d["m5"]["cut_B"])} kaki')
    r('m5', 'Dải bo cạnh dài', 'Thun, cotton', 2, dims(*d['m5']['bind_long']), 'rộng × dài; gấp đôi dọc')
    r('m5', 'Dải bo cạnh ngắn', 'Thun, cotton', 2, dims(*d['m5']['bind_short']), f'rộng × dài; đuôi {vn(d["m5"]["tail"])} cm')
    m6 = d['m6']
    r('m6', 'A mặt lau', 'Khăn bông, microfiber', 1, dims(*m6['cut_main']), f'dài × rộng; bàn lau {dims(m6["L"], m6["W"])}')
    r('m6', 'B lưng', 'Jeans, cotton dày', 1, dims(*m6['cut_main']), f'dài × rộng; khe {vn(m6["opening"])} cm')
    r('m6', 'Túi', 'Jeans, cotton dày', 2, dims(*m6['cut_pocket']), f'rộng × cao; gấp đôi')
    out = ''
    last = None
    for k, part, fab, qty, size, note in rows:
        span = sum(1 for x in rows if x[0] == k)
        first = k != last
        cell = f'<td rowspan="{span}" class="mk"><b>M{k[1]}</b><br>{escape(P[k]["short"])}<br><span class="dim">TP {dims(*d[k]["fin"])}</span></td>' if first else ''
        out += f'<tr class="{"first" if first else ""}">{cell}<td>{escape(part)}</td><td>{escape(fab)}</td><td class="c">{qty}</td><td class="c"><b>{size}</b></td><td class="dim">{escape(note)}</td></tr>'
        last = k
    ctx.d['_cut_rows'] = len(rows)
    return (f'<table class="tbl cutsum"><tr><th style="width:27mm">Mẫu</th><th>Chi tiết</th><th>Vải</th><th class="c">SL</th>'
            f'<th class="c">Cắt (cm)</th><th>Ghi chú</th></tr>{out}</table>')
