# Windows setup
1. Install Python 3.12 from python.org (tick "Add Python to PATH"), and FFmpeg (winget install ffmpeg).
2. Open PowerShell in this folder:
   py -m venv .venv
   .venv\Scripts\Activate.ps1
   pip install -r requirements.txt
   playwright install chromium
3. Copy .env.example to .env and fill it (Notepad). Never share .env.
4. Masai session: run Playwright once headed, log in yourself on the official
   site, save storage_state to data/storage_state.json. CAPTCHA = stop; the
   scraper never bypasses it.
5. Start: python -m backend.run  →  http://localhost:8000/health
6. Frontend (optional dev mode): cd frontend; npm install; npm run dev
