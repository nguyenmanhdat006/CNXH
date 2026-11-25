"""Áp các đáp án đã duyệt (data/sua_dap_an.json) vào data/questions.json.

Thứ tự chạy: parse.py -> chia_chuong.py -> ap_dung_sua.py. Chạy lại nhiều lần không sao.
Đáp án trong file Word được giữ ở trường original_answer.
"""
import json
from pathlib import Path

DATA = Path(__file__).resolve().parent.parent / "data"

fixes = json.loads((DATA / "sua_dap_an.json").read_text(encoding="utf-8"))
questions = json.loads((DATA / "questions.json").read_text(encoding="utf-8"))
by_id = {q["id"]: q for q in questions}

for qid, new in fixes.items():
    q = by_id[qid]
    assert new in q["options"], qid
    q.setdefault("original_answer", q["answer"])
    q["answer"] = new

(DATA / "questions.json").write_text(json.dumps(questions, ensure_ascii=False, indent=1), encoding="utf-8")
print("Đã sửa", len(fixes), "câu")
for qid in fixes:
    print(f"  {qid}: {by_id[qid]['original_answer']} -> {by_id[qid]['answer']}")
