"""AI Engineer interview simulator.

Flow (per student's request): BASIC questions first, then SUBJECT-RELATED
questions, difficulty increasing. One question at a time; each answer is
scored /10 with missed points, a strong sample answer, and a follow-up.
Subjects follow the build spec: Python, SQL, Mathematics, Machine Learning,
Deep Learning, Generative AI, AI Agents, MLOps, Coding Interviews, HR.
"""

def Q(q, keywords, sample):
    return {"q": q, "keywords": keywords, "sample": sample}

TOPICS = {
    "python": {"label": "Python", "basic": [
        Q("Variable ante enti? Python lo x = 10 ante em jaruguthundi?", ["box", "value", "store", "name", "10"], "A variable is a named reference to a value stored in memory; x = 10 binds the name x to the integer object 10."),
        Q("List ki tuple ki difference enti?", ["mutable", "immutable", "change"], "Lists are mutable and can be changed after creation; tuples are immutable and fixed."),
    ], "subject": [
        Q("Function ante enti? def enduku use chestam?", ["function", "reuse", "parameter", "return"], "A function is a reusable block of code defined with def; it takes parameters, does work, and can return a value."),
        Q("OOP lo class ki object ki difference enti?", ["class", "blueprint", "object", "instance"], "A class is a blueprint; an object is a concrete instance created from that blueprint."),
        Q("Decorator ante enti? Oka example ivvandi.", ["function", "wrapper", "return", "@"], "A decorator is a function that takes another function and returns a wrapped version with extra behaviour, applied with @ syntax."),
        Q("Exception handling lo try-except enduku use chestam?", ["error", "try", "except", "crash"], "try-except catches runtime errors so the program can recover instead of crashing."),
        Q("Generator ante enti? List tho difference enti?", ["yield", "lazy", "memory", "one at a time"], "A generator yields values one at a time with yield, using little memory, unlike a list which stores everything."),
    ]},
    "sql": {"label": "SQL", "basic": [
        Q("SQL ante enti? Database lo enduku use chestam?", ["query", "database", "data", "retrieve"], "SQL is the language used to query and manage data stored in a relational database."),
        Q("SELECT statement em chestundi?", ["select", "columns", "table", "rows"], "SELECT retrieves chosen columns and rows from a table."),
    ], "subject": [
        Q("WHERE ki HAVING ki difference enti?", ["where", "rows", "having", "group"], "WHERE filters rows before grouping; HAVING filters groups after GROUP BY."),
        Q("INNER JOIN ki LEFT JOIN ki difference enti?", ["inner", "matching", "left", "all rows"], "INNER JOIN returns only matching rows from both tables; LEFT JOIN returns all left-table rows plus matches."),
        Q("GROUP BY ante enti?", ["group", "aggregate", "count", "sum"], "GROUP BY groups rows sharing a value so aggregate functions like COUNT or SUM apply per group."),
        Q("Subquery ante enti?", ["query inside", "nested", "inner query"], "A subquery is a query nested inside another query, whose result feeds the outer query."),
        Q("Window function oka example ivvandi.", ["over", "partition", "row_number", "rank"], "Window functions like ROW_NUMBER() OVER (PARTITION BY dept ORDER BY salary DESC) compute values across a set of rows related to the current row."),
    ]},
    "mathematics": {"label": "Mathematics for AI", "basic": [
        Q("Average (mean) ante enti? Ela calculate chestam?", ["sum", "divide", "count"], "The mean is the sum of values divided by how many values there are."),
        Q("Probability ante enti simple ga cheppandi.", ["chance", "likelihood", "0", "1"], "Probability is the likelihood of an event, measured between 0 (impossible) and 1 (certain)."),
    ], "subject": [
        Q("Vector ante enti? ML lo enduku important?", ["direction", "magnitude", "numbers", "feature"], "A vector is an ordered list of numbers with magnitude and direction; in ML it represents features or embeddings."),
        Q("Derivative ante enti?", ["rate of change", "slope", "function"], "A derivative measures how fast a function's output changes when its input changes — the slope at a point."),
        Q("Gradient ante enti? Gradient descent lo ela use avuthundi?", ["gradient", "direction", "steepest", "minimize", "loss"], "The gradient points in the direction of steepest increase; gradient descent steps opposite to it to minimize loss."),
        Q("Matrix multiplication eppudu possible?", ["columns", "rows", "dimensions", "match"], "Matrix multiplication is possible when the first matrix's column count equals the second matrix's row count."),
    ]},
    "ml": {"label": "Machine Learning", "basic": [
        Q("Machine Learning ante enti simple ga?", ["data", "learn", "pattern", "predict"], "Machine learning lets computers learn patterns from data and make predictions on new data."),
        Q("Training data ante enti?", ["examples", "learn", "model", "input"], "Training data is the example data a model learns from."),
    ], "subject": [
        Q("Overfitting ante enti? Ela reduce chestaru?", ["memoriz", "training", "new data", "regularization", "cross-validation"], "Overfitting is memorising training data and failing on new data; reduce it with more data, regularization, simpler models and cross-validation."),
        Q("Regression ki classification ki difference enti?", ["continuous", "number", "class", "category"], "Regression predicts a continuous number; classification predicts a category or class."),
        Q("Accuracy saripothunda? Precision, recall eppudu chudali?", ["false positive", "false negative", "precision", "recall"], "Accuracy can mislead on imbalanced data; precision and recall show the cost of false positives and false negatives."),
        Q("Regularization ante enti?", ["penalty", "complex", "weights", "overfitting"], "Regularization adds a penalty on large weights to keep the model simpler and reduce overfitting."),
    ]},
    "deep-learning": {"label": "Deep Learning", "basic": [
        Q("Neural network ante enti simple ga?", ["layers", "neurons", "learn", "weights"], "A neural network is layers of connected neurons with weights that adjust during learning."),
        Q("Activation function enduku kavali?", ["non-linear", "relu", "complex patterns"], "Activation functions add non-linearity so the network can learn complex patterns."),
    ], "subject": [
        Q("Backpropagation ante enti?", ["gradient", "chain rule", "weights", "update", "loss"], "Backpropagation computes the gradient of the loss for each weight using the chain rule, so weights can be updated."),
        Q("CNN enduku images ki best?", ["convolution", "features", "edges", "spatial"], "CNNs use convolution filters that detect local features like edges while respecting the spatial structure of images."),
        Q("Transformer lo attention ante enti?", ["attention", "focus", "relevant", "tokens", "weights"], "Attention lets each token weigh which other tokens are most relevant to it when building its representation."),
        Q("Optimizer em chestadu? Adam ki SGD ki difference?", ["update", "weights", "learning rate", "adam", "momentum"], "An optimizer updates weights using gradients; Adam adapts the learning rate per parameter, while plain SGD uses one rate for all."),
    ]},
    "generative-ai": {"label": "Generative AI", "basic": [
        Q("Tokenization ante enti? LLM ki enduku important?", ["token", "split", "pieces", "id", "vocabulary"], "Tokenization splits text into tokens from a fixed vocabulary; each token maps to an ID the model embeds and processes."),
        Q("LLM ante enti?", ["large language model", "text", "predict", "trained"], "An LLM is a large language model trained on huge text data to predict and generate text."),
    ], "subject": [
        Q("Embeddings ante enti?", ["vector", "meaning", "numbers", "similar"], "Embeddings are dense vectors that capture meaning, so similar ideas sit close together in vector space."),
        Q("RAG ante enti? Eppudu use chestaru?", ["retriev", "vector", "context", "document", "ground"], "RAG retrieves relevant documents, adds them as context, and grounds the LLM answer in that evidence."),
        Q("Prompt engineering lo manchi prompt ela rayali?", ["clear", "context", "example", "instruction"], "A good prompt is clear and specific, gives context, states the output format, and includes examples when needed."),
        Q("Vector database enduku use chestam?", ["embedding", "similarity search", "fast", "nearest"], "A vector database stores embeddings and performs fast similarity (nearest-neighbour) search over them."),
    ]},
    "ai-agents": {"label": "AI Agents", "basic": [
        Q("AI agent ante enti? Chatbot tho difference enti?", ["agent", "tools", "actions", "goal", "steps"], "An agent uses an LLM plus tools to take multi-step actions toward a goal, not just reply with text like a basic chatbot."),
        Q("Tool calling ante enti?", ["function", "api", "tool", "arguments"], "Tool calling lets the model choose an external function/API and supply its arguments in a structured format."),
    ], "subject": [
        Q("Agent memory enduku important?", ["context", "remember", "previous", "state"], "Memory lets an agent remember previous steps and state so multi-step tasks stay coherent."),
        Q("Guardrails ante enti agents lo?", ["limit", "safe", "policy", "check"], "Guardrails constrain agent actions — allowed tools, checked inputs/outputs, and human approval for risky steps."),
        Q("Agent ni ela evaluate chestaru?", ["task success", "accuracy", "test", "human review"], "Evaluate agents by task completion rate, correctness of tool calls, cost/latency, and human review of outcomes."),
    ]},
    "mlops": {"label": "MLOps", "basic": [
        Q("Deployment ante enti?", ["live", "users", "server", "access"], "Deployment means putting the application on a server so real users can access it."),
        Q("API ante enti simple ga?", ["interface", "request", "response", "connect"], "An API is an interface through which two programs request and respond to each other."),
    ], "subject": [
        Q("FastAPI enduku ML services ki popular?", ["fast", "python", "validation", "async", "docs"], "FastAPI is popular for ML services because it is fast, async, validates data with Pydantic, and auto-generates API docs."),
        Q("Docker ante enti? Container enduku use chestam?", ["container", "environment", "same", "package"], "Docker packages an app with its environment into a container that runs the same everywhere."),
        Q("Model monitoring enduku kavali deployment tarvata?", ["drift", "performance", "data change", "alert"], "Monitoring detects data drift and performance drops after deployment so the model can be retrained or fixed."),
        Q("CI/CD ante enti?", ["continuous", "test", "deploy", "automatic"], "CI/CD automatically tests and deploys code changes through a pipeline whenever code is pushed."),
    ]},
    "coding-interviews": {"label": "Coding Interviews", "basic": [
        Q("List lo unna numbers anni kalipithe output enti? numbers = [10, 20, 30]", ["60", "sum"], "sum([10, 20, 30]) is 60."),
        Q("Loop ante enti?", ["repeat", "for", "while", "iterations"], "A loop repeats a block of code — for repeats over items, while repeats while a condition is true."),
    ], "subject": [
        Q("String palindrome aa kaada ela check chestaru?", ["reverse", "compare", "string"], "Compare the string with its reverse (s == s[::-1]) or use two pointers from both ends."),
        Q("Dictionary lo word frequency ela count chestaru?", ["dictionary", "count", "key", "get"], "Iterate words, using a dictionary to store and increment each word's count (d.get(w, 0) + 1)."),
        Q("Bug unna code ni debugging ela start chestaru?", ["error", "reproduce", "print", "step"], "First reproduce the bug, read the error, then isolate with prints/tests step by step until the failing line is found."),
    ]},
    "hr": {"label": "HR Interviews", "basic": [
        Q("Meeru me gurinchi cheppandi — self-introduction ela start chestaru?", ["name", "background", "skills", "goal"], "Start with your name, background, key skills with one example, and the role you are aiming for — in about one minute."),
        Q("Mee strength enti? Example tho cheppandi.", ["strength", "example", "evidence"], "Name one real strength and prove it with a short example of what you did and its result."),
    ], "subject": [
        Q("Ee project ni interviewer ki ela explain chestaru?", ["problem", "solution", "my role", "result"], "Explain the problem, your solution, your specific role, the tools used, and the measurable result."),
        Q("Mee weakness enti ani adigithe ela answer cheyyali?", ["honest", "improving", "steps", "example"], "Be honest about a real weakness and describe the concrete steps you are taking to improve it, with progress."),
        Q("Team lo disagreement vaste ela handle chestaru?", ["listen", "respect", "discuss", "goal"], "Listen first, discuss the trade-offs respectfully, and decide based on the team's shared goal."),
    ]},
}

# Backwards-compatible flat view: basic first, then subject-related.
BANK = {k: v["basic"] + v["subject"] for k, v in TOPICS.items()}
SESSIONS = {}

def topics():
    return [{"topic": k, "label": v["label"],
             "basic_count": len(v["basic"]), "subject_count": len(v["subject"])}
            for k, v in TOPICS.items()]

def _queue(topic):
    v = TOPICS[topic]
    return ([("basic", q) for q in v["basic"]] +
            [("subject", q) for q in v["subject"]])

def start(topic):
    if topic not in TOPICS:
        return {"ok": False, "error": "unknown topic", "topics": topics()}
    sid = "s-%s-%d" % (topic, len(SESSIONS) + 1)
    SESSIONS[sid] = {"topic": topic, "idx": 0, "scores": []}
    kind, cur = _queue(topic)[0]
    return {"session_id": sid, "topic": topic, "label": TOPICS[topic]["label"],
            "question_kind": kind, "question": cur["q"], "difficulty": 1,
            "total_questions": len(_queue(topic))}

def answer(db, session_id, text):
    s = SESSIONS.get(session_id)
    if not s: return {"ok": False, "error": "unknown session"}
    queue = _queue(s["topic"]); kind, cur = queue[s["idx"]]
    low = (text or "").lower()
    hit = [k for k in cur["keywords"] if k in low]
    missed = [k for k in cur["keywords"] if k not in low]
    score = round(10 * len(hit) / max(len(cur["keywords"]), 1), 1)
    s["scores"].append(score)
    out = {"score_out_of_10": score, "question_kind": kind, "hit_points": hit, "missed": missed,
           "sample_answer": cur["sample"],
           "feedback": "Baga chepparu — inka %s points add chesthe perfect answer." % ", ".join(missed) if missed else "Excellent — anni key points cover chesaru!"}
    s["idx"] += 1
    if s["idx"] < len(queue):
        nkind, nxt = queue[s["idx"]]
        out["next_question"] = nxt["q"]; out["next_question_kind"] = nkind
        out["difficulty"] = s["idx"] + 1
    else:
        avg = round(sum(s["scores"]) / len(s["scores"]), 1)
        db.save_interview(s["topic"], avg)
        out["finished"] = True; out["average_score"] = avg
    return out
