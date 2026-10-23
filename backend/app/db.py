"""SQLite storage (PostgreSQL can replace this layer via DATABASE_URL later).

Tables keep lectures deduplicated by summary hash, plus lessons, quizzes,
attempts, mistakes, spaced-revision schedule, coding/interview records and
an email log that prevents duplicate lesson emails.
"""
import hashlib, json, os, sqlite3, datetime

def now():
    return datetime.datetime.now(datetime.timezone.utc).isoformat()

def summary_hash(text):
    return hashlib.sha256((text or "").strip().encode("utf-8")).hexdigest()

class DB:
    def __init__(self, path=None):
        self.path = path or os.environ.get("DATABASE_PATH", "data/app.db")
        if self.path != ":memory:":
            os.makedirs(os.path.dirname(self.path) or ".", exist_ok=True)
        self.con = sqlite3.connect(self.path, check_same_thread=False)
        self.con.row_factory = sqlite3.Row
        self._init()

    def _init(self):
        c = self.con
        c.executescript("""
        CREATE TABLE IF NOT EXISTS lectures(
          id INTEGER PRIMARY KEY, title TEXT, module TEXT, lecture_date TEXT,
          summary TEXT, summary_hash TEXT UNIQUE, source TEXT, status TEXT,
          created_at TEXT);
        CREATE TABLE IF NOT EXISTS lessons(
          id INTEGER PRIMARY KEY, lecture_id INTEGER, script_json TEXT,
          video_path TEXT, pdf_path TEXT, created_at TEXT);
        CREATE TABLE IF NOT EXISTS quizzes(
          id INTEGER PRIMARY KEY, lecture_id INTEGER, questions_json TEXT,
          limitation TEXT, created_at TEXT);
        CREATE TABLE IF NOT EXISTS attempts(
          id INTEGER PRIMARY KEY, quiz_id INTEGER, answers_json TEXT,
          score REAL, detail_json TEXT, created_at TEXT);
        CREATE TABLE IF NOT EXISTS revision_schedule(
          id INTEGER PRIMARY KEY, concept TEXT, due_date TEXT, reason TEXT,
          done INTEGER DEFAULT 0, created_at TEXT);
        CREATE TABLE IF NOT EXISTS coding_results(
          id INTEGER PRIMARY KEY, challenge_id TEXT, passed INTEGER,
          detail TEXT, created_at TEXT);
        CREATE TABLE IF NOT EXISTS interviews(
          id INTEGER PRIMARY KEY, topic TEXT, score REAL, created_at TEXT);
        CREATE TABLE IF NOT EXISTS emails_sent(
          id INTEGER PRIMARY KEY, lecture_id INTEGER, summary_hash TEXT,
          kind TEXT, provider_id TEXT, created_at TEXT,
          UNIQUE(lecture_id, summary_hash, kind));
        """)
        c.commit()

    def add_lecture(self, title, module, lecture_date, summary, source="manual"):
        """Returns (lecture_id, is_new). Duplicates (same summary) are not re-inserted."""
        h = summary_hash(summary)
        row = self.con.execute("SELECT id FROM lectures WHERE summary_hash=?", (h,)).fetchone()
        if row:
            return row["id"], False
        cur = self.con.execute(
            "INSERT INTO lectures(title,module,lecture_date,summary,summary_hash,source,status,created_at) VALUES(?,?,?,?,?,?,?,?)",
            (title, module, lecture_date, summary, h, source, "pending", now()))
        self.con.commit()
        return cur.lastrowid, True

    def get_lecture(self, lecture_id):
        r = self.con.execute("SELECT * FROM lectures WHERE id=?", (lecture_id,)).fetchone()
        return dict(r) if r else None

    def list_lectures(self):
        return [dict(r) for r in self.con.execute("SELECT * FROM lectures ORDER BY id DESC")]

    def set_lecture_status(self, lecture_id, status):
        self.con.execute("UPDATE lectures SET status=? WHERE id=?", (status, lecture_id)); self.con.commit()

    def save_lesson(self, lecture_id, script, video_path=None, pdf_path=None):
        cur = self.con.execute("INSERT INTO lessons(lecture_id,script_json,video_path,pdf_path,created_at) VALUES(?,?,?,?,?)",
            (lecture_id, json.dumps(script, ensure_ascii=False), video_path, pdf_path, now()))
        self.con.commit(); return cur.lastrowid

    def save_quiz(self, lecture_id, questions, limitation=None):
        cur = self.con.execute("INSERT INTO quizzes(lecture_id,questions_json,limitation,created_at) VALUES(?,?,?,?)",
            (lecture_id, json.dumps(questions, ensure_ascii=False), limitation, now()))
        self.con.commit(); return cur.lastrowid

    def get_quiz(self, quiz_id):
        r = self.con.execute("SELECT * FROM quizzes WHERE id=?", (quiz_id,)).fetchone()
        if not r: return None
        d = dict(r); d["questions"] = json.loads(d.pop("questions_json")); return d

    def save_attempt(self, quiz_id, answers, score, detail):
        cur = self.con.execute("INSERT INTO attempts(quiz_id,answers_json,score,detail_json,created_at) VALUES(?,?,?,?,?)",
            (quiz_id, json.dumps(answers), score, json.dumps(detail, ensure_ascii=False), now()))
        self.con.commit(); return cur.lastrowid

    def list_attempts(self):
        return [dict(r) for r in self.con.execute("SELECT * FROM attempts ORDER BY id DESC")]

    def schedule_revision(self, concept, due_date, reason):
        self.con.execute("INSERT INTO revision_schedule(concept,due_date,reason,created_at) VALUES(?,?,?,?)",
            (concept, due_date, reason, now())); self.con.commit()

    def due_revisions(self, upto=None):
        upto = upto or datetime.date.today().isoformat()
        return [dict(r) for r in self.con.execute(
            "SELECT * FROM revision_schedule WHERE done=0 AND due_date<=? ORDER BY due_date", (upto,))]

    def save_coding(self, challenge_id, passed, detail):
        self.con.execute("INSERT INTO coding_results(challenge_id,passed,detail,created_at) VALUES(?,?,?,?)",
            (challenge_id, 1 if passed else 0, detail, now())); self.con.commit()

    def save_interview(self, topic, score):
        self.con.execute("INSERT INTO interviews(topic,score,created_at) VALUES(?,?,?)", (topic, score, now())); self.con.commit()

    def email_already_sent(self, lecture_id, shash, kind="lesson"):
        return self.con.execute("SELECT 1 FROM emails_sent WHERE lecture_id=? AND summary_hash=? AND kind=?",
            (lecture_id, shash, kind)).fetchone() is not None

    def log_email(self, lecture_id, shash, kind, provider_id):
        self.con.execute("INSERT OR IGNORE INTO emails_sent(lecture_id,summary_hash,kind,provider_id,created_at) VALUES(?,?,?,?,?)",
            (lecture_id, shash, kind, provider_id, now())); self.con.commit()
