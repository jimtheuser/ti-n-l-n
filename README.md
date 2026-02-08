# Tiến Lên Miền Nam (phiên bản đơn giản)

Đây là một bản mô phỏng CLI tối giản của trò chơi Tiến Lên Miền Nam. Mục tiêu là cung cấp
một bộ khung luật chơi và vòng lặp đánh bài cơ bản để bạn có thể mở rộng thêm.

## Tính năng

- Chia bài 4 người, mỗi người 13 lá.
- Hỗ trợ các bộ: bài lẻ, đôi, sám, sảnh, tứ quý, đôi thông.
- So sánh bộ bài cùng loại và xử lý "bom" để chặt 2 (phiên bản rút gọn).
- Chế độ chơi với bot hoặc thêm người chơi thật.

## Luật rút gọn

Một vài quy tắc đã được đơn giản hóa để dễ hiểu:

- So sánh bộ bài chủ yếu dựa trên hạng (rank).
- "Bom" (tứ quý hoặc đôi thông) chỉ được dùng để chặt các bộ có hạng 2.
- Không xử lý các luật chặt nâng cao khác (ví dụ đôi thông dài hơn).

Bạn có thể chỉnh sửa hàm `can_beat` và `detect_combo` trong `tien_len_mien_nam.py` để
phù hợp với luật chi tiết hơn.

## Chạy chương trình

```bash
python3 tien_len_mien_nam.py
```

Để chơi với người thật:

```bash
python3 tien_len_mien_nam.py --human
```

## Gợi ý mở rộng

- Thêm luật chặt đầy đủ (đôi 2, tứ quý chặt đôi thông, v.v.).
- Thêm AI cho bot thay vì chọn nước đi đầu tiên.
- Tạo giao diện web hoặc GUI.
