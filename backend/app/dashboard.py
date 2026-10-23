"""Job-readiness dashboard — calculated ONLY from real performance data.
No data = 0 with an explicit note. This estimate never guarantees a job."""
import json

SKILLS = ["Python", "SQL", "Machine Learning", "Deep Learning", "Generative AI", "MLOps", "Interview Preparation"]

def compute(db):
    attempts = db.list_attempts()
    quiz_avg = round(sum(a["score"] for a in attempts) / len(attempts), 1) if attempts else 0.0
    coding = db.con.execute("SELECT COUNT(*) c, COALESCE(SUM(passed),0) p FROM coding_results").fetchone()
    coding_pct = round(100.0 * coding["p"] / coding["c"], 1) if coding["c"] else 0.0
    iv = db.con.execute("SELECT AVG(score) a FROM interviews").fetchone()
    iv_pct = round((iv["a"] or 0) * 10, 1)
    lectures = db.list_lectures()
    readiness = {
        "Python": coding_pct,
        "SQL": 0.0,
        "Machine Learning": quiz_avg,
        "Deep Learning": 0.0,
        "Generative AI": quiz_avg,
        "MLOps": 0.0,
        "Interview Preparation": iv_pct,
    }
    overall = round(sum(readiness.values()) / len(readiness), 1)
    return {"readiness_percent": readiness, "overall_job_readiness": overall,
            "completed_lectures": sum(1 for l in lectures if l["status"] == "processed"),
            "pending_lectures": sum(1 for l in lectures if l["status"] != "processed"),
            "quiz_attempts": len(attempts), "quiz_average": quiz_avg,
            "note": "Calculated from actual quiz/coding/interview records only. Not a guarantee of employment."}
