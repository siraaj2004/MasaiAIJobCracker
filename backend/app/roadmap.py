"""Job roadmap integration.

The roadmap PDF (AI_Engineer_Job_Roadmap(6).pdf) is the career syllabus source.
It was NOT present in this workspace when the project was built, so:
- load_pdf_text() ingests it as soon as the user places it at data/roadmap.pdf
- until then, PHASES below mirror the 8 areas named in the build spec.
Lecture-specific teaching always comes from Masai summaries; roadmap mapping
and extra interview content are labelled separately.
"""
import os

PHASES = [
    "Programming and CS Foundations",
    "Mathematics for AI",
    "Machine Learning",
    "Deep Learning and Transformers",
    "Generative AI and LLM Engineering",
    "MLOps and Deployment",
    "Portfolio Projects",
    "Interview Preparation",
]

KEYWORD_MAP = {
    "Programming and CS Foundations": ["python", "variable", "function", "oop", "class", "sql", "list", "dictionary", "loop"],
    "Mathematics for AI": ["probability", "statistics", "linear algebra", "derivative", "gradient", "matrix", "calculus"],
    "Machine Learning": ["regression", "classification", "clustering", "overfitting", "regularization", "scikit", "evaluation"],
    "Deep Learning and Transformers": ["neural", "backpropagation", "activation", "optimizer", "cnn", "transformer", "attention"],
    "Generative AI and LLM Engineering": ["tokenization", "token", "embedding", "llm", "prompt", "rag", "vector"],
    "MLOps and Deployment": ["fastapi", "docker", "deployment", "ci/cd", "monitoring", "api"],
    "Portfolio Projects": ["project", "portfolio", "github"],
    "Interview Preparation": ["interview", "hr", "behavioural", "behavioral"],
}

TWELVE_WEEK_PLAN = [
    (1, "Programming and CS Foundations"), (2, "Programming and CS Foundations"),
    (3, "Mathematics for AI"), (4, "Mathematics for AI"),
    (5, "Machine Learning"), (6, "Machine Learning"),
    (7, "Deep Learning and Transformers"), (8, "Deep Learning and Transformers"),
    (9, "Generative AI and LLM Engineering"), (10, "Generative AI and LLM Engineering"),
    (11, "MLOps and Deployment"), (12, "Portfolio Projects + Interview Preparation"),
]

def map_summary_to_roadmap(summary):
    text = (summary or "").lower()
    hits = []
    for phase, words in KEYWORD_MAP.items():
        matched = [w for w in words if w in text]
        if matched:
            hits.append({"phase": phase, "matched_keywords": matched})
    return hits or [{"phase": "Unmapped", "matched_keywords": []}]

def load_pdf_text(path="data/roadmap.pdf"):
    if not os.path.exists(path):
        return None, "roadmap PDF not found at %s — place AI_Engineer_Job_Roadmap(6).pdf there" % path
    try:
        from pypdf import PdfReader
        reader = PdfReader(path)
        return "\n".join((p.extract_text() or "") for p in reader.pages), None
    except Exception as e:
        return None, "could not read roadmap PDF: %s" % e
