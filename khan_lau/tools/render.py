#!/usr/bin/env python3
"""Render section HTML -> PDF A4 + PNG xem trước + kiểm tra tự động (tràn trang, font, chữ nhỏ, định dạng số).

  python3 tools/render.py 20_chon_vai            # render 1 phần (bỏ qua nếu không đổi — có cache)
  python3 tools/render.py 20_chon_vai --force --dpi 110
  python3 tools/render.py all
Kết quả: build/pdf/<tên>.pdf, build/png/<tên>-p<N>.png
"""
import sys, os, re, json, argparse, hashlib, importlib
from pathlib import Path
from playwright.sync_api import sync_playwright
import pymupdf

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
sys.path.insert(0, str(HERE))
import tpl, defs  # noqa: E402

CHROME = os.environ.get('CHROME_PATH', '/opt/pw-browsers/chromium-1194/chrome-linux/chrome')
if not os.path.exists(CHROME):
    CHROME = None
BUILD = ROOT / 'build'
SECT = ROOT / 'sections'

HEAD = '''<!doctype html><html lang="vi"><head><meta charset="utf-8"><title>{title}</title>
<link rel="stylesheet" href="../../style.css">{extra_css}</head><body>{defs}
{body}
</body></html>'''

CHECK_JS = r"""
() => {
  const mm = 96/25.4;
  const out = {pages: [], images: [], smallText: [], fonts: {}, texts: []};
  out.fonts.bevn = document.fonts.check('700 12px "Be Vietnam Pro"');
  out.fonts.nunito = document.fonts.check('800 12px "Nunito"');
  out.fonts.lora = document.fonts.check('700 12px "Lora"');
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
      const b = el.getBoundingClientRect();
      if (b.width === 0 || b.height === 0) return;
      if (b.bottom > limB || b.right > limR || b.left < limL) {
        over.push({tag: el.tagName.toLowerCase(), cls: (el.className && el.className.baseVal !== undefined) ? el.className.baseVal : el.className,
                   text: (el.innerText || el.textContent || '').trim().slice(0, 50),
                   overBottomMM: +((b.bottom - limB) / mm).toFixed(1), overRightMM: +((b.right - limR) / mm).toFixed(1), overLeftMM: +((limL - b.left)/mm).toFixed(1)});
      }
    });
    // phần tử có nội dung bị cắt bên trong (scrollHeight > clientHeight) — ví dụ ô grid bị ép
    pg.querySelectorAll('.card,.note,.stepcard,.fig,td').forEach(el => {
      if (el.scrollHeight > el.clientHeight + 2 && getComputedStyle(el).overflow !== 'visible')
        over.push({tag: el.tagName.toLowerCase(), cls: String(el.className), text: 'NỘI DUNG BỊ CẮT: ' + (el.innerText||'').trim().slice(0,40)});
    });
    out.pages.push({index: i + 1, overflow: over.slice(-10), overflowCount: over.length});
    out.texts.push(pg.innerText + '\n' + [...pg.querySelectorAll('svg text')].map(t => t.textContent).join('\n'));
  });
  document.querySelectorAll('svg text').forEach(t => {
    const b = t.getBoundingClientRect();
    if (!t.textContent.trim() || b.height === 0) return;
    const fs = parseFloat(getComputedStyle(t).fontSize);
    const ctm = t.getScreenCTM();
    const scale = ctm ? Math.hypot(ctm.a, ctm.b) : 1;
    const eff = fs * scale;
    const pg = t.closest('.page'); const pi = pg ? pages.indexOf(pg) + 1 : 0;
    if (eff < 8.2) out.smallText.push({page: pi, px: +eff.toFixed(1), text: t.textContent.trim().slice(0, 40)});
  });
  return out;
}
"""

# Chromium raster hóa fill dạng <pattern> khi in PDF. Đổi mỗi hình tô pattern thành nhóm vector:
# clipPath theo đúng hình + các ô pattern lặp lại (dùng <use>).
EXPAND_PATTERNS_JS = (HERE / 'expand_patterns.js').read_text(encoding='utf-8')

# Nhãn chữ nằm trên vải họa tiết / nền đậm: chèn 1 ô nền trắng bo góc phía sau (thay cho viền chữ —
# viền chữ làm Chromium xuất font Type3 nặng và chữ bị lặp khi copy).
HALO_JS = r"""
() => {
  const NS = 'http://www.w3.org/2000/svg';
  let n = 0;
  const texts = [...document.querySelectorAll('svg text')].filter(t => !t.classList.contains('t-white') && t.textContent.trim());
  const isBusy = el => {
    if (!(el instanceof SVGGeometryElement) || el.closest('text')) return false;
    const cs = getComputedStyle(el);
    const f = cs.fill;
    if (!f || f === 'none') return false;
    if (f.startsWith('url(')) return true;
    const m = f.match(/rgba?\(([^)]+)\)/); if (!m) return false;
    const [r, g, b, a] = m[1].split(',').map(Number);
    const op = (a === undefined ? 1 : a) * parseFloat(cs.fillOpacity || 1) * parseFloat(cs.opacity || 1);
    if (op < 0.2) return false;
    const lum = 0.2126 * r + 0.7152 * g + 0.0722 * b;
    return lum < 225;
  };
  texts.forEach(t => t.style.pointerEvents = 'none');
  for (const t of texts) {
    const r = t.getBoundingClientRect();
    if (!r.width) continue;
    const pts = [[r.left + r.width * .5, r.top + r.height * .5], [r.left + 2, r.top + r.height * .5], [r.right - 2, r.top + r.height * .5]];
    let busy = false;
    for (const [x, y] of pts) {
      const els = document.elementsFromPoint(x, y);
      for (const el of els) {
        if (el === t) continue;
        if (el.tagName && el.tagName.toLowerCase() === 'svg') break;
        if (isBusy(el)) { busy = true; break; }
      }
      if (busy) break;
    }
    if (!busy) continue;
    const bb = t.getBBox();
    const rc = document.createElementNS(NS, 'rect');
    rc.setAttribute('x', bb.x - 2.5); rc.setAttribute('y', bb.y - 0.5);
    rc.setAttribute('width', bb.width + 5); rc.setAttribute('height', bb.height + 1);
    rc.setAttribute('rx', 3); rc.setAttribute('class', 'halo');
    if (t.getAttribute('transform')) rc.setAttribute('transform', t.getAttribute('transform'));
    t.parentNode.insertBefore(rc, t);
    n++;
  }
  return n;
}
"""

BAND_JS = r"""
() => {
  const NS = 'http://www.w3.org/2000/svg';
  document.querySelectorAll('.page').forEach(pg => {
    if (pg.querySelector(':scope > svg.band') || pg.classList.contains('noband')) return;
    const s = document.createElementNS(NS, 'svg');
    s.setAttribute('class', 'band'); s.setAttribute('viewBox', '0 0 210 7'); s.setAttribute('preserveAspectRatio', 'none');
    s.innerHTML = '<rect width="210" height="7" fill="#EFE6D3"/>' +
      '<rect y="1.3" width="210" height="1.5" fill="#2B4C74"/>' +
      '<rect y="3.35" width="210" height=".55" fill="#D96F43"/>' +
      '<rect y="4.45" width="210" height="1.5" fill="#2B4C74"/>';
    pg.insertBefore(s, pg.firstChild);
  });
  return true;
}
"""

TEXT_RULES = [
    (re.compile(r'(?<![\d/])\d+\.\d+(?!\.\d)'), 'số thập phân dùng dấu chấm (phải dùng dấu phẩy)'),
    (re.compile(r'\d\s*[xX]\s*\d'), 'dùng chữ x thay cho dấu nhân ×'),
    (re.compile(r'⟦'), 'placeholder chưa giải được'),
    (re.compile(r'\{\{|\}\}'), 'còn ngoặc {{ }}'),
    (re.compile(r'  +\S'), None),  # bỏ qua khoảng trắng kép (do innerText)
]


def sha(*parts):
    h = hashlib.sha256()
    for p in parts:
        h.update(p if isinstance(p, bytes) else p.encode('utf-8'))
    return h.hexdigest()[:16]


def build_html(name, ctx):
    importlib.reload(sys.modules.get('art') or __import__('art'))
    figs = importlib.reload(sys.modules['figs']) if 'figs' in sys.modules else importlib.import_module('figs')
    blocks = importlib.reload(sys.modules['blocks']) if 'blocks' in sys.modules else importlib.import_module('blocks')
    src = (SECT / f'{name}.html').read_text(encoding='utf-8')
    extra_css = ''
    m = re.search(r'<style>.*?</style>', src, re.S)
    if m:
        extra_css = m.group(0)
        src = src.replace(extra_css, '')
    body, missing = tpl.fill(src, ctx, figs, blocks)
    html = HEAD.format(title=name, extra_css=extra_css, defs=defs.defs_svg(), body=body)
    out = BUILD / 'html' / f'{name}.html'
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(html, encoding='utf-8')
    return out, html, missing


def text_issues(texts):
    iss = []
    for pi, t in enumerate(texts, 1):
        for rx, msg in TEXT_RULES:
            if not msg:
                continue
            for m in rx.finditer(t):
                ctx = t[max(0, m.start() - 25): m.end() + 25].replace('\n', ' ')
                iss.append(f'tr.{pi}: {msg}: «{ctx}»')
    return iss


def render(names, dpi=90, force=False, quiet=False, browser=None, ctx=None):
    ctx = ctx or tpl.Ctx()
    cache_f = BUILD / 'render_cache.json'
    cache = json.loads(cache_f.read_text()) if cache_f.exists() else {}
    css = (ROOT / 'style.css').read_text(encoding='utf-8')
    engine = sha(CHECK_JS, EXPAND_PATTERNS_JS, BAND_JS, HALO_JS)
    results = {}
    own = browser is None
    pw = None
    try:
        for name in names:
            out, html, missing = build_html(name, ctx)
            key = sha(html, css, engine, str(dpi))
            pdf_path = BUILD / 'pdf' / f'{name}.pdf'
            if not force and cache.get(name, {}).get('key') == key and pdf_path.exists():
                results[name] = cache[name]['result']
                if not quiet:
                    print(f'== {name}: không đổi (cache) — {results[name]["pdf_pages"]} trang')
                continue
            if browser is None:
                pw = sync_playwright().start()
                browser = pw.chromium.launch(executable_path=CHROME)
            page = browser.new_page(viewport={'width': 794, 'height': 1123})
            page.goto(out.as_uri(), wait_until='load')
            page.evaluate("Promise.all([document.fonts.load('800 12px Nunito'), document.fonts.load('700 12px Lora'), document.fonts.load('700 12px \"Be Vietnam Pro\"')]).then(() => document.fonts.ready).then(() => true)")
            page.wait_for_timeout(200)
            chk = page.evaluate(CHECK_JS)
            full_h = page.evaluate('document.documentElement.scrollHeight')
            page.set_viewport_size({'width': 794, 'height': int(full_h) + 10})  # elementsFromPoint cần mọi trang nằm trong viewport
            chk['halos'] = page.evaluate(HALO_JS)
            chk['expandedPatterns'] = page.evaluate(EXPAND_PATTERNS_JS)
            page.evaluate(BAND_JS)
            pdf_path.parent.mkdir(parents=True, exist_ok=True)
            page.pdf(path=str(pdf_path), format='A4', print_background=True, prefer_css_page_size=True,
                     margin={'top': '0', 'right': '0', 'bottom': '0', 'left': '0'})
            page.close()
            doc = pymupdf.open(pdf_path)
            png_dir = BUILD / 'png'
            png_dir.mkdir(exist_ok=True)
            for old in png_dir.glob(f'{name}-p*.png'):
                old.unlink()
            pngs = []
            for i, pg in enumerate(doc):
                p = png_dir / f'{name}-p{i + 1}.png'
                pg.get_pixmap(dpi=dpi).save(p)
                pngs.append(str(p))
            n_img = sum(len(pg.get_images()) for pg in doc)
            texts = chk.pop('texts')
            res = {'pdf': str(pdf_path), 'pdf_pages': doc.page_count, 'css_pages': len(chk['pages']), 'png': pngs,
                   'raster_images': n_img, 'missing': missing, 'text_issues': text_issues(texts), 'check': chk,
                   'text_sha': sha('\n'.join(re.sub(r'\s+', ' ', t).strip() for t in texts))}
            results[name] = res
            cache[name] = {'key': key, 'result': res}
            if not quiet:
                report(name, res)
    finally:
        if pw:
            browser.close()
            pw.stop()
        cache_f.parent.mkdir(exist_ok=True)
        cache_f.write_text(json.dumps(cache, ensure_ascii=False, indent=0))
    return results


def problems(res):
    p = []
    if res['pdf_pages'] != res['css_pages']:
        p.append(f"số trang PDF {res['pdf_pages']} ≠ số .page {res['css_pages']} (tràn trang)")
    for pg in res['check']['pages']:
        if pg['overflowCount']:
            p.append(f"trang {pg['index']}: {pg['overflowCount']} phần tử tràn lề: " + '; '.join(json.dumps(o, ensure_ascii=False) for o in pg['overflow'][-4:]))
    if res['check']['images']:
        p.append(f"ảnh lỗi: {res['check']['images']}")
    if res['check']['smallText']:
        p.append(f"chữ SVG < 8,2 px: {json.dumps(res['check']['smallText'][:8], ensure_ascii=False)}")
    if not all(res['check']['fonts'].values()):
        p.append(f"font chưa nạp: {res['check']['fonts']}")
    if res['missing']:
        p.append(f"placeholder lỗi: {res['missing']}")
    if res['raster_images']:
        p.append(f"có {res['raster_images']} ảnh raster trong PDF (pattern/gradient chưa vector hóa?)")
    p += res['text_issues']
    return p


def report(name, res):
    pr = problems(res)
    print(f"== {name}: {res['pdf_pages']} trang | pattern→vector: {res['check'].get('expandedPatterns')} | {'OK' if not pr else str(len(pr)) + ' VẤN ĐỀ'}")
    for x in pr:
        print('   !!', x)
    print('   PNG:', ' '.join(Path(p).name for p in res['png']))


if __name__ == '__main__':
    ap = argparse.ArgumentParser()
    ap.add_argument('names', nargs='+')
    ap.add_argument('--dpi', type=int, default=90)
    ap.add_argument('--force', action='store_true')
    a = ap.parse_args()
    names = a.names
    if names == ['all']:
        names = sorted(p.stem for p in SECT.glob('*.html') if not p.stem.startswith('_'))
    render(names, dpi=a.dpi, force=a.force)
