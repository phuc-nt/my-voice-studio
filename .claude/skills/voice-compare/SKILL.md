---
name: voice-compare
description: So sánh có kiểm soát giữa các cấu hình tạo giọng trong VoiceStudio (số bước, engine như OmniVoice và VoxCPM2, clip mẫu hoặc profile khác nhau) và tóm tắt bằng số đo. Dùng khi người dùng hỏi cấu hình, engine hay clip nào tốt hơn, hoặc muốn chạy A/B.
---

# So sánh A/B

Mỗi lần chỉ đổi một yếu tố. Giữ nguyên câu, seed và mọi thứ còn lại.

## 1. Chọn câu thử

Dùng các "câu kiểm tra" ở cuối [docs/recording-script-vietnamese.md](../../../docs/recording-script-vietnamese.md): thanh điệu, năm, tiền, viết tắt, từ tiếng Anh. Thêm một câu thật từ nội dung người dùng định làm. Một câu là chưa đủ để kết luận; dùng ít nhất ba câu và hai seed.

## 2. Chạy

So số bước hoặc engine:

```bash
scripts/ab-test.sh <profile_id> "<câu>" "omnivoice voxcpm2" "16 32" <seed>
```

So clip mẫu: tạo một profile cho mỗi clip bằng skill `voice-clip`, rồi chạy cùng lệnh với từng `profile_id`.

Engine chưa tải sẽ trả lỗi HTTP. Hỏi người dùng trước khi đề nghị tải, vì mỗi engine nặng vài GB.

## 3. Chấm điểm

```bash
uv run scripts/score.py outputs/ab-<thời gian> --profile <profile_id>
```

Các cột: `giống` là độ giống clip mẫu (cosine của vector giọng), `giọng`/`nền`/`tổng` là DNSMOS, `sai` là tỉ lệ chữ khác với văn bản gốc, `thiếu` là chữ bị nuốt.

## 4. Diễn giải

- Điểm giống đến từ model huấn luyện trên tiếng Anh. Chỉ so tương đối trong cùng một giọng. Chênh dưới khoảng 0,02 thì coi như ngang nhau.
- Khi so OmniVoice (24 kHz) với VoxCPM2 (48 kHz), DNSMOS đo ở 16 kHz nên không thấy được lợi thế về dải tần.
- Cột `sai` phụ thuộc Whisper. Lỗi đồng âm là của Whisper, cụm từ bị thiếu mới là của model.
- Ghi thời gian tạo từ `results.tsv`, vì cấu hình tốt hơn nhưng chậm gấp đôi là một đánh đổi người dùng cần biết.
- Số đo chỉ để loại cấu hình rõ ràng kém. Giữa các cấu hình còn lại, người dùng nghe và chọn. Đưa đường dẫn từng file cho họ.

## Báo cáo

Một bảng gộp mọi câu: cấu hình, giống, tổng, sai, thời gian tạo. Sau đó là một câu kết luận về cấu hình nào bị loại và vì sao, và danh sách file cần nghe để chọn giữa các cấu hình còn lại. Nếu kết quả cho thấy một khuyến nghị trong `docs/` không còn đúng, nêu ra và đề nghị sửa tài liệu.
