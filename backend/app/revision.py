"""Smart revision engine: prioritise by low scores, repeated mistakes,
time since revision and interview importance."""
import datetime

def todays_plan(db, today=None):
    today = today or datetime.date.today()
    due = db.due_revisions(today.isoformat())
    attempts = db.list_attempts()
    weak_counts = {}
    import json
    for a in attempts:
        try: detail = json.loads(a["detail_json"])
        except Exception: continue
        for d in detail.get("weak_concepts", {}):
            weak_counts[d] = weak_counts.get(d, 0) + detail["weak_concepts"][d]
    plan = []
    for r in due:
        plan.append({"topic": r["concept"], "reason": r["reason"],
                     "tasks": ["Watch a 5-minute Telugu explanation",
                               "Solve three questions",
                               "Complete one Python exercise",
                               "Answer one interview question"]})
    repeated = [c for c, n in weak_counts.items() if n >= 2 and c not in [p["topic"] for p in plan]]
    for c in repeated:
        plan.append({"topic": c, "reason": "Repeated mistake (%d times)" % weak_counts[c],
                     "tasks": ["Re-watch the Telugu explanation", "Solve three fresh questions"]})
    return {"date": today.isoformat(), "plan": plan,
            "note": "Topic is marked mastered only after demonstrating understanding in a fresh quiz."}
