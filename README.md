# my-voice-studio

Tài liệu và công cụ để clone giọng tiếng Việt của chính bạn bằng [VoiceStudio](https://github.com/debpalash/VoiceStudio). Mọi thứ chạy trên máy của bạn; bộ công cụ được thử trên Mac mini M4.

## Tóm tắt

- VoiceStudio 0.5.6 chạy được trên Mac mini M4 24GB, dùng GPU Metal. Khi model đã nạp, mỗi câu khoảng 5 giây mất 7 giây (16 bước) hoặc 13 giây (32 bước).
- Kết quả clone phụ thuộc nhiều nhất vào clip mẫu. Clip tốt là clip tiếng Việt dài 3–10 giây, thu ở phòng không vang, có transcript khớp từng chữ.
- Khi tạo giọng, hãy chọn Language Vietnamese, dùng 32 bước, và chia văn bản thành từng đoạn dưới 30 giây.

## Bắt đầu từ đâu

Người mới, hoặc agent được giao cài đặt từ đầu: đọc [docs/gioi-thieu.md](docs/gioi-thieu.md). File đó giới thiệu VoiceStudio, phần repo này bổ sung, cách cài và cách tạo profile giọng của chính mình.

Đã cài xong thì theo ba bước sau.

1. Đọc [docs/voice-prep-guide-vietnamese.md](docs/voice-prep-guide-vietnamese.md) để biết cần chuẩn bị gì.
2. Thu âm theo [docs/recording-session.md](docs/recording-session.md) bằng `uv run scripts/record.py`. Script hiện từng câu trong [kịch bản](docs/recording-script-vietnamese.md), thu, và lưu vào `recordings/`.
3. Kiểm tra clip, tạo profile, đọc văn bản và so sánh cấu hình bằng các script bên dưới. Nếu dùng Claude Code trong repo này, bạn có thể yêu cầu bằng lời, ví dụ "chọn take tốt nhất trong recordings/ và tạo profile" hoặc "đọc bài này bằng giọng lan02".

```bash
# Cài công cụ Python (một lần)
uv sync

# Chỉ bật backend của VoiceStudio, đủ cho các script
cd ~/workspace/VoiceStudio && bun run dev:api

# Từ bản thu đến profile
uv run scripts/prep-clip.py ban-thu.m4a recordings/tro-chuyen-01-take1.wav
uv run scripts/check-clip.py recordings/
uv run scripts/make-profile.py lan01 recordings/tro-chuyen-01-take1.wav "Lời đã đọc trong clip."

# Đọc một văn bản, mỗi dòng một đoạn, có soát chữ bị nuốt
uv run scripts/speak.py <profile_id> -f outputs/bai-viet.txt

# Chấm điểm một thư mục kết quả
uv run scripts/score.py outputs/ab-<thời gian> --profile <profile_id>
```

So sánh A/B:

```bash
# Mở VoiceStudio (dùng Terminal.app, hoặc thêm env -u ELECTRON_RUN_AS_NODE trong VS Code)
cd ~/workspace/VoiceStudio && bun run dev

# Lấy id profile, rồi so sánh 16 và 32 bước
curl -s http://127.0.0.1:3900/profiles
scripts/ab-test.sh <profile_id> "Năm 2024, tôi đã đi Đà Lạt ba lần."

# So sánh thêm VoxCPM2 (cần tải trong Model Catalogue trước)
scripts/ab-test.sh <profile_id> "Câu cần thử." "omnivoice voxcpm2" "32"

# Cho Whisper chép lại lời để soát chữ bị nuốt (cần Whisper large-v3 MLX)
TRANSCRIBE=1 scripts/ab-test.sh <profile_id> "Câu cần thử."
```

Kết quả A/B được lưu trong `outputs/ab-<thời gian>/`, gồm các file WAV và `results.tsv` ghi thời gian tạo.

## Cấu trúc thư mục

| Đường dẫn | Nội dung |
|---|---|
| [docs/operations-guide.md](docs/operations-guide.md) | Tài liệu vận hành: cơ chế, thành phần, thao tác thường ngày, xử lý sự cố, và cách gọi công cụ từ repo khác (mục 13) |
| [docs/voice-prep-guide-vietnamese.md](docs/voice-prep-guide-vietnamese.md) | Hướng dẫn chuẩn bị: thiết bị, phòng, clip mẫu, thiết lập tạo giọng, checklist |
| [docs/recording-session.md](docs/recording-session.md) | Trình tự một buổi thu: chọn cách thu, chỉnh gain, thu từng take, đọc kết quả |
| [docs/recording-script-vietnamese.md](docs/recording-script-vietnamese.md) | 12 câu mẫu đủ 6 thanh, chia theo phong cách, và các câu kiểm tra |
| [docs/261004-research-best-practices.md](docs/261004-research-best-practices.md) | Nghiên cứu best practice từ cộng đồng, các lỗi tiếng Việt đã biết, so sánh model |
| [docs/261004-test-voicestudio-mac-mini.md](docs/261004-test-voicestudio-mac-mini.md) | Báo cáo cài đặt và thử VoiceStudio trên Mac mini M4 |
| [scripts/ab-test.sh](scripts/ab-test.sh) | Tạo cùng một câu với nhiều engine hoặc số bước qua API của VoiceStudio |
| [scripts/record.py](scripts/record.py) | Buổi thu: hiện câu, thu từ mic hoặc tách bản thu iPhone thành các take, lưu đúng tên, đo ngay |
| [scripts/prep-clip.py](scripts/prep-clip.py) | Đổi bản thu sang WAV mono 48 kHz 24-bit, cắt câu và khoảng lặng hai đầu |
| [scripts/check-clip.py](scripts/check-clip.py) | Đo clip mẫu theo tiêu chí trong hướng dẫn và xếp hạng các take |
| [scripts/make-profile.py](scripts/make-profile.py) | Tạo profile qua API sau khi kiểm tra clip và transcript |
| [scripts/normalize-vi.py](scripts/normalize-vi.py) | Đổi số, ngày, tiền thành chữ (viết "ngàn") |
| [scripts/speak.py](scripts/speak.py) | Đọc văn bản theo từng đoạn, soát chữ thiếu bằng Whisper, tự tạo lại, ghép file |
| [scripts/score.py](scripts/score.py) | Chấm độ giống giọng, DNSMOS và chữ thiếu |
| [scripts/check-words.py](scripts/check-words.py) | Soát chữ bị rơi của từng câu đã tạo |
| [scripts/check-watermark.py](scripts/check-watermark.py) | Dò dấu nhận biết giọng tổng hợp trong file audio hoặc video |
| [scripts/word-times.py](scripts/word-times.py) | Mốc thời gian từng từ của câu đã tạo, gióng theo chữ đã biết |
| [CLAUDE.md](CLAUDE.md), [.claude/skills/](.claude/skills/) | Quy tắc và ba skill (`voice-clip`, `voice-speak`, `voice-compare`) để Claude Code điều phối workflow |
| `recordings/` | File thu âm gốc. Không đưa lên Git. |
| `outputs/` | Kết quả tạo giọng và A/B. Không đưa lên Git. |

## Quy tắc riêng tư

Giọng nói là dữ liệu sinh trắc học. File âm thanh trong `recordings/` và `outputs/`, cùng mọi file `.wav`, `.mp3`, `.m4a`, đều đã nằm trong `.gitignore`. Không đẩy chúng lên kho công khai và không chia sẻ profile giọng, trừ khi chủ giọng tự gửi gói `.omnivoice` cho một bên đã nhận điều kiện sử dụng bằng văn bản. Chỉ clone giọng của mình hoặc của người đã đồng ý.

Weights của OmniVoice theo giấy phép CC-BY-NC, nên giọng tạo bằng model này chỉ được dùng phi thương mại. Nếu cần dùng thương mại, hãy chuyển sang VoxCPM2 hoặc VieNeu-TTS (Apache-2.0). Chi tiết nằm trong báo cáo nghiên cứu.

## Giấy phép

Tài liệu và script trong repo này theo giấy phép [MIT](LICENSE). Giấy phép này không áp dụng cho VoiceStudio (AGPL-3.0) hay weights của OmniVoice (CC-BY-NC), là những thứ repo này gọi tới chứ không chứa.
