"""Render ONE lecture's video with the Microsoft Edge NEURAL Telugu voice
(te-IN-MohanNeural) for the current daily-delivery slot, and place it at
neural/lecture_<id>.mp4 in the repo.

Why this exists: the daily Gmail packages (10 AM / 11 AM / 10 PM / 11 PM IST)
should carry the human-like neural-voice video. The assistant's sandbox cannot
reach Microsoft's voice server, but GitHub's runners can — and on a PUBLIC repo
Actions are free. This script runs ~15 minutes before each delivery slot; the
delivery step then picks the MP4 up from the repo.

Which lecture: deterministic, shared with the delivery step so both sides
always agree without shared state.
    epoch  = 2026-10-24 (IST)
    slots  = 10 AM -> 0, 11 AM -> 1, 10 PM -> 2, 11 PM -> 3
    s      = days_since_epoch * 4 + slot
    id     = 2 + ((s - 1) % 45)          # lectures 2..46 (45 lectures)
This script runs at 09:45 / 10:45 / 21:45 / 22:45 IST, i.e. for the NEXT
delivery slot, so the IST hour maps 9->0, 10->1, 21->2, 22->3.

Overrides (manual runs): env SLOT=0..3 and/or LECTURE=<id>.

Safety rules:
  1. The Edge voice is tested FIRST. If the voice server is unreachable the
     script exits 1 and produces NOTHING (the delivery then honestly falls
     back to the existing clear-Telugu-TTS video).
  2. Neural voice ONLY — this script never falls back to gTTS.
"""
import os, sys, json, shutil, datetime

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "backend"))
os.chdir(ROOT)

from app.db import DB               # noqa: E402
from app import video as video_mod  # noqa: E402
from app import lesson as lesson_mod  # noqa: E402

VOICE = os.environ.get("TELUGU_VOICE", "te-IN-MohanNeural")
EPOCH = datetime.date(2026, 10, 24)
HOUR_TO_SLOT = {9: 0, 10: 1, 21: 2, 22: 3}   # this script runs 15 min early
TOTAL = 45                                    # lectures 2..46


def ist_now():
    return datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=5, minutes=30)))


def pick_lecture():
    if os.environ.get("LECTURE"):
        return int(os.environ["LECTURE"])
    now = ist_now()
    if os.environ.get("SLOT"):
        slot = int(os.environ["SLOT"])
    else:
        slot = HOUR_TO_SLOT[now.hour]
    days = (now.date() - EPOCH).days
    s = days * 4 + slot
    return 2 + ((s - 1) % TOTAL)


def edge_check():
    tmp = os.path.join("storage", "_voice_test.mp3")
    os.makedirs("storage", exist_ok=True)
    try:
        video_mod._edge_tts("Namaste! Idi oka chinna voice test.", tmp)
        return os.path.exists(tmp) and os.path.getsize(tmp) > 0
    except Exception as e:
        print("Edge voice test FAILED:", str(e)[:200])
        return False
    finally:
        if os.path.exists(tmp):
            os.remove(tmp)


def main():
    lid = pick_lecture()
    print("Voice:", VOICE)
    print("Lecture for this slot:", lid)
    if not edge_check():
        print("STOPPED - neural voice server unreachable; nothing produced.")
        return 1
    print("Voice test OK - neural voice is reachable.")

    db = DB(os.path.join("data", "app.db"))
    lec = db.get_lecture(lid)
    if not lec or not lec.get("summary"):
        print("Lecture %d missing or has no summary - nothing produced." % lid)
        return 1

    script = lesson_mod.generate_lesson_script(lec["title"], lec["summary"])
    out_dir = os.path.join("storage", "lecture_%d" % lid)
    os.makedirs(out_dir, exist_ok=True)
    mp3 = os.path.join(out_dir, "lesson.mp3")
    if os.path.exists(mp3):
        os.remove(mp3)  # force fresh neural audio
    video_mod._edge_tts(lesson_mod.narration_text(script), mp3)
    v = video_mod.render_video(script, out_dir, slug="lesson")
    src = v["video_path"]
    dest_dir = os.path.join(ROOT, "neural")
    os.makedirs(dest_dir, exist_ok=True)
    dest = os.path.join(dest_dir, "lecture_%d.mp4" % lid)
    shutil.copy2(src, dest)
    print("NEURAL_OK lecture %d  %ss  %d bytes  %s" % (
        lid, v["duration_seconds"], os.path.getsize(dest), lec["title"][:60]))
    return 0


if __name__ == "__main__":
    sys.exit(main())
