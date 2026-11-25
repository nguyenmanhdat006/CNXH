# Ôn thi Chủ nghĩa xã hội khoa học

558 câu trắc nghiệm chia theo 7 chương, có luyện tập, thi thử và tra cứu.

Mở `web/index.html` bằng trình duyệt là dùng được. Khi deploy (Vercel, ...), đặt thư mục gốc là `web`.

## Cập nhật dữ liệu

Cần Python và `python-docx`. Chạy theo thứ tự:

```sh
python -X utf8 scripts/parse.py        # đọc file Word -> data/questions.json
python -X utf8 scripts/chia_chuong.py  # gán chương (ghi đè duyet_chia_chuong.xlsx)
python -X utf8 scripts/ap_dung_sua.py  # áp data/sua_dap_an.json
python -X utf8 scripts/build_web.py    # sinh web/data.js
```

## Lưu ý về đáp án

16 đáp án đã được sửa so với đề gốc. Các câu 301, 425, 427, 497 chưa có căn cứ trong giáo trình.
