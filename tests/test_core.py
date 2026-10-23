import os, sys, tempfile, unittest
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "backend"))
os.environ["DATABASE_PATH"] = ":memory:"
from app.db import DB
from app import lesson, quiz_gen, mistake, coding, interview, dashboard, scraper
from app.roadmap import map_summary_to_roadmap

SUMMARY = open(os.path.join(os.path.dirname(__file__), "..", "data", "sample_summary_tokenization.txt"), encoding="utf-8").read()

class Core(unittest.TestCase):
    def setUp(self): self.db = DB(":memory:")
    def test_dedupe_no_duplicate_lectures(self):
        a, n1 = self.db.add_lecture("T", "M", "", SUMMARY)
        b, n2 = self.db.add_lecture("T", "M", "", SUMMARY)
        self.assertEqual(a, b); self.assertTrue(n1); self.assertFalse(n2)
    def test_manual_upload_rejects_empty(self):
        with self.assertRaises(ValueError): scraper.manual_upload(self.db, "T", "", "", "  ")
    def test_lesson_has_9_parts(self):
        s = lesson.generate_lesson_script("Tokenization", SUMMARY)
        self.assertEqual(len(s["parts"]), 9); self.assertTrue(s["has_code_in_summary"])
    def test_quiz_grounded_and_answers_hidden_publicly(self):
        q = quiz_gen.generate_quiz("Tokenization", SUMMARY)
        self.assertGreaterEqual(len(q["questions"]), 5)
        pub = quiz_gen.public_view(q)
        self.assertNotIn("correct_index", pub["questions"][0])
    def test_quiz_limitation_reported_for_tiny_summary(self):
        q = quiz_gen.generate_quiz("Tiny", "Cats are animals.")
        self.assertIsNotNone(q["limitation"]); self.assertLess(len(q["questions"]), 20)
    def test_mistake_bands(self):
        q = quiz_gen.generate_quiz("Tokenization", SUMMARY)
        ans = {str(x["id"]): x["correct_index"] for x in q["questions"]}
        r = mistake.evaluate_attempt(q, ans)
        self.assertEqual(r["score"], 100.0); self.assertEqual(r["band"], "provisionally_mastered")
        bad = {str(x["id"]): (x["correct_index"] + 1) % 4 for x in q["questions"]}
        r2 = mistake.evaluate_attempt(q, bad)
        self.assertLess(r2["score"], 60); self.assertTrue(r2["weak_concepts"])
    def test_spaced_repetition_offsets(self):
        mistake.schedule_spaced_repetition(self.db, ["tokens"], "provisionally_mastered")
        rows = self.db.con.execute("SELECT COUNT(*) c FROM revision_schedule").fetchone()
        self.assertEqual(rows["c"], 5)
    def test_coding_sandbox_and_challenge(self):
        r = coding.run_code("print(sum([10, 20, 30]))")
        self.assertTrue(r["ok"]); self.assertEqual(r["stdout"].strip(), "60")
        s = coding.submit_challenge(self.db, "sum-list", "numbers=[10,20,30]\nprint(sum(numbers))")
        self.assertTrue(s["passed"])
    def test_interview_scores_and_sample(self):
        st = interview.start("generative-ai"); sid = st["session_id"]
        r = interview.answer(self.db, sid, "Tokenization splits text into tokens, each token has an id from vocabulary")
        self.assertGreater(r["score_out_of_10"], 5); self.assertIn("sample_answer", r)
    def test_dashboard_from_real_data_only(self):
        d = dashboard.compute(self.db)
        self.assertEqual(d["overall_job_readiness"], 0.0)
        self.assertIn("Not a guarantee", d["note"])
    def test_session_categories_all_three(self):
        self.assertEqual(scraper.classify_session("Academic Session: Python Basics", ""), "academic")
        self.assertEqual(scraper.classify_session("IM Session with mentor", ""), "im")
        self.assertEqual(scraper.classify_session("MasterClass: System Design", ""), "masterclass")
        self.assertEqual(scraper.classify_session("", "https://learn.masaischool.com/masterclass/llms"), "masterclass")
        self.assertEqual(scraper.classify_session("Some other talk", "https://x/other"), "other")
        self.assertEqual(scraper.category_label("im"), "IM Sessions")
        self.assertEqual([c["key"] for c in scraper.SESSION_CATEGORIES], ["academic", "im", "masterclass"])
    def test_roadmap_mapping(self):
        m = map_summary_to_roadmap(SUMMARY)
        self.assertTrue(any(x["phase"] == "Generative AI and LLM Engineering" for x in m))

if __name__ == "__main__": unittest.main()
