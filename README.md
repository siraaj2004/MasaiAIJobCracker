# MASAI AI ENGINEER JOB CRACKER — TELUGU AI MENTOR

Working MVP pipeline: **Masai AI Summary → Telugu lesson script → Telugu video
(TTS + ffmpeg slides + SRT subtitles) → PDF notes → interactive quiz → mistake
detection → spaced revision**, plus coding practice (sandboxed), interview
simulator, revision engine, roadmap mapping and a job-readiness dashboard
calculated only from real records.

## Quick start (Windows / anywhere)
1. `python -m venv .venv` then activate it (see docs/WINDOWS_SETUP.md)
2. `pip install -r requirements.txt`
3. `playwright install chromium`
4. Copy `.env.example` to `.env` and fill values locally (never commit it)
5. Add a summary: run the server and POST to `/lectures/manual-upload`,
   or use the authorized scraper (saved session at `data/storage_state.json`)
6. Process it: `POST /lectures/{id}/process`
7. Open the quiz link it returns, submit, and get mistake analysis + revision

Run the server: `python -m backend.run` → http://localhost:8000/health

## Honesty rules (enforced in code)
- No summary is ever invented; manual upload is the supported fallback.
- A video is reported only if the MP4 exists; failures keep the script for retry.
- An email is reported sent only with a Gmail message id; duplicates blocked.
- Quiz answers are never in the public quiz payload.
- If a summary supports fewer than 20 grounded questions, the quiz says so.
- Dashboard percentages come only from your recorded performance.

## Costs / paid services
Free locally. Gemini/OpenRouter keys, Gmail API (free with your Google account),
hosting, and any premium TTS are optional and may need credits — see
docs/DEPLOYMENT.md. Reliable twice-daily automation needs persistent hosting;
Colab is for development only (docs/COLAB.md).

## Roadmap PDF
Place `AI_Engineer_Job_Roadmap(6).pdf` at `data/roadmap.pdf` — it was not in
this workspace at build time, so the 8 spec phases are built in until then.
