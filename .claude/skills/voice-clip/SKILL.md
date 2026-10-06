---
name: voice-clip
description: Biến các bản thu trong recordings/ thành clip mẫu đạt chuẩn và profile giọng trong VoiceStudio. Dùng khi người dùng vừa thu âm xong, muốn chọn take, kiểm tra clip, viết transcript hoặc tạo profile.
---

# Từ bản thu đến profile

Bạn không nghe được âm thanh. Mọi nhận xét dựa trên số đo của script và phải nói rõ điều đó.

## 1. Đưa bản thu về đúng định dạng

Nếu `recordings/` còn trống, người dùng chưa thu. Chỉ họ sang [docs/recording-session.md](../../../docs/recording-session.md); thu trực tiếp bằng `record.py` cần họ bấm phím nên bạn không chạy thay được.

Bản thu iPhone chứa nhiều lần đọc của một câu thì tách bằng:

```bash
uv run scripts/record.py --from-file <bản-thu> --sentences <số câu>
```

Bản thu chưa phải WAV mono (ví dụ M4A từ iPhone), còn khoảng lặng hai đầu, hoặc là một file dài chứa nhiều câu thì chạy:

```bash
uv run scripts/prep-clip.py <bản-thu> recordings/<phong-cach>-<so-cau>-take<lan>.wav [--start S --end S]
```

Tên phong cách: `tro-chuyen`, `ke-chuyen`, `doc-tin`, `nang-dong`, `cam-xuc`, `nhe-nhang`. Số câu theo [docs/recording-script-vietnamese.md](../../../docs/recording-script-vietnamese.md). Không ghi đè file gốc; nếu cần `--start`/`--end` mà không biết mốc thời gian thì hỏi người dùng.

## 2. Đo và xếp hạng

```bash
uv run scripts/check-clip.py --asr --json recordings/
```

- Clip `LỖI` (vỡ tiếng, quá dài, quá ngắn, tần số mẫu thấp) thì không dùng. Vỡ tiếng phải thu lại, không sửa được.
- Trong các take của cùng một câu, ưu tiên take `ĐẠT`, rồi đến DNSMOS tổng cao hơn, nền thấp hơn.
- Nếu nền ồn hoặc DNSMOS nền kém ở mọi take, vấn đề là phòng thu. Đề nghị thu lại theo mục "Phòng thu" của [docs/voice-prep-guide-vietnamese.md](../../../docs/voice-prep-guide-vietnamese.md). Không đề nghị khử ồn.
- `--asr` cần Whisper large-v3. Nếu chưa có, bỏ `--asr` và nói rằng bước soát transcript sẽ dựa vào người dùng.

## 3. Soát transcript

Đây là việc bạn làm tốt hơn script. Với take được chọn:

1. Lấy câu gốc trong kịch bản ghi âm theo số câu trong tên file.
2. So với dòng "nghe được" của Whisper. Whisper hay sai dấu thanh và viết số thành chữ số, nên khác biệt nhỏ về dấu chưa chắc là người đọc sai.
3. Nếu khác ở cấp độ từ (thêm, bớt, đổi từ), khả năng cao người dùng đã đọc khác kịch bản. Hỏi người dùng họ đã đọc gì, rồi dùng đúng lời đã đọc. Transcript phải khớp tiếng trong clip, không phải khớp kịch bản.
4. Transcript cuối: đủ dấu thanh, dấu câu theo chỗ ngắt hơi, số viết thành chữ, không có chữ số.

## 4. Tạo profile

Nêu cho người dùng take bạn chọn, số đo chính và transcript, rồi tạo:

```bash
uv run scripts/make-profile.py <tên><NN> recordings/<clip>.wav "<transcript>"
```

Tên theo quy ước `<tên>NN`: xem `curl -s http://127.0.0.1:3900/profiles` để lấy số tiếp theo. Tạo xong, thêm một dòng (tên, id, phong cách, clip mẫu) vào bảng trong `docs/profiles.local.md` (file chỉ lưu ở máy; mẫu ở mục 6 của [docs/operations-guide.md](../../../docs/operations-guide.md)).

Script đặt Language là Vietnamese và từ chối clip `LỖI`. Chỉ thêm `--force` khi người dùng yêu cầu.

## 5. Thử ngay

Chạy các câu kiểm tra thanh điệu trong kịch bản bằng skill `voice-speak`, rồi đưa đường dẫn `final.wav` để người dùng nghe. Nhắc người dùng xác nhận consent trong app nếu app yêu cầu.

## Báo cáo

Một bảng: take, kết luận, độ dài, đỉnh, nền, DNSMOS tổng. Sau đó là take được chọn cho mỗi câu, transcript, id của profile, và việc người dùng cần làm tiếp (nghe file nào).
