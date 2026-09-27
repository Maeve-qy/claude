"""Ghép dữ liệu vào section HTML.

Cú pháp trong sections/*.html:
  {{m2.cut}}          -> "32 × 32"   (danh sách 2 số -> kích thước)
  {{m2.diag}}         -> "45,3"      (số kiểu Việt Nam, dấu phẩy thập phân)
  {{m4.options.1.sq_cut}} -> chỉ số danh sách bằng số
  {{fig:ten_hinh}}    -> SVG sinh bởi figs.py (số liệu lấy từ derived)
  {{blk:ten_khoi}}    -> khối HTML sinh bởi blocks.py (bảng lấy từ spec)
"""
import json, re, sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
sys.path.insert(0, str(HERE))
import art  # noqa: E402

PH = re.compile(r'\{\{\s*([^{}]+?)\s*\}\}')


class Ctx:
    def __init__(self):
        self.spec = json.loads((ROOT / 'data' / 'spec.json').read_text(encoding='utf-8'))
        import calc
        self.d = calc.derive(self.spec)
        pm = ROOT / 'build' / 'pagemap.json'
        self.pagemap = json.loads(pm.read_text()) if pm.exists() else {}

    def get(self, path):
        cur = self.d
        for k in path.split('.'):
            if isinstance(cur, list):
                cur = cur[int(k)]
            elif k in cur:
                cur = cur[k]
            elif k in self.spec.get('products', {}) and cur is self.d:
                cur = self.spec['products'][k]
            else:
                raise KeyError(path)
        return cur


def fmt(v):
    if isinstance(v, list) and len(v) == 2 and all(isinstance(x, (int, float)) for x in v):
        return art.dims(*v)
    if isinstance(v, (int, float)):
        return art.vn(v)
    return str(v)


def fill(src, ctx, figs=None, blocks=None):
    missing = []

    def rep(m):
        key = m.group(1)
        try:
            if key.startswith('fig:'):
                return getattr(figs, key[4:])(ctx)
            if key.startswith('pg:'):
                return str(ctx.pagemap[key[3:]])
            if key.startswith('icon:'):
                return art.icon(key[5:])
            if key.startswith('blk:'):
                return getattr(blocks, key[4:])(ctx)
            return fmt(ctx.get(key))
        except (KeyError, AttributeError, IndexError, ValueError) as e:
            missing.append(f'{key} ({type(e).__name__}: {e})')
            return f'⟦{key}⟧'
    out = src
    for _ in range(3):  # khối/hình sinh ra có thể chứa {{...}} lồng
        new = PH.sub(rep, out)
        if new == out:
            break
        out = new
    return out, missing
