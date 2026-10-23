# Deployment
Docker: `docker compose up --build` (persistent volumes for data/ and storage/).
Any host works (Render/Railway/VPS): set env vars from .env.example, attach a
persistent disk for data/ + storage/ (free tiers often wipe files on redeploy),
serve over HTTPS, and keep APP_API_KEY set. Background scheduling
(backend/app/scheduler.py) needs the process running 24x7 — that is why Colab
cannot provide reliable 10 AM / 10 PM checks. Paid/credits: LLM API usage,
premium TTS voices, paid hosting/disk. Gmail API and gTTS are free tiers.
