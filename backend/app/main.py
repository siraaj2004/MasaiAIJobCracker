"""FastAPI app. Run: uvicorn backend.app.main:app --reload --port 8000"""
import os, threading
from fastapi import FastAPI, Header, HTTPException
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
from .db import DB
from . import scraper, pipeline, quiz_gen, mistake, revision, coding, interview, dashboard, revision_video

app = FastAPI(title="MASAI AI Engineer Job Cracker — Telugu AI Mentor")
db = DB()
API_KEY = os.environ.get("APP_API_KEY")

def auth(x_api_key: str = Header(default=None)):
    if API_KEY and x_api_key != API_KEY:
        raise HTTPException(401, "Invalid or missing X-API-Key")

class ManualUpload(BaseModel):
    title: str; module: str = ""; lecture_date: str = ""; summary: str
class AnswersIn(BaseModel):
    answers: dict
class CodeIn(BaseModel):
    code: str
class InterviewAnswer(BaseModel):
    session_id: str; text: str

@app.get("/health")
def health():
    return {"status": "ok", "lectures": len(db.list_lectures()),
            "gmail_configured": os.path.exists(os.environ.get("GMAIL_CREDENTIALS_FILE", "data/gmail_credentials.json")),
            "gemini_configured": bool(os.environ.get("GEMINI_API_KEY"))}

@app.post("/lectures/manual-upload")
def manual_upload(body: ManualUpload):
    lid, is_new = scraper.manual_upload(db, body.title, body.module, body.lecture_date, body.summary)
    return {"lecture_id": lid, "is_new": is_new}

@app.post("/lectures/check-masai")
def check_masai():
    return scraper.discover_and_extract(db)

@app.post("/lectures/{lecture_id}/process")
def process(lecture_id: int, make_video: bool = True, send_mail: bool = False):
    return pipeline.process_lecture(db, lecture_id, make_video, send_mail)

@app.get("/lectures")
def lectures(): return db.list_lectures()

@app.get("/quiz/{quiz_id}")
def get_quiz(quiz_id: int):
    q = db.get_quiz(quiz_id)
    if not q: raise HTTPException(404, "quiz not found")
    return quiz_gen.public_view({"title": "Quiz %d" % quiz_id, "questions": q["questions"], "limitation": q["limitation"]})

@app.post("/quiz/{quiz_id}/submit")
def submit_quiz(quiz_id: int, body: AnswersIn):
    q = db.get_quiz(quiz_id)
    if not q: raise HTTPException(404, "quiz not found")
    result = mistake.evaluate_attempt({"questions": q["questions"]}, body.answers)
    db.save_attempt(quiz_id, body.answers, result["score"], result)
    scheduled = mistake.schedule_spaced_repetition(db, list(result["weak_concepts"].keys()), result["band"])
    fresh = mistake.fresh_practice_questions({"questions": q["questions"]}, list(result["weak_concepts"].keys()))
    mv = {"status": "not_needed"}
    wrong = [d for d in result["detail"] if not d["correct"]]
    if wrong:
        by_id = {str(x["id"]): x for x in q["questions"]}
        for d in wrong:
            src = by_id.get(str(d["id"]), {})
            d["question_text"] = src.get("question", d["concept"])
        lec = db.get_lecture(q["lecture_id"])
        out_dir = os.path.join("storage", "lecture_%d" % q["lecture_id"])
        def _render():
            try:
                revision_video.render_mistake_video(lec["title"], wrong, out_dir)
            except Exception:
                pass  # status endpoint reports only a file that actually exists
        threading.Thread(target=_render, daemon=True).start()
        mv = {"status": "rendering", "wrong_count": len(wrong)}
    return {**result, "spaced_revision_scheduled": scheduled, "fresh_practice": fresh,
            "revision_video_needed": result["score"] < 90, "mistake_video": mv}

@app.get("/quiz/{quiz_id}/mistake-video")
def mistake_video_status(quiz_id: int):
    q = db.get_quiz(quiz_id)
    if not q: raise HTTPException(404, "quiz not found")
    p = os.path.join("storage", "lecture_%d" % q["lecture_id"], "mistake_revision.mp4")
    if os.path.exists(p):
        return {"status": "ready", "video_path": p}
    return {"status": "not_ready"}

@app.get("/revision/today")
def revision_today(): return revision.todays_plan(db)

@app.get("/coding/challenges")
def challenges(): return coding.CHALLENGES

@app.post("/coding/run")
def run_code(body: CodeIn): return coding.run_code(body.code)

@app.post("/coding/submit/{challenge_id}")
def submit_code(challenge_id: str, body: CodeIn): return coding.submit_challenge(db, challenge_id, body.code)

@app.get("/interview/topics")
def iv_topics(): return interview.topics()

@app.post("/interview/start/{topic}")
def iv_start(topic: str): return interview.start(topic)

@app.post("/interview/answer")
def iv_answer(body: InterviewAnswer): return interview.answer(db, body.session_id, body.text)

@app.get("/dashboard")
def dash(): return dashboard.compute(db)

@app.get("/", response_class=HTMLResponse)
def home():
    p = os.path.join(os.path.dirname(__file__), "..", "..", "frontend", "index.html")
    return open(p, encoding="utf-8").read() if os.path.exists(p) else "<h1>Masai Job Cracker API</h1>"
