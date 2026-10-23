"""Masai-format quiz as a single HTML file, per lecture.

Section A — Objective (Masai evaluation style): the lecture's grounded MCQs,
options A–D, answer key hidden at the end (open after attempting).
Section B — Descriptive (Masai evaluation style): written-answer questions
built ONLY from the lesson's own parts — each asks the student to explain a
concept from THIS lecture's summary, with the model-answer key points taken
from that same part's text (nothing invented from outside the summary).
"""
import html

STYLE = """<style>
body{font-family:system-ui,Arial,sans-serif;max-width:820px;margin:24px auto;padding:0 16px;color:#1b1b1b;line-height:1.55}
h1{font-size:22px} h2{margin-top:32px;border-bottom:2px solid #12355B;padding-bottom:4px}
.q{margin:14px 0} .opts{margin:6px 0 0 18px} .meta{color:#555;font-size:13px}
details{background:#f2f6fb;border:1px solid #d5e0ee;border-radius:8px;padding:10px 14px;margin:10px 0}
.tag{display:inline-block;background:#12355B;color:#fff;border-radius:10px;padding:1px 8px;font-size:12px}
</style>"""

def _esc(s): return html.escape(str(s or ""))

def descriptive_questions(script, limit=6):
    """One descriptive question per substantive lesson part."""
    skip = {"welcome", "checkpoint", "interview question", "summary", "practice"}
    out = []
    for p in script.get("parts", []):
        name = (p.get("name") or "").strip()
        text = (p.get("text") or "").strip()
        if not text or len(text) < 60: continue
        if any(s in name.lower() for s in skip): continue
        out.append({
            "question": "%s — ee concept ni mee own words lo, oka real-life example tho vivarinchandi." % name,
            "model_points": text,
            "marks": 5,
        })
        if len(out) >= limit: break
    return out

def render_quiz_html(lecture_title, quiz, script):
    qs = quiz.get("questions", [])
    desc = descriptive_questions(script)
    parts = []
    parts.append("<!DOCTYPE html><html lang='te'><head><meta charset='utf-8'>"
                 "<title>Quiz — %s</title>%s</head><body>" % (_esc(lecture_title), STYLE))
    parts.append("<h1>%s — Quiz</h1>" % _esc(lecture_title))
    parts.append("<p class='meta'>Masai format: Section A Objective + Section B Descriptive. "
                 "Mundhu answers rayandi/raayandi, tarvata answer key tho check cheskondi.</p>")
    if quiz.get("limitation"):
        parts.append("<p class='meta'>Note: %s</p>" % _esc(quiz["limitation"]))
    parts.append("<h2>Section A — Objective Questions (%d × 1 mark)</h2>" % len(qs))
    for i, q in enumerate(qs, 1):
        parts.append("<div class='q'><b>Q%d.</b> %s <span class='tag'>%s</span><div class='opts'>" %
                     (i, _esc(q["question"]), _esc(q.get("level", ""))))
        for j, opt in enumerate(q.get("options", [])):
            parts.append("<div>%s) %s</div>" % ("ABCD"[j], _esc(opt)))
        parts.append("</div></div>")
    parts.append("<h2>Section B — Descriptive Questions (%d × 5 marks)</h2>" % len(desc))
    for i, d in enumerate(desc, 1):
        parts.append("<div class='q'><b>Q%d.</b> %s</div>" % (i, _esc(d["question"])))
    parts.append("<h2>Answer Key — Objective</h2><details><summary>Attempt chesaka open cheyyandi</summary>")
    for i, q in enumerate(qs, 1):
        ci = q.get("correct_index")
        ans = q["options"][ci] if ci is not None and q.get("options") else "—"
        parts.append("<div>Q%d: <b>%s</b> — %s</div>" % (i, _esc(ans), _esc(q.get("explanation", ""))))
    parts.append("</details>")
    parts.append("<h2>Model Answer Points — Descriptive</h2><details><summary>Attempt chesaka open cheyyandi</summary>")
    for i, d in enumerate(desc, 1):
        parts.append("<div><b>Q%d.</b> %s</div>" % (i, _esc(d["model_points"])))
    parts.append("</details></body></html>")
    return "\n".join(parts)

def write_quiz_html(db, lecture_id, out_path):
    lec = db.get_lecture(lecture_id)
    row = db.con.execute("SELECT id FROM quizzes WHERE lecture_id=? ORDER BY id DESC", (lecture_id,)).fetchone()
    if not row: return None
    quiz = db.get_quiz(row[0])
    from .lesson import generate_lesson_script
    script = generate_lesson_script(lec["title"], lec["summary"])
    doc = render_quiz_html(lec["title"], quiz, script)
    with open(out_path, "w", encoding="utf-8") as f: f.write(doc)
    return {"path": out_path, "objective": len(quiz.get("questions", [])), "descriptive": len(descriptive_questions(script))}
