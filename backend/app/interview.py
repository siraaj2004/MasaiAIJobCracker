"""AI Engineer interview simulator: one question at a time, score /10,
what was missed, a strong sample answer, then a harder follow-up."""
BANK = {
    "python": [
        {"q": "Variable ante enti? Python lo x = 10 ante em jaruguthundi?", "keywords": ["box", "value", "store", "name", "10"], "sample": "A variable is a named reference to a value stored in memory; x = 10 binds the name x to the integer object 10."},
        {"q": "List ki tuple ki difference enti?", "keywords": ["mutable", "immutable", "change"], "sample": "Lists are mutable and can be changed after creation; tuples are immutable and fixed."},
        {"q": "Decorator ante enti? Oka example ivvandi.", "keywords": ["function", "wrapper", "return", "@"], "sample": "A decorator is a function that takes another function and returns a wrapped version with extra behaviour, applied with @ syntax."},
    ],
    "generative-ai": [
        {"q": "Tokenization ante enti? LLM ki enduku important?", "keywords": ["token", "split", "pieces", "id", "vocabulary"], "sample": "Tokenization splits text into tokens from a fixed vocabulary; each token maps to an ID the model embeds and processes."},
        {"q": "RAG ante enti? Eppudu use chestaru?", "keywords": ["retriev", "vector", "context", "document", "ground"], "sample": "RAG retrieves relevant documents, adds them as context, and grounds the LLM answer in that evidence."},
    ],
    "ml": [
        {"q": "Overfitting ante enti? Ela reduce chestaru?", "keywords": ["memoriz", "training", "new data", "regularization", "cross-validation"], "sample": "Overfitting is memorising training data and failing on new data; reduce it with more data, regularization, simpler models and cross-validation."},
    ],
}
SESSIONS = {}

def start(topic):
    qs = BANK.get(topic)
    if not qs: return {"ok": False, "error": "unknown topic", "topics": list(BANK)}
    sid = "s-%s-%d" % (topic, len(SESSIONS) + 1)
    SESSIONS[sid] = {"topic": topic, "idx": 0, "scores": []}
    return {"session_id": sid, "question": qs[0]["q"], "difficulty": 1}

def answer(db, session_id, text):
    s = SESSIONS.get(session_id)
    if not s: return {"ok": False, "error": "unknown session"}
    qs = BANK[s["topic"]]; cur = qs[s["idx"]]
    low = (text or "").lower()
    hit = [k for k in cur["keywords"] if k in low]
    missed = [k for k in cur["keywords"] if k not in low]
    score = round(10 * len(hit) / max(len(cur["keywords"]), 1), 1)
    s["scores"].append(score)
    out = {"score_out_of_10": score, "hit_points": hit, "missed": missed,
           "sample_answer": cur["sample"],
           "feedback": "Baga chepparu — inka %s points add chesthe perfect answer." % ", ".join(missed) if missed else "Excellent — anni key points cover chesaru!"}
    s["idx"] += 1
    if s["idx"] < len(qs):
        out["next_question"] = qs[s["idx"]]["q"]; out["difficulty"] = s["idx"] + 1
    else:
        avg = round(sum(s["scores"]) / len(s["scores"]), 1)
        db.save_interview(s["topic"], avg)
        out["finished"] = True; out["average_score"] = avg
    return out
