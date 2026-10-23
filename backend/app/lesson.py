"""Telugu lesson-script generator.

Grounded in the extracted summary: definitions and facts are taken from the
summary text itself. Simple-language analogies and interview extras are
clearly labelled as teaching additions, never presented as summary content.
Structure = the 9 parts from the spec.
"""
import re

def sentences(text):
    parts = re.split(r"(?<=[.!?])\s+", (text or "").replace("\n", " "))
    return [p.strip() for p in parts if len(p.strip()) > 15]

def extract_code(text):
    return re.findall(r"```(?:python)?\n(.*?)```", text or "", flags=re.S)

def key_terms(text, limit=8):
    terms = re.findall(r"\b([A-Z][A-Za-z0-9 ]{2,30}|tokenization|embedding|overfitting|regression|gradient|attention|vector|model|training data)\b", text or "")
    seen, out = set(), []
    for t in terms:
        k = t.strip().lower()
        if k not in seen: seen.add(k); out.append(t.strip())
    return out[:limit]

ANALOGIES = {
    "tokenization": "Manam oka pedda chocolate ni chinna pieces ga break chestham kada? Alage LLM oka sentence ni chinna parts ga divide chesthundi. Aa parts ni tokens antaru.",
    "overfitting": "Overfitting ante student textbook answers anni memorize chesadu, kaani new question adigithe answer cheyyalekapothunnadu. Model kuda training data ni memorize chesi new data meeda fail avvachu.",
    "variable": "Variable ante oka box laantidi. Manam aa box lo oka value store chestham. Python lo x = 10 ante x ane box lo 10 pettinattu.",
}

def generate_lesson_script(title, summary):
    sents = sentences(summary)
    codes = extract_code(summary)
    topic_key = (title or "").lower()
    analogy = next((v for k, v in ANALOGIES.items() if k in topic_key or k in (summary or "").lower()[:200]), 
                   "Ee topic ni oka simple example tho step by step ga ardham cheskundham.")
    definition = sents[0] if sents else "Summary lo definition available ledu — invent cheyyatledu."
    parts = [
        {"part": 1, "name": "Introduction", "text": "Namaste! Ee roju manam '%s' gurinchi nerchukuntam. Bayapadakandi, chala simple ga cheptha." % title},
        {"part": 2, "name": "Fourth-class explanation", "text": analogy},
        {"part": 3, "name": "Real-life example", "text": "Real life example: " + (sents[1] if len(sents) > 1 else analogy)},
        {"part": 4, "name": "Technical definition (from summary)", "text": definition},
        {"part": 5, "name": "Python code explanation", "text": ("Code summary lone undi, line by line ga explain chestha:\n" + codes[0]) if codes else "Ee summary lo code example ledu. Kindha unna code 'additional teaching example' — summary content kaadu."},
        {"part": 6, "name": "Practical demonstration", "text": "Input, execution, output step by step ga chudham. Summary facts: " + " ".join(sents[:3])},
        {"part": 7, "name": "Interview preparation (additional, not from summary)", "questions": [
            "What is %s? Interview lo simple English lo cheppandi." % title,
            "%s real project lo ekkada use chestaru?" % title,
            "%s lo common mistake enti?" % title]},
        {"part": 8, "name": "Revision", "text": "Important points: " + "; ".join(key_terms(summary))},
        {"part": 9, "name": "Mini challenge", "text": "Challenge: '%s' ni mee own words lo 3 lines lo rayandi, oka chinna Python example tho." % title},
    ]
    return {"title": title, "language": "te-mixed-en", "parts": parts,
            "terms": key_terms(summary), "source_sentences": sents,
            "has_code_in_summary": bool(codes),
            "checkpoint_question": "Interview Question: %s ante enti? Pause chesi answer cheyyandi, tarvata continue cheddam." % title}

def narration_text(script):
    out = []
    for p in script["parts"]:
        out.append(p.get("text") or " ".join(p.get("questions", [])))
    return "\n".join(out)
