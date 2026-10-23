"""End-to-end sample: manual-upload the tokenization summary, process it,
generate example_lesson.json / example_quiz.json, and submit a perfect quiz."""
import os, sys, json
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "backend"))
os.chdir(os.path.join(os.path.dirname(__file__), ".."))
from app.db import DB
from app import pipeline, mistake, quiz_gen

db = DB("data/app.db")
summary = open("data/sample_summary_tokenization.txt", encoding="utf-8").read()
lid, is_new = db.add_lecture("Tokenization", "Generative AI", "", summary, source="manual")
print("lecture", lid, "new" if is_new else "duplicate-skipped")
res = pipeline.process_lecture(db, lid, make_video=True, send_mail=False)
print(json.dumps(res, indent=1, ensure_ascii=False))
q = db.get_quiz(res["steps"]["quiz"]["quiz_id"])
os.makedirs("examples", exist_ok=True)
lec = db.get_lecture(lid)
from app import lesson as L
json.dump(L.generate_lesson_script(lec["title"], lec["summary"]), open("examples/example_lesson.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)
json.dump(quiz_gen.public_view({"title": lec["title"], "questions": q["questions"], "limitation": q["limitation"]}), open("examples/example_quiz.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)
ans = {str(x["id"]): x["correct_index"] for x in q["questions"]}
r = mistake.evaluate_attempt({"questions": q["questions"]}, ans)
print("sample perfect-attempt score:", r["score"], r["band"])
