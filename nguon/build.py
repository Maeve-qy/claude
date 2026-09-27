#!/usr/bin/env python3
"""Ghép PDF cuối cùng: bìa cũ + Mục lục + phần hướng dẫn mới + trang Phụ lục + các trang cũ (đánh số lại)."""
import re, html, sys, json
from pathlib import Path
import pymupdf
from playwright.sync_api import sync_playwright
import render as R

ROOT = Path(__file__).resolve().parent
OLD = ROOT / 'goc' / 'Tui_day_rut_co_quai_ban_cu.pdf'
OUT = Path(sys.argv[1]) if len(sys.argv) > 1 else ROOT / 'out' / 'final.pdf'
import os
SECTIONS = os.environ['BUILD_SECTIONS'].split(',') if os.environ.get('BUILD_SECTIONS') else ['10_mo_dau', '20_chon_vai', '30_phoi_mau', '40_kich_thuoc', '50_cat_vai',
            '60_than_lot', '70_quai', '80_rap_mieng', '90_dieu_luon', '95_hoan_thien']
CANON = {
    'Phần 1': 'Hiểu mẫu túi: thành phẩm & cấu tạo', 'Phần 2': 'Chọn vải, vật liệu & dụng cụ',
    'Phần 3': 'Phối màu đẹp', 'Phần 4': 'Kích thước, rập & công thức tính', 'Phần 5': 'Đo, vẽ & cắt vải',
    'Bước 1': 'May thân ngoài (chừa khe luồn dây)', 'Bước 2': 'May góc đáy (đáy vuông)',
    'Bước 3': 'May lớp lót (chừa khe lộn)', 'Bước 4': 'May quai rộng 2 cm',
    'Bước 5': 'Gắn quai vào thân ngoài', 'Bước 6': 'Ráp miệng túi', 'Bước 7': 'Lộn túi & đóng khe lộn',
    'Bước 8': 'Ủi miệng & diễu 3 đường', 'Bước 9': 'Luồn 2 dây rút & thắt nút',
}
FONT_NUM = str(ROOT / 'fonts' / 'Nunito-800-latin.ttf')
FONT_TXT = str(ROOT / 'fonts' / 'BeVietnamPro-400-latin.ttf')


def strip_tags(s):
    s = re.sub(r'<[^>]+>', ' ', s)
    s = re.sub(r'\s+', ' ', html.unescape(s)).strip()
    return re.sub(r'\s+([?!.,:;])', r'\1', s)


def page_meta(name):
    """(badge, h1) cho từng <section class="page"> của file."""
    src = (ROOT / 'sections' / f'{name}.html').read_text(encoding='utf-8')
    parts = re.split(r'<section\b[^>]*class="[^"]*\bpage\b[^"]*"[^>]*>', src)[1:]
    out = []
    for p in parts:
        b = re.search(r'class="badge"[^>]*>(.*?)</span>', p, re.S)
        h = re.search(r'<h1[^>]*>(.*?)</h1>', p, re.S)
        out.append((strip_tags(b.group(1)) if b else '', strip_tags(h.group(1)) if h else ''))
    return out


def toc_html(entries, first_new, last_new, appendix_page):
    groups = [('Chuẩn bị', 'prep'), ('May từng bước', 'sew'), ('Hoàn thiện', 'fin')]
    rows = {g: [] for g, _ in groups}
    for e in entries:
        rows[e['group']].append(e)
    def row(e):
        cls = 'sub' if e['sub'] else ''
        badge = '' if e['sub'] else f'<span class="tb {e["kind"]}">{html.escape(e["badge"])}</span>'
        return (f'<div class="tr {cls}">{badge}<span class="tt">{html.escape(e["title"])}</span>'
                f'<span class="dots"></span><span class="tp num">{e["page"]}</span></div>')
    blocks = ''
    for g, kind in groups:
        blocks += f'<div class="tg"><div class="tgh {kind}">{g}</div>' + ''.join(row(e) for e in rows[g]) + '</div>'
    return f'''<!doctype html><html lang="vi"><head><meta charset="utf-8"><link rel="stylesheet" href="../style.css">
<style>
.tg{{ margin-bottom:2.6mm; }}
.tgh{{ font-weight:800; font-size:11px; letter-spacing:.1em; text-transform:uppercase; color:var(--green-700); margin:0 0 1.4mm; display:flex; align-items:center; gap:8px; }}
.tgh::after{{ content:""; flex:1; border-top:1.4px dashed var(--lime-500); }}
.tgh.sew{{ color:var(--pink-600); }} .tgh.sew::after{{ border-color:var(--pink-300); }}
.tgh.fin{{ color:var(--blue-600); }} .tgh.fin::after{{ border-color:#9EC0E6; }}
.tr{{ display:flex; align-items:baseline; gap:7px; padding:.8mm 0; font-size:12.4px; }}
.tr .tb{{ flex:none; width:80px; text-align:center; font-size:9.6px; font-weight:800; letter-spacing:.05em; text-transform:uppercase; color:#fff; border-radius:9px; padding:2px 0; background:var(--green-700); }}
.tr .tb.sew{{ background:var(--pink-500); }} .tr .tb.fin{{ background:var(--blue-600); }}
.tr .tt{{ font-weight:600; }}
.tr.sub{{ padding:.2mm 0 .2mm 87px; font-size:11px; color:var(--ink-2); }}
.tr.sub .tt{{ font-weight:400; }}
.tr .dots{{ flex:1; border-bottom:1.6px dotted #C9C2B1; transform:translateY(-3px); min-width:8mm; }}
.tr .tp{{ font-size:13px; color:var(--green-900); min-width:18px; text-align:right; }}
.tr.sub .tp{{ font-size:11px; font-weight:600; color:var(--ink-2); }}
.appx{{ display:flex; align-items:center; gap:4mm; }}
.appx .tb{{ background:#8A8F87; }}
.hero-mini{{ position:absolute; right:16mm; top:16mm; width:40mm; height:40mm; border-radius:50%; object-fit:cover; border:3px solid #fff; box-shadow:0 0 0 1.6px var(--lime-500); }}
</style></head><body><!--DEFS-->
<section class="page">
  <div class="runhead">Túi dây rút có quai · <b>Hướng dẫn dễ hiểu</b></div>
  <img class="hero-mini" src="../assets/photo_hero.jpg" style="object-position:50% 45%">
  <header class="ph" style="padding-right:44mm">
    <div class="kicker k-prep"><span class="badge">Mục lục</span> Đọc theo thứ tự</div>
    <h1 class="title">Mục lục <span class="script">từng bước một</span></h1>
    <p class="lead">Trang {first_new}–{last_new}: <b>phần hướng dẫn mới</b>, viết lại dễ hiểu, có sơ đồ kích thước và ảnh thật từ video. Từ trang {appendix_page}: <b>bản cũ</b> giữ lại để tham khảo — chỗ nào khác nhau, hãy làm theo phần mới.</p>
  </header>
  <div class="content" style="gap:0">
    {blocks}
    <div class="tg"><div class="tgh">Phụ lục</div>
      <div class="tr"><span class="tb" style="background:#8A8F87">Bản cũ</span><span class="tt">Bản cũ (moodboard, bảng màu, thông số máy) &amp; các điểm đã đính chính</span><span class="dots"></span><span class="tp num">{appendix_page}</span></div>
    </div>
    <div class="spacer"></div>
    <div class="cols" style="margin-top:3mm">
      <div class="note video"><div class="nt">Mẹo đọc cùng video</div><p>Mở video song song. Mỗi ảnh có nhãn <b>▶ Video 0:xx</b> — tua tới đúng giây đó để xem thao tác thật.</p></div>
      <div class="note tip"><div class="nt">Nên in ra</div><p>In <b>trang {last_new}</b> (bảng kiểm 1 trang) dán cạnh máy may; đánh dấu từng bước khi làm xong.</p></div>
    </div>
  </div>
</section></body></html>'''


def appendix_html(pmap, old_off):
    def op(k):  # số trang mới của trang cũ k
        return k + old_off
    rows = [
        ('Bề rộng quai', 'Gấp 3 theo chiều dọc, quai rộng khoảng 2,6–2,7 cm (tr. ' + str(op(13)) + ')',
         'Gấp 2 mép dài vào giữa rồi gập đôi → quai <b>rộng 2 cm, 4 lớp vải</b> (video 0:19–0:23)', pmap.get('Bước 4')),
        ('Số đường diễu ở miệng', 'Chỉ may 2 đường kênh cách nhau 2 cm (tr. ' + str(op(17)) + ')',
         '<b>3 đường</b>: ① may mí sát miệng 0,2–0,3 cm, ② cách miệng 4 cm, ③ cách miệng 6 cm (video 0:44 — "lần lượt may diễu 3 đường")', pmap.get('Bước 8')),
        ('Vị trí chân quai', 'Mốc 6 cm là tâm của chân quai (tr. ' + str(op(14)) + ')',
         '<b>Mép trong</b> chân quai chạm mốc 6 cm, quai nằm phía ngoài mốc (chiếm 6 → 8 cm tính từ tâm) (video 0:27)', pmap.get('Bước 5')),
        ('Kích thước thành phẩm', 'Đáy 20 × 8 cm, cao 19 cm; công thức ô góc "G = D/2 + s" (tr. ' + str(op(7)) + ', ' + str(op(9)) + ')',
         'Túi thật: <b>18 × 10 × 18 cm</b> (dài đáy × sâu đáy × cao). Đường may góc nằm cách mép cắt 1 cm nên sâu đáy = 2 × 5 = <b>10 cm</b>; ô góc = sâu đáy ÷ 2', pmap.get('Phần 4')),
        ('Hình minh họa AI', 'Túi dáng hộp, miệng phẳng/cứng (tr. 1, ' + ', '.join(str(op(k)) for k in (2, 5, 6)) + ', ' + str(op(21)) + '–' + str(op(23)) + ')',
         'Túi trong video là túi <b>mềm, miệng nhún bèo 4 cm</b> phía trên kênh dây. Chỉ nên tham khảo màu sắc từ các hình AI', pmap.get('Phần 1')),
    ]
    trs = ''.join(f'<tr><td><b>{a}</b></td><td>{b}</td><td>{c}</td><td class="c num">{p or ""}</td></tr>' for a, b, c, p in rows)
    useful = [('Moodboard phong cách & phối vải', op(2)), ('Bảng 6 phong cách phối màu', op(5)), ('Moodboard thành phẩm', op(6)),
              ('Bảng thông số máy may & độ chính xác', op(19)), ('Gợi ý thành phẩm theo màu', f'{op(21)}–{op(23)}'), ('Checklist bản cũ', op(24))]
    lis = ''.join(f'<li><span>{t}</span><span class="dots"></span><b class="num">tr. {p}</b></li>' for t, p in useful)
    return f'''<!doctype html><html lang="vi"><head><meta charset="utf-8"><link rel="stylesheet" href="../style.css">
<style>
.ul-use{{ list-style:none; padding:0; margin:0; }}
.ul-use li{{ display:flex; gap:6px; align-items:baseline; margin:0 0 1.3mm; }}
.ul-use .dots{{ flex:1; border-bottom:1.5px dotted #C9C2B1; transform:translateY(-3px); }}
.big-arrow{{ font:800 34px/1 'Nunito',sans-serif; color:var(--pink-500); }}
</style></head><body><!--DEFS-->
<section class="page">
  <div class="runhead">Túi dây rút có quai · <b>Phụ lục</b></div>
  <header class="ph">
    <div class="kicker"><span class="badge" style="background:#8A8F87">Phụ lục</span> Bản hướng dẫn cũ</div>
    <h1 class="title">Bản cũ phía sau <span class="script">để tham khảo</span></h1>
    <p class="lead">Các trang tiếp theo (tr. {op(2)}–{op(24)}) là bản hướng dẫn cũ, giữ nguyên để bạn tham khảo moodboard, bảng màu và thông số máy. Khi đối chiếu lại từng cảnh trong video, có vài chỗ bản cũ <b>chưa khớp</b> — bảng dưới đây đã đính chính. <b>Hãy làm theo phần hướng dẫn mới.</b></p>
  </header>
  <div class="content">
    <h2>Những điểm đã đính chính</h2>
    <table class="tbl pinkhead" style="font-size:10.8px">
      <tr><th style="width:21%">Nội dung</th><th style="width:30%">Bản cũ ghi</th><th>Đúng theo video (đã kiểm tra)</th><th class="c" style="width:11%">Xem trang</th></tr>
      {trs}
    </table>
    <div class="cols al-start">
      <div class="card soft">
        <h2>Vẫn dùng tốt trong bản cũ</h2>
        <ul class="ul-use">{lis}</ul>
      </div>
      <div class="stack">
        <div class="note tip"><div class="nt">Cách dùng tài liệu</div><p>May theo <b>phần mới</b> (tr. {pmap.get('Phần 1')}–{pmap.get('_last')}). Mở bản cũ khi muốn xem thêm ý tưởng phối màu hoặc moodboard.</p></div>
        <div class="note video"><div class="nt">Đã đối chiếu video</div><p>Mọi số đo ở phần mới đều lấy từ cảnh "kích thước" (0:05) và các cảnh thao tác: thân <b>30 × 25 cm</b>, khoét góc <b>5 × 5</b>, vạch <b>5 cm + 2 cm</b>, quai <b>30 × 8</b>, mốc quai <b>6 cm</b>.</p></div>
      </div>
    </div>
    <h2>Dáng túi thật trong video (để so với hình AI của bản cũ)</h2>
    <div class="cols-3">
      <figure class="photo" style="--h:34mm"><img src="../assets/photo_hero.jpg" style="object-position:50% 40%"><span class="tc">Video 0:01</span><figcaption><b>Rút dây:</b> miệng nhún bèo.</figcaption></figure>
      <figure class="photo" style="--h:34mm"><img src="../assets/photo_mouth_detail.jpg" style="object-position:50% 50%"><span class="tc">Video 0:02</span><figcaption><b>Miệng túi:</b> may mí + 2 đường kênh.</figcaption></figure>
      <figure class="photo" style="--h:34mm"><img src="../assets/photo_done_flat.jpg" style="object-position:50% 45%"><span class="tc">Video 0:51</span><figcaption><b>Thành phẩm:</b> túi mềm, nút dây 2 bên.</figcaption></figure>
    </div>
  </div>
</section></body></html>'''


def stamp_number(page, n):
    fn = pymupdf.Font(fontfile=FONT_NUM)
    ft = pymupdf.Font(fontfile=FONT_TXT)
    s = str(n)
    wn = fn.text_length(s, fontsize=10.5)
    wd = ft.text_length('—', fontsize=8)
    gap = 5.5
    cx = page.rect.width / 2
    y = 822.5
    tw = pymupdf.TextWriter(page.rect)
    tw.append((cx - wn / 2 - gap - wd, y - 0.5), '—', font=ft, fontsize=8)
    tw.append((cx + wn / 2 + gap, y - 0.5), '—', font=ft, fontsize=8)
    tw.write_text(page, color=(0x87 / 255, 0x91 / 255, 0x8d / 255))
    tw2 = pymupdf.TextWriter(page.rect)
    tw2.append((cx - wn / 2, y), s, font=fn, fontsize=10.5)
    tw2.write_text(page, color=(0x33 / 255, 0x41 / 255, 0x55 / 255))


def main():
    pw = sync_playwright().start()
    br = pw.chromium.launch(executable_path=R.CHROME)
    try:
        files = [str(ROOT / 'sections' / f'{s}.html') for s in SECTIONS]
        res = R.render(files, dpi=40, browser=br, quiet=True)
        bad = []
        counts = {}
        for s in SECTIONS:
            r = res[f'{s}.html']
            counts[s] = r['pdf_pages']
            ov = [p for p in r['check']['pages'] if p['overflowCount']]
            if r['pdf_pages'] != r['css_pages'] or ov or r['check']['images'] or r['check']['smallText']:
                bad.append((s, r['pdf_pages'], r['css_pages'], len(ov), r['check']['images'], len(r['check']['smallText'])))
        if bad:
            print('CẢNH BÁO render:', bad)
        # bảng trang
        page_no = 3  # 1 = bìa cũ, 2 = mục lục
        entries, pmap, seen = [], {}, set()
        for s in SECTIONS:
            for i, (badge, h1) in enumerate(page_meta(s)):
                grp = 'prep' if badge.startswith('Phần') else ('sew' if badge.startswith('Bước') else 'fin')
                group = {'prep': 'Chuẩn bị', 'sew': 'May từng bước', 'fin': 'Hoàn thiện'}[grp]
                if badge not in seen or grp == 'fin':
                    title = CANON.get(badge, h1)
                    entries.append({'badge': badge if badge not in seen else '', 'title': title, 'page': page_no, 'group': group, 'kind': grp, 'sub': badge in seen})
                    seen.add(badge)
                    pmap.setdefault(badge, page_no)
                else:
                    entries.append({'badge': '', 'title': h1, 'page': page_no, 'group': group, 'kind': grp, 'sub': True})
                page_no += 1
        last_new = page_no - 1
        appendix_page = page_no
        pmap['_last'] = last_new
        old_off = appendix_page - 1  # trang cũ k (k>=2) -> k + old_off
        (ROOT / 'sections' / '02_muc_luc.html').write_text(toc_html(entries, 3, last_new, appendix_page), encoding='utf-8')
        (ROOT / 'sections' / '98_phu_luc.html').write_text(appendix_html(pmap, old_off), encoding='utf-8')
        res2 = R.render([str(ROOT / 'sections' / '02_muc_luc.html'), str(ROOT / 'sections' / '98_phu_luc.html')], dpi=100, browser=br, quiet=True)
        # nhãn "MỚI" dán lên bìa cũ
        bp = br.new_page()
        bp.goto((ROOT / 'sections' / '01_nhan_bia.html').as_uri()); bp.evaluate('document.fonts.ready.then(() => true)'); bp.wait_for_timeout(200)
        bp.pdf(path=str(ROOT / 'out' / '01_nhan_bia.pdf'), width='46mm', height='46mm', print_background=True,
               margin={'top': '0', 'right': '0', 'bottom': '0', 'left': '0'})
        bp.close()
        for k, r in res2.items():
            ov = [p for p in r['check']['pages'] if p['overflowCount']]
            print(k, r['pdf_pages'], 'trang', 'TRÀN!' if ov or r['pdf_pages'] != 1 else 'ok')
    finally:
        br.close(); pw.stop()

    old = pymupdf.open(OLD)
    doc = pymupdf.open()
    doc.insert_pdf(old, from_page=0, to_page=0)
    doc[0].show_pdf_page(pymupdf.Rect(425, 128, 555, 258), pymupdf.open(ROOT / 'out' / '01_nhan_bia.pdf'), 0)
    doc.insert_pdf(pymupdf.open(ROOT / 'out' / '02_muc_luc.pdf'))
    for s in SECTIONS:
        doc.insert_pdf(pymupdf.open(ROOT / 'out' / f'{s}.pdf'))
    doc.insert_pdf(pymupdf.open(ROOT / 'out' / '98_phu_luc.pdf'))
    first_old = doc.page_count
    doc.insert_pdf(old, from_page=1, to_page=old.page_count - 1)
    # đánh số lại
    for i in range(1, doc.page_count):
        pg = doc[i]
        if i >= first_old:
            for b in pg.get_text('dict')['blocks']:
                for l in b.get('lines', []):
                    for sp in l['spans']:
                        if sp['bbox'][1] > 800 and re.fullmatch(r'[—\s\d]+', sp['text']):
                            pg.add_redact_annot(pymupdf.Rect(sp['bbox']) + (-1, -1, 1, 1), fill=(1, 1, 1))
            pg.apply_redactions(images=pymupdf.PDF_REDACT_IMAGE_NONE, graphics=pymupdf.PDF_REDACT_LINE_ART_NONE)
        if not pg.is_wrapped:
            pg.wrap_contents()  # Chromium để lại ma trận CTM chưa đóng q/Q -> phải bọc lại trước khi đóng dấu số trang
        stamp_number(pg, i + 1)
    # mục lục (bookmark)
    toc = [[1, 'Bìa', 1], [1, 'Mục lục', 2], [1, 'PHẦN HƯỚNG DẪN DỄ HIỂU (mới)', 3]]
    for e in entries:
        label = (e['badge'] + ' · ' if e['badge'] else '') + e['title']
        toc.append([3 if e['sub'] else 2, label, e['page']])
    toc.append([1, 'PHỤ LỤC · Bản hướng dẫn cũ (tham khảo)', appendix_page])
    for lvl, title, p in old.get_toc():
        toc.append([lvl + 1, title, p + old_off])
    # sửa cấp: mục cấp 3 chỉ được đứng sau cấp 2
    doc.set_toc(toc)
    meta = old.metadata
    meta['subject'] = 'Hướng dẫn may túi dây rút có quai (30 × 25 cm) — phần hướng dẫn dễ hiểu có sơ đồ kích thước và ảnh từ video + bản cũ'
    meta['modDate'] = pymupdf.get_pdf_now()
    meta['producer'] = 'PyMuPDF / Chromium'
    doc.set_metadata(meta)
    OUT.parent.mkdir(parents=True, exist_ok=True)
    doc.save(OUT, garbage=4, deflate=True)
    print('Đã lưu', OUT, doc.page_count, 'trang', round(OUT.stat().st_size / 1e6, 2), 'MB')
    json.dump({'counts': counts, 'pmap': pmap, 'appendix': appendix_page, 'old_off': old_off}, open(ROOT / 'out' / 'build_info.json', 'w'), ensure_ascii=False, indent=1)


if __name__ == '__main__':
    main()
