# my-voice-studio

Repo này chứa tài liệu và công cụ để clone giọng tiếng Việt của chủ repo. Lõi là app VoiceStudio ở `~/workspace/VoiceStudio` (không sửa repo đó). Các script ở đây gọi API của nó tại `http://127.0.0.1:3900`.

Trả lời bằng tiếng Việt. Đọc [docs/operations-guide.md](docs/operations-guide.md) trước khi làm việc gì liên quan đến tạo giọng.

## Vai trò của Claude trong workflow

Claude không nghe được âm thanh. Mọi nhận xét về audio phải dựa trên số đo của script, và phải nói rõ điều đó. Người dùng là người nghe và quyết định cuối cùng.

| Việc | Ai làm |
|---|---|
| Thu âm, nghe, chọn bản ưng ý, xác nhận consent trong app | Người dùng |
| Đo clip, tạo giọng, chép lời lại, chấm điểm | Script trong `scripts/` |
| Chọn take từ số đo, soát transcript với kịch bản, viết lại văn bản cho model đọc, chia đoạn, phân biệt lỗi chép lời với chữ bị nuốt thật, quyết định tạo lại hay viết lại, tóm tắt kết quả A/B | Claude |

Ba skill ứng với ba giai đoạn: `voice-clip` (bản thu → profile), `voice-speak` (văn bản → audio), `voice-compare` (so cấu hình, engine, clip mẫu).

## Lệnh

Chạy từ thư mục gốc của repo. Lần đầu chạy `uv sync`.

```bash
uv run scripts/record.py [--test | --sentences 1-5 | --from-file <bản-thu> --sentences <số câu>]
uv run scripts/prep-clip.py <bản-thu> recordings/<phong-cach>-<so-cau>-take<lan>.wav
uv run scripts/check-clip.py [--asr] recordings/
uv run scripts/make-profile.py <tên> <clip.wav> "<transcript>"
uv run scripts/normalize-vi.py "<văn bản>"
uv run scripts/speak.py <profile_id> -f <file.txt>
uv run scripts/speak.py --redo outputs/speak-<thời gian> <số đoạn> [--text "<viết lại>"]
scripts/ab-test.sh <profile_id> "<câu>" "<engines>" "<steps>"
uv run scripts/score.py outputs/<thư mục> --profile <profile_id>
uv run scripts/check-words.py --manifest <cau.json>
uv run scripts/word-times.py <câu.wav> --text "<chữ đã gửi đi>"
uv run scripts/check-watermark.py <file audio hoặc video>...
```

Nếu API chưa chạy, bật riêng backend ở chế độ nền, không cần mở cửa sổ app:

```bash
cd ~/workspace/VoiceStudio && bun run dev:api
```

`record.py` ở chế độ thu trực tiếp cần người dùng bấm phím, nên Claude không chạy được. Hướng dẫn người dùng chạy theo [docs/recording-session.md](docs/recording-session.md). Chế độ `--from-file` thì Claude chạy được.

## Quy tắc

- Giọng nói là dữ liệu sinh trắc học. Không `git add` file audio, không gửi audio hay clip mẫu ra dịch vụ bên ngoài, không đẩy `recordings/` hay `outputs/` lên remote nào.
- Đặt tên profile theo quy ước `<tên>NN` (tên người, rồi số thứ tự theo thứ tự tạo, ví dụ `lan01`). Mỗi lần tạo profile, thêm một dòng vào bảng trong `docs/profiles.local.md` theo mẫu ở mục 6 của [docs/operations-guide.md](docs/operations-guide.md). File đó và `CLAUDE.local.md` chỉ lưu ở máy.
- Không đưa tên profile thật, id profile hay chi tiết máy của người dùng vào file được Git theo dõi.
- Chỉ tạo profile từ giọng của chủ repo hoặc của người đã đồng ý bằng văn bản.
- Không tải model mới (VoxCPM2, dots.tts, model gióng của WhisperX) khi chưa hỏi. Whisper large-v3 MLX đã có. Mỗi model nặng vài GB.
- Không xóa profile, clip trong `recordings/` hay kết quả trong `outputs/` khi chưa hỏi.
- Điểm giống giọng của `score.py` đến từ model huấn luyện trên tiếng Anh. Chỉ dùng để so tương đối, không kết luận "giống" hay "không giống" từ một con số.
- Các ngưỡng nền ồn và DNSMOS trong `check-clip.py` là ước lượng. Ngưỡng độ dài, định dạng và mức âm lấy từ [docs/voice-prep-guide-vietnamese.md](docs/voice-prep-guide-vietnamese.md).
