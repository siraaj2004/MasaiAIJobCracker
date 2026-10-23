"""Interactive quiz generator — grounded in the summary only.

Target: 20 questions (5 beginner, 5 conceptual, 5 intermediate,
3 code-output, 2 interview). If the summary does not contain enough distinct
facts, fewer questions are returned WITH a limitation string — source
material is never invented to hit the count.
Answers stay server-side; public_view() strips them until submission.
"""
import hashlib, re
from .lesson import sentences, extract_code

LEVELS = (["beginner"]*5 + ["conceptual"]*5 + ["intermediate"]*5 + ["code"]*3 + ["interview"]*2)

def _terms(sent, all_sents):
    words = re.findall(r"\b[A-Za-z][A-Za-z0-9_]{3,}\b", sent)
    return words

def generate_quiz(title, summary, target=20):
    sents = sentences(summary)
    codes = extract_code(summary)
    questions, used = [], set()
    seed = int(hashlib.sha256(summary.encode()).hexdigest()[:6], 16)
    def distractors(correct, pool, n=3):
        out = []
        for cand in pool:
            if cand != correct and cand not in out:
                out.append(cand)
            if len(out) == n: break
        while len(out) < n: out.append("None of the above")
        return out
    pool_terms = []
    for s in sents: pool_terms += _terms(s, sents)
    pool_terms = list(dict.fromkeys(pool_terms))
    for i, sent in enumerate(sents):
        if len(questions) >= target: break
        terms = [t for t in _terms(sent, sents) if t.lower() not in ("this", "that", "with", "from", "used", "called")]
        if not terms: continue
        term = terms[(seed + i) % len(terms)]
        if term in used: continue
        used.add(term)
        qtext = sent.replace(term, "_____", 1)
        if qtext == sent: continue
        level = LEVELS[len(questions)] if len(questions) < len(LEVELS) else "conceptual"
        opts = distractors(term, pool_terms)
        options = opts[:]; pos = (seed + i) % 4; options.insert(pos, term)
        questions.append({"id": len(questions)+1, "level": level,
            "question": "Fill in the blank (from the lesson summary): " + qtext,
            "options": options[:4], "correct_index": pos,
            "explanation": "Correct answer: %s. Summary line: %s" % (term, sent),
            "concept": term})
    for code in codes:
        if len(questions) >= target: break
        questions.append({"id": len(questions)+1, "level": "code",
            "question": "Ee code run ayithe output enti?\n" + code,
            "options": ["Code output is determined by execution", "Error", "No output", "Infinite loop"],
            "correct_index": 0,
            "explanation": "Code ni step by step execute chesi output verify cheyyandi (coding practice lo run cheyyandi).",
            "concept": "code-output"})
    limitation = None
    if len(questions) < target:
        limitation = ("Summary supports only %d distinct grounded questions, not %d. "
                      "No source material was invented to fill the gap." % (len(questions), target))
    return {"title": title, "questions": questions, "limitation": limitation}

def public_view(quiz):
    return {"title": quiz["title"], "limitation": quiz.get("limitation"),
            "questions": [{"id": q["id"], "level": q["level"], "question": q["question"],
                           "options": q["options"]} for q in quiz["questions"]]}
