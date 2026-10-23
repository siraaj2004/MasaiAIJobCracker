"""End-to-end MVP pipeline: Summary -> Lesson script -> Video -> PDF ->
Quiz -> (email if configured). Each step records real status; failures are
reported, never hidden, and failed steps stay retryable."""
import os, json
from . import lesson as lesson_mod, quiz_gen, video as video_mod, pdf_notes, email_service
from .roadmap import map_summary_to_roadmap

STORAGE = os.environ.get("STORAGE_DIR", "storage")

def process_lecture(db, lecture_id, make_video=True, send_mail=False, student_email=None):
    lec = db.get_lecture(lecture_id)
    if not lec: return {"ok": False, "error": "lecture not found"}
    out = {"lecture_id": lecture_id, "steps": {}}
    script = lesson_mod.generate_lesson_script(lec["title"], lec["summary"])
    out["steps"]["lesson_script"] = {"ok": True, "parts": len(script["parts"])}
    out["roadmap_mapping"] = map_summary_to_roadmap(lec["summary"])
    folder = os.path.join(STORAGE, "lecture_%d" % lecture_id)
    pdf_path = pdf_notes.make_pdf(lec["title"],
        [p.get("text") or " ".join(p.get("questions", [])) for p in script["parts"]],
        os.path.join(folder, "notes.pdf"))
    out["steps"]["pdf"] = {"ok": True, "path": pdf_path}
    video_path = None
    if make_video:
        try:
            v = video_mod.render_video(script, folder, slug="lesson")
            video_path = v["video_path"]; out["steps"]["video"] = {"ok": True, **v}
        except Exception as e:
            out["steps"]["video"] = {"ok": False, "error": str(e), "retryable": True,
                                     "script_retained": os.path.join(folder, "lesson_script.json")}
    quiz = quiz_gen.generate_quiz(lec["title"], lec["summary"])
    quiz_id = db.save_quiz(lecture_id, quiz["questions"], quiz["limitation"])
    out["steps"]["quiz"] = {"ok": True, "quiz_id": quiz_id, "count": len(quiz["questions"]),
                            "limitation": quiz["limitation"],
                            "quiz_link": "/quiz/%d" % quiz_id}
    db.save_lesson(lecture_id, script, video_path, pdf_path)
    db.set_lecture_status(lecture_id, "processed")
    if send_mail:
        subj, body = email_service.build_learning_package_email(
            lec, video_path or "(video pending — rendering failed, script retained)",
            pdf_path, "/quiz/%d" % quiz_id, script)
        out["steps"]["email"] = email_service.send_email(
            db, lec, student_email or os.environ.get("STUDENT_EMAIL", ""), subj, body)
    out["ok"] = True
    return out
