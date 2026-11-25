"""Đọc file Word ngân hàng câu hỏi -> data/questions.json, kèm kiểm tra cấu trúc."""
import json
import re
import sys
from pathlib import Path

import docx

ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / "data" / "CNXHKH_ngan_hang_555_cau.docx"
GREEN = "1F7A3A"

doc = docx.Document(str(SRC))
questions, cur, unknown = [], None, []

for p in doc.paragraphs[2:]:
    # Bỏ tiêu đề chương dính vào cuối đáp án và tiền tố "Cáu 35:" lọt vào câu hỏi
    text = re.sub(r"\s*CHƯƠNG \d.*$", "", p.text.strip()).replace("Cáu 35: ", "")
    if not text:
        continue
    if m := re.match(r"^Câu\s+(\d+\s*b?)\s*[.:]\s*(.*)$", text, re.S):
        cur = {"id": m[1].replace(" ", ""), "question": m[2].strip(),
               "options": {}, "answer": None, "marked": []}
        questions.append(cur)
    elif cur and (m := re.match(r"^Đáp án\s*:\s*(.*)$", text)):
        cur["answer"] = m[1].strip()
    elif cur and (m := re.match(r"^([A-H])\s*[.)]\s*(.*)$", text, re.S)):
        cur["options"][m[1]] = m[2].strip()
        if any(r.font.color and r.font.color.type and str(r.font.color.rgb) == GREEN for r in p.runs):
            cur["marked"].append(m[1])
    else:
        unknown.append((cur["id"] if cur else None, text))

out = ROOT / "data" / "questions.json"
out.write_text(json.dumps(questions, ensure_ascii=False, indent=1), encoding="utf-8")

print("Số câu:", len(questions))
print("Dòng không nhận dạng:", unknown)
for q in questions:
    problems = []
    if len(q["options"]) != 4:
        problems.append(f"{len(q['options'])} lựa chọn")
    if q["answer"] not in q["options"]:
        problems.append(f"đáp án {q['answer']!r}")
    if q["marked"] != [q["answer"]]:
        problems.append(f"tô màu {q['marked']} != đáp án {q['answer']}")
    if problems:
        print(q["id"], "; ".join(problems))
