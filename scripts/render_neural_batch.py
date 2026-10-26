"""Render ALL missing lecture videos with the Microsoft Edge NEURAL Telugu
voice (te-IN-MohanNeural, male, human-like) and place them at
neural/lecture_<id>.mp4 in the repo.

Why this exists: the daily delivery crons now send NEURAL-ONLY videos.
Local renders in the assistant's sandbox fall back to robotic gTTS because
Microsoft's voice server is SSL-blocked there, and the old daily workflow
rendered only ONE lecture per slot with the Shruti voice. This batch script
runs on GitHub's runners, where the voice server IS reachable, and renders
every in-scope lecture that does not already have a neural video.

Safety rules (by design):
  1. It FIRST tests the Edge neural voice with a tiny sample. If the voice
     server is unreachable, it exits 1 and changes NOTHING.
  2. NEURAL ONLY - it never falls back to gTTS. A lecture that fails is
     listed at the end and simply keeps no neural video yet (the delivery
     cron then sends its quiz only, with a "neural video pending" note).
  3. Lectures that already have neural/lecture_<id>.mp4 larger than 1 MB
     are SKIPPED, so re-runs only fill the gaps instead of re-rendering
     all 45 every time.
  4. It never touches the local gTTS videos, the sender, or any other repo.

Usage (from the project folder, on a GitHub runner):
    TELUGU_VOICE=te-IN-MohanNeural python scripts/render_neural_batch.py

In-scope order (same as scripts/render_slot.py ORDERED, extended with any
new lectures the DB gained, e.g. Module-3 Academics):
    Academics, IM Sessions, MasterClasses, Foundations (45 total, id 1 excluded).
"""
import os, sys, shutil

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "backend"))
sys.path.insert(0, os.path.join(ROOT, "scripts"))
os.chdir(ROOT)

from app.db import DB  # noqa: E402
from app import video as video_mod  # noqa: E402
from app import lesson as lesson_mod  # noqa: E402
import render_slot  # noqa: E402

VOICE = os.environ.get("TELUGU_VOICE", "te-IN-MohanNeural")


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
    print("Voice:", VOICE)
    print("Step 1/2: testing the Edge neural voice...")
    if not edge_check():
        print("\nSTOPPED - neural voice server unreachable; nothing produced.")
        return 1
    print("Voice test OK - neural voice is reachable.\n")

    db = DB(os.path.join("data", "app.db"))
    order = render_slot.effective_order(db, 0)
    order = [i for i in order if i != 1]
    print("Lectures in scope:", len(order))

    neural_dir = os.path.join(ROOT, "neural")
    os.makedirs(neural_dir, exist_ok=True)
    done, skipped, failed = [], [], []
    for lid in order:
        dest = os.path.join(neural_dir, "lecture_%d.mp4" % lid)
        if os.path.exists(dest) and os.path.getsize(dest) > 1_000_000:
            print("  SKIP lecture %d (neural video already exists)" % lid)
            skipped.append(lid)
            continue
        try:
            lec = db.get_lecture(lid)
            if not lec or not lec.get("summary"):
                print("  FAIL lecture %d: missing or no summary" % lid)
                failed.append(lid)
                continue
            script = lesson_mod.generate_lesson_script(lec["title"], lec["summary"])
            out_dir = os.path.join("storage", "lecture_%d" % lid)
            os.makedirs(out_dir, exist_ok=True)
            mp3 = os.path.join(out_dir, "lesson.mp3")
            if os.path.exists(mp3):
                os.remove(mp3)  # force fresh neural audio, never reuse gTTS audio
            video_mod._edge_tts(lesson_mod.narration_text(script), mp3)
            v = video_mod.render_video(script, out_dir, slug="lesson")
            shutil.copy2(v["video_path"], dest)
            print("  OK   lecture %d  %ss  %s" % (lid, v["duration_seconds"], lec["title"][:55]))
            done.append(lid)
        except Exception as e:
            print("  FAIL lecture %d: %s" % (lid, str(e)[:200]))
            failed.append(lid)

    print("\nDone: %d newly rendered neural, %d already had neural, %d failed." % (len(done), len(skipped), len(failed)))
    if failed:
        print("Failed lecture ids:", failed, "- just re-run to retry them.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
