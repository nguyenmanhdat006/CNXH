"""Sinh web/data.js từ data/*.json. Chạy lại mỗi khi sửa câu hỏi hoặc đáp án."""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "data"

# Câu đã sửa nhưng giáo trình 2019 không nói tới
UNSURE = {"301", "425", "427", "497"}
# Căn cứ trong giáo trình 2019 (số trang in)
PAGES = {"42": "15", "43": "12", "44": "14", "45": "8-9", "278": "69", "356": "92", "391": "109", "465": "108"}
# Gợi ý cho câu hỏi bị thiếu chữ (phỏng đoán)
MM = "C.Mác và Ph.Ăngghen"
HINTS = {
    **{i: f"…của {MM}?" for i in "4 12 17 63 64 65".split()},
    "26": f"Vai trò của {MM} đối với chủ nghĩa xã hội là gì?",
    "31": f"Vai trò của {MM} đối với tổ chức nào?",
    "59": f"…bước chuyển biến tư tưởng của {MM} là gì?",
    "68": f"…bước chuyển biến tư tưởng của {MM} là gì?",
    "60": "…sự chuyển biến tư tưởng của C.Mác từ duy tâm sang duy vật?",
    "62": f"Từ 1843 đến 1848, {MM} đã chuyển biến lập trường thế nào?",
    "70": f"…KHÔNG được {MM} viết trong giai đoạn 1848 đến Công xã Pari?",
    "71": f"…KHÔNG được {MM} viết trong giai đoạn sau Công xã Pari?",
    "174": "…dự báo của C.Mác về giai đoạn thấp của xã hội cộng sản?",
    "175": "…dự báo của C.Mác về giai đoạn cao của xã hội cộng sản?",
    "173": "", "188": "", "192": "",
}
NOTES = {"553": "Đáp án theo Luật 2007. Luật mới (2022) có hiệu lực từ 1/7/2023.",
         "519": "Đề gốc có hai lựa chọn trùng nhau (A và D)."}

questions = json.loads((DATA / "questions.json").read_text(encoding="utf-8"))
chapters = json.loads((DATA / "chapters.json").read_text(encoding="utf-8"))

out = []
for q in questions:
    i = q["id"]
    item = {"id": i, "c": q["chapter"], "q": q["question"], "o": q["options"], "a": q["answer"]}
    assert item["a"] in item["o"], f"Câu {i}: đáp án không hợp lệ (đã chạy ap_dung_sua.py chưa?)"
    if "original_answer" in q:
        item["orig"] = q["original_answer"]
    if i in UNSURE:
        item["unsure"] = True
    if i in PAGES:
        item["page"] = PAGES[i]
    if i in HINTS:
        item["cut"] = HINTS[i]
    if i in NOTES:
        item["note"] = NOTES[i]
    out.append(item)

payload = json.dumps({"chapters": chapters, "questions": out}, ensure_ascii=False, separators=(",", ":"))
(ROOT / "web").mkdir(exist_ok=True)
(ROOT / "web" / "data.js").write_text(f"window.CNXH={payload};\n", encoding="utf-8")
print("web/data.js:", len(out), "câu,", len(chapters), "chương")
