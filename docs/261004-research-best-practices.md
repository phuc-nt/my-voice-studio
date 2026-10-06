# Best practice từ cộng đồng: VoiceStudio, OmniVoice và các model tiếng Việt

Thời điểm nghiên cứu: 2026-10-04. Phạm vi: VoiceStudio 0.5.6 (commit `c4d63ef`), model mặc định `k2-fsa/OmniVoice`, các engine khác có hỗ trợ tiếng Việt, và các model tiếng Việt từ cộng đồng. Mục tiêu là clone giọng của chính người dùng bằng tiếng Việt trên Mac mini M4 24GB.

## Kết luận chính

1. **Clip mẫu ngắn và sạch quan trọng hơn mọi tham số.**
   - Chính OmniVoice khuyên dùng clip 3–10 giây và cảnh báo clip dài làm giảm chất lượng.
   - Trong issue #50 của repo OmniVoice, clip 6 giây cho kết quả rất tốt, còn clip 60 giây làm giọng méo và mất chữ.
   - VoiceStudio còn ghi rõ rằng tiếng vang của phòng sẽ được chép sang giọng tạo ra.
2. **Tiếng Việt trên OmniVoice đạt mức tốt trên benchmark nhưng vẫn có lỗi thực tế.**
   - Theo paper, OmniVoice có khoảng 8.482 giờ dữ liệu tiếng Việt. Trên bộ MiniMax-24, lỗi nhận dạng là 1,373%, tương đồng giọng là 0,804.
   - Người dùng VoiceStudio đã báo các lỗi nuốt chữ, đọc vội và đọc sai năm. Tác giả xếp lỗi nuốt chữ vào giới hạn của model. Lỗi đọc năm và lỗi không ổn định thì đã sửa ở PR #1142.
3. **Ba thiết lập có bằng chứng rõ nhất cho tiếng Việt** là:
   - chọn rõ Language Vietnamese;
   - dùng 32 bước thay vì 16;
   - tạo từng đoạn ngắn dưới 30 giây.

   Đo trên Mac mini M4, 32 bước mất khoảng 12,7 giây cho 4,7 giây âm thanh, chậm gần gấp đôi 16 bước nhưng vẫn dùng được.
4. **Ô Style không điều khiển được phong cách tiếng Việt.** Ô này chỉ nhận một bộ tag tiếng Anh hoặc tiếng Trung cố định. Muốn đổi phong cách thì cần mỗi phong cách một clip mẫu riêng.
5. **Có lựa chọn thay thế mạnh cho tiếng Việt.**
   - VoxCPM2: Apache-2.0, 48 kHz, có sẵn trong VoiceStudio.
   - VieNeu-TTS v3 Turbo: chuyên tiếng Việt, Apache-2.0, chạy CPU.

   Cả hai cho phép dùng thương mại, khác với weights CC-BY-NC của OmniVoice. Chưa có benchmark độc lập so sánh trực tiếp các model này trên tiếng Việt.

## 1. OmniVoice: tác giả và paper nói gì

- **Độ dài clip mẫu.** README khuyên: "Use a 3–10 seconds reference audio clip. Longer audio slows down inference and may degrade cloning quality." Issue #50 xác nhận điều này bằng thực nghiệm (6 giây so với 60 giây).
- **Cùng ngôn ngữ.** README khuyên dùng clip mẫu cùng ngôn ngữ với giọng đầu ra. Clone khác ngôn ngữ có thể mang theo âm sắc của ngôn ngữ trong clip.
- **Reference và instruct.** Theo tips.md, khi clip mẫu và `instruct` mâu thuẫn, model ưu tiên clip mẫu. Khi chúng khớp nhau, `instruct` giúp ổn định hơn.
- **Câu rất ngắn.** Câu 1–2 giây khó tạo nếu không có clip mẫu.
- **Tham số mặc định của thư viện:**

  | Tham số | Giá trị |
  |---|---|
  | `num_step` | 32 |
  | `guidance_scale` | 2.0 |
  | `t_shift` | 0.1 |
  | `denoise` | True |
  | `position_temperature` | 5.0 |
  | `class_temperature` | 0 |
  | `preprocess_prompt` | True (cắt khoảng lặng dài trong clip, thêm dấu câu cuối transcript) |

  Paper cũng dùng 32 bước và guidance 2.
- **Số liệu tiếng Việt trong paper.** Paper công bố 8.481,98 giờ dữ liệu tiếng Việt, xếp vào nhóm "mid-resource".

  | Hệ thống | Lỗi nhận dạng (MiniMax-24) | SIM-o (tương đồng giọng) |
  |---|---|---|
  | OmniVoice | 1,373 | 0,804 |
  | MiniMax | 0,880 | 0,743 |
  | ElevenLabs | 73,415 | 0,369 |

  Như vậy, MiniMax đọc chính xác hơn một chút, còn OmniVoice giống giọng gốc hơn. Con số 73,4 của ElevenLabs bất thường, có thể do cách chấm, nên không nên dựa vào nó. Trên FLEURS, OmniVoice đạt CER 2,63%, trong khi audio thật đạt 3,49%.

## 2. VoiceStudio: các lỗi tiếng Việt đã gặp và cách xử lý

| Issue | Triệu chứng | Kết quả | Bài học |
|---|---|---|---|
| [#502](https://github.com/debpalash/VoiceStudio/issues/502) | Giọng clone tiếng Việt bị méo, khó nghe (v0.3.5) | Đã sửa bằng #565 (truyền đúng ngôn ngữ của profile) và #587 (chuẩn hóa NFC, chia đoạn theo mật độ chữ). Người dùng xác nhận "Output is clear and intelligible". | Luôn đặt Language là Vietnamese. |
| [#612](https://github.com/debpalash/VoiceStudio/issues/612) | Lỗi 400 khi gõ Style bằng tiếng Việt ("quảng cáo, sôi nổi") | #600 và #658 bỏ qua chữ không hợp lệ thay vì báo lỗi. Tác giả giải thích ô Style chỉ là bộ tag EN/ZH cố định. | Với tiếng Việt, cách đáng tin cậy là clone từ clip mẫu tiếng Việt. Ô Style chỉ chỉnh thô giới tính, tuổi, cao độ. |
| [#668](https://github.com/debpalash/VoiceStudio/issues/668) | Ngẫu nhiên bỏ từ, bỏ cụm từ. Càng dài càng hay bị. | Đóng với lý do giới hạn của model. Tác giả đã kiểm tra pipeline chữ và không thấy chữ nào bị rơi trước khi vào model. | Giữ mỗi lần tạo dưới 30 giây, speed khoảng 1.0, tăng nhẹ CFG và số bước, không tăng temperature. |
| [#1139](https://github.com/debpalash/VoiceStudio/issues/1139) và [PR #1142](https://github.com/debpalash/VoiceStudio/pull/1142) | Trang Voice đọc không ổn định, sai năm. Audiobook thì ổn hơn. | Sửa ba nguyên nhân. (1) num2words đọc số tiếng Việt sai, ví dụ 2024 thành "hai nghìn lẻ hai mươi bốn", nên giờ giữ nguyên chữ số cho model tự đọc. (2) Seed ghim của profile không được dùng trong Audiobook. (3) Trang Voice mặc định 16 bước, còn Audiobook 32 bước. | 16 bước "has audibly higher variance (rushed delivery, dropped/mispronounced syllables)". Hãy dùng 32 bước khi cần chất lượng. |

Ngoài các issue trên, tài liệu của VoiceStudio còn có các quy tắc sau:

- **Quy tắc clip mẫu ([docs/engines/omnivoice.md](https://github.com/debpalash/VoiceStudio/blob/main/docs/engines/omnivoice.md)):**
  - 3–10 giây là "sweet spot", và transcript giúp model bám giọng tốt hơn.
  - Clip có transcript bị giới hạn 20 giây.
  - Clip không có transcript được tìm trong 75 giây đầu, rồi app chọn đoạn 15 giây tốt nhất. Clip dài hơn 75 giây bị từ chối.
  - Clip đã mã hóa được lưu cache trong `prompt_cache/`.
- **Âm học truyền sang ([docs/generation-parameters.md](https://github.com/debpalash/VoiceStudio/blob/main/docs/generation-parameters.md)):** "a clip recorded in an echoey room clones echoey. Record dry and close-mic for clean output."
- **Diễn xuất ([docs/expressive-speech.md](https://github.com/debpalash/VoiceStudio/blob/main/docs/expressive-speech.md)):**
  - Clip mẫu là "performance direction": "a flat reference clones flat, an animated one clones animated".
  - `[pause Nms]` dùng được với mọi engine.
  - OmniVoice hiểu 13 tag. Chỉ `[laughter]` và `[sigh]` dùng tốt rộng rãi, các tag còn lại thiên về tiếng Trung.
  - Tag lạ không bị lọc đi, model sẽ đọc to chúng thành chữ.
  - Phát âm có thể ghi đè bằng `[[...]]` hoặc bằng từ điển phát âm.
  - Khóa profile hoặc "Keep this seed" giúp tái tạo đúng một bản đọc.
- **Chất lượng xuất ([docs/audio-quality.md](https://github.com/debpalash/VoiceStudio/blob/main/docs/audio-quality.md)):**
  - Có WAV 16, 24 và 32-bit.
  - "Check audio" quét khoảng lặng, vỡ tiếng và đoạn rỗng.
  - Tài liệu ghi: "Keep private recordings and generated voice comparisons outside Git."

## 3. Đo trên Mac mini M4 24GB (2026-10-04)

Cách đo: dùng profile demo, câu "Hôm nay trời Hà Nội mát mẻ, tôi ra hồ Gươm đi dạo và uống một ly cà phê sữa đá.", Language Vietnamese, seed 42, chạy qua API `/generate`, mỗi cấu hình chạy hai lần khi model đã nạp sẵn.

| Steps | Thời gian tạo | Độ dài âm thanh | Tỉ lệ so với thời gian thực |
|---|---|---|---|
| 16 | 6,83–6,85 giây | 4,68 giây | khoảng 1,46 lần |
| 32 | 12,74–12,75 giây | 4,66 giây | khoảng 2,7 lần |

Với cùng seed, độ dài đầu ra giữ nguyên giữa các lần chạy, tức là seed tái tạo được kết quả. Lần chạy đầu sau khi app nhàn rỗi mất khoảng 16 giây, vì backend nạp lại model sau 900 giây không dùng. Profile demo là giọng tiếng Anh, nên phép đo này chỉ cho biết tốc độ, không cho biết chất lượng tiếng Việt.

## 4. Các engine và model khác cho tiếng Việt

| Model | Có trong VoiceStudio? | Giấy phép weights | Clip mẫu | Transcript | Âm thanh ra | Chạy trên Mac | Fine-tune |
|---|---|---|---|---|---|---|---|
| OmniVoice (mặc định) | Có, đã cài | CC-BY-NC (không thương mại) | 3–10 giây | Nên có | 24 kHz | MPS, đã đo ở trên | Có script train, viết cho GPU NVIDIA |
| [VoxCPM2](https://github.com/OpenBMB/VoxCPM) | Có, chưa cài (Model Catalogue) | Apache-2.0 | App cắt khoảng lặng ở hai đầu và giữ tối đa 30 giây đầu | Có thì chạy chế độ nối tiếp (upstream gọi là "Ultimate cloning"). Nếu clip bị cắt ở 30 giây thì transcript bị bỏ qua. | 48 kHz | Hỗ trợ MPS | LoRA, 5–10 phút audio |
| Confucius4-TTS | Có, phải tự bật | Apache-2.0 | Không bắt buộc | Không cần | 22,05 kHz | CPU chậm khoảng 17 lần thời gian thực, MPS còn chậm hơn | Không rõ |
| [VieNeu-TTS v3 Turbo](https://github.com/pnnbao97/VieNeu-TTS) | Không | Apache-2.0, kể cả weights, dùng thương mại được | 3–8 giây, tự khử ồn | Không cần | 48 kHz | CPU qua ONNX, khoảng 0,55 RTF trên CPU theo tác giả | LoRA, 10–30 phút audio, GPU khoảng 6GB |
| [omnivoice-vietnamese](https://huggingface.co/splendor1811/omnivoice-vietnamese) | Không dùng thẳng được | Thẻ model ghi Apache-2.0, dataset CC-BY-NC-SA-4.0, model gốc CC-BY-NC | Như OmniVoice | Nên có | 24 kHz | Như OmniVoice | Đây chính là một bản fine-tune (1.000 giờ, 152 người nói) |
| [F5-TTS-Vietnamese-ViVoice](https://huggingface.co/hynt/F5-TTS-Vietnamese-ViVoice) | Không | CC-BY-NC-SA-4.0 | Khoảng 5–15 giây, theo bản port cho Mac | Có | 24 kHz | Có bản port cho Apple Silicon | Có (họ F5-TTS) |

Ghi chú về `omnivoice-vietnamese`:

- VoiceStudio cho phép đổi checkpoint OmniVoice qua biến môi trường `OMNIVOICE_MODEL`, nhận repo Hugging Face hoặc thư mục local (`backend/services/model_manager.py`).
- Tuy nhiên, repo fine-tune này không có thư mục `audio_tokenizer/` như repo gốc, nên gần như chắc chắn không chạy thẳng được.
- Một hướng thử là tạo thư mục local gồm file của bản fine-tune cộng với `audio_tokenizer/` của bản gốc, rồi trỏ `OMNIVOICE_MODEL` vào đó. Cách này chưa được kiểm chứng.
- Về giấy phép: bản fine-tune kế thừa weights CC-BY-NC của OmniVoice, nên dù thẻ model ghi Apache-2.0, an toàn nhất vẫn là coi nó là phi thương mại.

## 5. Best practice thu âm chung

Các nguồn hướng dẫn chung đồng thuận ở những điểm sau:

- Phòng yên tĩnh có đồ vải, không vang. [OpenVox](https://openvoxai.com/blog/best-voice-cloning-results-open-source-models) viết: "a quiet, furnished space beats expensive mic in reverberant room".
- Mic cách miệng 10–15 cm hoặc khoảng một bàn tay, đặt hơi lệch để tránh bật hơi, giữ cố định.
- Âm lượng đỉnh từ −12 đến −6 dBFS, WAV mono, không nén mất dữ liệu.
- Không lọc ồn mạnh, không nén, không reverb, không chỉnh cao độ.
- Chỉ một người nói, không nhạc nền. Âm lượng và cảm xúc đều trong cả clip.
- Clip cùng ngôn ngữ với giọng đầu ra. Cảm xúc và tốc độ của clip được chép sang giọng tạo ra.
- Transcript khớp từng chữ, dấu câu theo chỗ ngắt hơi thật.

Nguồn: [Fish Audio](https://docs.fish.audio/developer-guide/best-practices/voice-cloning), [Smallest.ai](https://docs.smallest.ai/waves/documentation/best-practices/voice-cloning-best-practices), [OpenVox](https://openvoxai.com/blog/best-voice-cloning-results-open-source-models).

Các nguồn khác nhau ở độ dài clip:

| Nguồn | Độ dài khuyên dùng |
|---|---|
| Fish Audio | Ít nhất 10 giây, tốt nhất 30–60 giây |
| OpenVox | 8–20 giây |
| Smallest.ai | 5–15 giây |
| OmniVoice | 3–10 giây |

Khác biệt này đến từ kiến trúc của từng model. Với OmniVoice, hãy theo hướng dẫn của chính nó, rồi tự so sánh vài độ dài theo cách OpenVox gợi ý (5, 10 và 20 giây). Lưu ý VoiceStudio giới hạn clip có transcript ở 20 giây.

## 6. Đề xuất hành động

1. Thu theo [recording-script-vietnamese.md](recording-script-vietnamese.md) và làm theo [voice-prep-guide-vietnamese.md](voice-prep-guide-vietnamese.md). Bắt đầu với hai profile, trò chuyện và kể chuyện.
2. Tải Whisper large-v3 (MLX) trong Model Catalogue. App sẽ tự chép lời clip mẫu, và `scripts/ab-test.sh` sẽ dùng nó để soát chữ bị nuốt.
3. Chạy `scripts/ab-test.sh` với 16 và 32 bước trên các câu kiểm tra, nghe và chọn.
4. Nếu OmniVoice chưa đạt, cài VoxCPM2 rồi chạy lại A/B. Sau đó cân nhắc VieNeu-TTS ngoài VoiceStudio.
5. Nếu cần giống hơn nữa, dùng 15–30 phút audio đã thu để fine-tune LoRA trên Colab, với VieNeu-TTS hoặc VoxCPM2.

## Nguồn

- OmniVoice: [README](https://github.com/k2-fsa/OmniVoice/blob/master/README.md), [docs/tips.md](https://github.com/k2-fsa/OmniVoice/blob/master/docs/tips.md), [issue #50](https://github.com/k2-fsa/OmniVoice/issues/50), [paper arXiv 2604.00688](https://arxiv.org/html/2604.00688v1).
- VoiceStudio: tài liệu trong repo đã clone (`docs/engines/omnivoice.md`, `docs/engines/voxcpm2.md`, `docs/engines/confucius4-tts.md`, `docs/generation-parameters.md`, `docs/expressive-speech.md`, `docs/audio-quality.md`, `docs/training.md`, `LICENSE-NOTICE.md`). Các issue: [#502](https://github.com/debpalash/VoiceStudio/issues/502), [#612](https://github.com/debpalash/VoiceStudio/issues/612), [#668](https://github.com/debpalash/VoiceStudio/issues/668), [#1139](https://github.com/debpalash/VoiceStudio/issues/1139), và [PR #1142](https://github.com/debpalash/VoiceStudio/pull/1142).
- Model tiếng Việt: [VieNeu-TTS](https://github.com/pnnbao97/VieNeu-TTS), [VieNeu-TTS-v3-Turbo trên Hugging Face](https://huggingface.co/pnnbao-ump/VieNeu-TTS-v3-Turbo), [splendor1811/omnivoice-vietnamese](https://huggingface.co/splendor1811/omnivoice-vietnamese), [hynt/F5-TTS-Vietnamese-ViVoice](https://huggingface.co/hynt/F5-TTS-Vietnamese-ViVoice), [bản port F5-TTS cho Mac](https://github.com/thomasvuong/F5-TTS-Vietnamese_Clone_Voice_RunOnMac), [VoxCPM](https://github.com/OpenBMB/VoxCPM).
- Hướng dẫn thu âm chung: [Fish Audio](https://docs.fish.audio/developer-guide/best-practices/voice-cloning), [Smallest.ai](https://docs.smallest.ai/waves/documentation/best-practices/voice-cloning-best-practices), [OpenVox](https://openvoxai.com/blog/best-voice-cloning-results-open-source-models).
- Chuẩn hóa văn bản tiếng Việt, nếu sau này muốn tự động hóa: [soe-vinorm](https://pypi.org/project/soe-vinorm/), [Vinorm](https://github.com/v-nhandt21/Vinorm), [VietNormalizer (arXiv 2603.04145)](https://arxiv.org/pdf/2603.04145).

## Câu hỏi còn mở

- Không tìm thấy thảo luận đáng kể nào trên Reddit hay diễn đàn về chất lượng tiếng Việt của OmniVoice. Nguồn cộng đồng chủ yếu là các issue GitHub của VoiceStudio.
- Chưa có benchmark độc lập so sánh OmniVoice, VoxCPM2 và VieNeu-TTS trên tiếng Việt. Cần tự nghe bằng `ab-test.sh`.
- Chưa rõ VoxCPM2 chạy trên MPS của M4 nhanh đến đâu và giữ thanh điệu tiếng Việt tốt đến đâu.
- Chưa kiểm chứng được cách ghép `audio_tokenizer/` để chạy `omnivoice-vietnamese` trong VoiceStudio.
- Giấy phép của bản fine-tune `omnivoice-vietnamese` mâu thuẫn: thẻ model ghi Apache-2.0, nhưng model gốc là CC-BY-NC. Cần hỏi tác giả nếu định dùng thương mại.
- Issue #668 đóng mà chưa có bản sửa ở tầng model. Chưa rõ lỗi bỏ từ tiếng Việt có giảm ở các bản OmniVoice mới hơn hay không.
