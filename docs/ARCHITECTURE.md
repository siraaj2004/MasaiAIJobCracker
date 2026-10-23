# Architecture
Masai Learn (authorized session) → scraper.py (AI Summary only, dedupe by hash; discovers ALL THREE session types — Academic Sessions, IM Sessions, MasterClasses — and stores the category as the lecture module)
→ db.py (SQLite; PostgreSQL-swappable) → lesson.py (9-part Telugu script)
→ video.py (gTTS Telugu audio + ffmpeg slides + SRT) → pdf_notes.py →
quiz_gen.py (grounded questions, answers server-side) → mistake.py
(evaluation, mastery bands, 1/3/7/14/30-day spaced repetition) →
revision.py (daily plan) → coding.py (subprocess sandbox) → interview.py
(one question at a time, /10 scoring) → dashboard.py (readiness from records
only) → email_service.py (Gmail API, dedupe, provider id required) →
scheduler.py (10:00/22:00 checks, 11:00 coding, 14:00 revision, 17:00
interview, 22:00 report). Portfolio mentoring follows the same task/review
loop as coding.py with the 3 spec projects in PROJECT.md order.
