"""Re-render ALL lecture videos with the Microsoft Edge NEURAL Telugu voice
(te-IN-MohanNeural by default; set TELUGU_VOICE=te-IN-ShrutiNeural for female).

Why this exists: the videos in this package were rendered on a machine where
Microsoft's voice server was unreachable, so they silently used the robotic
gTTS fallback voice. On a normal home internet connection Edge TTS works, and
this script upgrades every video to the natural, human-like neural voice.

Safety rules (by design):
  1. It FIRST tests the Edge voice with a tiny sample. If the voice server is
     unreachable, it exits WITHOUT touching any video.
  2. Every existing lesson.mp4 is backed up to lesson_gtts_backup.mp4 before
     its lecture is re-rendered. If a render fails, the backup is restored.
  3. Neural voice ONLY - this script never falls back to gTTS. A lecture that
     fails keeps its old video and is listed at the end so you can re-run.

Usage (from the project folder):
    python scripts/rerender_neural.py              # all lectures
    python scripts/rerender_neural.py --only 2     # just lecture 2 (test one)
"""
import os, sys, json, shutil, argparse

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "backend"))
os.chdir(ROOT)

from app.db import DB               # noqa: E402
from app import video as video_mod  # noqa: E402
from app import lesson as lesson_mod  # noqa: E402

VOICE = os.environ.get("TELUGU_VOICE", "te-IN-MohanNeural")


def edge_check():
    """Return True only if the Edge neural voice actually produces audio."""
    tmp = os.path.join("storage", "_voice_test.mp3")
    os.makedirs("storage", exist_ok=True)
    try:
        video_mod._edge_tts("Namaste! Idi oka chinna voice test.", tmp)
        ok = os.path.exists(tmp) and os.path.getsize(tmp) > 0
    except Exception as e:
        print("Edge voice test FAILED:", str(e)[:200])
        return False
    finally:
        if os.path.exists(tmp):
            os.remove(tmp)
    return ok


def load_script(db, lec, folder):
    sp = os.path.join(folder, "lesson_script.json")
    if os.path.exists(sp):
        return json.load(open(sp, encoding="utf-8"))
    script = lesson_mod.generate_lesson_script(lec["title"], lec["summary"])
    os.makedirs(folder, exist_ok=True)
    json.dump(script, open(sp, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
    return script


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--only", type=int, default=None, help="only this lecture id")
    args = ap.parse_args()

    print("Voice:", VOICE)
    print("Step 1/2: testing the Edge neural voice...")
    if not edge_check():
        print("\nSTOPPED - nothing was changed.")
        print("The Microsoft voice server could not be reached from this PC.")
        print("Check your internet connection and run the script again.")
        return 1
    print("Voice test OK - neural voice is reachable.\n")

    print("Step 2/2: re-rendering lecture videos (neural voice only)...")
    db = DB(os.path.join("data", "app.db"))
    lectures = db.list_lectures()
    if args.only:
        lectures = [l for l in lectures if l["id"] == args.only]
    done, failed = [], []
    for lec in lectures:
        lid = lec["id"]
        folder = os.path.join("storage", "lecture_%d" % lid)
        mp4 = os.path.join(folder, "lesson.mp4")
        backup = os.path.join(folder, "lesson_gtts_backup.mp4")
        try:
            full = db.get_lecture(lid)
            script = load_script(db, full, folder)
            if os.path.exists(mp4) and not os.path.exists(backup):
                shutil.copy2(mp4, backup)
            mp3 = os.path.join(folder, "lesson.mp3")
            if os.path.exists(mp3):
                os.remove(mp3)  # old gTTS audio - render_video would reuse it
            video_mod._edge_tts(lesson_mod.narration_text(script), mp3)
            v = video_mod.render_video(script, folder, slug="lesson")
            print("  OK   lecture %d  %ss  %s" % (lid, v["duration_seconds"], lec["title"][:55]))
            done.append(lid)
        except Exception as e:
            if os.path.exists(backup):
                shutil.copy2(backup, mp4)  # restore the old video untouched
            print("  FAIL lecture %d  %s  (%s)" % (lid, lec["title"][:55], str(e)[:120]))
            failed.append(lid)
    print("\nDone: %d re-rendered with the neural voice, %d failed/kept old video." % (len(done), len(failed)))
    if failed:
        print("Failed lecture ids:", failed, "- just run the script again to retry them.")
    print("Old gTTS videos are kept as lesson_gtts_backup.mp4 in each lecture folder.")
    return 0 if not failed else 2


if __name__ == "__main__":
    sys.exit(main())
