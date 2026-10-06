# Chuẩn bị để clone giọng của chính bạn bằng tiếng Việt

Cập nhật: 2026-10-04. Áp dụng cho VoiceStudio 0.5.6 với engine mặc định OmniVoice, chạy trên Mac mini M4 24GB.

## Kết luận nhanh

Muốn clone giọng tiếng Việt tốt nhất với VoiceStudio, bạn cần chuẩn bị đúng một clip mẫu cho mỗi phong cách nói. Clip đó phải đạt các điều kiện sau:

- Dài 6–10 giây.
- Thu khô, gần mic, trong phòng yên tĩnh có đồ vải.
- Lưu dạng WAV mono.
- Đọc đúng phong cách bạn muốn giọng tạo ra sẽ có.
- Có transcript khớp từng chữ, đủ dấu.

Khi tạo giọng, cần làm thêm những việc sau:

- Chọn rõ ngôn ngữ Vietnamese.
- Tăng Steps từ 16 lên 32.
- Mỗi lần tạo chỉ dùng một đến ba câu (dưới 30 giây âm thanh).
- Khi có một bản đọc ưng ý, khóa seed để các lần sau giữ đúng giọng đó.

Clip mẫu quyết định gần như toàn bộ chất lượng. Mic đắt tiền không bù được cho phòng vang hay clip quá dài. VoiceStudio cũng có nói rằng "zero-shot cloning mirrors the acoustics of the reference clip" (clone zero-shot bắt chước cả âm học của clip mẫu, không chỉ giọng).

Bằng chứng và nguồn cho từng khuyến nghị nằm trong [261004-research-best-practices.md](261004-research-best-practices.md). Câu cần đọc khi thu nằm trong [recording-script-vietnamese.md](recording-script-vietnamese.md).

## 1. Thiết bị

- **Mic:** Mic USB rời là tốt nhất. Nếu chưa có, dùng mic iPhone hoặc tai nghe có mic cũng được, miễn là đặt đúng khoảng cách và không bị rè. Điều quan trọng là phòng yên và đặt mic đúng chỗ, không phải giá mic.
- **Khoảng cách:** Đặt mic cách miệng 10–15 cm, tức khoảng một bàn tay. Hơi lệch mic sang một bên để tránh tiếng bật hơi ở các âm "p", "b", "t". Nếu có màng lọc pop thì dùng.
- **Giữ cố định:** Không cầm mic trên tay, không xoay đầu khi đọc. Mọi clip nên thu cùng một vị trí để các profile nghe nhất quán.
- **Phần mềm thu:** Có hai cách.
  - Dùng trình ghi âm có sẵn trong VoiceStudio, ở panel Voice. Trình này có chọn mic, chế độ Mono và đồng hồ đo mức tín hiệu.
  - Dùng Audacity (miễn phí). Đặt Project Rate 48000 Hz, kênh Mono, rồi xuất WAV 24-bit.
  - Nếu thu bằng iPhone, vào Settings → Voice Memos → Audio Quality và chọn Lossless trước khi thu.

## 2. Phòng thu

- Chọn phòng nhỏ có rèm, thảm, giường, tủ quần áo hoặc ghế nệm. Có thể ngồi trước tủ quần áo đang mở. Tránh phòng trống, phòng tắm, hành lang và tường kính, vì những chỗ đó vang nhiều.
- Tắt máy lạnh, quạt, tủ lạnh gần đó và thông báo trên điện thoại. Đóng cửa sổ. Chọn giờ yên tĩnh, thường là tối muộn hoặc sáng sớm.
- Không bật nhạc hay TV, và trong phòng chỉ có một người nói. Model sẽ học luôn tiếng ồn, tiếng vang và giọng người khác lẫn trong clip.

## 3. Định dạng file

| Thông số | Nên dùng | Lý do |
|---|---|---|
| Định dạng | WAV (PCM) | Tránh nén mất dữ liệu như MP3 hay AAC. |
| Kênh | Mono | Chỉ có một giọng, nên stereo không cần thiết. |
| Tần số mẫu | 48 kHz (tối thiểu 24 kHz) | OmniVoice xuất ra 24 kHz và VoxCPM2 xuất ra 48 kHz. Thu ở 48 kHz thì dùng được cho mọi engine. |
| Độ sâu bit | 24-bit (16-bit cũng được) | Có dư biên độ khi chỉnh âm lượng. |
| Mức âm | Đỉnh khoảng −12 đến −6 dBFS, không bao giờ chạm 0 | Clipping (vỡ tiếng) không sửa được. |
| Xử lý hậu kỳ | Chỉ cắt khoảng lặng đầu và cuối | Không lọc ồn mạnh, không nén, không EQ, không thêm reverb, không auto-tune. Model sẽ chép lại cả các dấu vết xử lý đó. |

## 4. Ghi clip mẫu

### Độ dài

- OmniVoice khuyên dùng 3–10 giây. Tác giả repo đã ghi nhận rằng clip 6 giây cho kết quả rất tốt, còn clip 60 giây làm giọng méo và nuốt chữ.
- Trong VoiceStudio, clip có transcript bị giới hạn 20 giây. Clip không có transcript sẽ bị app tự chọn ra một đoạn 15 giây. Vì vậy, bạn nên tự cắt sẵn đoạn 6–10 giây tốt nhất.
- Các dịch vụ khác như Fish Audio khuyên dùng clip dài hơn (10–60 giây), nhưng đó là hướng dẫn cho model của họ. Với OmniVoice, hãy theo hướng dẫn của chính OmniVoice. Nếu muốn chắc, hãy so sánh clip 5, 8 và 12 giây cho cùng một câu.

### Nội dung

- Mỗi clip là một đến hai câu trọn vẹn. Clip nên bắt đầu và kết thúc đúng ở ranh giới câu, không cắt giữa chữ.
- Nói liền mạch, không ngập ngừng, không có khoảng lặng dài. Giữa hai câu chỉ nghỉ khoảng nửa giây.
- Clip mẫu cũng là chỉ đạo diễn xuất. Đọc đều đều thì giọng tạo ra cũng đều đều. Đọc tươi thì giọng tạo ra cũng tươi. Thì thầm thì giọng tạo ra bị hụt hơi. Đọc vội thì giọng tạo ra cũng vội.
- Clip phải bằng tiếng Việt. Nếu dùng clip tiếng Anh để đọc tiếng Việt, giọng tạo ra sẽ mang âm sắc của clip tiếng Anh.

### Nhiều profile theo phong cách

Ô Style trong VoiceStudio chỉ hiểu một bộ từ khóa tiếng Anh hoặc tiếng Trung cố định, ví dụ male, female, low pitch, whisper. Mô tả bằng tiếng Việt như "quảng cáo, sôi nổi" sẽ bị bỏ qua. Vì vậy, cách điều khiển phong cách tiếng Việt chắc chắn nhất là tạo một profile riêng cho mỗi phong cách. Kịch bản ghi âm đã chia sẵn sáu nhóm. Profile đặt tên theo quy ước `<tên>NN`, đánh số theo thứ tự tạo; bảng các profile đã tạo nằm ở mục 6 của [operations-guide.md](operations-guide.md).

| Phong cách | Dùng cho |
|---|---|
| Trò chuyện | Vlog, tin nhắn thoại, video đời thường |
| Kể chuyện | Audiobook, truyện, podcast |
| Đọc tin | Thuyết trình, video giải thích, đọc tin |
| Năng động | Quảng cáo, video ngắn |
| Cảm xúc | Đoạn có cảm xúc mạnh |
| Nhẹ nhàng | Thiền, ru ngủ, nội dung thư giãn |

Nên bắt đầu với hai profile, trò chuyện và kể chuyện. Chỉ thêm các profile khác khi thật sự cần.

## 5. Transcript

- Viết đúng từng chữ bạn đã nói, đủ dấu thanh, đủ dấu câu theo chỗ bạn ngắt hơi.
- Số đã đọc thành lời thì viết thành chữ, ví dụ "mười lăm độ", không viết "15 độ". Mục tiêu là chữ trong transcript khớp với tiếng trong clip.
- Nếu để trống, VoiceStudio sẽ tự chép lời bằng Whisper. Tuy nhiên, máy bạn hiện chỉ có Whisper tiny, và model này yếu với tiếng Việt. Muốn app tự chép lời tốt, hãy tải Whisper large-v3 (MLX, 3GB) trong Model Catalogue. Dù vậy, vẫn nên đọc lại và sửa tay, vì Whisper hay viết số thành chữ số và đôi khi sai dấu.
- Gõ bằng bộ gõ Unicode dựng sẵn, chuẩn NFC. Đây là mặc định của Telex và VNI trên macOS. VoiceStudio đã tự chuẩn hóa NFC sau khi sửa issue #502, nhưng giữ văn bản sạch từ đầu vẫn hơn.

## 6. Tạo profile trong VoiceStudio

1. Mở app bằng lệnh `cd ~/workspace/VoiceStudio && bun run dev`, chạy trong Terminal.app.
2. Vào Voice Clone, tạo profile mới, tải lên clip WAV (hoặc thu trực tiếp) và dán transcript.
3. Đặt Language là **Vietnamese**, không để Auto. Lỗi giọng tiếng Việt bị méo trước đây (issue #502) được sửa một phần bằng cách truyền đúng ngôn ngữ vào model.
4. Tạo thử bằng các "câu kiểm tra" trong kịch bản ghi âm.

## 7. Thiết lập khi tạo giọng

| Thiết lập | Khuyến nghị | Ghi chú |
|---|---|---|
| Language | Vietnamese | Luôn chọn rõ. |
| Steps | 32 | Mặc định của app là 16 để chạy nhanh. Theo phân tích trong PR #1142, 16 bước dễ đọc vội, nuốt hoặc sai âm tiết hơn. Trên máy bạn, 32 bước mất khoảng 12,7 giây cho 4,7 giây âm thanh, còn 16 bước mất khoảng 6,8 giây. |
| Guidance (CFG) | 2.0, tăng lên khoảng 2.5 nếu bị nuốt chữ | Tác giả VoiceStudio khuyên "bump CFG slightly" khi gặp lỗi bỏ từ. Tăng quá nhiều có thể làm giọng gắt, nên hãy nghe thử. |
| Speed | 1.0 | Đẩy tốc độ xa khỏi 1.0 làm tăng nguy cơ bỏ từ. |
| Temperature | Giữ mặc định | Tăng temperature làm tăng lỗi lặp và bỏ từ. |
| Seed | Để ngẫu nhiên lúc thử. Khi được bản ưng ý thì khóa profile hoặc dùng "Keep this seed". | Khóa seed giúp giọng ổn định giữa các lần tạo. |
| Độ dài mỗi lần tạo | Một đến ba câu, dưới 30 giây âm thanh | Văn bản càng dài thì càng dễ bị bỏ từ. Đây là giới hạn của model với tiếng Việt (issue #668). |
| Văn bản dài | Dùng tab Audiobook | Audiobook chạy 32 bước và gieo seed theo từng đoạn khi profile đã khóa seed (PR #1142). |
| Xuất file | WAV 24-bit nếu còn chỉnh sửa, 16-bit để nghe | Bấm "Check audio" để quét khoảng lặng dài, vỡ tiếng và đoạn rỗng. |

## 8. Viết văn bản đầu vào cho tiếng Việt

- **Số:** Từ bản sửa ở PR #1142, VoiceStudio giữ nguyên chữ số tiếng Việt và để model tự đọc. Lý do là thư viện num2words đọc sai, ví dụ đọc 2024 thành "hai nghìn lẻ hai mươi bốn". Hãy thử cả hai kiểu bằng các câu kiểm tra. Với năm, tiền, số điện thoại và giờ quan trọng, cách an toàn là viết thành chữ.
- **Viết tắt:** Viết đầy đủ, ví dụ "Thành phố Hồ Chí Minh" thay cho "TP.HCM", "Đại học" thay cho "ĐH", "giáo sư tiến sĩ" thay cho "GS.TS".
- **Từ tiếng Anh và tên riêng:** Nghe thử trước. Nếu model đọc sai, dùng cú pháp `[[phiên âm]]` ngay trong câu hoặc thêm vào Pronunciation dictionary của app.
- **Ngắt nghỉ:** Dấu phẩy, dấu chấm, dấu ba chấm và dấu chấm than thật sự ảnh hưởng nhịp đọc. Cần nghỉ dài thì dùng `[pause 500ms]` hoặc `[pause 1s]`, cú pháp này dùng được với mọi engine.
- **Âm thanh phi ngôn ngữ:** OmniVoice hiểu `[laughter]` và `[sigh]`. Các tag khác chủ yếu dành cho tiếng Trung. Đừng dán tag kiểu ElevenLabs như `[excited]`, vì model sẽ đọc to chúng thành chữ.

## 9. Kiểm tra chất lượng và so sánh A/B

1. **Nghe bằng tai nghe.** Tìm các lỗi sau: nuốt chữ, sai thanh (nhất là hỏi và ngã), giọng méo, tiếng vang, nhịp vội.
2. **Soát chữ bị nuốt.** Sau khi tải Whisper large-v3, chạy `TRANSCRIBE=1 scripts/ab-test.sh ...` để app chép lời lại từng file, rồi so với văn bản gốc.
3. **So sánh có kiểm soát** bằng [../scripts/ab-test.sh](../scripts/ab-test.sh). Script đọc cùng một câu, cùng seed, qua nhiều engine và số bước, rồi ghi thời gian vào `outputs/ab-*/results.tsv`.

   ```bash
   cd ~/workspace/my-voice-studio
   curl -s http://127.0.0.1:3900/profiles              # lấy profile_id
   scripts/ab-test.sh <profile_id> "Ông lão chậm rãi mở chiếc hộp gỗ cũ." "omnivoice" "16 32" 42
   ```

   Muốn so OmniVoice với VoxCPM2 thì cài VoxCPM2 trong Model Catalogue trước, tải về vài GB. Sau đó thêm `voxcpm2` vào danh sách engine. Script `scripts/compare_generation_quality.py` có sẵn trong repo VoiceStudio luôn gọi model với ngôn ngữ English, nên không dùng để đánh giá tiếng Việt được.
4. **Đổi clip mẫu trước khi đổi tham số.** Nếu giọng không giống bạn, thường nguyên nhân là clip mẫu, không phải tham số. Hãy thử take khác hoặc câu khác.

## 10. Khi zero-shot chưa đủ giống

Hãy theo thứ tự rẻ đến đắt:

1. **Đổi clip mẫu.** Thử clip dài hơn hoặc ngắn hơn, phong cách khác, take khác.
2. **Thử engine khác trong VoiceStudio.** VoxCPM2 hỗ trợ tiếng Việt, xuất 48 kHz và có chế độ clone kèm transcript. Confucius4-TTS cũng hỗ trợ tiếng Việt, nhưng chạy CPU trên Mac chậm khoảng 17 lần thời gian thực.
3. **Thử model chuyên tiếng Việt ngoài VoiceStudio.**
   - VieNeu-TTS v3 Turbo: giấy phép Apache-2.0, cần clip 3–8 giây, không cần transcript, chạy CPU được.
   - Bản OmniVoice fine-tune tiếng Việt `splendor1811/omnivoice-vietnamese`: chưa dùng thẳng trong VoiceStudio được, xem báo cáo research.
4. **Fine-tune hoặc LoRA bằng giọng của bạn.**
   - Cần 10–30 phút audio sạch kèm transcript. VieNeu khuyên 10–30 phút trên GPU khoảng 6GB, còn VoxCPM2 khuyên 5–10 phút.
   - Hướng dẫn train OmniVoice trong VoiceStudio được viết cho GPU NVIDIA, không phù hợp với Mac mini.
   - Bạn có thể dùng Google Colab như repo `google-colab-remote` đang làm với LoRA ảnh.
   - Vì vậy, hãy thu sẵn 15–30 phút ngay từ buổi thu đầu, xem phần cuối của kịch bản ghi âm.

## 11. Quyền riêng tư và giấy phép

- Chỉ clone giọng của chính bạn hoặc của người đã đồng ý bằng văn bản. VoiceStudio có endpoint ghi nhận consent cho profile, và OmniVoice cấm rõ việc dùng để mạo danh hay lừa đảo.
- Weights của OmniVoice theo giấy phép CC-BY-NC, tức là không dùng thương mại. Nếu cần dùng thương mại, hãy cân nhắc VoxCPM2 hoặc VieNeu-TTS (đều Apache-2.0) và tự đọc lại giấy phép trước khi dùng.
- Giọng nói là dữ liệu sinh trắc học. Thư mục `recordings/` và `outputs/` cùng mọi file audio đã bị loại khỏi Git qua `.gitignore`. Đừng push file ghi âm lên bất kỳ remote nào, kể cả repo private. Hãy sao lưu riêng, ví dụ ổ ngoài có mã hóa.
- Audio tạo ra có thể được VoiceStudio gắn dấu nhận diện là giọng tổng hợp. Đừng tìm cách gỡ dấu đó.

## Checklist trước buổi thu

- [ ] Phòng nhỏ có đồ vải. Đã tắt máy lạnh, quạt và thông báo.
- [ ] Mic cách miệng 10–15 cm, đặt hơi lệch, cố định.
- [ ] Thu WAV mono 48 kHz, đỉnh âm từ −12 đến −6 dBFS, thu thử 10 giây rồi nghe lại.
- [ ] In hoặc mở sẵn kịch bản ghi âm. Đã uống nước và tránh sữa ngay trước khi thu.
- [ ] Mỗi câu đọc 2–3 take, đặt tên file đúng mẫu.
- [ ] Chọn take tốt nhất, cắt còn 6–10 giây, viết transcript khớp từng chữ.
- [ ] Tạo profile với Language Vietnamese, chạy câu kiểm tra ở 32 bước.
- [ ] Khóa seed của bản tốt nhất.
- [ ] (Tùy chọn) Thu thêm 15–30 phút cho fine-tune.

## Câu hỏi còn mở

- Chưa ai kiểm chứng được clip mẫu "đủ sáu thanh" có làm giọng tạo ra đúng thanh hơn hay không. Đây là suy luận hợp lý, không có số liệu. Cách kiểm tra là so profile dùng câu đủ thanh với profile dùng câu bình thường.
- Chưa rõ OmniVoice giữ giọng miền Nam (hỏi và ngã gần như nhập một) hay miền Trung tốt đến đâu, vì dữ liệu huấn luyện không công bố tỉ lệ vùng miền.
- Chưa đo trên máy bạn: chất lượng tiếng Việt của VoxCPM2 so với OmniVoice, và tốc độ của VoxCPM2 trên MPS. Cả hai cần cài VoxCPM2 rồi chạy `ab-test.sh`.
- Chữ số tiếng Việt để nguyên cho model đọc thì có ổn với mọi loại số (năm, tiền, số thập phân) hay không thì chưa có kết luận. Hãy thử bằng các câu kiểm tra.
