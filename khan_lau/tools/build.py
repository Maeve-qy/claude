#!/usr/bin/env python3
"""Dựng PDF hoàn chỉnh — mọi bước tất định đều làm bằng code:

  1. validate.py  : schema + bất biến công thức + sơ đồ xếp mẫu (dừng nếu lỗi)
  2. render.py    : render từng phần (có cache), kiểm tra tràn trang / font / định dạng số
  3. mục lục      : sinh từ data-* của từng <section class="page">, số trang tính tự động
  4. ghép PDF, đóng số trang, bookmark 3 cấp, metadata
  5. nén (garbage=4, deflate, clean) + xác minh file cuối
  6. QC ledger    : so hash nội dung chữ từng phần với lần QC ngữ nghĩa gần nhất
                    -> chỉ phần có CHỮ thay đổi mới cần QC lại; đổi layout thì giữ nguyên QC

  python3 tools/build.py [đường_dẫn_pdf_ra]
"""
import sys, re, json, html, hashlib, subprocess
from pathlib import Path
import pymupdf

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
sys.path.insert(0, str(HERE))
import render as R  # noqa: E402
import tpl  # noqa: E402

OUT = Path(sys.argv[1]).resolve() if len(sys.argv) > 1 else ROOT.parent / 'Khan_lau_tu_vai_cu_huong_dan_chi_tiet.pdf'
ORDER = ['00_bia', '01_muc_luc', '10_mo_dau', '20_chon_vai', '21_tan_dung', '22_so_che', '30_phoi_mau', '40_ky_thuat', '45_cong_thuc',
         '50_m1', '51_m2', '52_m3', '53_m4', '54_m5', '55_m6', '90_hoan_thien']
GROUPS = {'cover': None, 'toc': None, 'intro': 'Mở đầu', 'prep': 'Chuẩn bị: vải, màu, kỹ thuật', 'make': '6 mẫu khăn', 'fin': 'Hoàn thiện & phụ lục'}
CHAPTER_TITLES = {'Mở đầu': 'Mở đầu', 'Phần 1': 'Chọn vải & tận dụng quần áo cũ', 'Phần 2': 'Phối màu', 'Phần 3': 'Dụng cụ & kỹ thuật',
                  'Phần 4': 'Công thức & kích thước', 'Mẫu 1': 'Giẻ áo thun không cần may', 'Mẫu 2': 'Khăn lau bàn 2 lớp may lộn',
                  'Mẫu 3': 'Khăn bếp treo gấp mép đôi', 'Mẫu 4': 'Khăn ghép mảnh vải vụn', 'Mẫu 5': 'Khăn lau nhà 3 lớp bo viền',
                  'Mẫu 6': 'Vỏ bọc bàn lau nhà dẹt', 'Hoàn thiện': 'Giặt, bảo quản & sửa lỗi', 'Phụ lục': 'Bảng tra & bảng kiểm'}
FONT_NUM = str(ROOT / 'fonts' / 'Nunito-800-latin.ttf')
FONT_TXT = str(ROOT / 'fonts' / 'BeVietnamPro-400-latin.ttf')


def page_meta(name):
    src = (R.SECT / f'{name}.html').read_text(encoding='utf-8')
    out = []
    for m in re.finditer(r'<section\b([^>]*)class="[^"]*\bpage\b[^"]*"([^>]*)>', src):
        attrs = m.group(1) + m.group(2)
        get = lambda k: html.unescape(re.search(rf'data-{k}="([^"]*)"', attrs).group(1)) if re.search(rf'data-{k}="', attrs) else ''
        out.append({'group': get('group'), 'badge': get('badge'), 'title': get('title')})
    return out


def toc_html(entries):
    cols = {'L': ['intro', 'prep'], 'R': ['make', 'fin']}

    def block(gr):
        rows = ''
        chap = None
        for e in entries:
            if e['group'] != gr:
                continue
            if e['badge'] != chap:
                chap = e['badge']
                kind = {'make': 'make', 'fin': 'fin'}.get(gr, 'prep')
                rows += (f'<div class="tr ch"><span class="tb {kind}">{html.escape(chap)}</span><span class="tt">{html.escape(CHAPTER_TITLES.get(chap, e["title"]))}</span>'
                         f'<span class="dots"></span><span class="tp num">{e["page"]}</span></div>')
            if e['title'] != CHAPTER_TITLES.get(chap):
                rows += f'<div class="tr sub"><span class="tt">{html.escape(e["title"])}</span><span class="dots"></span><span class="tp">{e["page"]}</span></div>'
        return f'<div class="tg"><div class="tgh {gr}">{html.escape(GROUPS[gr])}</div>{rows}</div>'
    L = ''.join(block(g) for g in cols['L'])
    Rr = ''.join(block(g) for g in cols['R'])
    return f'''<style>
.tocc{{ display:grid; grid-template-columns:1fr 1fr; gap:0 7mm; }}
.tg{{ margin-bottom:3mm; }}
.tgh{{ font-weight:800; font-size:10.4px; letter-spacing:.1em; text-transform:uppercase; color:var(--denim-700); margin:0 0 1.2mm; display:flex; align-items:center; gap:8px; }}
.tgh::after{{ content:""; flex:1; border-top:1.4px dashed var(--denim-300); }}
.tgh.make{{ color:var(--terra-700); }} .tgh.make::after{{ border-color:var(--terra-300); }}
.tgh.fin{{ color:var(--sage-700); }} .tgh.fin::after{{ border-color:var(--sage-300); }}
.tr{{ display:flex; align-items:baseline; gap:6px; padding:.5mm 0; }}
.tr.ch{{ margin-top:1.3mm; font-size:12px; }}
.tr .tb{{ flex:none; width:19mm; text-align:center; font-size:9px; font-weight:800; letter-spacing:.04em; text-transform:uppercase; color:#fff; border-radius:8px; padding:1.5px 0; background:var(--denim-700); }}
.tr .tb.make{{ background:var(--terra-600); }} .tr .tb.fin{{ background:var(--sage-700); }}
.tr.ch .tt{{ font-weight:700; color:var(--ink); }}
.tr.sub{{ padding-left:21mm; font-size:10.6px; color:var(--ink-2); }}
.tr .dots{{ flex:1; border-bottom:1.5px dotted #C9C2B1; transform:translateY(-3px); min-width:5mm; }}
.tr .tp{{ font-size:12px; color:var(--denim-900); min-width:16px; text-align:right; }}
.tr.sub .tp{{ font:600 10.4px 'Be Vietnam Pro'; color:var(--ink-2); }}
</style>
<section class="page" data-group="toc" data-badge="Mục lục" data-title="Mục lục">
  <div class="runhead">Khăn lau từ vải cũ · <b>Mục lục</b></div>
  <header class="ph">
    <div class="kicker"><span class="badge">Mục lục</span> Đọc theo thứ tự hoặc tra theo mẫu</div>
    <h1 class="title">Mục lục</h1>
  </header>
  <div class="content" style="gap:0">
    <div class="tocc"><div>{L}</div><div>{Rr}</div></div>
    <div class="spacer"></div>
    <div class="cols" style="margin-top:2mm">
      <div class="note tip"><div class="nt">Người mới bắt đầu</div><p>Đọc Mở đầu → Phần 1 → may <b>Mẫu 1</b> rồi <b>Mẫu 2</b>. Phần 3 (kỹ thuật) tra khi cần.</p></div>
      <div class="note info"><div class="nt">Nên in ra</div><p>Trang <b>Bảng tổng hợp kích thước cắt</b> và <b>Bảng kiểm</b> ở cuối sổ — dán cạnh bàn máy.</p></div>
    </div>
  </div>
</section>'''


def stamp_number(page, n):
    fn = pymupdf.Font(fontfile=FONT_NUM)
    s = str(n)
    wn = fn.text_length(s, fontsize=10)
    cx, y = page.rect.width / 2, 822
    page.draw_circle((cx, y - 3.6), 9.5, color=None, fill=(0xEF / 255, 0xE6 / 255, 0xD3 / 255))
    tw = pymupdf.TextWriter(page.rect)
    tw.append((cx - wn / 2, y), s, font=fn, fontsize=10)
    tw.write_text(page, color=(0x2B / 255, 0x4C / 255, 0x74 / 255))


def sha(s):
    return hashlib.sha256(s.encode('utf-8')).hexdigest()[:16]


def main():
    # 1. dữ liệu
    r = subprocess.run([sys.executable, str(HERE / 'validate.py')], capture_output=True, text=True)
    print(r.stdout.strip().splitlines()[-1])
    if r.returncode:
        print(r.stdout)
        sys.exit('DỪNG: dữ liệu chưa đạt kiểm tra.')
    ctx = tpl.Ctx()
    # 2. render các phần (trừ mục lục)
    content = [n for n in ORDER if n != '01_muc_luc']
    res = R.render(content, dpi=60, quiet=True, ctx=ctx)
    bad = {n: R.problems(res[n]) for n in content if R.problems(res[n])}
    if bad:
        for n, p in bad.items():
            print('!!', n, p[:3])
        sys.exit('DỪNG: còn lỗi render.')
    # 3. mục lục
    entries, page = [], 3
    for n in content[1:]:
        metas = page_meta(n)
        assert len(metas) == res[n]['pdf_pages'], (n, len(metas), res[n]['pdf_pages'])
        for m in metas:
            entries.append(dict(m, page=page, section=n))
            page += 1
    (R.SECT / '01_muc_luc.html').write_text(toc_html(entries), encoding='utf-8')
    res.update(R.render(['01_muc_luc'], dpi=80, quiet=True, ctx=ctx))
    if R.problems(res['01_muc_luc']) or res['01_muc_luc']['pdf_pages'] != 1:
        sys.exit(f'DỪNG: mục lục lỗi {R.problems(res["01_muc_luc"])}')
    # 4. ghép
    doc = pymupdf.open()
    for n in ORDER:
        doc.insert_pdf(pymupdf.open(res[n]['pdf']))
    total = doc.page_count
    assert total == page - 1, (total, page - 1)
    for i in range(1, total):
        pg = doc[i]
        if not pg.is_wrapped:
            pg.wrap_contents()
        stamp_number(pg, i + 1)
    toc = [[1, 'Bìa', 1], [1, 'Mục lục', 2]]
    cur_g, cur_c = None, None
    for e in entries:
        if e['group'] != cur_g:
            cur_g = e['group']
            toc.append([1, GROUPS[cur_g], e['page']])
            cur_c = None
        if e['badge'] != cur_c:
            cur_c = e['badge']
            toc.append([2, f"{cur_c} · {CHAPTER_TITLES.get(cur_c, e['title'])}", e['page']])
        if e['title'] != CHAPTER_TITLES.get(cur_c):
            toc.append([3, e['title'], e['page']])
    doc.set_toc(toc)
    doc.set_metadata({'title': 'Khăn lau từ vải cũ — Hướng dẫn chi tiết cắt may', 'author': 'Sổ tay tự làm tại nhà',
                      'subject': 'Cắt may khăn lau bàn, khăn bếp, khăn lau nhà, vỏ bàn lau từ quần áo cũ và vải thừa: chọn vải, phối màu, đo cắt, ráp, xử lý mép (vắt sổ)',
                      'keywords': 'khăn lau, tái chế vải, quần áo cũ, may vá, vắt sổ, phối màu, patchwork',
                      'creator': 'Chromium + PyMuPDF', 'producer': 'PyMuPDF', 'creationDate': pymupdf.get_pdf_now(), 'modDate': pymupdf.get_pdf_now()})
    doc.set_language('vi')
    # 5. nén + lưu
    OUT.parent.mkdir(parents=True, exist_ok=True)
    raw = sum(Path(res[n]['pdf']).stat().st_size for n in ORDER)
    doc.save(OUT, garbage=4, deflate=True, deflate_fonts=True, clean=True, use_objstms=True)
    doc.close()
    # xác minh
    v = pymupdf.open(OUT)
    fonts = {}
    for p in v:
        for f in p.get_fonts():
            fonts[f[3]] = f[1] != 'n/a'
    not_emb = [k for k, x in fonts.items() if not x]
    t = v.get_toc()
    errs = []
    if v.page_count != total: errs.append('số trang lệch')
    if not_emb: errs.append(f'font không nhúng: {not_emb}')
    if any(not (1 <= e[2] <= v.page_count) for e in t): errs.append('bookmark trỏ sai trang')
    imgs = sum(len(p.get_images()) for p in v)
    if imgs: errs.append(f'{imgs} ảnh raster')
    for i in range(1, v.page_count):
        words = v[i].get_text('words', clip=pymupdf.Rect(250, 805, 345, 835))
        if str(i + 1) not in [w[4] for w in words]:
            errs.append(f'trang {i + 1} thiếu số trang')
            break
    empty = [i + 1 for i, p in enumerate(v) if len(p.get_text().strip()) < 20]
    if empty: errs.append(f'trang gần như không có chữ: {empty}')
    size = OUT.stat().st_size
    print(f'PDF: {OUT.name} | {v.page_count} trang | {size / 1e6:.2f} MB (trước nén {raw / 1e6:.2f} MB) | bookmark {len(t)} mục | font {len(fonts)} (nhúng đủ: {not not_emb}) | ảnh raster: {imgs}')
    print('XÁC MINH:', 'ĐẠT' if not errs else errs)
    # 6. QC ledger
    ledger_f = ROOT / 'qc' / 'ledger.json'
    ledger = json.loads(ledger_f.read_text()) if ledger_f.exists() else {}
    spec_sha = sha((ROOT / 'data' / 'spec.json').read_text(encoding='utf-8'))
    need = []
    for n in ORDER:
        tsha = res[n]['text_sha']
        st = ledger.get(n, {})
        if st.get('text_sha') != tsha or st.get('status') != 'passed':
            need.append(n)
    state = {'pages': v.page_count, 'size_mb': round(size / 1e6, 2), 'bookmarks': len(t), 'spec_sha': spec_sha,
             'text_sha': {n: res[n]['text_sha'] for n in ORDER}, 'need_semantic_qc': need, 'verify_errors': errs}
    (ROOT / 'build' / 'build_state.json').write_text(json.dumps(state, ensure_ascii=False, indent=1), encoding='utf-8')
    print('QC ngữ nghĩa cần làm cho:', need if need else 'không phần nào (chữ không đổi kể từ lần QC trước)')
    return 0 if not errs else 1


if __name__ == '__main__':
    sys.exit(main())
