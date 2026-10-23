"""Mistake-correction video: after a quiz attempt, build a short Telugu
revision video that re-teaches ONLY the concepts the student got wrong —
question, the correct answer, and the simple explanation, all taken from
the attempt's own evaluation detail (which is grounded in the summary).
Rendered with the same pipeline as lesson videos (natural Telugu voice
via video.synthesize_tts). Returns a path only if the MP4 exists."""
import os
from . import video

def build_mistake_script(lecture_title, detail):
    wrong = [d for d in detail if not d.get("correct")]
    parts = [{"part": 1, "name": "Mistake revision intro",
              "text": "Ee video mee quiz mistakes kosam matrame. Meeru tappu chesina concepts ni simple ga, slow ga malli cheptha. Last ki anni correct ga gurthu pettukondi."}]
    for i, d in enumerate(wrong, 1):
        parts.append({"part": i + 1, "name": "Mistake %d — %s" % (i, d.get("concept", "")),
                      "text": "Question: %s. Correct answer option number %s. %s Simple ga cheppalante: %s" % (
                          d.get("question_text", d.get("concept", "")),
                          (d.get("correct_index", 0) + 1),
                          d.get("explanation", ""),
                          d.get("simple_explanation", ""))})
    parts.append({"part": len(parts) + 1, "name": "Revision close",
                  "text": "Ippudu ee concepts ni mee own words lo okasari cheppukondi. Tarvata fresh practice quiz attempt cheyyandi. Meeru cheyyagalugutharu."})
    return {"title": "Mistake Revision — %s" % lecture_title, "parts": parts, "wrong_count": len(wrong)}

def render_mistake_video(lecture_title, detail, out_dir):
    script = build_mistake_script(lecture_title, detail)
    if script["wrong_count"] == 0:
        return {"ok": True, "wrong_count": 0, "video_path": None, "note": "No mistakes — no revision video needed."}
    res = video.render_video(script, out_dir, slug="mistake_revision")
    return {"ok": True, "wrong_count": script["wrong_count"], "video_path": res["video_path"],
            "duration_seconds": res["duration_seconds"]}
