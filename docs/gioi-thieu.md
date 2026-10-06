# Tạo profile giọng nói cá nhân bằng VoiceStudio và my-voice-studio

Tài liệu này dành cho một agent (hoặc một người) chưa biết gì về hai repo dưới đây. Đọc xong, bạn cài được cả hai, giúp một người thu giọng, tạo profile giọng của chính họ, và dùng profile đó để đọc văn bản tiếng Việt. Mọi thứ chạy trên máy của người dùng, không gửi audio đi đâu.

| Repo | Vai trò | Địa chỉ |
|---|---|---|
| VoiceStudio (repo gốc) | App và backend tạo giọng | <https://github.com/debpalash/VoiceStudio> |
| my-voice-studio (repo này) | Tài liệu, script và skill bao quanh VoiceStudio cho tiếng Việt | <https://github.com/phuc-nt/my-voice-studio> |

## 1. Đọc trước khi làm

Bốn điều sau quyết định cách bạn làm việc, nên chúng đứng trước phần cài đặt.

- **Chỉ clone giọng của chính người dùng**, hoặc của người đã đồng ý bằng văn bản. Nếu người dùng đưa clip của người khác mà không có văn bản đồng ý, hãy dừng lại.
- **Giọng nói là dữ liệu sinh trắc học.** Không `git add` file audio, không gửi bản thu hay clip mẫu lên dịch vụ bên ngoài (kể cả dịch vụ chép lời hay lọc ồn trực tuyến), không đẩy `recordings/` hay `outputs/` lên remote nào. `.gitignore` của repo này đã chặn sẵn các định dạng audio.
- **Agent không nghe được âm thanh.** Mọi nhận xét của bạn về audio phải dựa trên số đo của script, và bạn phải nói rõ điều đó. Người dùng là người nghe và quyết định cuối cùng.
- **Hỏi trước khi tải model.** Mỗi model nặng vài GB. Cũng hỏi trước khi xóa profile, clip trong `recordings/` hay kết quả trong `outputs/`.

Giấy phép: mã nguồn VoiceStudio theo AGPL-3.0. Weights của OmniVoice (model mặc định) theo CC-BY-NC, nên giọng tạo bằng model này chỉ được dùng phi thương mại.

## 2. VoiceStudio là gì

VoiceStudio là một app desktop (Electron) kèm backend FastAPI chạy ở `http://127.0.0.1:3900`. Tài liệu này viết theo bản 0.5.6. App tạo giọng theo kiểu zero-shot: bạn đưa một clip mẫu ngắn và transcript khớp từng chữ, model đọc văn bản mới bằng giọng trong clip. Không có bước huấn luyện.

- Engine mặc định là OmniVoice (3,27 GB, xuất audio 24 kHz).
- Một "profile" là một clip mẫu, transcript của nó và ngôn ngữ. Profile lưu trong dữ liệu của app trên máy, và id của profile chỉ đúng trên máy đó.
- App tự gắn dấu nhận biết giọng tổng hợp (watermark) vào audio tạo ra. Không tìm cách gỡ dấu này.
- App có giao diện đầy đủ: Voice Clone, Model Catalogue, lịch sử. Các script trong repo này chỉ cần backend.

## 3. Repo này bổ sung gì

VoiceStudio lo phần tạo giọng. Repo này lo những việc trước và sau đó, là chỗ quyết định chất lượng với tiếng Việt.

| VoiceStudio chưa có | Repo này thêm |
|---|---|
| Hướng dẫn thu clip mẫu tiếng Việt | [voice-prep-guide-vietnamese.md](voice-prep-guide-vietnamese.md), [recording-session.md](recording-session.md), kịch bản 12 câu đủ sáu thanh trong [recording-script-vietnamese.md](recording-script-vietnamese.md) |
| Công cụ thu và chuẩn bị clip | `record.py` (hiện từng câu, thu, đặt tên, đo ngay), `prep-clip.py` (đổi sang WAV mono 48 kHz 24-bit, cắt khoảng lặng) |
| Cách biết clip nào đủ tốt | `check-clip.py` đo độ dài, mức âm, nền ồn, DNSMOS rồi xếp hạng các take |
| Tạo profile có kiểm tra | `make-profile.py` từ chối clip bị `LỖI` và transcript có chữ số, đặt Language Vietnamese |
| Đọc số, ngày, tiền tiếng Việt | `normalize-vi.py` viết tất cả thành chữ |
| Đọc văn bản dài | `speak.py` chia đoạn, tạo từng đoạn, soát chữ bị nuốt, tự tạo lại, ghép file |
| Kiểm tra kết quả | `check-words.py` (chữ bị rơi), `score.py` (độ giống giọng, DNSMOS), `word-times.py` (mốc thời gian từng từ để làm phụ đề), `check-watermark.py` (dấu giọng tổng hợp) |
| So sánh cấu hình | `ab-test.sh` tạo cùng một câu với nhiều engine hoặc số bước |
| Quy trình cho agent | [CLAUDE.md](../CLAUDE.md) và ba skill trong `.claude/skills/`: `voice-clip` (bản thu → profile), `voice-speak` (văn bản → audio), `voice-compare` (so cấu hình) |

Tài liệu đầy đủ nhất là [operations-guide.md](operations-guide.md). Tài liệu bạn đang đọc chỉ đủ cho lần đầu.

## 4. Yêu cầu

- Mac dùng chip Apple Silicon. Bộ công cụ được thử trên Mac mini M4, 24 GB RAM. Bước soát chữ dùng Whisper trên MLX nên chỉ chạy trên Apple Silicon. VoiceStudio có bản cho Linux và Windows, nhưng các script ở đây chưa được thử ngoài macOS.
- Khoảng 10 GB ổ đĩa trống cho model và thư viện.
- `git`, `bun`, `uv`, `ffmpeg` (script cần cả `ffprobe`). Kiểm tra bằng `which git bun uv ffmpeg ffprobe`. Thiếu cái nào thì cài bằng Homebrew: `brew install oven-sh/bun/bun uv ffmpeg`.
- Một micro. Máy không có mic thì thu bằng iPhone: app Voice Memos, đặt chất lượng Lossless, rồi AirDrop sang máy.
- Một phòng yên tĩnh, ít vang.

## 5. Cài đặt

Các lệnh dưới đây giả định cả hai repo nằm trong `~/workspace`. Đặt chỗ khác thì đổi đường dẫn cho khớp.

### Bước 1: cài VoiceStudio

```bash
mkdir -p ~/workspace && cd ~/workspace
git clone https://github.com/debpalash/VoiceStudio.git
cd VoiceStudio
bun install
bun run setup:api
```

`bun run setup:api` cài thư viện Python của backend và mất vài phút. Repo gốc cũng có trình cài một lệnh (`curl -fsSL https://voicestudio.sh/install | sh`), nhưng cách clone ở trên là cách đã được thử với bộ script này.

### Bước 2: bật backend và tải model

```bash
cd ~/workspace/VoiceStudio && bun run dev:api
```

Lệnh này chạy liên tục, nên hãy chạy ở chế độ nền hoặc trong một cửa sổ terminal riêng. Kiểm tra backend đã lên:

```bash
curl -sf http://127.0.0.1:3900/health
```

Sau đó cần hai model. Hãy hỏi người dùng trước khi tải.

| Model | Dung lượng | Dùng cho |
|---|---|---|
| OmniVoice | 3,27 GB | Tạo giọng. Bắt buộc. |
| Whisper large-v3 MLX | Khoảng 3 GB | Soát chữ bị nuốt và lấy mốc thời gian từng từ. Thiếu model này vẫn tạo được audio, nhưng `speak.py` sẽ ghi các đoạn là `chưa soát`. |

Cách tải: mở app đầy đủ bằng `cd ~/workspace/VoiceStudio && bun run dev`, vào Model Catalogue, và bấm tải từng model. Nếu chạy lệnh này trong terminal của VS Code thì dùng `env -u ELECTRON_RUN_AS_NODE bun run dev`.

### Bước 3: cài repo này

```bash
cd ~/workspace
git clone https://github.com/phuc-nt/my-voice-studio.git
cd my-voice-studio
uv sync
```

Mọi lệnh ở các mục sau chạy từ thư mục gốc của repo này. Nếu backend không ở địa chỉ mặc định, đặt biến môi trường `VOICESTUDIO_API`.

Nếu bạn là Claude Code và đang mở repo này, [CLAUDE.md](../CLAUDE.md) và ba skill đã được nạp sẵn. Tên và id profile của từng máy ghi trong `docs/profiles.local.md`, file này không vào Git.

## 6. Use case: tạo profile giọng của chính bạn

Dưới đây "người dùng" là người có giọng được clone. Mỗi bước ghi rõ ai làm.

### Bước 1: thu âm (người dùng)

Người dùng đọc [recording-session.md](recording-session.md) rồi thu theo một trong hai cách.

Thu trực tiếp bằng mic của máy. Script cần người bấm phím, nên agent không chạy thay được:

```bash
uv run scripts/record.py --test             # thu thử để chỉnh gain và đo nền phòng
uv run scripts/record.py --sentences 1-5    # thu các câu 1 đến 5, mỗi câu ba take
```

Hoặc thu bằng iPhone: mỗi câu trong [kịch bản](recording-script-vietnamese.md) thu thành một bản ghi riêng, trong đó đọc câu ấy ba lần và im lặng ít nhất ba giây giữa hai lần. AirDrop các bản ghi sang máy. Phần tách mỗi bản ghi thành các take thì agent chạy được:

```bash
uv run scripts/record.py --from-file <bản-thu-câu-1.m4a> --sentences 1
```

Cả hai cách đều lưu các take vào `recordings/` với tên dạng `<phong-cách>-<số câu>-take<lần>.wav`. Nếu người dùng đã có sẵn một clip riêng, đổi nó sang đúng định dạng bằng:

```bash
uv run scripts/prep-clip.py <bản-thu> recordings/tro-chuyen-01-take1.wav
```

Một clip mẫu tốt dài 6–10 giây (ngắn hơn vẫn dùng được, dài hơn 10 giây thì nên cắt), là một câu tiếng Việt trọn vẹn, đọc bằng đúng giọng và phong cách mà người dùng muốn nghe lại. Model bắt chước cả tốc độ lẫn cảm xúc của clip.

### Bước 2: đo và chọn clip (agent đo, người dùng nghe)

```bash
uv run scripts/check-clip.py recordings/
uv run scripts/check-clip.py --asr recordings/    # thêm bước chép lời, cần Whisper
```

Script chấm từng clip và xếp hạng. Bỏ các clip bị `LỖI`. Trong các clip còn lại, agent đề xuất hai hoặc ba bản có số đo tốt nhất, và người dùng nghe để chọn bản giống mình nhất. Số đo không thay được tai người ở bước này.

### Bước 3: chốt transcript (agent)

Transcript phải khớp từng chữ với những gì người dùng thật sự đọc trong clip, kể cả khi họ đọc lệch kịch bản. Viết số thành chữ. Dùng kết quả `--asr` để phát hiện chỗ lệch, rồi hỏi người dùng nếu chưa chắc. Transcript sai một chữ sẽ làm giọng tạo ra bị nuốt hoặc thêm chữ.

### Bước 4: tạo profile (agent)

```bash
uv run scripts/make-profile.py <tên> recordings/<clip đã chọn>.wav "Lời đã đọc trong clip."
```

Script in ra id của profile. Ghi lại id này, vì mọi lệnh tạo giọng đều cần nó. Xem lại danh sách bất cứ lúc nào bằng `curl -s http://127.0.0.1:3900/profiles`.

Đặt tên theo kiểu tên người cộng số thứ tự hai chữ số, ví dụ `lan01`, `lan02`. Nên tạo riêng một profile cho mỗi phong cách (trò chuyện, kể chuyện), mỗi profile từ một clip đọc đúng phong cách đó. Ghi vào `docs/profiles.local.md` mỗi profile ứng với id, clip và phong cách nào, vì tên không nói điều đó.

Nếu app hỏi xác nhận đây là giọng của bạn (consent), người dùng tự xác nhận trong app. Agent không xác nhận thay.

### Bước 5: đọc thử và soát (agent tạo, người dùng nghe)

```bash
uv run scripts/normalize-vi.py "Năm 2024 doanh thu tăng 15% lên 3,5 tỷ đồng."
uv run scripts/speak.py <profile_id> "Chào bạn, đây là giọng của tôi do máy tạo ra."
uv run scripts/speak.py <profile_id> -f outputs/bai-viet.txt
```

Với file văn bản, mỗi dòng là một đoạn. `speak.py` tạo từng đoạn, cho Whisper chép lời lại để so với chữ đã gửi, tự tạo lại đoạn thiếu chữ, rồi ghép tất cả thành một file trong `outputs/speak-<thời gian>/`. Người dùng nghe file ghép. Đoạn nào chưa ổn thì tạo lại riêng đoạn đó:

```bash
uv run scripts/speak.py --redo outputs/speak-<thời gian> 3
uv run scripts/speak.py --redo outputs/speak-<thời gian> 3 --text "Câu đã viết lại."
```

Nếu người dùng thấy giọng chưa giống, nguyên nhân thường nằm ở clip mẫu. Quay lại bước 2 và thử clip khác trước khi chỉnh thông số.

### Bước 6: các kiểm tra khác khi cần (agent)

```bash
uv run scripts/check-words.py --manifest cau.json                    # soát rơi chữ cho nhiều câu
uv run scripts/score.py outputs/<thư mục> --profile <profile_id>     # độ giống giọng và DNSMOS
uv run scripts/word-times.py <câu.wav> --text "<chữ đã gửi đi>"      # mốc từng từ cho phụ đề
uv run scripts/check-watermark.py <file audio>                       # dấu giọng tổng hợp
scripts/ab-test.sh <profile_id> "Câu cần thử." "omnivoice" "16 32"   # so 16 và 32 bước
```

`cau.json` có dạng `[{"file": "001.wav", "text": "..."}]`.

## 7. Thiết lập và mẹo đã kiểm chứng

- Luôn đặt Language là **Vietnamese**, không để Auto. Các script đã làm sẵn việc này.
- Dùng 32 bước và CFG 2.0. Trên Mac mini M4, một câu dài khoảng 5 giây mất chừng 13 giây để tạo (16 bước mất chừng 7 giây).
- Giữ mỗi đoạn dưới 30 giây âm thanh. `speak.py` tự chia ở khoảng 220 ký tự.
- Viết mọi con số thành chữ trước khi tạo. `normalize-vi.py` viết "ngàn" thay cho "nghìn", vì có câu model nuốt mất chữ "nghìn".
- Từ mượn và chữ viết tắt: viết `[[chữ gốc|cách đọc]]`, ví dụ `[[app|áp]]`, `[[OPDS|ô pê đê ét]]`. Model đọc phần sau dấu gạch đứng, còn các script soát chữ hiểu cả hai phần.
- Cùng văn bản, cùng seed và cùng thông số thì cho ra cùng một file. Muốn một bản đọc khác, đổi seed. Mặc định là 42.
- Cần câu dài hay ngắn hơn một chút thì dùng tham số `duration` của API, trong khoảng cộng trừ 10% so với độ dài tự nhiên. Chi tiết ở mục 13 của [operations-guide.md](operations-guide.md).

## 8. Giới hạn cần biết

- Điểm giống giọng của `score.py` đến từ model huấn luyện trên tiếng Anh. Chỉ dùng để so hai bản với nhau, không kết luận "giống" hay "không giống" từ một con số.
- Ngưỡng nền ồn và DNSMOS trong `check-clip.py` là ước lượng.
- Whisper đôi khi chép sai từ mượn dù audio đọc đúng. Khi `check-words.py` báo `XEM LẠI`, người dùng nghe lại câu đó trước khi tạo lại.
- `word-times.py` cho mốc bắt đầu đáng tin hơn mốc kết thúc ở từ đứng ngay sau một quãng nghỉ dài. Khi làm phụ đề, lấy mốc bắt đầu của từ kế tiếp làm mốc kết thúc.
- Dấu watermark dò được trên file giọng chưa trộn nhạc, nhưng không còn dò được ổn định sau khi trộn nhạc nền. Hãy giữ file giọng gốc, và ghi rõ trong phần mô tả sản phẩm rằng đây là giọng tổng hợp.

## 9. Khi gặp lỗi

| Hiện tượng | Cách xử lý |
|---|---|
| Script báo không kết nối được API | Backend chưa chạy. Chạy `cd ~/workspace/VoiceStudio && bun run dev:api`, rồi thử lại `curl -sf http://127.0.0.1:3900/health`. |
| `speak.py` ghi mọi đoạn là `chưa soát` | Chưa có Whisper large-v3 MLX. Tải trong Model Catalogue sau khi hỏi người dùng. |
| `make-profile.py` từ chối clip | Clip bị `LỖI` theo `check-clip.py`. Đọc lý do script in ra, thu lại hoặc chọn take khác. |
| `make-profile.py` từ chối transcript | Transcript còn chữ số. Viết thành chữ đúng như người dùng đã đọc. |
| App không mở khi chạy `bun run dev` trong VS Code | Dùng `env -u ELECTRON_RUN_AS_NODE bun run dev`. |
| Giọng tạo ra nuốt chữ ở một câu | Tạo lại với seed khác bằng `--redo`. Vẫn lỗi thì viết lại câu: tách câu dài, đổi từ, viết phiên âm cho từ mượn. |

Các tình huống khác nằm trong mục xử lý sự cố của [operations-guide.md](operations-guide.md).
