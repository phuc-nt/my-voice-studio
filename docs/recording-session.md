# Hướng dẫn buổi thu clip mẫu

Tài liệu này là trình tự làm trong một buổi thu, dùng [../scripts/record.py](../scripts/record.py). Lý do của từng yêu cầu nằm ở [voice-prep-guide-vietnamese.md](voice-prep-guide-vietnamese.md), các câu cần đọc nằm ở [recording-script-vietnamese.md](recording-script-vietnamese.md).

Buổi đầu chỉ cần câu 1–5 (trò chuyện và kể chuyện), mỗi câu ba take. Tính cả chuẩn bị là khoảng 20–30 phút.

## Chọn cách thu

Mac mini không có mic tích hợp. Nếu máy bạn không có thiết bị thu nào, bạn cần một trong hai cách:

| Cách | Cần gì | Khi nào chọn |
|---|---|---|
| A. Thu thẳng trên Mac | Mic USB hoặc tai nghe có mic cắm vào Mac mini | Có mic rời. Script hiện câu, đo mức và báo kết quả ngay sau mỗi take. |
| B. Thu bằng iPhone | iPhone với app Voice Memos | Chưa có mic rời. Thu xong mới biết kết quả. |

Tai nghe Bluetooth (kể cả AirPods) thường thu ở tần số mẫu thấp khi dùng làm mic, và `check-clip.py` sẽ báo `LỖI` nếu dưới 24 kHz. Nên dùng mic có dây.

## Trước khi thu

1. **Phòng:** phòng nhỏ có rèm, thảm, giường, hoặc ngồi trước tủ quần áo đang mở. Tắt máy lạnh, quạt, đóng cửa sổ, tắt thông báo điện thoại.
2. **Mic:** đặt cố định cách miệng 10–15 cm (khoảng một bàn tay), hơi lệch sang một bên. Không cầm tay. Giữ nguyên vị trí cho cả buổi.
3. **Người:** uống nước, tránh sữa ngay trước khi thu. Đọc thành tiếng cả năm câu một lượt cho quen miệng.
4. **Giọng:** giữ giọng vùng miền của bạn. Đọc đúng phong cách ghi ở đầu mỗi nhóm, vì model chép cả tốc độ và cảm xúc trong clip.

## Cách A. Thu thẳng trên Mac

Chạy trong Terminal.app. Lần đầu macOS sẽ hỏi quyền Microphone cho Terminal, hãy đồng ý.

```bash
cd ~/workspace/my-voice-studio

# 1. Xem máy đã nhận mic chưa. Dòng có "(1 in" hoặc "(2 in" là mic.
uv run scripts/record.py --devices

# 2. Thu thử để chỉnh gain: im lặng 3 giây, đọc một câu, rồi dừng
uv run scripts/record.py --test

# 3. Thu câu 1–5, mỗi câu ba take
uv run scripts/record.py
```

Nếu có nhiều mic, chọn bằng `--device <số thứ tự hoặc tên>`.

**Bước thu thử.** Script báo đỉnh âm và nền phòng. Chỉnh Input volume trong System Settings → Sound → Input cho đến khi đỉnh nằm trong khoảng −12 đến −6 dBFS. Nếu nền phòng trên −50 dBFS, tìm nguồn ồn trước khi thu thật. Sau đó không đổi gain hay khoảng cách nữa.

**Mỗi take.**

1. Script hiện câu và gợi ý phong cách. Đọc thầm một lần.
2. Bấm Enter, **chờ một nhịp**, rồi đọc. Đọc xong **chờ một nhịp**, rồi bấm Enter. Script bỏ 0,3 giây ở mỗi đầu để loại tiếng gõ phím, nên nếu đọc ngay sau khi bấm thì chữ đầu sẽ bị cắt.
3. Script cắt khoảng lặng hai đầu, lưu vào `recordings/` với tên đúng mẫu, rồi in kết luận `ĐẠT`, `XEM LẠI` hoặc `LỖI` kèm lý do.
4. Bấm `x` để xóa take nếu bạn đọc vấp, đọc sai chữ, hoặc có tiếng động lạ. Bấm Enter để giữ.

Các phím khác: `n` sang câu tiếp, `q` thoát. Chạy lại lệnh thì script tiếp tục từ câu chưa đủ take, không ghi đè file cũ.

## Cách B. Thu bằng iPhone

1. Trên iPhone: Settings → Voice Memos → Audio Quality → **Lossless**.
2. Đặt iPhone cố định trên bàn, đầu dưới (chỗ có mic) hướng về miệng, cách 10–15 cm. Không cầm tay.
3. Mở kịch bản trên màn hình Mac: `uv run scripts/record.py --list`.
4. **Thu mỗi câu một bản ghi.** Trong mỗi bản ghi, đọc câu đó ba lần, giữa hai lần **im lặng ít nhất ba giây**. Đọc vấp thì cứ im lặng ba giây rồi đọc lại; đọc bao nhiêu lần cũng được.
5. Chuyển các bản ghi sang Mac bằng AirDrop. Không gửi qua dịch vụ nào khác.
6. Tách từng bản ghi thành các take:

   ```bash
   cd ~/workspace/my-voice-studio
   uv run scripts/record.py --from-file ~/Downloads/cau-1.m4a --sentences 1
   uv run scripts/record.py --from-file ~/Downloads/cau-2.m4a --sentences 2
   # ... đến câu 5
   ```

   Script tìm các quãng có tiếng nói cách nhau hơn 1,5 giây (tiếng hít hơi ngắn không tính), lưu mỗi quãng thành một take và in kết luận cho từng take.

Nếu bạn thu cả buổi vào một bản ghi duy nhất, chạy `--from-file buoi-thu.m4a --sentences 1-5`. Cách này chỉ dùng được khi bạn đọc đúng thứ tự và mỗi câu đúng ba lần. Số lần đọc không khớp thì script in bảng mốc thời gian và dừng, không lưu gì; khi đó cắt tay bằng `prep-clip.py --start --end`.

Vì cách B không thu thử được, hãy thu câu 1 trước, tách và xem kết quả, rồi mới thu các câu còn lại.

## Sau khi thu

1. **Nghe lại bằng tai nghe.** Mở từng file trong `recordings/` (nhấn Space trong Finder). Loại take đọc vấp, sai chữ, có tiếng thở mạnh, tiếng bật hơi hoặc tiếng động nền. Số đo không bắt được các lỗi này.
2. **Xếp hạng theo số đo:**

   ```bash
   uv run scripts/check-clip.py recordings/
   ```

3. **Tạo profile.** Nói với Claude Code "chọn take tốt nhất trong recordings/ và tạo profile", hoặc tự chạy:

   ```bash
   cd ~/workspace/VoiceStudio && bun run dev:api      # ở một terminal khác
   uv run scripts/make-profile.py lan01 recordings/tro-chuyen-01-take2.wav "Sáng nay mình dậy sớm, pha một ấm trà nóng rồi ngồi ngoài hiên nghe những hạt mưa nhỏ rơi trên mái tôn."
   ```

   Transcript phải là lời bạn đã đọc thật. Nếu take được chọn có chỗ đọc khác kịch bản, sửa transcript theo lời đã đọc.

4. **Sao lưu** `recordings/` ra ổ ngoài có mã hóa. Thư mục này không vào Git.

## Đọc kết quả của script

| Thông báo | Ý nghĩa | Làm gì |
|---|---|---|
| `LỖI: vỡ tiếng` | Tín hiệu chạm 0 dBFS | Giảm gain hoặc lùi xa mic, thu lại. Không sửa được bằng phần mềm. |
| `đỉnh ... quá sát 0` | Còn ít khoảng dư | Giảm gain một chút cho các take sau |
| `đỉnh ... quá nhỏ` | Thu quá nhỏ | Tăng gain hoặc lại gần mic |
| `ngắn hơn 6 giây` | Đọc nhanh, hoặc bị cắt mất chữ | Nghe lại. Nếu đủ câu thì vẫn dùng được. |
| `dài hơn 10 giây` | Đọc chậm hoặc ngập ngừng | Thu lại liền mạch hơn |
| `có khoảng lặng ... giữa clip` | Ngắt quá lâu giữa câu | Thu lại, giữa hai vế chỉ nghỉ khoảng nửa giây |
| `nền ồn` hoặc `DNSMOS nền thấp` | Phòng ồn hoặc vang | Tìm nguồn ồn, thêm đồ vải, đổi chỗ ngồi. Không lọc ồn bằng phần mềm. |
| `LỖI: tần số mẫu ... thấp hơn 24 kHz` | Mic thu ở chất lượng thấp | Đổi mic (thường gặp với tai nghe Bluetooth) |
| `Không thu được tín hiệu` | Chưa cấp quyền hoặc chọn sai mic | System Settings → Privacy & Security → Microphone, hoặc `--device` |

Ngưỡng nền ồn và DNSMOS là ước lượng, chưa được hiệu chỉnh trên giọng thật. Take bị `XEM LẠI` mà bạn nghe thấy sạch thì vẫn dùng được.

## Các nhóm còn lại

Khi đã có profile trò chuyện và kể chuyện và thấy cần thêm phong cách:

```bash
uv run scripts/record.py --sentences 6-7      # đọc tin
uv run scripts/record.py --sentences 8-9      # năng động
uv run scripts/record.py --sentences 10-11    # cảm xúc
uv run scripts/record.py --sentences 12       # nhẹ nhàng
```
