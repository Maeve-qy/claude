# -*- coding: utf-8 -*-
"""ASS scripts for the generated (non-source) segments of the practice video: title, strategy,
answer + explanation for 1番 and 2番, summary; plus the pass label overlays. Text is wrapped with libass measurement."""
import os, re, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from assr import Renderer

W, H = 1920, 1080
STY = [
    # name, font, size, primary, outline colour, outline, bold
    ("Box", "Noto Sans", 20, "&H00201A14", "&H00000000", 0, 0),
    ("HJ", "Noto Sans CJK JP", 84, "&H00FFFFFF", "&H00101010", 0, 1),
    ("HV", "Noto Sans", 54, "&H0070C8F5", "&H00101010", 0, 1),
    ("B", "Noto Sans", 40, "&H00F0F0F0", "&H00101010", 0, 0),
    ("Q", "Noto Sans", 36, "&H00DCEEF4", "&H00101010", 0, 0),
    ("S", "Noto Sans", 28, "&H00B4B4B4", "&H00101010", 0, 0),
    ("Chip", "Noto Sans", 30, "&H00161210", "&H00101010", 0, 1),
    ("Lbl", "Noto Sans", 28, "&H00161210", "&H00101010", 0, 1),
]


def header():
    s = ["[Script Info]", "ScriptType: v4.00+", f"PlayResX: {W}", f"PlayResY: {H}", "WrapStyle: 2",
         "ScaledBorderAndShadow: yes", "YCbCr Matrix: TV.709", "", "[V4+ Styles]",
         "Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, "
         "Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, "
         "MarginR, MarginV, Encoding"]
    for n, f, z, p, o, ol, b in STY:
        s.append(f"Style: {n},{f},{z},{p},&H000000FF,{o},&H00000000,{-1 if b else 0},0,0,0,100,100,0,0,1,{ol},0,7,0,0,0,1")
    s += ["", "[Events]", "Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text"]
    return "\n".join(s) + "\n"


CJK = re.compile(r"[　-ヿ一-鿿＀-￯〜・「」]+")


def mix(text, base="Noto Sans"):
    """wrap CJK runs with an explicit Japanese font switch (no reliance on fallback)."""
    return CJK.sub(lambda m: "{\\fnNoto Sans CJK JP}" + m.group(0) + "{\\fn" + base + "}", text)


_R = Renderer(4000, 1200)
_H = header().replace(f"PlayResX: {W}", "PlayResX: 4000").replace(f"PlayResY: {H}", "PlayResY: 1200")


def width(style, text):
    b, _ = _R.render(_H + f"Dialogue: 0,0:00:00.00,0:00:05.00,{style},,0,0,0,,{{\\an7\\pos(100,100)}}{mix(text)}\n", 1000)
    return 0 if b is None else b[2] - b[0]


def wrap(style, text, maxw):
    toks = re.findall(r"「[^」]*」[、。,.]?|\S+", text)
    lines, cur = [], ""
    for t in toks:
        cand = (cur + " " + t) if cur else t
        if width(style, cand) <= maxw:
            cur = cand
        else:
            assert cur, ("token too wide", t)
            lines.append(cur); cur = t
    if cur: lines.append(cur)
    for l in lines:
        assert width(style, l) <= maxw, l
    return lines


def ts(t):
    cs = int(round(t * 100))
    return f"{cs // 360000}:{(cs // 6000) % 60:02d}:{(cs // 100) % 60:02d}.{cs % 100:02d}"


def rr(w, h, r):
    k = 0.5523 * r
    f = lambda v: f"{round(v, 1):g}"
    return (f"m {f(r)} 0 l {f(w - r)} 0 b {f(w - r + k)} 0 {f(w)} {f(r - k)} {f(w)} {f(r)} l {f(w)} {f(h - r)} "
            f"b {f(w)} {f(h - r + k)} {f(w - r + k)} {f(h)} {f(w - r)} {f(h)} l {f(r)} {f(h)} b {f(r - k)} {f(h)} 0 "
            f"{f(h - r + k)} 0 {f(h - r)} l 0 {f(r)} b 0 {f(r - k)} {f(r - k)} 0 {f(r)} 0")


class Card:
    def __init__(self, dur):
        self.dur, self.ev = dur, []

    def text(self, t0, style, x, y, txt, an=7, extra="", layer=2):
        self.ev.append(f"Dialogue: {layer},{ts(t0)},{ts(self.dur)},{style},,0,0,0,,"
                       f"{{\\an{an}\\pos({x},{y})\\fad(300,0){extra}}}{mix(txt)}")

    def box(self, t0, x, y, w, h, color="&H201A14&", alpha="&H20&", r=18, layer=1):
        self.ev.append(f"Dialogue: {layer},{ts(t0)},{ts(self.dur)},Box,,0,0,0,,"
                       f"{{\\an7\\pos({x},{y})\\fad(300,0)\\1c{color}\\1a{alpha}\\p1}}{rr(w, h, r)}{{\\p0}}")

    def chip(self, t0, x, y, label, color, style="Chip", h=48):
        w = width(style, label) + 36
        self.box(t0, x, y, w, h, color=color, alpha="&H00&", r=12, layer=2)
        self.text(t0, style, x + w / 2, y + h / 2, label, an=5, layer=3)
        return w

    def para(self, t0, style, x, y, txt, maxw, lh):
        lines = wrap(style, txt, maxw)
        for i, l in enumerate(lines):
            self.text(t0, style, x, y + i * lh, l)
        return y + len(lines) * lh

    def write(self, path):
        with open(path, "w", encoding="utf-8-sig", newline="\n") as f:
            f.write(header() + "\n".join(self.ev) + "\n")


AMBER, GREEN, RED, BLUE, PINK = "&H6EC8F5&", "&H8CDC9A&", "&H7C7CF0&", "&HF0C878&", "&HC8A0F0&"


def title_card(path):
    c = Card(6.0)
    c.text(0.0, "S", 160, 150, "JLPT N1 · 聴解 · 日本語能力試験 2026年7月")
    c.text(0.2, "HJ", 160, 230, "問題5　統合理解", extra="\\fs110")
    c.text(0.5, "HV", 160, 400, "Luyện nghe hướng tới 満点")
    y = 520
    for i, (lab, col, txt) in enumerate([("LƯỢT 1", AMBER, "Nghe như thi thật — tự chọn đáp án"),
                                         ("ĐÁP ÁN", GREEN, "Đáp án & giải thích từ lời thoại"),
                                         ("LƯỢT 2", BLUE, "Học kỹ: phụ đề Nhật trên – Việt dưới + 60 thẻ từ vựng/ngữ pháp")]):
        w = c.chip(0.9 + i * 0.4, 160, y, lab, col)
        c.text(0.9 + i * 0.4, "B", 160 + w + 24, y + 2, txt)
        y += 76
    c.text(1.6, "S", 160, 930, "Âm thanh & slide: video “2026.07” (@LuyendeJLPTcungto). Phụ đề, thẻ học và giải thích: biên soạn cho bài luyện này.")
    c.write(path)
    return c.dur


def strategy_card(path):
    c = Card(17.0)
    c.text(0.0, "HV", 140, 90, "Chiến lược 問題5 (統合理解)")
    y = 210
    blocks = [("1番", AMBER, "Hội thoại 3 người, đề không in gì. Ghi nhanh: AI đề xuất GÌ → ai phản đối, vì sao → KẾT LUẬN cuối cùng."),
              ("2番", BLUE, "Một người trình bày 4 lựa chọn → ghi 4 dòng từ khóa. Sau đó hai người bàn → nối mong muốn của TỪNG người với một dòng. Hai câu hỏi chỉ được đọc ở cuối."),
              ("BẪY", RED, "Phương án bị bác hoặc bị hoãn (「様子を見てから」), chi tiết gây nhiễu, và cách nói lại bằng từ khác (言い換え).")]
    for i, (lab, col, txt) in enumerate(blocks):
        t0 = 0.6 + i * 3.0
        w = c.chip(t0, 140, y, lab, col)
        yb = c.para(t0, "B", 140 + w + 28, y + 2, txt, 1680 - w - 60, 54)
        y = max(yb, y + 60) + 46
    c.text(10.0, "Q", 140, 900, "Lượt 1: hãy tự chọn đáp án trước khi xem phần giải thích.", extra="\\1c&H6EC8F5&")
    c.write(path)
    return c.dur


def answer1_card(path):
    c = Card(38.0)
    w = c.chip(0.0, 110, 56, "1番 · ĐÁP ÁN", GREEN)
    c.text(0.0, "HV", 110 + w + 30, 46, "4　ベンチを設置する  (lắp đặt ghế băng)")
    c.text(0.4, "Q", 110, 140, "Q: この商店街では、まずどんな工夫をすることにしましたか。")
    c.text(0.4, "S", 110, 188, "Trước tiên, khu phố mua sắm này quyết định áp dụng biện pháp nào?")
    y = 262
    rows = [(3.0, "LOẠI", RED, "1 祭りを企画する ・ 2 セールを実施する",
             "男 đề xuất sự kiện (祭り, 格安セール) → 女2: 「一時的な効果しかないんじゃないですか」 → 女1 chốt: 「イベントは様子を見てからまた検討しましょう」 = hoãn lại."),
            (11.0, "LOẠI", RED, "3 ポイント制を導入する",
             "男: 「スーパーがもうやってるからなあ」 + 女1: 「同じことをしてもね」 = làm giống siêu thị thì vô ích."),
            (19.0, "CHỌN", GREEN, "4 ベンチを設置する",
             "女2: 「商店街のあちこちにベンチを置いたらどうでしょう。すぐにでもできますよね」 → 女1: 「人が自然に集まるようになれば、商店街も活気づきますね」.")]
    for t0, lab, col, head, txt in rows:
        cw = c.chip(t0, 110, y, lab, col)
        c.text(t0, "B", 110 + cw + 24, y + 1, head, extra="\\b1")
        y = c.para(t0, "Q", 140, y + 66, txt, 1660, 48) + 34
    tip = "Mẹo 満点: chú ý 「まず」 trong câu hỏi = việc làm TRƯỚC TIÊN. Phương án bị hoãn (様子を見てから) hay bị bác đều loại."
    n = len(wrap("Q", tip, 1680))
    c.box(27.0, 90, y - 6, 1740, n * 46 + 34, color="&H3A2A18&", alpha="&H10&")
    c.para(27.0, "Q", 120, y + 10, tip, 1680, 46)
    c.write(path)
    return c.dur


def answer2_card(path):
    c = Card(52.0)
    w = c.chip(0.0, 110, 50, "2番 · ĐÁP ÁN", GREEN)
    c.text(0.0, "HV", 110 + w + 30, 40, "質問1 → 1 (コース1) ・ 質問2 → 3 (コース3)")
    c.text(0.6, "S", 110, 132, "Ghi chú khi nghe giảng viên (4 dòng từ khóa):")
    notes = [("コース1", "指導者 cho VĐV hướng tới chuyên nghiệp ・ トレーニングのノウハウ ・ スポーツ心理"),
             ("コース2", "指導者 thể thao cho HS tiểu học, THCS ・ đặc điểm thể chất & tâm lý"),
             ("コース3", "健康づくり cho 幅広い世代 (trẻ em → người lớn) ・ quản lý 運動施設"),
             ("コース4", "運動指導 cho 高齢者 ・ nhu cầu HLV chuyên tăng")]
    y = 182
    for i, (k, v) in enumerate(notes):
        t0 = 1.5 + i * 1.5
        c.text(t0, "Q", 130, y, k, extra="\\1c&H6EC8F5&\\b1")
        c.text(t0, "Q", 300, y, v)
        y += 52
    y += 24
    q = [(14.0, "質問1 · 男の学生 → 1", BLUE,
          "「選手としての自分の経験を生かせるコース」 + 「プレイヤーの気持ちとか、心の状態みたいなものにも興味ある」 ⇒ đào tạo 指導者 cho VĐV + スポーツ心理 = コース1."),
         (27.0, "質問2 · 女の学生 → 3", PINK,
          "「子供の指導」 chỉ là 「将来の保険」, 「特に夢ってわけじゃない」 ⇒ loại コース2. 「色んな世代の人がスポーツを楽しめる場」 = 幅広い世代の健康づくり ⇒ コース3.")]
    for t0, lab, col, txt in q:
        cw = c.chip(t0, 110, y, lab, col)
        y = c.para(t0, "Q", 140, y + 64, txt, 1660, 48) + 30
    trap = "Bẫy: chuyện mẹ đi 運動教室 dễ kéo sang コース4 (高齢者), nhưng mong muốn của cô ấy là cho MỌI thế hệ (色んな世代)."
    n = len(wrap("Q", trap, 1680))
    c.box(40.0, 90, y - 6, 1740, n * 46 + 34, color="&H3A2A18&", alpha="&H10&")
    c.para(40.0, "Q", 120, y + 10, trap, 1680, 46)
    c.write(path)
    return c.dur


def end_card(path):
    c = Card(10.0)
    c.text(0.0, "HV", 140, 150, "Tổng kết 問題5")
    c.text(0.3, "HJ", 140, 260, "1番 → 4　・　2番 質問1 → 1　・　質問2 → 3", extra="\\fs64")
    c.text(1.0, "B", 140, 400, "Khớp với bảng đáp án ở cuối video nguồn (2026年7月N1聴解正解表).")
    c.text(1.6, "B", 140, 470, "Ôn lại 60 thẻ từ vựng/ngữ pháp trong Lượt 2 — tạm dừng video để đọc kỹ từng thẻ.")
    c.text(2.2, "S", 140, 900, "Âm thanh & slide: video “2026.07” (@LuyendeJLPTcungto). Phụ đề Nhật–Việt, thẻ học, giải thích: biên soạn cho bài luyện này.")
    c.write(path)
    return c.dur


def pass_label(path, dur, label, color):
    c = Card(dur)
    w = width("Lbl", label) + 36
    c.ev.append(f"Dialogue: 5,{ts(0)},{ts(dur)},Box,LABEL.BOX,0,0,0,,{{\\an7\\pos(24,16)\\1c{color}\\1a&H18&\\p1}}{rr(w, 46, 12)}{{\\p0}}")
    c.ev.append(f"Dialogue: 6,{ts(0)},{ts(dur)},Lbl,LABEL,0,0,0,,{{\\an5\\pos({24 + w / 2},{16 + 23})}}{mix(label)}")
    c.write(path)
