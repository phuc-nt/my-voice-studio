---
name: voice-speak
description: Đọc một văn bản tiếng Việt bằng giọng đã clone qua VoiceStudio, có chuẩn bị văn bản, chia đoạn, soát chữ bị nuốt và tạo lại. Dùng khi người dùng đưa văn bản, bài viết, kịch bản video hoặc câu cần tạo thành audio.
---

# Từ văn bản đến audio

Bạn không nghe được âm thanh. Bạn kiểm soát chất lượng qua văn bản đầu vào và qua lời Whisper chép lại.

## 1. Chọn profile

```bash
curl -s http://127.0.0.1:3900/profiles
```

Profile đặt tên `<tên>NN`, tên không ghi phong cách. Tra bảng trong `docs/profiles.local.md` (hoặc `curl -s http://127.0.0.1:3900/profiles`) rồi chọn theo phong cách của văn bản. Nếu không rõ, hỏi. Không dùng profile demo cho sản phẩm thật: đó là giọng tiếng Anh.

## 2. Viết lại văn bản cho model đọc

Đây là phần bạn làm tốt nhất. Viết ra file `outputs/<tên>.txt` (thư mục này không vào Git), **mỗi dòng là một đoạn sẽ được tạo riêng**:

- Mỗi dòng một câu, dưới khoảng 220 ký tự. Hai câu ngắn liền ý có thể chung một dòng, nhưng bên làm video đã gặp cảnh model bỏ mất một vế khi gửi nhiều câu một lần, nên khi nghi ngờ thì tách.
- Số, ngày, giờ, tiền, phần trăm, số điện thoại, đơn vị: viết thành chữ đúng cách người Việt đọc trong ngữ cảnh đó. Viết "ngàn" thay cho "nghìn": "tám nghìn sáu trăm" từng bị đọc thành "tám sáu" ở cả năm seed, "tám ngàn sáu trăm" thì đúng. Năm 2024 là "hai ngàn không trăm hai mươi tư", số điện thoại đọc từng chữ số theo nhóm.
- Chữ viết tắt: viết đầy đủ (TP.HCM, ĐH, GS.TS, UBND).
- Từ tiếng Anh và tên riêng nước ngoài: giữ nguyên ở lần đầu. Nếu bước soát cho thấy model đọc sai thì đổi sang phiên âm tiếng Việt, hoặc dùng `[[i-pắp]]` và `[[EPUB|i-pắp]]` để giữ chữ gốc trong kịch bản. Các phiên âm đã dùng được: EPUB `i-pắp`, OPDS `ô pê đê ét`, app `áp`, PIN `pin`.
- Chữ không dấu trong ngoặc kép và câu kết bằng dấu `:` hay bị đọc lệch. Viết có dấu, bỏ ngoặc kép, đổi `:` thành `.`.
- Giữ chữ hoa và dấu câu. Dấu phẩy, dấu chấm, dấu ba chấm quyết định nhịp. Cần nghỉ dài thì thêm `[pause 500ms]`.
- Chỉ dùng tag `[laughter]` và `[sigh]`. Tag khác sẽ bị đọc to thành chữ.
- Không đổi nội dung hay giọng văn của người dùng. Chỉ đổi cách viết để model đọc đúng.

Với văn bản nhiều số, đối chiếu cách đọc số với script:

```bash
uv run scripts/normalize-vi.py -f <file gốc>
```

Kết quả của script là chữ thường toàn bộ và đọc sai ký hiệu "$", nên chỉ lấy cách đọc số từ đó, không dùng nguyên văn. Script đã viết "ngàn" thay cho "nghìn".

Nếu bạn đã đổi cách đọc một chỗ có thể hiểu hai nghĩa (ví dụ "3/4" là ngày hay phân số), nêu chỗ đó cho người dùng.

## 3. Tạo

```bash
uv run scripts/speak.py <profile_id> -f outputs/<tên>.txt
```

Mặc định là 32 bước, CFG 2.0, Speed 1.0, tối đa hai lần tạo lại cho mỗi đoạn. Mỗi đoạn mất khoảng 2,7 lần độ dài âm thanh, nên với văn bản dài hãy chạy ở chế độ nền. Thêm `--bits 24` khi người dùng còn chỉnh sửa hậu kỳ, `--engine voxcpm2` khi họ muốn engine khác và đã tải nó.

## 4. Đọc kết quả soát chữ

Mở `report.json` trong thư mục kết quả. Với mỗi đoạn bị đánh dấu, phân loại:

- **Whisper chép sai, model đọc đúng.** Dấu hiệu: chỉ có mục "khác" với từ đồng âm hoặc gần âm (gươm → gương), tên riêng, từ tiếng Anh, hoặc số viết bằng chữ số. Không tạo lại. Ghi vào danh sách "nên nghe để chắc".
- **Bị nuốt chữ thật.** Dấu hiệu: mục "thiếu" có cả cụm từ, hoặc audio ngắn hẳn so với số chữ. Tạo lại với seed khác:

  ```bash
  uv run scripts/speak.py --redo outputs/speak-<thời gian> <số đoạn>
  ```

- **Vẫn thiếu sau khi tạo lại.** Đổi văn bản, không đổi seed nữa: tách đoạn làm hai dòng ngắn hơn, bỏ từ khó, hoặc phiên âm từ tiếng Anh. Sau đó:

  ```bash
  uv run scripts/speak.py --redo outputs/speak-<thời gian> <số đoạn> --text "<câu đã viết lại>"
  ```

  Nếu vẫn không được sau hai lượt viết lại, thử `--cfg 2.5` cho một lượt chạy mới, rồi báo người dùng rằng đây là giới hạn của model (issue #668).

Nếu `speak.py` báo chưa có model chép lời, kết quả chưa được soát. Nói rõ điều đó, đừng báo là "ổn".

Tạo lại mà không đổi seed thì ra đúng kết quả cũ: cùng chữ, cùng seed, cùng CFG luôn cho một audio. `--redo` tự cộng seed lên một.

## 5. Mốc từng từ và dấu nhận biết (khi audio đi vào video)

Khi người dùng hoặc bên làm video cần phụ đề hay khớp hình:

```bash
uv run scripts/word-times.py outputs/speak-<thời gian> -o outputs/speak-<thời gian>/words.json
```

Mốc tính bằng giây từ đầu file của **từng câu**, chưa cộng vị trí trong `final.wav`. Script ép chữ vào audio, nên từ bị nuốt vẫn có mốc: chỉ chạy sau khi bước 4 đã sạch. Nếu từ đầu câu dài dưới 0,05 giây, dùng `speech_start` làm mốc đầu và nói cho người dùng biết.

Với các câu tạo ngoài `speak.py` (ví dụ gọi thẳng `/generate`), soát rơi chữ bằng cùng một luật:

```bash
uv run scripts/check-words.py --manifest <cau.json>
```

`RƠI CHỮ` thì tạo lại với seed khác. `XEM LẠI` thường là Whisper chép sai tên riêng hay phiên âm: đọc cột "khác" rồi quyết định, và nói cho người dùng biết câu nào cần nghe.

Khi cần xác nhận một file (kể cả MP4 đã dựng) còn dấu nhận biết giọng tổng hợp:

```bash
uv run scripts/check-watermark.py <file>...
```

"KHÔNG THẤY DẤU" trên bản đã trộn nhạc không có nghĩa là audio sạch dấu từ đầu: nền dày che được dấu. Báo đúng như vậy và đề nghị giữ tệp giọng chưa trộn.

Bên dùng ở repo khác gọi các lệnh này theo mục 13 của [docs/operations-guide.md](../../../docs/operations-guide.md).

## Báo cáo

- Đường dẫn `final.wav` và tổng thời lượng.
- Các chỗ bạn đã viết lại trong văn bản (số, viết tắt, phiên âm).
- Các đoạn đã tạo lại và lý do.
- Danh sách đoạn người dùng nên nghe lại, kèm số đoạn để họ yêu cầu tạo lại.
