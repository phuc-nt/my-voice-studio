# Tài liệu vận hành

Cập nhật: 2026-10-04. Áp dụng cho VoiceStudio 0.5.6 (commit `c4d63ef`) với engine OmniVoice, chạy trên Mac mini M4 24GB.

Tài liệu này mô tả hệ thống đang chạy thế nào và các thao tác thường ngày. Cách thu âm chi tiết nằm ở [voice-prep-guide-vietnamese.md](voice-prep-guide-vietnamese.md), bằng chứng cho từng khuyến nghị nằm ở [261004-research-best-practices.md](261004-research-best-practices.md).

## 1. Cơ chế

- **Zero-shot cloning, không huấn luyện gì.** Model nhận một clip mẫu 6–10 giây kèm transcript, dùng nó làm lời nhắc rồi đọc văn bản mới bằng giọng đó.
- **Model chép mọi thứ trong clip.** Ngoài âm sắc, nó chép cả tiếng vang phòng, tiếng ồn, tốc độ và cảm xúc. Clip mẫu quyết định gần hết chất lượng, còn tham số chỉ tinh chỉnh.
- **Transcript phải khớp từng chữ.** Model dựa vào đó để ghép chữ với tiếng trong clip.
- **Âm thanh được tạo dần qua nhiều bước lặp (Steps).** 16 bước thì nhanh nhưng dễ đọc vội và nuốt âm tiết, 32 bước ổn định hơn.
- **Phong cách đi theo clip.** Ô Style không hiểu mô tả tiếng Việt, nên mỗi phong cách cần một clip mẫu và một profile riêng.

## 2. Thành phần

| Lớp | Thành phần | Trạng thái (2026-10-04) |
|---|---|---|
| App | VoiceStudio 0.5.6: Electron, backend FastAPI cổng 3900, giao diện cổng 3902 | Đã cài ở `~/workspace/VoiceStudio` |
| Model giọng | OmniVoice, 3,27GB, xuất 24 kHz, chạy GPU Metal (`device: mps`) | Đã tải |
| Chép lời | Whisper tiny, khoảng 80MB | Đã tải, yếu với tiếng Việt |
| Chép lời, mốc từng từ | Whisper large-v3 MLX, 3GB | Đã tải ngày 2026-10-06 |
| Engine dự phòng | VoxCPM2, xuất 48 kHz, Apache-2.0 | Chưa tải |
| Mic | Mac mini không có mic tích hợp | Cần mic USB, hoặc thu bằng iPhone |
| Công cụ | bun 1.3.11, uv 0.10.4, Python 3.11.14, PyTorch 2.8, MLX | Đã cài |
| So sánh A/B | [../scripts/ab-test.sh](../scripts/ab-test.sh), gọi API `/generate` | Có sẵn |
| Công cụ bổ sung | Các script Python trong [../scripts/](../scripts/), chạy bằng `uv run` (xem mục 12) | Có sẵn, cần `uv sync` lần đầu |
| Đo độ giống giọng | WeSpeaker ResNet34 (ONNX, 26MB, huấn luyện trên tiếng Anh), lưu ở `models/` | Tự tải khi chạy `score.py` lần đầu |
| Đo chất lượng | DNSMOS qua `speechmos`, độ to qua `pyloudnorm` | Cài cùng `uv sync` |
| Chuẩn hóa văn bản | `sea-g2p` | Cài cùng `uv sync` |

Tốc độ đo trên Mac mini M4 khi model đã nạp, với một câu khoảng 4,7 giây:

| Steps | Thời gian tạo |
|---|---|
| 16 | Khoảng 6,8 giây |
| 32 | Khoảng 12,7 giây |

Backend chiếm khoảng 4GB RAM. Sau 900 giây không dùng, backend gỡ model khỏi bộ nhớ, nên lần tạo kế tiếp mất thêm khoảng 10 giây để nạp lại.

## 3. Nơi lưu dữ liệu

| Dữ liệu | Vị trí | Vào Git? |
|---|---|---|
| Clip thu âm gốc | `recordings/` | Không |
| Kết quả A/B | `outputs/ab-<thời gian>/` (WAV, `results.tsv`, `text.txt`, `scores.tsv`) | Không |
| Kết quả đọc văn bản | `outputs/speak-<thời gian>/` (`chunk-NNN.wav`, `final.wav`, `report.json`) | Không |
| Model đo độ giống giọng | `models/` | Không |
| Môi trường Python | `.venv/` | Không |
| Audio tạo trong app | `~/Library/Application Support/OmniVoice/outputs/` | Ngoài repo |
| Mã nguồn app và model | `~/workspace/VoiceStudio` | Repo riêng |

Giọng nói là dữ liệu sinh trắc học. `.gitignore` đã loại mọi file audio, và không được đẩy chúng lên remote nào, kể cả repo private. Hãy sao lưu `recordings/` ra ổ ngoài có mã hóa.

## 4. Mở và tắt app

```bash
# Terminal.app
cd ~/workspace/VoiceStudio && bun run dev

# Terminal tích hợp của VS Code: phải bỏ biến ELECTRON_RUN_AS_NODE
cd ~/workspace/VoiceStudio && env -u ELECTRON_RUN_AS_NODE bun run dev

# Kiểm tra backend đã sẵn sàng
curl -sf http://127.0.0.1:3900/health && echo OK
```

Tắt app bằng Ctrl+C trong terminal đang chạy `bun run dev`.

Các script chỉ cần backend, không cần cửa sổ app:

```bash
cd ~/workspace/VoiceStudio && bun run dev:api
```

## 5. Chuẩn bị clip mẫu

Checklist đầy đủ nằm ở cuối [voice-prep-guide-vietnamese.md](voice-prep-guide-vietnamese.md). Tóm tắt:

1. **Phòng:** phòng nhỏ có rèm, thảm, giường hoặc tủ quần áo mở. Tắt máy lạnh, quạt và thông báo, đóng cửa sổ.
2. **Mic:** đặt cố định cách miệng 10–15 cm, hơi lệch sang một bên.
3. **Thiết lập thu:** WAV mono, 48 kHz, 24-bit, đỉnh âm từ −12 đến −6 dBFS. Không lọc ồn, nén hay EQ; chỉ cắt khoảng lặng ở hai đầu.
4. **Kịch bản:** đọc theo [recording-script-vietnamese.md](recording-script-vietnamese.md), mỗi câu 2–3 take. Bắt đầu với hai phong cách: trò chuyện (câu 1–3) và kể chuyện (câu 4–5).
5. **Tên file:** `recordings/<phong-cach>-<so-cau>-take<lan>.wav`, ví dụ `recordings/tro-chuyen-01-take2.wav`.
6. **Chọn và cắt:** lấy take sạch nhất, cắt còn 6–10 giây đúng ranh giới câu.
7. **Transcript:** viết đúng lời đã đọc, đủ dấu thanh và dấu câu, số viết thành chữ.

Trình tự cả buổi thu, kể cả cách thu bằng iPhone khi Mac mini chưa có mic, nằm ở [recording-session.md](recording-session.md). `record.py` hiện từng câu, thu, cắt khoảng lặng, lưu đúng tên và đo ngay:

```bash
uv run scripts/record.py --test                                  # thu thử để chỉnh gain
uv run scripts/record.py                                         # thu câu 1–5, mỗi câu ba take
uv run scripts/record.py --from-file cau-1.m4a --sentences 1     # tách bản thu iPhone thành các take
```

Hai script làm phần đo và cắt cho bản thu có sẵn:

```bash
# Đổi bản thu bất kỳ (ví dụ M4A từ iPhone) sang WAV mono 48 kHz 24-bit và cắt khoảng lặng hai đầu
uv run scripts/prep-clip.py ban-thu.m4a recordings/tro-chuyen-01-take1.wav
# Cắt một câu ra khỏi bản thu dài
uv run scripts/prep-clip.py ban-thu.m4a recordings/tro-chuyen-02-take1.wav --start 12.4 --end 20.1

# Đo mọi clip và xếp hạng các take; thêm --asr để xem Whisper nghe được gì
uv run scripts/check-clip.py recordings/
```

`prep-clip.py` không lọc ồn, không nén, không chỉnh độ to. `check-clip.py` đo độ dài, định dạng, đỉnh âm, độ to, mẫu bị vỡ, khoảng lặng, nền ồn và DNSMOS, rồi kết luận `ĐẠT`, `XEM LẠI` hoặc `LỖI`. Ngưỡng nền ồn và DNSMOS là ước lượng; khi số đo và tai bạn khác nhau thì tin tai.

## 6. Tạo profile

Bằng script (tự đo clip, từ chối clip `LỖI` và transcript có chữ số, đặt Language Vietnamese, in ra id):

```bash
uv run scripts/make-profile.py lan01 recordings/tro-chuyen-01-take2.wav "Lời đã đọc trong clip."
```

Hoặc làm tay trong app:

1. Vào Voice Clone, tạo profile mới, tải clip WAV lên và dán transcript.
2. Đặt Language là **Vietnamese**, không để Auto.
3. Đặt tên theo quy ước `<tên>NN`: tên người, rồi số thứ tự hai chữ số theo thứ tự tạo, ví dụ `lan01`, `lan02`. Tên không ghi phong cách, nên mỗi lần tạo profile phải thêm một dòng vào bảng profile của bạn.
4. Lấy id của profile để dùng với script:

   ```bash
   curl -s http://127.0.0.1:3900/profiles
   ```

Ghi bảng profile vào `docs/profiles.local.md`. File này bị Git bỏ qua, vì tên và id profile là thông tin riêng của từng máy. Mẫu:

| Tên | Id | Phong cách | Clip mẫu | Dùng cho |
|---|---|---|---|---|
| `lan01` | `<id>` | Trò chuyện | `recordings/tro-chuyen-02-take2.wav` | Vlog, video đời thường |
| `lan02` | `<id>` | Kể chuyện | `recordings/ke-chuyen-04-take2.wav` | Truyện, podcast, lời dẫn chậm |

Id do VoiceStudio sinh ra và chỉ đúng trên máy đã tạo ra nó. Profile nhập từ gói `.omnivoice` trên máy khác sẽ có id khác.

## 7. Tạo giọng

| Thiết lập | Giá trị |
|---|---|
| Language | Vietnamese |
| Steps | 32 |
| Guidance (CFG) | 2.0, tăng lên khoảng 2.5 nếu bị nuốt chữ |
| Speed | 1.0 |
| Temperature | Mặc định |
| Seed | Ngẫu nhiên lúc thử. Khi có bản ưng ý thì khóa profile hoặc bấm "Keep this seed". |
| Độ dài mỗi lần | Một đến ba câu, dưới 30 giây âm thanh |
| Văn bản dài | Dùng tab Audiobook |
| Xuất file | WAV 24-bit nếu còn chỉnh sửa, 16-bit để nghe. Bấm "Check audio" trước khi dùng. |

Quy tắc viết văn bản đầu vào:

- Viết năm, tiền, giờ và số điện thoại quan trọng thành chữ.
- Viết đầy đủ các chữ viết tắt, ví dụ "Thành phố Hồ Chí Minh" thay cho "TP.HCM".
- Từ tiếng Anh và tên riêng đọc sai thì dùng `[[phiên âm]]` hoặc Pronunciation dictionary.
- Cần nghỉ dài thì dùng `[pause 500ms]`. Chỉ dùng tag `[laughter]` và `[sigh]`; tag khác sẽ bị đọc to thành chữ.

### Đọc văn bản dài bằng script

`speak.py` thay cho việc dán từng đoạn vào app. Mỗi dòng trong file là một đoạn; dòng dài hơn 220 ký tự được tách theo câu.

```bash
uv run scripts/speak.py <profile_id> -f outputs/bai-viet.txt
```

Với mỗi đoạn, script tạo audio, cho Whisper chép lại, so với văn bản gốc, và tạo lại với seed khác (tối đa hai lần) nếu thiếu chữ. Kết quả nằm trong `outputs/speak-<thời gian>/`: từng đoạn, bản ghép `final.wav`, và `report.json` ghi chữ thiếu của từng đoạn. Đoạn được đánh dấu `CẦN XEM` là đoạn bạn nên nghe.

```bash
# Tạo lại đoạn 3 và 7 với seed khác, rồi ghép lại
uv run scripts/speak.py --redo outputs/speak-<thời gian> 3 7
# Tạo lại đoạn 3 với câu đã viết lại
uv run scripts/speak.py --redo outputs/speak-<thời gian> 3 --text "Câu đã viết lại."
```

Bước soát chữ cần Whisper large-v3 MLX. Khi chưa có, script vẫn tạo audio nhưng ghi các đoạn là `chưa soát`.

`normalize-vi.py` đổi số, ngày, tiền thành chữ bằng `sea-g2p`. Kết quả là chữ thường toàn bộ và đọc sai ký hiệu "$", nên dùng nó để tham khảo cách đọc số, không dán nguyên văn vào model. Số hàng nghìn được viết là "ngàn", vì "nghìn" từng bị nuốt ở một giọng thử; cờ `--nghin` giữ cách viết cũ.

```bash
uv run scripts/normalize-vi.py "Ngày 3/4/2024 tôi trả 150.000đ."
```

## 8. Kiểm tra và so sánh A/B

```bash
cd ~/workspace/my-voice-studio

# So 16 và 32 bước, seed 42
scripts/ab-test.sh <profile_id> "Ông lão chậm rãi mở chiếc hộp gỗ cũ."

# So thêm engine khác (cần tải VoxCPM2 trong Model Catalogue trước)
scripts/ab-test.sh <profile_id> "Câu cần thử." "omnivoice voxcpm2" "32"

# Cho Whisper chép lại lời để soát chữ bị nuốt (cần Whisper large-v3 MLX)
TRANSCRIBE=1 scripts/ab-test.sh <profile_id> "Câu cần thử."
```

Tham số theo thứ tự: `profile_id`, câu cần đọc, danh sách engine (mặc định `omnivoice`), danh sách số bước (mặc định `16 32`), seed (mặc định `42`). Đổi địa chỉ backend bằng biến `VOICESTUDIO_API`.

Chấm điểm một thư mục kết quả (của `ab-test.sh` hoặc `speak.py`):

```bash
uv run scripts/score.py outputs/ab-<thời gian> --profile <profile_id>
```

Script in bảng và ghi `scores.tsv` với độ giống clip mẫu, DNSMOS, tỉ lệ chữ sai và chữ thiếu. Độ giống đo bằng model huấn luyện trên tiếng Anh, nên chỉ dùng để so các cấu hình với nhau trên cùng một giọng. Số đo giúp loại cấu hình rõ ràng kém; chọn giữa các cấu hình còn lại vẫn là việc của tai.

Khi nghe, dùng tai nghe và tìm các lỗi: nuốt chữ, sai thanh (nhất là hỏi và ngã), giọng méo, tiếng vang, nhịp vội. Các câu kiểm tra số, viết tắt và từ tiếng Anh nằm ở cuối [recording-script-vietnamese.md](recording-script-vietnamese.md).

### Mốc thời gian từng từ

```bash
uv run scripts/word-times.py cau.wav --text "Chữ đã gửi đi."
uv run scripts/word-times.py outputs/speak-<thời gian> -o outputs/speak-<thời gian>/words.json
```

Script gióng audio theo chữ đã biết bằng Whisper large-v3, nên số từ trả về luôn bằng số từ trong chữ. Mốc tính bằng giây từ đầu file. Mỗi file là một câu dưới 30 giây.

Đừng lấy mốc từng từ từ API của app (`/v1/audio/transcriptions` với `verbose_json`): thử ngày 2026-10-06, nó trả các từ cách đều nhau trong 1,57 giây cho một câu dài 4,07 giây, tức là mốc được chia đều chứ không đo.

Chỗ ngắt hơi được đẩy ra khỏi từ. Nếu trong khoảng của một từ có quãng lặng từ 0,25 giây (thấp hơn khung to nhất 30 dB), mốc đầu của từ ấy dời tới chỗ tiếng nói bắt đầu lại, và mốc cuối của từ trước kéo tới chỗ tiếng nói dừng. Trường hợp này gặp khi một lần tạo có hai câu ngắn, hoặc có dấu phẩy ngắt dài.

Giới hạn đã thấy trên 32 câu, 517 từ: mốc luôn tăng dần và nằm trong vùng có tiếng nói. Từ đứng ngay sau chỗ ngắt thường ra ngắn hơn thật (0,04–0,12 giây trong 6 trường hợp), và có một từ đầu câu chỉ dài 0,02 giây: mốc đầu của các từ này đáng tin, mốc cuối thì không. Chưa có mốc chuẩn do người đánh dấu để đo sai số.

## 9. Xử lý sự cố

| Triệu chứng | Nguyên nhân | Cách xử lý |
|---|---|---|
| Electron thoát ngay khi chạy `bun run dev` trong VS Code | VS Code đặt `ELECTRON_RUN_AS_NODE=1` | Chạy bằng Terminal.app hoặc thêm `env -u ELECTRON_RUN_AS_NODE` |
| `ab-test.sh` báo "VoiceStudio chưa chạy" | Backend cổng 3900 chưa lên | Mở app, đợi `/health` trả về rồi chạy lại |
| `ab-test.sh` báo lỗi HTTP với engine `voxcpm2` | Engine chưa được tải | Tải trong Model Catalogue |
| `TRANSCRIBE=1` báo "chưa chép lời được" | Chưa có Whisper large-v3 MLX | Tải trong Model Catalogue |
| `speak.py` ghi mọi đoạn là `chưa soát` | Chưa có Whisper large-v3 MLX | Tải trong Model Catalogue |
| Script Python báo thiếu module | Chưa cài môi trường | Chạy `uv sync` ở thư mục gốc repo |
| `check-clip.py` báo nền ồn với clip thu sạch | Clip không có chỗ ngắt hơi nào để đo nền | Nghe lại; nếu sạch thì bỏ qua cảnh báo |
| Lần tạo đầu chậm hơn hẳn | Model bị gỡ sau 900 giây không dùng | Bình thường, các lần sau nhanh lại |
| Bỏ từ, bỏ cụm từ | Giới hạn của OmniVoice với tiếng Việt, nặng hơn khi văn bản dài | Chia đoạn dưới 30 giây, dùng 32 bước, Speed 1.0, tăng nhẹ CFG, không tăng temperature |
| Đọc vội, sai âm tiết | Đang dùng 16 bước | Đổi sang 32 bước |
| Giọng méo hoặc mang âm sắc nước ngoài | Language để Auto, hoặc clip mẫu không phải tiếng Việt | Đặt Language Vietnamese, dùng clip mẫu tiếng Việt |
| Giọng tạo ra có tiếng vang hoặc ồn | Clip mẫu thu trong phòng vang hoặc ồn | Thu lại clip, không sửa bằng tham số |
| Giọng không giống mình | Clip mẫu quá dài, sai phong cách, hoặc transcript lệch | Đổi clip hoặc take khác trước khi đổi tham số |
| Đọc sai số hoặc viết tắt | Model tự đọc chữ số | Viết thành chữ |
| Mô tả Style bằng tiếng Việt không có tác dụng | Ô Style chỉ nhận bộ tag tiếng Anh và tiếng Trung cố định | Tạo profile riêng cho từng phong cách |

## 10. Khi zero-shot chưa đủ giống

Làm theo thứ tự từ rẻ đến đắt:

1. Đổi clip mẫu: độ dài khác, take khác, phong cách khác.
2. Thử VoxCPM2 trong VoiceStudio rồi chạy lại A/B.
3. Thử model chuyên tiếng Việt ngoài VoiceStudio, ví dụ VieNeu-TTS v3 Turbo.
4. Fine-tune LoRA trên Google Colab bằng 15–30 phút audio sạch kèm transcript. Hướng dẫn train OmniVoice trong VoiceStudio viết cho GPU NVIDIA nên không chạy trên Mac mini.

## 11. Giấy phép và giới hạn

- App VoiceStudio dùng AGPL-3.0.
- Weights OmniVoice dùng CC-BY-NC, nên giọng tạo bằng model này chỉ dùng phi thương mại. Nếu cần dùng thương mại, chuyển sang VoxCPM2 hoặc VieNeu-TTS (Apache-2.0).
- Chỉ clone giọng của mình hoặc của người đã đồng ý bằng văn bản.
- Ngày 2026-10-06 đã clone từ giọng thật (hai profile, trò chuyện và kể chuyện). Chủ giọng nghe và đánh giá là giống. Soát bằng Whisper large-v3 trên 20 câu của hai bài dài: không câu nào bị nuốt chữ.
- Các ngưỡng trong script ở mục 12 (nền ồn, DNSMOS, tỉ lệ chữ sai 15%) chưa được hiệu chỉnh trên giọng thật.

## 12. Công cụ và phân vai

Cài một lần: `uv sync` ở thư mục gốc repo.

| Script | Việc |
|---|---|
| [record.py](../scripts/record.py) | Buổi thu: hiện câu, thu từ mic hoặc tách bản thu có sẵn thành các take, lưu đúng tên, đo ngay |
| [prep-clip.py](../scripts/prep-clip.py) | Đổi định dạng, cắt câu, cắt khoảng lặng hai đầu |
| [check-clip.py](../scripts/check-clip.py) | Đo clip mẫu, kết luận, xếp hạng các take |
| [make-profile.py](../scripts/make-profile.py) | Tạo profile qua API sau khi kiểm tra clip và transcript |
| [normalize-vi.py](../scripts/normalize-vi.py) | Đổi số, ngày, tiền thành chữ để tham khảo |
| [speak.py](../scripts/speak.py) | Đọc văn bản theo từng đoạn, soát chữ thiếu, tự tạo lại, ghép file |
| [ab-test.sh](../scripts/ab-test.sh) | Tạo cùng một câu với nhiều engine hoặc số bước |
| [score.py](../scripts/score.py) | Chấm độ giống giọng, DNSMOS và chữ thiếu cho một thư mục kết quả |
| [check-words.py](../scripts/check-words.py) | Soát chữ bị rơi của từng câu theo manifest, kết luận ĐẠT, XEM LẠI hoặc RƠI CHỮ |
| [check-watermark.py](../scripts/check-watermark.py) | Dò dấu nhận biết giọng tổng hợp trong file audio hoặc video |
| [word-times.py](../scripts/word-times.py) | Mốc thời gian từng từ của một câu đã tạo, gióng theo chữ đã biết, để làm phụ đề và khớp hình |

Ai làm việc gì:

| Việc | Người làm | Lý do |
|---|---|---|
| Thu âm, nghe, chọn bản cuối, xác nhận consent | Bạn | Chỉ bạn nghe được và chỉ bạn có quyền với giọng mình |
| Đo, tạo, chép lời, chấm điểm | Script | Lặp lại được và cho ra số |
| Điều phối các script, viết lại văn bản cho model đọc, soát transcript, đọc kết quả | Claude Code | Cần hiểu tiếng Việt và ngữ cảnh |

Claude Code không nghe được âm thanh. Nó làm việc qua số đo và lời Whisper chép lại, nên mọi kết luận của nó về audio cần bạn nghe xác nhận. Quy tắc cho Claude nằm ở [../CLAUDE.md](../CLAUDE.md). Ba skill trong [../.claude/skills/](../.claude/skills/) ứng với ba giai đoạn:

| Skill | Khi nào dùng | Ví dụ yêu cầu |
|---|---|---|
| `voice-clip` | Vừa thu âm xong | "Tôi vừa thu sáu take vào recordings/, chọn take tốt nhất và tạo profile" |
| `voice-speak` | Có văn bản cần đọc | "Đọc bài này bằng giọng lan02" |
| `voice-compare` | Cần chọn cấu hình, engine hoặc clip | "So 16 và 32 bước với ba câu kiểm tra" |

Trong `voice-speak`, Claude viết lại số, viết tắt và từ nước ngoài theo ngữ cảnh, chia đoạn ở chỗ nghỉ tự nhiên, rồi đọc `report.json` để phân biệt lỗi do Whisper chép sai với chữ bị nuốt thật. Trường hợp sau nó tạo lại hoặc viết lại câu.

## 13. Dùng từ repo khác

Mục này dành cho pipeline hoặc agent ở repo khác trên cùng máy (ví dụ pipeline dựng video) cần dùng một profile giọng trên máy đó. Điều kiện sử dụng giọng do chủ giọng quy định riêng; mục này chỉ nói cách gọi.

Cần có: backend VoiceStudio chạy ở `http://127.0.0.1:3900` (`cd ~/workspace/VoiceStudio && bun run dev:api`) và `uv`. Mọi thứ chạy trên máy, không gửi audio đi đâu.

Gọi script của repo này từ thư mục bất kỳ bằng tiền tố sau, viết tắt là `VS` trong các ví dụ:

```bash
VS="uv run --project $HOME/workspace/my-voice-studio $HOME/workspace/my-voice-studio/scripts"
```

| Việc | Lệnh | Kết quả |
|---|---|---|
| Tra id profile theo tên | `curl -s http://127.0.0.1:3900/profiles` | JSON; lấy `id` theo `name` |
| Tạo một câu | `POST /generate` (xem dưới) | WAV 24 kHz mono |
| Xem chữ sau khi thay phát âm | `POST /pronunciation/test` | JSON, không tạo audio |
| Mốc từng từ của một câu | `$VS/word-times.py cau.wav --text "..."` | JSON ra stdout |
| Mốc từng từ của nhiều câu | `$VS/word-times.py --manifest cau.json -o words.json` | Một mảng JSON, nạp model một lần |
| Soát rơi chữ của từng câu | `$VS/check-words.py --manifest cau.json --json` | JSON: `verdict`, `missing`, `changed`; mã thoát 0, 1, 2 |
| Chấm độ giống giọng và độ sạch | `$VS/score.py <thư mục> --profile <id>` | Bảng và `scores.tsv` |
| Dò dấu nhận biết giọng tổng hợp | `$VS/check-watermark.py --json video.mp4 giong.wav` | JSON: `watermarked`, `confidence` |
| Đổi số, ngày, tiền thành chữ | `$VS/normalize-vi.py "<văn bản>"` | Chữ thường, viết "ngàn"; chỉ lấy cách đọc số |

### Tạo một câu

```bash
curl -s -o 001.wav http://127.0.0.1:3900/generate \
  -F "text=Câu cần đọc." -F "profile_id=<id>" -F "language=Vietnamese" \
  -F "engine=omnivoice" -F "num_step=32" -F "guidance_scale=2.0" \
  -F "speed=1.0" -F "seed=42" -F "wav_bits=24" -F "max_chunk_chars=0"
```

- Mỗi lần gọi một câu. Mỗi lần mất 10–20 giây, nên chạy nền và lưu kết quả theo seed.
- Cùng chữ, cùng seed, cùng `guidance_scale` luôn cho ra cùng một audio. Thử lại phải đổi seed.
- Thứ tự thử lại đã dùng được: seed 42, 43, 44 ở CFG 2.0, rồi 45, 46 ở CFG 2.5.
- Thời lượng nằm ở header `x-audio-duration`, thời gian tạo ở `x-gen-time`.

### Cách đọc từ khó

Trong `text`, `[[i-pắp]]` đọc đúng phần trong ngoặc, `[[EPUB|i-pắp]]` giữ chữ gốc và ghi cách đọc. Kiểm tra trước khi tạo:

```bash
curl -s -H 'Content-Type: application/json' \
  -d '{"text":"Tải file [[EPUB|i-pắp]] về máy.","language":"Vietnamese"}' \
  http://127.0.0.1:3900/pronunciation/test
```

Bản dùng cú pháp và bản viết thẳng phiên âm cho ra tệp giống nhau từng byte (thử 4 câu, 2026-10-06). Chủ giọng đã nghe và duyệt các cách viết: `[[EPUB|i-pắp]]`, `[[OPDS|ô pê đê ét]]`, `[[app|áp]]`, `[[PIN|pin]]`, `[[manga|man ga]]`. Trong các câu thử đó bản để nguyên chữ gốc cũng đọc đúng, nhưng ở câu khác từng lệch, nên vẫn dùng cách viết đã duyệt.

### Ép độ dài

Thêm `-F "duration=<giây>"` và **bỏ** trường `speed`; gửi kèm `speed` thì `duration` bị bỏ qua. Một câu dài tự nhiên 4,36 s: yêu cầu 4 s ra 4,20 s, yêu cầu 7 s ra 6,15 s. Thử thêm hai câu ở ±10%: độ dài ra lệch yêu cầu 0,11–0,31 s, và chủ giọng nghe thấy cả bản ngắn lẫn bản dài đều tự nhiên (2026-10-06). Dùng được trong ±10%; ngoài khoảng đó chưa ai nghe.

### Soát rơi chữ

```bash
$VS/check-words.py --manifest cau.json --json -o soat.json
```

`cau.json` cùng định dạng với `word-times.py`: `[{"file": "001.wav", "text": "..."}]`. Mỗi câu được Whisper large-v3 chép lời lại rồi so với chữ đã gửi đi:

| `verdict` | Nghĩa | Làm gì |
|---|---|---|
| `ĐẠT` | Không thiếu chữ, tỉ lệ chữ khác không quá 0,15 | Dùng |
| `XEM LẠI` | Không thiếu chữ, nhưng Whisper nghe ra nhiều chữ khác | Cần người nghe; thường là lỗi chép lời ở tên riêng và phiên âm |
| `RƠI CHỮ` | Có chữ Whisper không nghe thấy (`missing`) | Tạo lại với seed khác |

Mã thoát là 0 khi mọi câu đạt, 1 khi có câu cần xem lại, 2 khi có câu rơi chữ. Đây là luật soát chung cho mọi bên dùng giọng, cùng ngưỡng với `speak.py`.

- So có dấu thanh. Trước khi so, số Whisper viết bằng chữ số được đổi thành chữ, "nghìn" coi như "ngàn", và chữ viết liền hay rời coi như nhau ("man ga", "manga").
- Với `[[EPUB|i-pắp]]`, nghe ra "epub" hay "i pắp" đều đúng. Phiên âm viết thẳng vào chữ thì vẫn bị báo "khác", nên dùng cú pháp `[[...]]` giúp bước soát bớt báo oan.
- Thử trên 22 câu của một video thật (đều đã được người nghe nhận): 20 câu `ĐẠT`, 2 câu `XEM LẠI` (câu có "i-pắp" và "ô pê đê ét" viết thẳng), không câu nào `RƠI CHỮ`.
- Whisper tự sửa thanh điệu theo ngữ cảnh, nên lệnh này không bắt được lỗi sai thanh. Chưa có ai nghe đối chiếu để biết tỉ lệ bỏ sót.

### Mốc từng từ

```bash
$VS/word-times.py 001.wav --text "Chữ đã gửi đi." -o 001.words.json
```

```json
{"file": "001.wav", "duration": 4.07, "speech_start": 0.2, "speech_end": 3.86,
 "words": [{"word": "Chào", "start": 0.2, "end": 0.3}, {"word": "mọi", "start": 0.3, "end": 0.44}]}
```

- Giây, tính từ đầu file. Chạy trên từng câu trước khi nối, rồi cộng vị trí của câu trong tệp đã nối.
- Từ đứng ngay sau một chỗ ngắt dài có mốc đầu đúng chỗ tiếng nói bắt đầu lại, nhưng mốc cuối thường quá sớm. Khi tô sáng từng từ, lấy mốc đầu của từ kế tiếp làm mốc cuối.
- `--text` là đúng chữ đã gửi cho `/generate`, kể cả phần phiên âm. Từ tách theo dấu cách, dấu câu dính vào từ đứng trước, `[[a|b]]` tính là `b`, tag như `[pause 500ms]` bị bỏ.
- Với nhiều câu, dùng `--manifest` để chỉ nạp model một lần. File manifest là `[{"file": "001.wav", "text": "..."}]`, đường dẫn tính từ thư mục chứa manifest.
- Lệnh này ép chữ vào audio, nên không phát hiện được từ bị nuốt. Soát rơi từ trước, gióng sau.
- Từ đầu câu đôi khi ngắn bất thường (đã gặp một từ 0,02 s trong 195 từ). Khi đó lấy `speech_start` làm mốc đầu.

### Dò dấu nhận biết

```bash
$VS/check-watermark.py --json renders/video.mp4
```

Script tự tách tiếng và gộp mono, nên nhận cả MP4. Dấu chịu được đổi tần số mẫu, chuẩn hoá độ to và AAC 128 kbps. App coi là có dấu khi `confidence` trên 0,5.

Trộn nhạc thì không chắc còn dò ra, và **hạ nhạc không cứu được**. Thử ngày 2026-10-06 với 10 tệp giọng và nhạc nền thật của một video (nhạc chiptune, trộn ở hệ số 0,3 như bản dựng, rồi hạ thêm; mọi bản đều qua AAC 128 kbps):

| Bản | Số tệp dò ra dấu | `confidence` thấp nhất, giữa, cao nhất |
|---|---|---|
| Giọng chưa trộn, chỉ AAC | 10/10 | 0,71 · 0,91 · 0,94 |
| Nhạc ở mức của bản dựng | 7/10 | 0,27 · 0,58 · 0,69 |
| Nhạc hạ thêm 6 dB | 7/10 | 0,34 · 0,69 · 0,78 |
| Nhạc hạ thêm 12 dB | 7/10 | 0,34 · 0,78 · 0,87 |
| Nhạc hạ thêm 20 dB | 7/10 | 0,42 · 0,82 · 0,89 |

Ba tệp không dò ra ở mọi mức, kể cả khi nhạc đã nhỏ tới mức gần như không còn tác dụng làm nền. Vì vậy không có ngưỡng "nhạc thấp hơn giọng bao nhiêu dB" nào dùng được, và kết quả trên cả MP4 (một con số cho cả video) không đáng tin. Đây là một bản nhạc; nhạc khác có thể cho kết quả khác.

Quy định của chủ giọng (2026-10-06): không yêu cầu dò ra dấu trong bản đã trộn. Thay vào đó, mọi **tệp giọng chưa trộn** phải dò ra dấu trước khi trộn; giữ các tệp đó cùng chữ và seed chừng nào video còn đăng; và mô tả video ghi rõ giọng đọc là giọng tổng hợp. Kết quả "không thấy dấu" trên bản đã trộn không chứng minh được điều gì.
