"""Render ONE lecture's video with the Microsoft Edge NEURAL Telugu voice
(te-IN-ShrutiNeural, female) for the current daily-delivery slot, and place it at
neural/lecture_<id>.mp4 in the repo.

Why this exists: the daily Gmail packages (10 AM / 11 AM / 10 PM / 11 PM IST)
should carry the human-like neural-voice video. The assistant's sandbox cannot
reach Microsoft's voice server, but GitHub's runners can — and on a PUBLIC repo
Actions are free. This script runs ~15 minutes before each delivery slot; the
delivery step then picks the MP4 up from the repo.

Which lecture: deterministic, shared with the delivery step so both sides
always agree without shared state. The order is CATEGORY-WISE, not mixed:
all Academic Sessions first (oldest -> newest), then all IM Sessions
(1 -> 14), then all MasterClasses, then the Python Foundations lectures.
    epoch  = 2026-10-24 (IST)
    slots  = 10 AM -> 0, 11 AM -> 1, 10 PM -> 2, 11 PM -> 3
    idx    = (days_since_epoch * 4 + slot - 2) % 45
    id     = ORDERED[idx]
The "-2" bases the sequence so the first slot under this order,
2026-10-24 10 PM, sends the first Academic Session (id 18).
This script runs at 09:45 / 10:45 / 21:45 / 22:45 IST, i.e. for the NEXT
delivery slot, so the IST hour maps 9->0, 10->1, 21->2, 22->3.

Overrides (manual runs): env SLOT=0..3 and/or LECTURE=<id>.

Safety rules:
  1. The Edge voice is tested FIRST. If the voice server is unreachable the
     script exits 1 and produces NOTHING (the delivery then honestly falls
     back to the existing clear-Telugu-TTS video).
  2. Neural voice ONLY — this script never falls back to gTTS.
"""
import os, sys, json, shutil, datetime, re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "backend"))
os.chdir(ROOT)

from app.db import DB               # noqa: E402
from app import video as video_mod  # noqa: E402
from app import lesson as lesson_mod  # noqa: E402

VOICE = os.environ.get("TELUGU_VOICE", "te-IN-ShrutiNeural")
EPOCH = datetime.date(2026, 10, 24)
HOUR_TO_SLOT = {9: 0, 10: 1, 21: 2, 22: 3}   # this script runs 15 min early

# Category-wise order (45 lectures):
#   Academics oldest -> newest (A15..A29, A21 has no usable summary),
#   IM Sessions 1 -> 14, MasterClasses MC1..MC4 + Overview + maths series,
#   Python Foundations last.
ORDERED = [
    18, 17, 16, 15, 14, 13, 12, 11, 10, 9, 8, 7, 6, 4, 3, 2,   # Academics
    32, 31, 30, 29, 28, 27, 26, 25, 24, 23, 22, 21, 20, 19,   # IM Sessions
    42, 41, 40, 39, 38, 37, 36, 35, 34, 33, 5,               # MasterClasses
    46, 45, 44, 43,                                          # Foundations
]


def ist_now():
    return datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=5, minutes=30)))


def _category(title):
    t = (title or "").strip().lower()
    if t.startswith("academic session"):
        return "acad"
    if t.startswith("im session"):
        return "im"
    if t.startswith("master"):
        return "mc"
    return "found"


def _acad_num(title):
    m = re.search(r"academic session\s+(\d+(?:\.\d+)?)", title or "", re.I)
    return float(m.group(1)) if m else 9999.0


def _im_num(title):
    m = re.search(r"im session\s+(\d+)", title or "", re.I)
    return int(m.group(1)) if m else 9999


_MC_MATHS = ["numbers", "tables", "mathematics behind learning",
             "probability", "vectors", "calculus"]


def _mc_key(title):
    t = (title or "").lower()
    m = re.search(r"masterclass\s+(\d+)", t)
    if m:
        return (0, int(m.group(1)), "")
    if "overview" in t:
        return (1, 0, "")
    for i, name in enumerate(_MC_MATHS):
        if name in t:
            return (2, i, "")
    return (3, 0, t)


_FOUND_ORDER = ["python foundations", "expressions", "loops", "lists"]


def _found_key(title):
    t = (title or "").lower()
    for i, name in enumerate(_FOUND_ORDER):
        if name in t:
            return (i, "")
    return (99, t)


def effective_order(db, current_idx):
    """Base ORDERED list extended with any lectures the DB gained since it
    was written (e.g. upcoming Module-3 Academics like A31/A32).

    A new lecture joins the END of its category block — so a new Academic
    lands after A29, before IM1. If that block already passed in the current
    cycle (its end position is behind current_idx), the lecture instead goes
    right after the current lecture, so a just-held class is sent promptly
    instead of waiting for the next full cycle. Insertions only ever happen
    after the current position, so already-sent lectures never repeat or
    shift under the advancing index. Lectures with no usable summary and
    the Tokenization sample (id 1) never enter the rotation.
    """
    blocks = {"acad": ORDERED[0:16], "im": ORDERED[16:30],
              "mc": ORDERED[30:41], "found": ORDERED[41:45]}
    block_end = {"acad": 15, "im": 29, "mc": 40, "found": 44}
    known = set(ORDERED) | {1}
    new_by_cat = {"acad": [], "im": [], "mc": [], "found": []}
    for row in db.list_lectures():
        lid = row["id"]
        if lid in known:
            continue
        if not (row.get("summary") or "").strip():
            continue
        new_by_cat[_category(row["title"])].append(row)
    new_by_cat["acad"].sort(key=lambda r: _acad_num(r["title"]))
    new_by_cat["im"].sort(key=lambda r: _im_num(r["title"]))
    new_by_cat["mc"].sort(key=lambda r: _mc_key(r["title"]))
    new_by_cat["found"].sort(key=lambda r: _found_key(r["title"]))
    pos = current_idx % len(ORDERED)
    urgent = []
    for cat in ("acad", "im", "mc", "found"):
        items = [r["id"] for r in new_by_cat[cat]]
        if not items:
            continue
        if pos > block_end[cat]:
            urgent.extend(items)
        else:
            blocks[cat].extend(items)
    order = blocks["acad"] + blocks["im"] + blocks["mc"] + blocks["found"]
    if urgent:
        order = order[:pos + 1] + urgent + order[pos + 1:]
    return order


def slot_and_index():
    """Return (slot_number, sequence_index) for right now (IST)."""
    now = ist_now()
    if os.environ.get("SLOT"):
        slot = int(os.environ["SLOT"])
    else:
        slot = HOUR_TO_SLOT[now.hour]
    days = (now.date() - EPOCH).days
    return slot, days * 4 + slot - 2


def pick_lecture():
    if os.environ.get("LECTURE"):
        return int(os.environ["LECTURE"])
    _slot, idx = slot_and_index()
    db = DB(os.path.join("data", "app.db"))
    order = effective_order(db, idx)
    return order[idx % len(order)]


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
