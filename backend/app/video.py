"""Telugu video pipeline: script -> TTS audio -> animated slides (ffmpeg) -> MP4 + SRT.

Honesty rule: a video is only reported when the MP4 file exists on disk.
If TTS or ffmpeg fails, VideoRenderError is raised and the script is retained
for retry (scripts are always saved before rendering is attempted).
Slides use Roman Telugu / English text (reliable font rendering); the audio
narration is Telugu TTS and an .srt subtitle file is written alongside.
"""
import os, subprocess, textwrap, json
from .lesson import narration_text

class VideoRenderError(Exception): pass

def _run(cmd):
    r = subprocess.run(cmd, capture_output=True, text=True, timeout=900)
    if r.returncode != 0:
        raise VideoRenderError("command failed: %s\n%s" % (" ".join(cmd[:4]), r.stderr[-800:]))
    return r

def synthesize_tts(text, mp3_path, provider=None):
    provider = provider or os.environ.get("TTS_PROVIDER", "gtts")
    if provider == "gtts":
        try:
            from gtts import gTTS
        except ImportError:
            raise VideoRenderError("gTTS not installed — script retained for retry")
        gTTS(text=text, lang="te").save(mp3_path)
    elif provider == "none":
        raise VideoRenderError("TTS provider set to 'none' — script retained for retry")
    else:
        raise VideoRenderError("unknown TTS provider: %s" % provider)
    if not os.path.exists(mp3_path) or os.path.getsize(mp3_path) == 0:
        raise VideoRenderError("TTS produced no audio")

def _duration(path):
    r = _run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", path])
    return float(r.stdout.strip())

def _slide_png(text, out, idx):
    safe = text.replace("'", "").replace(":", " -")
    lines = textwrap.wrap(safe, 42)[:8]
    draw = ",".join("drawtext=text='%s':fontcolor=white:fontsize=44:x=80:y=%d" % (ln.replace("%", ""), 120 + i*70)
                    for i, ln in enumerate(lines)) or "drawbox=color=navy"
    _run(["ffmpeg", "-y", "-f", "lavfi", "-i", "color=c=0x12355B:s=1920x1080:d=1",
          "-vf", draw, "-frames:v", "1", out])

def write_srt(script, srt_path, total_seconds):
    parts = script["parts"]; per = max(total_seconds / max(len(parts), 1), 1.0)
    def ts(s):
        h = int(s//3600); m = int((s%3600)//60); sec = s%60
        return "%02d:%02d:%06.3f" % (h, m, sec)
    lines = []
    for i, p in enumerate(parts):
        txt = p.get("text") or " ".join(p.get("questions", []))
        lines.append("%d\n%s --> %s\n%s\n" % (i+1, ts(i*per).replace(".", ","), ts((i+1)*per).replace(".", ","), txt[:200]))
    open(srt_path, "w", encoding="utf-8").write("\n".join(lines))

def render_video(script, out_dir, slug="lesson"):
    os.makedirs(out_dir, exist_ok=True)
    script_path = os.path.join(out_dir, slug + "_script.json")
    open(script_path, "w", encoding="utf-8").write(json.dumps(script, ensure_ascii=False, indent=2))
    text = narration_text(script)
    mp3 = os.path.join(out_dir, slug + ".mp3")
    if os.path.exists(mp3) and os.path.getsize(mp3) > 0:
        pass  # retry path: reuse audio from the earlier attempt
    else:
        synthesize_tts(text, mp3)
    total = _duration(mp3)
    parts = script["parts"]; per = total / max(len(parts), 1)
    slides = []
    for i, p in enumerate(parts):
        png = os.path.join(out_dir, "slide_%02d.png" % i)
        _slide_png("Part %d - %s\n%s" % (p["part"], p["name"], (p.get("text") or "")[:220]), png, i)
        slides.append(png)
    concat = os.path.join(out_dir, "concat.txt")
    with open(concat, "w") as f:
        for png in slides:
            f.write("file '%s'\nduration %.2f\n" % (os.path.abspath(png), per))
        f.write("file '%s'\n" % os.path.abspath(slides[-1]))
    mp4 = os.path.join(out_dir, slug + ".mp4")
    _run(["ffmpeg", "-y", "-f", "concat", "-safe", "0", "-i", concat, "-i", mp3,
          "-c:v", "libx264", "-pix_fmt", "yuv420p", "-vf", "scale=1920:1080", "-r", "30",
          "-c:a", "aac", "-shortest", mp4])
    if not os.path.exists(mp4) or os.path.getsize(mp4) == 0:
        raise VideoRenderError("ffmpeg finished but MP4 missing — script retained")
    write_srt(script, os.path.join(out_dir, slug + ".srt"), total)
    return {"video_path": mp4, "duration_seconds": round(total, 1),
            "subtitles": os.path.join(out_dir, slug + ".srt"), "script_path": script_path,
            "checkpoint_question": script.get("checkpoint_question")}
