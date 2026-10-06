# Thử VoiceStudio trên Mac mini M4

Ngày thử: 2026-10-04. Repo: [debpalash/VoiceStudio](https://github.com/debpalash/VoiceStudio), bản 0.5.6, commit `c4d63ef`, clone vào `~/workspace/VoiceStudio`.

## Kết luận

Máy chạy được VoiceStudio.

- Backend dùng GPU Metal của Apple (`device: mps`).
- Tôi đã tải model giọng nói mặc định (OmniVoice) và tạo thử ba clip. Cả ba đều thành công.
- Khi model đã nạp, tốc độ tạo chậm hơn thời gian thực khoảng 1,3–1,5 lần với 16 bước. Mức này đủ để dùng hằng ngày.
- Backend chiếm khoảng 4GB RAM, còn nhiều chỗ trống trên máy 24GB.

## Cấu hình máy

| Mục | Giá trị |
|---|---|
| Máy | Mac mini, chip M4 |
| RAM | 24GB |
| Hệ điều hành | macOS 27 |
| Công cụ | bun 1.3.11, uv 0.10.4, Python 3.11.14 |

## Các bước cài đặt

1. Clone repo, rồi cài thư viện JavaScript bằng `bun install`.
2. Cài thư viện Python bằng `bun run setup:api` (chạy `uv sync`). PyTorch 2.8 và MLX đều nhận GPU.
3. Chạy app bằng `bun run dev`. Backend FastAPI chạy ở cổng 3900, giao diện ở cổng 3902.
4. Tải model OmniVoice (3,27GB) và Whisper tiny (khoảng 80MB) trong Model Catalogue.

## Kết quả tạo giọng

Giọng dùng là profile demo, vốn là giọng tiếng Anh. Mỗi lần tạo dùng 16 bước, mức mặc định của trang Voice.

| Lần chạy | Thời gian tạo | Độ dài âm thanh |
|---|---|---|
| Lần đầu (gồm nạp model) | 24,0 giây | 6,0 giây |
| Tiếng Anh, model đã nạp | 7,67 giây | 5,74 giây |
| Tiếng Việt, model đã nạp | 7,17 giây | 4,74 giây |

Tôi cho Whisper tiny chép lời hai clip tiếng Anh, kết quả gần đúng từng chữ. Clip tiếng Việt thì cần bạn tự nghe, vì hai lý do. Thứ nhất, Whisper tiny nhận dạng tiếng Việt kém. Thứ hai, profile demo là giọng tiếng Anh, nên giọng tiếng Việt tạo ra sẽ mang âm sắc nước ngoài. Muốn đánh giá đúng chất lượng tiếng Việt, cần clone từ clip mẫu tiếng Việt, theo [voice-prep-guide-vietnamese.md](voice-prep-guide-vietnamese.md).

## Sự cố và cách khắc phục

Lần chạy đầu, Electron thoát ngay lúc khởi động. Nguyên nhân là VS Code đặt biến `ELECTRON_RUN_AS_NODE=1` cho terminal tích hợp, khiến Electron chạy như Node thuần thay vì mở cửa sổ app. Có hai cách khắc phục:

```bash
# Cách 1: bỏ biến khi chạy trong terminal của VS Code
env -u ELECTRON_RUN_AS_NODE bun run dev

# Cách 2: mở bằng Terminal.app, nơi không có biến này
cd ~/workspace/VoiceStudio && bun run dev
```

## Dữ liệu và giấy phép

- Các file âm thanh tạo ra được lưu tại `~/Library/Application Support/OmniVoice/outputs/`.
- App VoiceStudio dùng giấy phép AGPL-3.0, được phép dùng cả cho mục đích thương mại.
- Weights của model OmniVoice dùng giấy phép CC-BY-NC, tức là chỉ dùng phi thương mại. Audio tokenizer còn có thêm điều khoản riêng của Higgs Audio 2 và Llama.
- Chỉ clone giọng của bạn hoặc của người đã đồng ý.

## Phụ lục: so sánh 16 và 32 bước

Đo cùng ngày với câu tiếng Việt, profile demo, seed 42, khi model đã nạp.

| Steps | Thời gian tạo | Độ dài âm thanh |
|---|---|---|
| 16 | 6,8 giây | 4,7 giây |
| 32 | 12,7 giây | 4,7 giây |

Phân tích chi tiết và lý do nên dùng 32 bước cho tiếng Việt nằm trong [261004-research-best-practices.md](261004-research-best-practices.md).

## Câu hỏi còn mở

- Chưa đánh giá được chất lượng tiếng Việt khi clone từ chính giọng của bạn. Bước này cần clip mẫu thật.
- Chưa thử engine VoxCPM2 và model Whisper large-v3, vì cả hai chưa được tải.
