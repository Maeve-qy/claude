# Sổ tay may vá tự làm

Repo gồm 2 tài liệu PDF, mỗi tài liệu có thư mục mã nguồn riêng để dựng lại.

| Tài liệu | File PDF | Mã nguồn |
|---|---|---|
| Khăn lau từ vải cũ (39 trang) | [`Khan_lau_tu_vai_cu_huong_dan_chi_tiet.pdf`](Khan_lau_tu_vai_cu_huong_dan_chi_tiet.pdf) | [`khan_lau/`](khan_lau/) |
| Túi dây rút có quai xách (49 trang) | [`Tui_day_rut_co_quai_huong_dan_chi_tiet.pdf`](Tui_day_rut_co_quai_huong_dan_chi_tiet.pdf) | [`nguon/`](nguon/) |

---

# Khăn lau từ vải cũ — hướng dẫn chi tiết cắt may

**File: [`Khan_lau_tu_vai_cu_huong_dan_chi_tiet.pdf`](Khan_lau_tu_vai_cu_huong_dan_chi_tiet.pdf)** (A4, 39 trang, có bookmark 3 cấp)

| Trang | Nội dung |
|---|---|
| 1–4 | Bìa, mục lục, 6 mẫu khăn, quy ước ký hiệu & thuật ngữ, mặt cắt khăn may lộn |
| 5–10 | **Phần 1 · Chọn vải**: 8 loại vải (thấm/bền/tưa sợi), 4 phép thử, vải nên tránh, sơ đồ tháo & xếp mẫu trên áo sơ mi, áo thun, jeans, khăn tắm (vẽ đúng tỉ lệ), phân loại vải thừa, sơ chế & canh sợi |
| 11–13 | **Phần 2 · Phối màu**: vòng màu, 4 cách phối, quy tắc 60–30–10, độ đậm nhạt, màu chỉ, mã màu theo khu vực, 6 bảng phối |
| 14–17 | **Phần 3 · Dụng cụ & kỹ thuật**: cài đặt máy, cắt bằng rập, kiểm tra đường chéo, xoay góc, cắt góc, diễu, chần, **vắt sổ khi nào cần/không cần** |
| 18–19 | **Phần 4 · Công thức**: 8 công thức tính kích thước cắt, cỡ chuẩn, bảng số miếng cắt được từ mỗi món đồ cũ |
| 20–35 | **6 mẫu**: giẻ áo thun, khăn lau bàn may lộn, khăn bếp gấp mép đôi (góc vát 45°), khăn ghép mảnh, khăn lau nhà 3 lớp bo viền, vỏ bàn lau nhà dẹt (tính theo số đo) |
| 36–39 | Giặt & bảo quản, lỗi thường gặp, bảng tổng hợp kích thước cắt, bảng kiểm, phiếu tính |

## Số đo chính
- Đường may chừa luôn **1 cm**, diễu **0,5 cm**. Kích thước ghi ngang × dọc (cm).
- Khăn lau bàn 30 × 30 → cắt 2 × **32 × 32**, khe lộn 8 cm.
- Khăn bếp treo 35 × 50, gấp mép 1 + 1 cm → cắt **39 × 54**; quai 5 × 14.
- Khăn ghép 3 × 3 ô → ô **12 × 12**, lớp sau 32 × 32.
- Khăn lau nhà 30 × 40, 3 lớp → cắt đúng TP; dải bo **7,5 cm** (= 6b + 2t + 0,5).
- Vỏ bàn lau (bàn 40 × 12, dày 1,5) → vỏ (L + h + 1,5) × (W + h + 1,5) = 43 × 15, cắt thân **45 × 17**, 2 túi **17 × 22**.

## Dựng lại PDF
```bash
pip install playwright pymupdf jsonschema fonttools brotli
cd khan_lau
python3 tools/validate.py                 # schema + công thức + sơ đồ xếp mẫu
python3 tools/render.py 51_m2             # xem thử 1 phần: build/png/*.png
python3 tools/build.py                    # dựng PDF ở thư mục gốc repo, có xác minh
python3 tools/qc.py status                # phần nào cần QC ngữ nghĩa lại
```
- `data/spec.json`: dữ liệu gốc (kích thước thành phẩm, vải, bảng màu...). Mọi số dẫn xuất do `tools/calc.py` tính, chèn vào trang qua `{{...}}`.
- `sections/*.html`: nội dung từng phần; `tools/figs.py`, `tools/art.py`: hình vẽ SVG sinh từ số liệu.
- `qc/ledger.json`: sổ QC ngữ nghĩa theo hash nội dung chữ — sửa layout không làm mất trạng thái đã QC.

---

# Túi dây rút có quai xách — hướng dẫn may chi tiết

**File chính: [`Tui_day_rut_co_quai_huong_dan_chi_tiet.pdf`](Tui_day_rut_co_quai_huong_dan_chi_tiet.pdf)** (A4, 49 trang)

| Trang | Nội dung |
|---|---|
| 1 | Bìa cũ (có dán nhãn "MỚI") |
| 2 | Mục lục |
| 3–25 | **Phần hướng dẫn mới, dễ hiểu**: có ảnh thật trích từ video (ghi giây) và sơ đồ vẽ đúng tỉ lệ, kèm kích thước |
| 26 | Phụ lục: các điểm bản cũ viết chưa đúng, đã sửa |
| 27–49 | Bản hướng dẫn cũ, giữ nguyên để tham khảo (đã đánh số lại trang) |

Nội dung phần mới:
- Chuẩn bị:
  - Phần 1: hiểu mẫu túi
  - Phần 2: chọn vải, vật liệu, dụng cụ
  - Phần 3: phối màu
  - Phần 4: rập, công thức và cách đổi cỡ
  - Phần 5: đo, vẽ và cắt vải
- May: 9 bước, từ thân ngoài, góc đáy, lót, quai, gắn quai, ráp miệng, lộn túi, diễu 3 đường đến luồn dây.
- Hoàn thiện:
  - có cần vắt sổ không
  - 8 lỗi hay gặp và cách sửa
  - bảng kiểm 1 trang để in ra

## Số đo chính (theo video)
- Thân: 30 × 25 cm, khoét 2 góc 5 × 5 cm, cắt 2 vải ngoài và 2 vải lót.
- Kênh dây: vạch 5 cm và 7 cm tính từ mép trên. Ở 2 sườn thân ngoài chừa khe 2 cm.
- Quai: 2 dải 30 × 8 cm, gấp 4 lớp thành quai rộng 2 cm. Mép trong chân quai đặt ở mốc 6 cm mỗi bên tâm.
- Đường may 1 cm. Thành phẩm **18 × 10 × 18 cm**, vòng miệng 56 cm, 2 dây rút mỗi dây 80 cm.

## Dựng lại PDF (tùy chọn)
Mã nguồn nằm trong `nguon/`: mỗi phần là 1 file HTML trong `nguon/sections/`, ảnh trích từ video ở `nguon/assets/`, dữ kiện chuẩn ở `nguon/FACTS.md`.

```bash
pip install playwright pymupdf
cd nguon
python3 render.py sections/60_than_lot.html   # xem thử 1 phần: out/*.png
python3 build.py ../Tui_day_rut_co_quai_huong_dan_chi_tiet.pdf
```
