"""Minimal libass (ctypes) wrapper: render ASS events exactly as libass does, return RGBA/alpha + bbox."""
import ctypes, ctypes.util, numpy as np

_lib = ctypes.CDLL("libass.so.9")

class ASS_Image(ctypes.Structure):
    pass
ASS_Image._fields_ = [("w", ctypes.c_int), ("h", ctypes.c_int), ("stride", ctypes.c_int),
                      ("bitmap", ctypes.POINTER(ctypes.c_ubyte)), ("color", ctypes.c_uint32),
                      ("dst_x", ctypes.c_int), ("dst_y", ctypes.c_int),
                      ("next", ctypes.POINTER(ASS_Image)), ("type", ctypes.c_int)]

_lib.ass_library_init.restype = ctypes.c_void_p
_lib.ass_renderer_init.restype = ctypes.c_void_p
_lib.ass_renderer_init.argtypes = [ctypes.c_void_p]
_lib.ass_set_frame_size.argtypes = [ctypes.c_void_p, ctypes.c_int, ctypes.c_int]
_lib.ass_set_storage_size.argtypes = [ctypes.c_void_p, ctypes.c_int, ctypes.c_int]
_lib.ass_set_fonts.argtypes = [ctypes.c_void_p, ctypes.c_char_p, ctypes.c_char_p, ctypes.c_int, ctypes.c_char_p, ctypes.c_int]
_lib.ass_read_memory.restype = ctypes.c_void_p
_lib.ass_read_memory.argtypes = [ctypes.c_void_p, ctypes.c_char_p, ctypes.c_size_t, ctypes.c_char_p]
_lib.ass_render_frame.restype = ctypes.POINTER(ASS_Image)
_lib.ass_render_frame.argtypes = [ctypes.c_void_p, ctypes.c_void_p, ctypes.c_longlong, ctypes.POINTER(ctypes.c_int)]
_lib.ass_free_track.argtypes = [ctypes.c_void_p]
_lib.ass_library_version.restype = ctypes.c_int

class Renderer:
    def __init__(self, w, h):
        self.lib = _lib.ass_library_init()
        self.r = _lib.ass_renderer_init(self.lib)
        self.w, self.h = w, h
        _lib.ass_set_frame_size(self.r, w, h)
        _lib.ass_set_storage_size(self.r, w, h)
        _lib.ass_set_fonts(self.r, None, b"Noto Sans", 1, None, 1)
    def version(self):
        return hex(_lib.ass_library_version())
    def render(self, ass_text, t_ms, want_rgba=False):
        """Render whole script at time t_ms. Returns (bbox, alpha_mask[, rgba]) over the frame."""
        buf = ass_text.encode("utf-8")
        tr = _lib.ass_read_memory(self.lib, buf, len(buf), None)
        ch = ctypes.c_int(0)
        img = _lib.ass_render_frame(self.r, tr, int(t_ms), ctypes.byref(ch))
        alpha = np.zeros((self.h, self.w), np.float32)
        rgba = np.zeros((self.h, self.w, 4), np.float32) if want_rgba else None
        x0 = y0 = 10**9; x1 = y1 = -1
        while img:
            im = img.contents
            if im.w > 0 and im.h > 0:
                bm = np.ctypeslib.as_array(im.bitmap, shape=(im.h, im.stride))[:, :im.w].astype(np.float32) / 255.0
                c = im.color
                a = (255 - (c & 0xFF)) / 255.0
                cov = bm * a
                ys, xs = im.dst_y, im.dst_x
                ye, xe = min(self.h, ys + im.h), min(self.w, xs + im.w)
                sub = cov[: ye - ys, : xe - xs]
                nz = np.argwhere(sub > 0.02)
                if len(nz):
                    x0 = min(x0, xs + nz[:, 1].min()); x1 = max(x1, xs + nz[:, 1].max())
                    y0 = min(y0, ys + nz[:, 0].min()); y1 = max(y1, ys + nz[:, 0].max())
                alpha[ys:ye, xs:xe] = sub + alpha[ys:ye, xs:xe] * (1 - sub)
                if want_rgba:
                    r_, g_, b_ = (c >> 24) & 255, (c >> 16) & 255, (c >> 8) & 255
                    reg = rgba[ys:ye, xs:xe]
                    for k, v in enumerate((r_, g_, b_)):
                        reg[..., k] = v / 255.0 * sub + reg[..., k] * (1 - sub)
                    reg[..., 3] = sub + reg[..., 3] * (1 - sub)
            img = im.next
        _lib.ass_free_track(tr)
        bbox = None if x1 < 0 else (int(x0), int(y0), int(x1) + 1, int(y1) + 1)
        return (bbox, alpha, rgba) if want_rgba else (bbox, alpha)
