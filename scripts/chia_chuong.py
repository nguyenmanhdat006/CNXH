"""Gán chương cho data/questions.json và xuất file Excel để duyệt.

Chạy sau parse.py. Lưu ý: chạy lại sẽ ghi đè duyet_chia_chuong.xlsx.
"""
import json
import re
from pathlib import Path

import openpyxl
from openpyxl.styles import Alignment, Font, PatternFill
from openpyxl.worksheet.datavalidation import DataValidation

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "data" / "questions.json"

# (chương, tên, số câu đầu, số câu cuối)
CHAPTERS = [
    (1, "Nhập môn chủ nghĩa xã hội khoa học", 1, 74),
    (2, "Sứ mệnh lịch sử của giai cấp công nhân", 75, 171),
    (3, "Chủ nghĩa xã hội và thời kỳ quá độ lên CNXH", 172, 233),
    (4, "Dân chủ XHCN và Nhà nước XHCN", 234, 309),
    (5, "Cơ cấu xã hội - giai cấp và liên minh giai cấp, tầng lớp", 310, 379),
    (6, "Vấn đề dân tộc và tôn giáo", 380, 497),
    (7, "Vấn đề gia đình", 498, 555),
]

# Câu có nội dung giao thoa giữa hai chương
BORDERLINE = {
    "20": "Nói về vai trò lịch sử của giai cấp vô sản, có thể xếp chương 2",
    "75": "Trùng ý câu 30 (chương 1)",
    "111b": "Quan hệ công nhân - nông dân, có thể xếp chương 5",
    "169": "Trùng câu 200 (chương 3)",
    "200": "Trùng câu 169 (chương 2)",
    "215": "Về nhà nước XHCN, có thể xếp chương 4",
    "216": "Về nhà nước vô sản, có thể xếp chương 4",
    "335": "Vai trò giai cấp công nhân VN, có thể xếp chương 2",
    "336": "Vai trò giai cấp công nhân VN, có thể xếp chương 2",
    "363": "Khẩu hiệu về dân tộc bị áp bức, có thể xếp chương 6",
}
for i in ("154", "155", "156", "157", "166", "167", "168"):
    BORDERLINE[i] = "Cách mạng XHCN, có thể xếp chương 3"

# Đáp án trong file gốc có vẻ chưa đúng (KHÔNG tự sửa)
SUSPECT = {
    "43": "File ghi C. Nghi đúng là B (Mác và Ph. Ăngghen); có vẻ đảo với câu 44",
    "44": "File ghi B. Nghi đúng là C (V.I. Lênin); có vẻ đảo với câu 43",
    "45": "File ghi A, nhưng định luật bảo toàn là tiền đề KHTN. Nghi đúng là B",
    "46": "File ghi A. Lênin sáng lập Quốc tế III, nghi đúng là D",
    "413": "Đáp án B đáng ngờ, nên đối chiếu giáo trình",
    "425": "'Trình độ dân trí' thường thuộc nguyên nhân nhận thức, nên đối chiếu",
    "465": "File ghi B (liên kết khu vực). Nghi đúng là A (độc lập dân tộc)",
    "492": "File ghi 2 đáp án (A, C). Số liệu 2019 là 14,7% (C)",
    "493": "File ghi 2 đáp án (A, D). Số liệu 2019 là 85,3% (D)",
    "553": "Luật 2007 (hiệu lực 2008) đã được thay bằng luật 2022, hiệu lực 1/7/2023",
}

questions = json.loads(DATA.read_text(encoding="utf-8"))
for q in questions:
    num = int(re.match(r"\d+", q["id"])[0])
    q["chapter"] = next(c for c, _, a, b in CHAPTERS if a <= num <= b)
DATA.write_text(json.dumps(questions, ensure_ascii=False, indent=1), encoding="utf-8")
(ROOT / "data" / "chapters.json").write_text(
    json.dumps([{"chapter": c, "title": t} for c, t, _, _ in CHAPTERS], ensure_ascii=False, indent=1),
    encoding="utf-8")

wb = openpyxl.Workbook()
summary = wb.active
summary.title = "Tổng hợp"
summary.append(["Chương", "Tên chương", "Từ câu", "Đến câu", "Số câu"])
for c, title, a, b in CHAPTERS:
    row = summary.max_row + 1
    summary.append([c, title, a, b, f"=COUNTIF('Câu hỏi'!B:B,A{row})"])
summary.append(["", "Tổng", "", "", f"=SUM(E2:E{summary.max_row})"])

sheet = wb.create_sheet("Câu hỏi")
sheet.append(["Câu", "Chương", "Câu hỏi", "A", "B", "C", "D", "Đáp án",
              "Giao thoa chương", "Đáp án cần kiểm tra"])
for q in questions:
    sheet.append([q["id"], q["chapter"], q["question"],
                  *[q["options"].get(k, "") for k in "ABCD"], q["answer"],
                  BORDERLINE.get(q["id"], ""), SUSPECT.get(q["id"], "")])

dv = DataValidation(type="list", formula1='"1,2,3,4,5,6,7"', allow_blank=False)
sheet.add_data_validation(dv)
dv.add(f"B2:B{sheet.max_row}")

for ws, widths in ((summary, [9, 60, 9, 9, 9]), (sheet, [7, 9, 60, 28, 28, 28, 28, 8, 32, 40])):
    for i, width in enumerate(widths):
        ws.column_dimensions[chr(65 + i)].width = width
    for row in ws.iter_rows():
        for cell in row:
            cell.alignment = Alignment(wrap_text=True, vertical="top")
    for cell in ws[1]:
        cell.font = Font(bold=True)
        cell.fill = PatternFill("solid", fgColor="D9E1F2")
    ws.freeze_panes = "A2"

for row in sheet.iter_rows(min_row=2):
    for cell, color in ((row[8], "FFF2CC"), (row[9], "FCE4D6")):
        if cell.value:
            cell.fill = PatternFill("solid", fgColor=color)
sheet.auto_filter.ref = sheet.dimensions

wb.save(ROOT / "duyet_chia_chuong.xlsx")
for c, title, a, b in CHAPTERS:
    print(c, title, sum(q["chapter"] == c for q in questions))
print("Tổng", len(questions), "| giao thoa", len(BORDERLINE), "| nghi sai", len(SUSPECT))
