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
