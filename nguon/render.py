#!/usr/bin/env python3
"""Render một (hoặc nhiều) file section HTML -> PDF A4 + ảnh PNG xem trước + kiểm tra tràn trang.

Cách dùng:
  python3 render.py sections/50_cat_vai.html            # render + kiểm tra, PNG 100 dpi
  python3 render.py sections/50_cat_vai.html --dpi 160  # PNG nét hơn
  python3 render.py sections/50_cat_vai.html --zoom 2:0,0.5,1,1   # PNG phóng to trang 2, vùng (x0,y0,x1,y1) theo tỉ lệ 0..1
Kết quả: out/<tên>.pdf, out/<tên>-p1.png, -p2.png ...
"""
import sys, os, re, json, argparse
from pathlib import Path
from playwright.sync_api import sync_playwright
import pymupdf

ROOT = Path(__file__).resolve().parent
CHROME = os.environ.get('CHROME_PATH', '/opt/pw-browsers/chromium-1194/chrome-linux/chrome')
if not os.path.exists(CHROME):
    CHROME = None  # dùng Chromium mặc định của Playwright
DEFS = (ROOT / 'defs.svg').read_text(encoding='utf-8')

CHECK_JS = r"""
() => {
  const mm = 96/25.4;
  const out = {pages: [], images: [], smallText: [], bigText: [], fonts: {}};
  out.fonts.bevn = document.fonts.check('700 12px "Be Vietnam Pro"');
  out.fonts.nunito = document.fonts.check('800 12px "Nunito"');
  document.querySelectorAll('img').forEach(im => { if (!im.complete || im.naturalWidth === 0) out.images.push(im.getAttribute('src')); });
  const pages = [...document.querySelectorAll('.page')];
  pages.forEach((pg, i) => {
    const r = pg.getBoundingClientRect();
    const cs = getComputedStyle(pg);
    const limB = r.bottom - parseFloat(cs.paddingBottom) + 1.5;
    const limR = r.right - parseFloat(cs.paddingRight) + 1.5;
    const limL = r.left + parseFloat(cs.paddingLeft) - 1.5;
    const over = [];
    pg.querySelectorAll('*').forEach(el => {
      if (el.closest('svg') && el.tagName.toLowerCase() !== 'svg') return;
      if (el.classList.contains('runhead') || el.classList.contains('allow-bleed') || el.closest('.allow-bleed')) return;
      const s = getComputedStyle(el);
      if (s.position === 'absolute' && el.classList.contains('deco')) return;
      const b = el.getBoundingClientRect();
      if (b.width === 0 || b.height === 0) return;
      if (b.bottom > limB || b.right > limR || b.left < limL) {
        over.push({tag: el.tagName.toLowerCase(), cls: el.className && el.className.baseVal !== undefined ? el.className.baseVal : el.className,
                   text: (el.innerText || el.textContent || '').trim().slice(0, 60),
                   overBottomMM: +((b.bottom - limB) / mm).toFixed(1), overRightMM: +((b.right - limR) / mm).toFixed(1), overLeftMM: +((limL - b.left)/mm).toFixed(1)});
      }
    });
    // chỉ giữ phần tử sâu nhất (tránh báo trùng cha/con)
    out.pages.push({index: i + 1, overflow: over.slice(-12), overflowCount: over.length});
  });
  document.querySelectorAll('svg text').forEach(t => {
    const b = t.getBoundingClientRect();
    if (!t.textContent.trim() || b.height === 0) return;
    const fs = parseFloat(getComputedStyle(t).fontSize);
    const ctm = t.getScreenCTM();
    const scale = ctm ? Math.hypot(ctm.a, ctm.b) : 1;
    const eff = fs * scale;
    const pg = t.closest('.page'); const pi = pg ? pages.indexOf(pg) + 1 : 0;
    if (eff < 8.4) out.smallText.push({page: pi, px: +eff.toFixed(1), text: t.textContent.trim().slice(0, 40)});
    if (eff > 24) out.bigText.push({page: pi, px: +eff.toFixed(1), text: t.textContent.trim().slice(0, 40)});
  });
  return out;
}
"""


# Chromium in PDF sẽ raster hóa fill dạng <pattern> (bị mờ/rỗ). Đoạn JS này thay mỗi hình được tô
# bằng pattern thành một nhóm vector: clipPath theo đúng hình + các ô pattern lặp lại (dùng <use>).
EXPAND_PATTERNS_JS = r"""
() => {
  const NS = 'http://www.w3.org/2000/svg';
  let uid = 0, n = 0;
  const tileCache = {};
  const defsHost = document.querySelector('svg defs');
  const getHref = e => e.getAttribute('href') || e.getAttributeNS('http://www.w3.org/1999/xlink', 'href');
  function resolve(pat) {
    let w = +pat.getAttribute('width') || 0, h = +pat.getAttribute('height') || 0;
    let tr = pat.getAttribute('patternTransform') || '';
    let units = pat.getAttribute('patternUnits');
    let x = +pat.getAttribute('x') || 0, y = +pat.getAttribute('y') || 0;
    let src = pat, guard = 0;
    while (src.children.length === 0 && getHref(src) && guard++ < 5) {
      const ref = document.getElementById(getHref(src).replace(/^#/, ''));
      if (!ref) break;
      src = ref;
      if (!w) w = +ref.getAttribute('width') || 0;
      if (!h) h = +ref.getAttribute('height') || 0;
      if (!tr) tr = ref.getAttribute('patternTransform') || '';
      if (!units) units = ref.getAttribute('patternUnits');
    }
    return {src, w, h, tr, units: units || 'objectBoundingBox', x, y};
  }
  const els = [...document.querySelectorAll('svg *')].filter(el => {
    if (el.closest('defs,pattern,clipPath,mask,marker,symbol')) return false;
    if (!(el instanceof SVGGeometryElement)) return false;
    const f = getComputedStyle(el).fill;
    return f && f.startsWith('url(');
  });
  for (const el of els) {
    const m = getComputedStyle(el).fill.match(/url\("?#([^")]+)"?\)/);
    if (!m) continue;
    const pat = document.getElementById(m[1]);
    if (!pat || pat.tagName.toLowerCase() !== 'pattern') continue;
    const P = resolve(pat);
    if (P.units !== 'userSpaceOnUse' || !P.w || !P.h) continue;
    const svg = el.ownerSVGElement;
    // ma trận patternTransform
    const tmp = document.createElementNS(NS, 'g');
    if (P.tr) tmp.setAttribute('transform', P.tr);
    svg.appendChild(tmp);
    const cons = tmp.transform.baseVal.consolidate();
    const M = cons ? cons.matrix : svg.createSVGMatrix();
    tmp.remove();
    const inv = M.inverse();
    let bb; try { bb = el.getBBox(); } catch (e) { continue; }
    if (bb.width === 0 || bb.height === 0) continue;
    const pts = [[bb.x, bb.y], [bb.x + bb.width, bb.y], [bb.x, bb.y + bb.height], [bb.x + bb.width, bb.y + bb.height]].map(([px, py]) => {
      const p = svg.createSVGPoint(); p.x = px; p.y = py; return p.matrixTransform(inv);
    });
    const minX = Math.min(...pts.map(p => p.x)) - P.x, maxX = Math.max(...pts.map(p => p.x)) - P.x;
    const minY = Math.min(...pts.map(p => p.y)) - P.y, maxY = Math.max(...pts.map(p => p.y)) - P.y;
    // tile symbol (1 lần cho mỗi pattern)
    let tileId = tileCache[m[1]];
    if (!tileId) {
      tileId = 'tile-' + m[1] + '-' + (uid++);
      const g = document.createElementNS(NS, 'g'); g.id = tileId;
      [...P.src.children].forEach(c => g.appendChild(c.cloneNode(true)));
      (defsHost || svg).appendChild(g);
      tileCache[m[1]] = tileId;
    }
    const cid = 'clip-pat-' + (uid++);
    const cp = document.createElementNS(NS, 'clipPath'); cp.id = cid;
    const shape = el.cloneNode(false); shape.removeAttribute('transform'); shape.removeAttribute('class'); shape.removeAttribute('style');
    shape.removeAttribute('clip-path');
    cp.appendChild(shape);
    const wrap = document.createElementNS(NS, 'g');
    if (el.getAttribute('transform')) wrap.setAttribute('transform', el.getAttribute('transform'));
    const op = getComputedStyle(el).fillOpacity;
    if (op && op !== '1') wrap.setAttribute('opacity', op);
    wrap.setAttribute('clip-path', 'url(#' + cid + ')');
    wrap.appendChild(cp);
    const inner = document.createElementNS(NS, 'g');
    let t = (P.tr ? P.tr + ' ' : '') + (P.x || P.y ? `translate(${P.x} ${P.y})` : '');
    if (t.trim()) inner.setAttribute('transform', t.trim());
    const i0 = Math.floor(minX / P.w), i1 = Math.ceil(maxX / P.w), j0 = Math.floor(minY / P.h), j1 = Math.ceil(maxY / P.h);
    if ((i1 - i0) * (j1 - j0) > 4000) continue;
    for (let i = i0; i < i1; i++) for (let j = j0; j < j1; j++) {
      const u = document.createElementNS(NS, 'use');
      u.setAttribute('href', '#' + tileId);
      u.setAttribute('transform', `translate(${i * P.w} ${j * P.h})`);
      inner.appendChild(u);
    }
    wrap.appendChild(inner);
    el.parentNode.insertBefore(wrap, el);
    el.style.fill = 'none';
    n++;
  }
  return n;
}
"""


# Dải caro trên đầu mỗi trang (vẽ bằng SVG vector để in nét)
BAND_JS = r"""
() => {
  const NS = 'http://www.w3.org/2000/svg';
  document.querySelectorAll('.page').forEach(pg => {
    if (pg.querySelector(':scope > svg.band') || pg.classList.contains('noband')) return;
    const s = document.createElementNS(NS, 'svg');
    s.setAttribute('class', 'band'); s.setAttribute('viewBox', '0 0 210 6.5'); s.setAttribute('preserveAspectRatio', 'none');
    let h = '<rect width="210" height="6.5" fill="#FFFFF2"/>';
    for (let x = 0; x < 210; x += 10) h += `<rect x="${x}" y="0" width="5" height="6.5" fill="#A8CF45" fill-opacity=".55"/>`;
    h += '<rect x="0" y="0" width="210" height="3.25" fill="#A8CF45" fill-opacity=".55"/>';
    s.innerHTML = h;
    pg.insertBefore(s, pg.firstChild);
  });
  return true;
}
"""


def build_html(src: Path) -> Path:
    html = src.read_text(encoding='utf-8')
    if '<!--DEFS-->' in html:
        html = html.replace('<!--DEFS-->', DEFS, 1)
    else:
        html = re.sub(r'(<body[^>]*>)', lambda m: m.group(1) + DEFS, html, count=1)
    tmp = src.parent / ('.build_' + src.name)
    tmp.write_text(html, encoding='utf-8')
    return tmp


def render(srcs, dpi=100, zoom=None, quiet=False, browser=None):
    results = {}
    own = browser is None
    pw = None
    if own:
        pw = sync_playwright().start()
        browser = pw.chromium.launch(executable_path=CHROME)
    try:
        for s in srcs:
            src = Path(s).resolve()
            tmp = build_html(src)
            page = browser.new_page(viewport={'width': 794, 'height': 1123})
            page.goto(tmp.as_uri(), wait_until='load')
            page.evaluate('document.fonts.ready.then(() => true)')
            page.wait_for_timeout(250)
            chk = page.evaluate(CHECK_JS)
            chk['expandedPatterns'] = page.evaluate(EXPAND_PATTERNS_JS)
            page.evaluate(BAND_JS)
            out_dir = ROOT / 'out'; out_dir.mkdir(exist_ok=True)
            pdf_path = out_dir / (src.stem + '.pdf')
            page.pdf(path=str(pdf_path), format='A4', print_background=True, prefer_css_page_size=True,
                     margin={'top': '0', 'right': '0', 'bottom': '0', 'left': '0'})
            page.close()
            tmp.unlink(missing_ok=True)
            doc = pymupdf.open(pdf_path)
            for old in out_dir.glob(src.stem + '-p*.png'):
                old.unlink()
            pngs = []
            for i, pg in enumerate(doc):
                p = out_dir / f'{src.stem}-p{i+1}.png'
                pg.get_pixmap(dpi=dpi).save(p)
                pngs.append(str(p))
            if zoom:
                zp, box = zoom.split(':')
                x0, y0, x1, y1 = map(float, box.split(','))
                pg = doc[int(zp) - 1]
                R = pg.rect
                clip = pymupdf.Rect(R.x0 + x0 * R.width, R.y0 + y0 * R.height, R.x0 + x1 * R.width, R.y0 + y1 * R.height)
                zpath = out_dir / f'{src.stem}-zoom.png'
                pg.get_pixmap(dpi=220, clip=clip).save(zpath)
                pngs.append(str(zpath))
            n_css_pages = len(chk['pages'])
            results[src.name] = {'pdf': str(pdf_path), 'pdf_pages': doc.page_count, 'css_pages': n_css_pages, 'png': pngs, 'check': chk}
            if not quiet:
                print(f'== {src.name}: {doc.page_count} trang PDF ({n_css_pages} .page)')
                if doc.page_count != n_css_pages:
                    print('  !! SỐ TRANG PDF KHÁC SỐ .page -> có nội dung tràn sang trang mới')
                print('  fonts ok:', chk['fonts'], '| pattern->vector:', chk.get('expandedPatterns'))
                if chk['images']:
                    print('  !! ẢNH LỖI:', chk['images'])
                for p in chk['pages']:
                    if p['overflowCount']:
                        print(f"  !! TRANG {p['index']}: {p['overflowCount']} phần tử vượt lề/tràn (hiển thị tối đa 12 cái cuối):")
                        for o in p['overflow']:
                            print('     ', json.dumps(o, ensure_ascii=False))
                if chk['smallText']:
                    print('  !! CHỮ SVG QUÁ NHỎ (<8.4px):', json.dumps(chk['smallText'][:15], ensure_ascii=False))
                if chk['bigText']:
                    print('  ?? CHỮ SVG RẤT LỚN (>24px):', json.dumps(chk['bigText'][:10], ensure_ascii=False))
                print('  PNG:', ' '.join(pngs))
    finally:
        if own:
            browser.close(); pw.stop()
    return results


if __name__ == '__main__':
    ap = argparse.ArgumentParser()
    ap.add_argument('files', nargs='+')
    ap.add_argument('--dpi', type=int, default=100)
    ap.add_argument('--zoom', default=None, help='trang:x0,y0,x1,y1 (tỉ lệ 0..1)')
    a = ap.parse_args()
    render(a.files, dpi=a.dpi, zoom=a.zoom)
