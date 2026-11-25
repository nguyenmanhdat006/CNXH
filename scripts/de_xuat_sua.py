"""Xuất de_xuat_sua_dap_an.xlsx để duyệt. Không sửa data/questions.json."""
import json
from pathlib import Path

import openpyxl
from openpyxl.styles import Alignment, Font, PatternFill
from openpyxl.worksheet.datavalidation import DataValidation

ROOT = Path(__file__).resolve().parent.parent
qs = {q["id"]: q for q in json.loads((ROOT / "data" / "questions.json").read_text(encoding="utf-8"))}

# Số trang là số in trong "Giáo trình Chủ nghĩa xã hội khoa học - 2019" (data/giao_trinh_2019.pdf)
SURE, LIKELY, CHECK = "1. Giáo trình xác nhận", "2. Suy ra, giáo trình không nói trực tiếp", "3. Giáo trình không đề cập"

# (câu, mức độ, đáp án đề xuất, căn cứ, lý do)
FIXES = [
    ("42", SURE, "A", "tr.15", "Lênin hoàn chỉnh lý luận về cách mạng xã hội chủ nghĩa, cách mạng dân chủ tư sản kiểu mới."),
    ("43", SURE, "B", "tr.12", "Mục 2.1: C.Mác và Ph.Ăngghen phát triển CNXHKH. Có vẻ bị đảo đáp án với câu 44."),
    ("44", SURE, "C", "tr.14", "V.I.Lênin kế tục, bảo vệ, vận dụng và phát triển."),
    ("45", SURE, "B", "tr.8-9", "Ba tiền đề KHTN: tiến hóa, bảo toàn và chuyển hóa năng lượng, tế bào."),
    ("278", SURE, "B", "tr.69", "Giáo trình dùng thuật ngữ khớp với đáp án B."),
    ("356", SURE, "B", "tr.92", "Câu trích nói về chuyên chính vô sản."),
    ("391", SURE, "B", "tr.109", "Trước hết phải thủ tiêu áp bức giai cấp, trên cơ sở đó xóa bỏ áp bức dân tộc."),
    ("465", SURE, "A", "tr.108", "Độc lập dân tộc là mục tiêu chính trị chủ yếu của mọi quốc gia trong thời đại ngày nay."),
    ("46", LIKELY, "D", "tr.17 (chỉ nhắc Quốc tế III)", "Giáo trình không nói ai sáng lập. Theo lịch sử, Lênin sáng lập Quốc tế III."),
    ("413", LIKELY, "D", "tr.115, 118", "Giáo trình nói tôn giáo đã có từ công xã nguyên thủy nên B sai. D là lựa chọn hợp lý còn lại."),
    ("492", LIKELY, "C", "tr.110 (số cũ 14,3%)", "File ghi hai đáp án. Câu hỏi theo số 2019 (14,7%); giáo trình dùng số cũ."),
    ("493", LIKELY, "D", "tr.110 (số cũ 85,7%)", "File ghi hai đáp án. Câu hỏi theo số 2019 (85,3%); giáo trình dùng số cũ."),
    ("301", CHECK, "A", "Không thấy câu trích", "Theo trí nhớ của tôi: Đại hội VI. Nên hỏi giảng viên."),
    ("425", CHECK, "C", "Không có mục này", "Giáo trình 2019 không có phần 'nguyên nhân tồn tại tôn giáo'. Đề xuất theo giáo trình cũ mà tôi nhớ."),
    ("427", CHECK, "A", "Không có mục này", "Đi cùng câu 425."),
    ("497", CHECK, "A", "Không thấy cụm 'sợi chỉ đỏ'", "Đề xuất theo hiểu biết của tôi, độ tin cậy thấp."),
]

# Vấn đề khác: không đổi đáp án
OTHERS = {
    "553": ("Đáp án đúng với Luật 2007. Luật hiện hành là Luật 2022, hiệu lực 1/7/2023, không có trong các lựa chọn.", ""),
    "519": ("Lựa chọn A và D giống hệt nhau (gia đình).", ""),
}
MM = "C.Mác và Ph.Ăngghen"
HINTS = {
    **{i: f"...của {MM}? (tr.11)" for i in "4 12 17 63 64 65".split()},
    "26": f"Vai trò của {MM} đối với chủ nghĩa xã hội là gì? (tr.14)",
    "31": f"Vai trò của {MM} đối với tổ chức nào? (suy từ đáp án)",
    "59": f"...bước chuyển biến tư tưởng của {MM} là... (tr.10)",
    "68": f"...bước chuyển biến tư tưởng của {MM} là... (tr.10)",
    "60": "...sự chuyển biến tư tưởng của C.Mác từ duy tâm sang duy vật...? (tr.10)",
    "62": f"Từ 1843 đến 1848, {MM} đã chuyển biến lập trường như thế nào? (tr.11)",
    "70": f"...KHÔNG được {MM} viết trong giai đoạn 1848 đến Công xã Pari (1871)? (suy từ đáp án, tr.12-13)",
    "71": f"...KHÔNG được {MM} viết trong giai đoạn sau Công xã Pari? (suy từ đáp án, tr.12-13)",
    "174": "...dự báo của C.Mác về giai đoạn thấp của xã hội cộng sản? (suy từ đáp án)",
    "175": "...dự báo của C.Mác về giai đoạn cao của xã hội cộng sản? (suy từ đáp án)",
    "173": "", "188": "", "192": "",
}
for i, hint in HINTS.items():
    OTHERS[i] = ("Câu hỏi thiếu chữ, file Word gốc đã thiếu sẵn.", hint)
for i in ("59", "68"):
    OTHERS[i] = (OTHERS[i][0] + " Lựa chọn C cũng bị cụt.", OTHERS[i][1])

wb = openpyxl.Workbook()
fix = wb.active
fix.title = "Đề xuất sửa"
fix.append(["Câu", "Chương", "Mức độ", "Câu hỏi", "A", "B", "C", "D",
            "Đáp án trong file", "Đề xuất", "Căn cứ giáo trình", "Lý do", "Bạn duyệt"])
for i, level, new, page, why in FIXES:
    q = qs[i]
    old = q.get("original_answer", q["answer"])
    assert new in q["options"] and new != old, i
    fix.append([i, q["chapter"], level, q["question"], *[q["options"][k] for k in "ABCD"],
                old, new, page, why, ""])
dv = DataValidation(type="list", formula1='"Đồng ý,Giữ nguyên"', allow_blank=True)
fix.add_data_validation(dv)
dv.add(f"M2:M{fix.max_row}")

other = wb.create_sheet("Lỗi nội dung khác")
other.append(["Câu", "Chương", "Câu hỏi", "Vấn đề", "Gợi ý bổ sung (phỏng đoán)", "Bạn bổ sung/sửa"])
for i in sorted(OTHERS, key=int):
    other.append([i, qs[i]["chapter"], qs[i]["question"], *OTHERS[i], ""])

for ws, widths in ((fix, [6, 8, 18, 45, 22, 22, 22, 22, 10, 9, 55, 13]), (other, [6, 8, 60, 60, 45])):
    for n, width in enumerate(widths):
        ws.column_dimensions[chr(65 + n)].width = width
    for row in ws.iter_rows():
        for cell in row:
            cell.alignment = Alignment(wrap_text=True, vertical="top")
    for cell in ws[1]:
        cell.font = Font(bold=True)
        cell.fill = PatternFill("solid", fgColor="D9E1F2")
    ws.freeze_panes = "B2"
    ws.auto_filter.ref = ws.dimensions

wb.save(ROOT / "de_xuat_sua_dap_an.xlsx")
print(len(FIXES), "đề xuất sửa;", len(OTHERS), "lỗi khác")
