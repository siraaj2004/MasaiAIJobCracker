"""Mistake detection, mastery rules and spaced repetition.

<60% beginner revision, 60-79% targeted revision, 80-89% interview level,
>=90% provisionally mastered + spaced revision at 1/3/7/14/30 days.
"""
import datetime

SIMPLE = {
    "overfitting": "Overfitting ante student textbook answers anni memorize chesadu, kaani new question adigithe answer cheyyalekapothunnadu. Machine learning model kuda training data ni memorize chesi new data meeda fail avvachu.",
}

def evaluate_attempt(quiz, answers):
    """answers: {question_id: chosen_index}. Returns score + per-question detail."""
    total = len(quiz["questions"]); correct = 0; detail = []
    weak = {}
    for q in quiz["questions"]:
        chosen = answers.get(str(q["id"]), answers.get(q["id"]))
        ok = chosen == q["correct_index"]
        if ok: correct += 1
        else: weak[q["concept"]] = weak.get(q["concept"], 0) + 1
        detail.append({"id": q["id"], "correct": ok, "chosen": chosen,
                       "correct_index": q["correct_index"], "explanation": q["explanation"],
                       "concept": q["concept"],
                       "simple_explanation": SIMPLE.get(q["concept"].lower(),
                           "Ee concept ni simple ga: %s — summary line malli chadivi, own words lo cheppandi." % q["explanation"])})
    score = round(100.0 * correct / total, 1) if total else 0.0
    if score < 60: band, action = "beginner", "Beginner Telugu explanation + new beginner practice quiz"
    elif score < 80: band, action = "targeted", "Targeted revision + intermediate questions"
    elif score < 90: band, action = "interview", "Interview-level questions + review mistakes"
    else: band, action = "provisionally_mastered", "Provisionally mastered — spaced revision scheduled"
    return {"score": score, "correct": correct, "total": total, "band": band,
            "next_action": action, "weak_concepts": weak, "detail": detail}

def schedule_spaced_repetition(db, weak_concepts, band, today=None):
    today = today or datetime.date.today()
    offsets = [1, 3, 7, 14, 30] if band in ("provisionally_mastered", "interview") else [1, 3, 7]
    scheduled = []
    for concept in weak_concepts or ["general revision"]:
        for off in offsets:
            due = (today + datetime.timedelta(days=off)).isoformat()
            db.schedule_revision(concept, due, "spaced repetition +%dd (%s)" % (off, band))
            scheduled.append({"concept": concept, "due": due})
    return scheduled

def fresh_practice_questions(quiz, weak_concepts, count=3):
    """New questions on the same concepts — never the exact same questions."""
    out = []
    for q in quiz["questions"]:
        if q["concept"] in weak_concepts and len(out) < count:
            out.append({"question": "Own words lo explain cheyyandi: %s ante enti? Oka example ivvandi." % q["concept"],
                        "concept": q["concept"], "type": "explain"})
    return out
