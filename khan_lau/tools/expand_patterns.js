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
