# JLPT N1 聴解 tháng 7/2026 — 問題5: video Full HD luyện 満点

Bài luyện dựng từ video nguồn `2026.07.mp4` (đề nghe N1 07/2026 do kênh @LuyendeJLPTcungto dựng lại). Chỉ dùng phần **問題5 (統合理解)**: từ 36:00.80 đến 42:19.40 của video nguồn.

## Các file

| File | Nội dung |
|---|---|
| [`{VIDEO_NAME}`]({VIDEO_NAME}) | **Video 1920×1080**, {VIDEO_DUR}, H.264 + AAC, có chương. {VIDEO_MB} MB |
| [`2026.07.vi.ass`](2026.07.vi.ass) | Phụ đề song ngữ **Nhật trên – Việt dưới**, không có thẻ học. Khớp thời gian với video gốc `2026.07.mp4` |
| [`2026.07.vi-ja-study.ass`](2026.07.vi-ja-study.ass) | Cùng phụ đề song ngữ đó + **60 thẻ học** (furigana thật phía trên kanji, [HÁN VIỆT], nghĩa tiếng Việt). Dữ liệu đối soát nằm trong các dòng Comment |
| [`build/`](build/) | Mã nguồn để dựng lại: lời thoại đã khóa, thẻ học, căn thời gian, dàn trang, kiểm tra, dựng video |

## Cấu trúc video

| Thời điểm | Chương |
|---|---|
{CHAPTERS}

Cách luyện gợi ý: ở **Lượt 1**, tự ghi chú và chọn đáp án. Sau đó xem phần đáp án. Cuối cùng học kỹ ở **Lượt 2**, có thể tạm dừng để đọc từng thẻ.

## Đáp án 問題5

- **1番 → 4** ベンチを設置する. Phương án 1 và 2 (sự kiện) bị chê 「一時的な効果しかない」 rồi bị hoãn: 「様子を見てから」. Phương án 3 (ポイント制) bị loại vì 「スーパーがもうやってる」. Ghế băng thì 「すぐにでもできます」.
- **2番 質問1 → 1** (コース1): nam sinh viên muốn khóa 「選手としての自分の経験を生かせる」 và quan tâm 「心の状態」, tức スポーツ心理.
- **2番 質問2 → 3** (コース3): với nữ sinh viên, việc dạy trẻ em chỉ là 「将来の保険」. Cô muốn tạo 「色んな世代の人がスポーツを楽しめる場」, khớp với 幅広い世代の健康づくり.

Đáp án trên khớp bảng đáp án ở cuối video nguồn (2026年7月N1聴解正解表).

## Phụ đề và thẻ học

- **83 cặp Nhật–Việt.** Mỗi cặp có 1 dòng JA và 1 dòng VI, cùng thời gian. Có nhãn người nói: 女1/女2/男 ở 1番, 先生/女の学生/男の学生 ở 2番.
- **60 thẻ học**: 43 từ/cụm từ và 17 mẫu ngữ pháp hoặc diễn ngôn.
  - 50 thẻ có kanji: đủ furigana và [HÁN VIỆT].
  - 10 thẻ chỉ có kana: ghi "CHỈ KANA", không bịa âm Hán Việt.
  - 40 ứng viên khác đã xét rồi loại, lý do ghi trong Comment của file học.
- Mỗi thẻ hiện đúng lúc bắt đầu câu chứa nó, không bị dời trễ. Mỗi mục được nhìn rõ ít nhất 4 giây.
- Cỡ chữ ở 1080p: JA 58, VI 64, chữ trên thẻ 50, ruby 28, nhãn 26, Hán Việt 34, nghĩa 36. Các cỡ này đều lớn hơn mức sàn của master prompt.
- Font cần có: **Noto Sans CJK JP** và **Noto Sans**.

Mở phụ đề cùng video gốc, ví dụ với mpv:

```bash
mpv --sub-file=2026.07.vi-ja-study.ass 2026.07.mp4
```

Hãy tua tới khoảng 36:00. Phụ đề chỉ có cho phần 問題5.

## Phạm vi kiểm chứng (nói rõ)

- **Lời Nhật** dựa vào âm thanh, đối chiếu bằng máy. Không có người nghe duyệt trực tiếp. Các bước đã làm:
  - Nhận dạng âm thanh bằng Whisper small (CTranslate2), giải mã tự do và căn chỉnh cưỡng bức.
  - Chấm điểm từng phương án tranh chấp so với âm thanh.
  - Đối chiếu với script hiện trên video nguồn (lúc 39:00 và 42:21).
  - Phân tích âm học: đường năng lượng, cao độ F0, phổ âm đầu.
- **Những chỗ script trên video nguồn khác âm thanh**, phụ đề theo âm thanh:

  | Script nguồn | Phụ đề |
  |---|---|
  | 1つケーキ付けに | ひとつ景気付けに |
  | 一時に的な | 一時的な |
  | プロ似って | プロにって |
  | イベントとかは | イベントとか |
  | それじゃ | それじゃあ |
  | という | っていう |
  | うん、継続性 | うーん、継続性 |
  | ふーん | うーん |

  Chữ hiện trên slide hướng dẫn cũng khác lời đọc, ví dụ 「メモとても」 so với 「問題用紙にメモを取っても」.
- **Thời gian**: căn theo từng câu, chưa căn tới từng từ. Điểm đầu và cuối mỗi câu bám theo đường năng lượng âm thanh thật.
- **Cách đọc và từ loại** lấy từ JMdict. **Âm Hán Việt** lấy từ KANJIDIC2, đối chiếu thêm Unihan 17.0 bằng dạng chữ cũ khi cần (ví dụ 択 → 擇 TRẠCH). Thi Viện và Mazii không truy cập được từ môi trường dựng, nên chưa đối chiếu hai nguồn này.
- **Nhãn cấp N1/N2 không hiển thị** vì không có nguồn cấp độ truy cập được. Thẻ dùng nhãn chức năng: TỪ VỰNG, NGỮ PHÁP, KHẨU NGỮ, QUÁN NGỮ, SẮC THÁI, ÔN NỀN.
- **Kiểm tra file**: đọc lại cả hai ASS từ đĩa và render lại bằng libass 0.17.1 trên khung 1920×1080.
  - Các cổng G1, G3, G4, G5, G6 và G7 (hình học) đều PASS.
  - JA và VI giữa hai file giống hệt nhau.
  - Ruby nằm trên và căn giữa đúng chữ. Không có va chạm giữa khung phụ đề, các thẻ và vùng chữ quan trọng của slide.
  - Đã xem ảnh ghép cho đủ 83 cặp và 37 khung thẻ.
- **Ghi chú bố cục**:
  - 3 khung thẻ che một phần hình nhân vật trang trí ở góc phải.
  - Ở 2番, khi giảng viên và hai sinh viên đang nói, thẻ có lúc che tạm danh sách コース1–4.
  - Từ lúc đọc 質問1/質問2 trở đi, danh sách コース1–4 luôn hiện đủ.

## Toàn vẹn file

| File | Byte | SHA-256 |
|---|---|---|
{HASHES}

## Dựng lại

Cần ffmpeg (có libass), Python 3, Pillow, numpy, font Noto Sans CJK JP và Noto Sans. `build/timing.json` đã lưu kết quả căn thời gian, nên không cần model nhận dạng giọng nói.

```bash
cd build
python3 layout_m5.py timing.json ../out
```

```bash
python3 qc_m5.py ../out ../out/qc_report.json
```

```bash
python3 video_m5.py /path/to/2026.07.mp4 ../out ../work ../out/video.mp4
```

Bước căn thời gian lại từ âm thanh (`timing_m5.py`, `fa.py`) cần thêm `faster-whisper` và model Whisper small dạng CTranslate2.
