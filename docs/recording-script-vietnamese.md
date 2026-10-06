# Kịch bản ghi âm giọng mẫu tiếng Việt

Tài liệu này là phần dùng trực tiếp khi ngồi thu âm. Cách chuẩn bị phòng, mic và thiết lập nằm ở [voice-prep-guide-vietnamese.md](voice-prep-guide-vietnamese.md).

## Cách dùng

- Mỗi câu dưới đây dài khoảng 20–26 âm tiết, đọc tự nhiên mất khoảng 5–7 giây. Độ dài này nằm trong khoảng 3–10 giây mà OmniVoice khuyên dùng.
- Câu nào cũng có đủ sáu thanh (ngang, huyền, sắc, hỏi, ngã, nặng), đã kiểm tra bằng script. Nhờ vậy mỗi clip đều cho model nghe cách bạn phát âm đủ các thanh.
- Mỗi câu đọc 2–3 lần, giữa các lần nghỉ một nhịp. Sau đó chọn lần đọc sạch nhất, không vấp, không có tiếng động lạ.
- Đọc đúng từng chữ như văn bản. Transcript của profile phải khớp chính xác với những gì bạn đã nói. Nếu lỡ đọc khác đi, hãy sửa transcript theo lời đã đọc, đừng giữ văn bản gốc.
- Đặt tên file theo mẫu `recordings/<phong-cach>-<so-cau>-take<lan>.wav`, ví dụ `recordings/tro-chuyen-01-take2.wav`. Thư mục `recordings/` đã được loại khỏi Git.
- Giữ nguyên giọng vùng miền của bạn (Bắc, Trung hay Nam) trong mọi clip. Model sẽ bắt chước giọng có trong clip mẫu.

## Nhóm A. Trò chuyện tự nhiên

Đọc như đang nói chuyện với bạn bè, tốc độ vừa phải.

1. Sáng nay mình dậy sớm, pha một ấm trà nóng rồi ngồi ngoài hiên nghe những hạt mưa nhỏ rơi trên mái tôn.
2. Cuối tuần này bạn có rảnh không? Mình định rủ cả nhóm đi ăn lẩu ở quán cũ gần trường.
3. Hồi nhỏ tôi hay theo bà ra chợ, đến giờ vẫn nhớ giọng bà kể chuyện ngày xưa ở quê.

## Nhóm B. Kể chuyện, đọc sách

Đọc chậm hơn một chút, có nhấn nhá, ngắt hơi ở dấu phẩy.

4. Ngôi làng nhỏ nằm lặng lẽ bên bờ sông, mỗi buổi chiều khói bếp lại bay lên giữa những rặng tre xanh.
5. Ông lão chậm rãi mở chiếc hộp gỗ cũ, bên trong là một bức thư đã ngả màu theo năm tháng.

## Nhóm C. Đọc tin, thuyết trình

Đọc rõ ràng, đều giọng, ít cảm xúc.

6. Theo dự báo, từ ngày mai miền Bắc sẽ đón một đợt không khí lạnh, nhiệt độ có nơi giảm xuống dưới mười lăm độ.
7. Thành phố đã đưa vào sử dụng tuyến xe buýt điện đầu tiên, giúp người dân đi lại thuận tiện hơn và giảm bớt khói bụi.

## Nhóm D. Năng động, quảng cáo

Đọc nhanh hơn, tươi, cười nhẹ khi đọc.

8. Chỉ còn ba ngày nữa thôi! Nhanh tay đặt chỗ để nhận ngay ưu đãi giảm nửa giá cho khóa học mùa hè.
9. Bạn đã sẵn sàng chưa? Cùng mình ăn thử những món ngon đường phố nổi tiếng nhất Sài Gòn trong tập hôm nay nhé!

## Nhóm E. Cảm xúc

Thể hiện cảm xúc thật nhưng đừng la to hay làm quá, vì model chép lại cả cường độ.

10. Trời ơi, thật không thể tin được! Sau bao nhiêu năm, cuối cùng chúng ta cũng gặp lại nhau rồi.
11. Sao hôm qua em không gọi cho anh? Anh đã đợi suốt cả buổi tối mà chẳng thấy tin nhắn nào.

## Nhóm F. Nhẹ nhàng, thư giãn

Giọng thấp, chậm, mềm. Không thì thầm, vì clip thì thầm sẽ làm giọng tạo ra bị hụt hơi.

12. Nếu bạn đang thấy mệt mỏi, hãy thử hít một hơi thật sâu, thả lỏng đôi vai và nghỉ ngơi vài phút.

## Câu kiểm tra sau khi tạo profile

Những câu này không dùng để ghi âm. Hãy dán chúng vào VoiceStudio để xem model đọc tiếng Việt của bạn đến đâu. Mỗi cặp có một bản để nguyên chữ số hoặc viết tắt và một bản đã viết ra thành chữ. Bản nào nghe đúng hơn thì sau này viết văn bản theo kiểu đó.

| Thử gì | Bản để nguyên | Bản viết thành chữ |
|---|---|---|
| Thanh điệu | Ma, mà, má, mả, mã, mạ. Bà ba bán bánh bò. | (giữ nguyên) |
| Năm | Năm 2024 công ty chuyển về Đà Nẵng. | Năm hai nghìn không trăm hai mươi tư công ty chuyển về Đà Nẵng. |
| Số tiền và phần trăm | Doanh thu tăng 15% lên 3,5 tỷ đồng. | Doanh thu tăng mười lăm phần trăm lên ba phẩy năm tỷ đồng. |
| Giờ và số điện thoại | Gọi 0912 345 678 trước 9h30 sáng thứ Hai. | Gọi không chín một hai, ba bốn năm, sáu bảy tám trước chín giờ ba mươi sáng thứ Hai. |
| Viết tắt | Tôi học ở ĐH Bách khoa TP.HCM. | Tôi học ở Đại học Bách khoa Thành phố Hồ Chí Minh. |
| Từ tiếng Anh | Mình vừa cập nhật iPhone rồi mở app Facebook. | Mình vừa cập nhật ai-phôn rồi mở áp phây-búc. |
| Câu dài (dễ bị nuốt chữ) | Ghép 4–5 câu bất kỳ ở trên thành một đoạn hơn 30 giây. | Tách lại thành từng câu và tạo riêng từng câu. |

## Ghi thêm để fine-tune sau này (tùy chọn)

Nếu muốn có thêm dữ liệu cho fine-tune hoặc LoRA, hãy dành thêm một buổi đọc 15–30 phút trong cùng phòng, cùng mic và cùng khoảng cách. Có thể đọc truyện cổ tích, bài báo hoặc bài viết của chính bạn. Sau đó cắt thành các câu 3–15 giây, mỗi câu kèm transcript chính xác. Bộ dữ liệu này cũng là kho để chọn clip mẫu tốt nhất cho zero-shot.
