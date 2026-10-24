"""Daily package SENDER — runs FREE on GitHub Actions (public repo).

At each of the four daily slots (10 AM / 11 AM / 10 PM / 11 PM IST) this
script emails shaik the day's learning package:
  1. AI Summary video — Telugu explainer with slides/visualization, in the
     real human-like Edge NEURAL voice. The video is rendered ~15 minutes
     earlier by .github/workflows/neural-daily.yml and committed to
     neural/lecture_<id>.mp4; this script attaches it when it exists. If it
     does not exist yet, the package still goes out with the quiz and the
     interview questions, and the email says so honestly (video follows).
  2. Quiz from the AI Summary — Masai-format HTML: Section A Objective
     MCQs + Section B Descriptive, generated from the lecture's own summary
     (backend/app/quiz_html.py), never invented.
  3. AI Engineer interview questions — HTML quiz that CHANGES every run:
     5 Objective MCQs + 3 Descriptive, rotated deterministically over the
     59-question bank (backend/app/interview.py), with the answer key in a
     separate section at the end.

Mistake-rectification videos: when shaik sends his quiz answers in chat,
wrong concepts are queued there and the rectification video goes out with
the NEXT slot's package from the chat delivery (see the daily-run crons).
This script's email always carries the line telling him to send answers in
chat for that.

Lecture selection is DETERMINISTIC and shared with neural-daily.yml and
with the chat delivery crons — no shared state file is needed. The order is
CATEGORY-WISE: all Academic Sessions first (oldest -> newest), then all IM
Sessions (1 -> 14), then all MasterClasses, then Python Foundations:
    epoch = 2026-10-24 (IST)
    slot  = 10 AM -> 0, 11 AM -> 1, 10 PM -> 2, 11 PM -> 3
    idx   = (days_since_epoch * 4 + slot - 2) % 45
    id    = ORDERED[idx]   (first slot under this order, 2026-10-24 10 PM,
                            sends the first Academic Session, id 18)

Email is sent via Gmail SMTP with an App Password. The two credentials come
ONLY from GitHub repository secrets (never from chat, never printed):
    SENDER_EMAIL         — the Gmail address to send from and to
    SENDER_APP_PASSWORD  — a Google App Password for that account
If either secret is missing, the script exits 0 WITHOUT sending, printing a
clear notice — the chat crons keep delivering in the meantime, so nothing
is duplicated and nothing is silently lost.

Stdlib only: no pip install is needed to run this script.
"""
import os, sys, json, html, random, smtplib, datetime
from email.message import EmailMessage

ROOT = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(ROOT, "backend"))
os.chdir(ROOT)

from app.db import DB                    # noqa: E402
from app import quiz_html as quiz_html_mod  # noqa: E402
from app.interview import TOPICS         # noqa: E402

EPOCH = datetime.date(2026, 10, 24)
HOUR_TO_SLOT = {10: 0, 11: 1, 22: 2, 23: 3}
SLOT_LABELS = {0: "10:00 AM", 1: "11:00 AM", 2: "10:00 PM", 3: "11:00 PM"}
MAX_ATTACH_BYTES = 24 * 1024 * 1024

# Category-wise order — must match scripts/render_slot.py exactly.
ORDERED = [
    18, 17, 16, 15, 14, 13, 12, 11, 10, 9, 8, 7, 6, 4, 3, 2,   # Academics
    32, 31, 30, 29, 28, 27, 26, 25, 24, 23, 22, 21, 20, 19,   # IM Sessions
    42, 41, 40, 39, 38, 37, 36, 35, 34, 33, 5,               # MasterClasses
    46, 45, 44, 43,                                          # Foundations
]


def ist_now():
    return datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=5, minutes=30)))


def pick_slot_and_lecture():
    """Return (slot_number, lecture_id, days_since_epoch)."""
    if os.environ.get("LECTURE"):
        return None, int(os.environ["LECTURE"]), None
    now = ist_now()
    slot = int(os.environ["SLOT"]) if os.environ.get("SLOT") else HOUR_TO_SLOT[now.hour]
    days = (now.date() - EPOCH).days
    lecture_id = ORDERED[(days * 4 + slot - 2) % len(ORDERED)]
    return slot, lecture_id, days


def build_interview_html(seed, out_path):
    """Deterministic rotating interview quiz: 5 MCQs + 3 descriptive + key."""
    flat = []  # (topic_key, label, question, sample)
    for key, v in TOPICS.items():
        for q in v["basic"] + v["subject"]:
            flat.append((key, v["label"], q["q"], q["sample"]))
    total = len(flat)
    start = (seed * 8) % total
    picked = [flat[(start + i) % total] for i in range(8)]
    mcqs, descriptive = picked[:5], picked[5:]
    rng = random.Random(seed)
    parts = ["<html><head><meta charset='utf-8'><style>",
             "body{font-family:system-ui,Arial,sans-serif;max-width:820px;margin:24px auto;"
             "padding:0 16px;line-height:1.55}h2{border-bottom:2px solid #12355B;padding-bottom:4px}"
             ".q{margin:14px 0}.opts{margin:6px 0 0 18px}"
             "details{background:#f2f6fb;border:1px solid #d5e0ee;border-radius:8px;padding:10px 14px;margin:10px 0}",
             "</style></head><body>",
             "<h1>AI Engineer Interview Questions — Daily Practice</h1>",
             "<p>Modata answers mee own words lo rayandi / cheppandi, tarvata answer key tho check cheskondi.</p>",
             "<h2>Section A — Objective (MCQs)</h2>"]
    key_lines = []
    for i, (key, label, q, sample) in enumerate(mcqs, 1):
        distractors = [s for (k, _l, _q, s) in flat if k == key and s != sample]
        rng.shuffle(distractors)
        options = [sample] + distractors[:3]
        rng.shuffle(options)
        correct = "ABCD"[options.index(sample)]
        parts.append("<div class='q'><b>%d. [%s] %s</b><div class='opts'>%s</div></div>" % (
            i, html.escape(label), html.escape(q),
            "".join("<div>%s. %s</div>" % (letter, html.escape(opt))
                    for letter, opt in zip("ABCD", options))))
        key_lines.append("Q%d: %s" % (i, correct))
    parts.append("<h2>Section B — Descriptive</h2>")
    for j, (key, label, q, sample) in enumerate(descriptive, 1):
        parts.append("<div class='q'><b>%d. [%s] %s</b></div>" % (
            j, html.escape(label), html.escape(q)))
        key_lines.append("Descriptive %d model points: %s" % (j, sample))
    parts.append("<details><summary><b>Answer Key (attempt ayyaka open cheyyandi)</b></summary>")
    parts.append("<br>".join(html.escape(k) for k in key_lines))
    parts.append("</details></body></html>")
    open(out_path, "w", encoding="utf-8").write("\n".join(parts))
    return out_path


def main():
    sender = os.environ.get("SENDER_EMAIL")
    app_password = os.environ.get("SENDER_APP_PASSWORD")
    if not sender or not app_password:
        print("GMAIL SECRETS NOT CONFIGURED — skipping send.")
        print("Set repository secrets SENDER_EMAIL and SENDER_APP_PASSWORD, "
              "then the next slot's run will send from GitHub. "
              "Until then the chat delivery keeps sending the packages.")
        return 0

    slot, lecture_id, days = pick_slot_and_lecture()
    now = ist_now()
    if slot is None:
        slot = HOUR_TO_SLOT.get(now.hour, 0)
    label = SLOT_LABELS[slot]
    date_str = now.strftime("%Y-%m-%d")
    seed = (days if days is not None else 0) * 4 + slot

    db = DB(os.path.join("data", "app.db"))
    lec = db.get_lecture(lecture_id)
    if not lec:
        print("Lecture %d not found in data/app.db — nothing sent." % lecture_id)
        return 1
    title = lec["title"]

    out_dir = os.path.join("daily_out", "lecture_%d" % lecture_id)
    os.makedirs(out_dir, exist_ok=True)

    attachments = []  # (path, filename)
    video_neural = False
    neural_path = os.path.join("neural", "lecture_%d.mp4" % lecture_id)
    if os.path.exists(neural_path) and os.path.getsize(neural_path) > 1024 * 1024:
        attachments.append((neural_path, "lesson_neural_voice.mp4"))
        video_neural = True

    quiz_ok = False
    quiz_path = os.path.join(out_dir, "quiz.html")
    try:
        quiz_html_mod.write_quiz_html(db, lecture_id, quiz_path)
        if os.path.exists(quiz_path) and os.path.getsize(quiz_path) > 0:
            attachments.append((quiz_path, "quiz.html"))
            quiz_ok = True
    except Exception as e:
        print("Quiz HTML generation failed:", str(e)[:200])

    interview_path = os.path.join(out_dir, "interview_questions.html")
    build_interview_html(seed, interview_path)
    attachments.append((interview_path, "interview_questions.html"))

    if video_neural:
        voice_line = "Ee video real human-like neural Telugu voice tho GitHub lo render ayindi."
    else:
        voice_line = ("Ee slot ki neural voice video inka ready kaledu — "
                      "video render fail ayithe next slot lo malli try avuthundi; "
                      "quiz + interview questions ee email lo unnayi.")

    body = (
        "Shaik,\n\n"
        "Eeroju package — %s (%s, %s):\n\n"
        "1. Telugu explainer video — AI Summary nundi slides/visualization tho.\n"
        "   %s\n"
        "2. Lecture quiz (HTML) — Section A Objective MCQs + Section B Descriptive, "
        "aa lecture summary nundiye%s.\n"
        "3. Interview questions (HTML) — ee run ki fresh set: 5 MCQs + 3 Descriptive + answer key.\n\n"
        "Quiz answers naaku chat lo pampandi — check chesi guide chestha; "
        "wrong ayina concepts ki Telugu rectification video next slot (10 AM / 11 AM / 10 PM / 11 PM) Gmail lone vasthundi.\n\n"
        "Goal: AI Engineer job crack cheyyadam.\n" % (
            title, label, date_str, voice_line,
            "" if quiz_ok else " (ee run lo quiz HTML generate kaledu — next run lo vasthundi)"))

    total_bytes = sum(os.path.getsize(p) for p, _ in attachments)
    subject = "Masai Daily Package — %s (%s, %s)" % (title, label, date_str)

    def send(files, subj):
        msg = EmailMessage()
        msg["From"] = sender
        msg["To"] = sender
        msg["Subject"] = subj
        msg.set_content(body)
        for path, name in files:
            with open(path, "rb") as f:
                data = f.read()
            maintype = "video" if name.endswith(".mp4") else "text"
            subtype = "mp4" if name.endswith(".mp4") else "html"
            msg.add_attachment(data, maintype=maintype, subtype=subtype, filename=name)
        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as smtp:
            smtp.login(sender, app_password)
            smtp.send_message(msg)

    if total_bytes <= MAX_ATTACH_BYTES:
        send(attachments, subject)
    else:
        video_files = [a for a in attachments if a[1].endswith(".mp4")]
        html_files = [a for a in attachments if not a[1].endswith(".mp4")]
        send(video_files, subject)
        send(html_files, subject + " (HTML files)")

    print("SENT lecture %d %s video=%s quiz=%s interview=ok attachments=%d" % (
        lecture_id, title[:50], "neural" if video_neural else "missing",
        "ok" if quiz_ok else "fail", len(attachments)))
    return 0


if __name__ == "__main__":
    sys.exit(main())
