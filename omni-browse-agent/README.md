# OmniBrowse Agent

OmniBrowse Agent is a local-first browser automation agent scaffold. This first implementation focuses on Phase 1 and Phase 2:

- FastAPI local backend bound to `127.0.0.1` by default
- SQLite persistence for tasks, runs, actions, logs, screenshots, results, approvals, and safety events
- WebSocket event hub for live run updates
- Safety policy checker and CAPTCHA detector
- CDP controller using Playwright `connect_over_cdp`
- Browser detection for Chromium CDP endpoints plus visible Windows browser processes
- Hacker News top 10 extraction demo through CDP
- Ollama planner interface for local model testing
- Next.js dashboard shell
- Browser extension and native-messaging bridge scaffold

## Run the backend

```powershell
cd C:\Users\mobol\Downloads\browser-automation\omni-browse-agent\local-agent
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -e ".[test]"
playwright install chromium
uvicorn app.main:app --host 127.0.0.1 --port 8765
```

## Use Ollama locally

```powershell
ollama pull llama3.1
$env:OMNI_OLLAMA_MODEL="llama3.1"
$env:OMNI_OLLAMA_BASE_URL="http://127.0.0.1:11434"
```

The HN demo is deterministic for now, so it does not require Ollama to be running. The local planner wrapper is ready for Phase 6.

## Launch a CDP browser

```powershell
cd C:\Users\mobol\Downloads\browser-automation\omni-browse-agent
.\scripts\launch-chrome-cdp.ps1
```

Then open the dashboard or call the API directly.

## Run the dashboard

```powershell
cd C:\Users\mobol\Downloads\browser-automation\omni-browse-agent\apps\frontend
npm install
npm run dev
```

Open [http://localhost:3000](http://localhost:3000).

## Hacker News demo by API

```powershell
$task = Invoke-RestMethod -Method Post -Uri http://127.0.0.1:8765/tasks -ContentType application/json -Body '{"user_prompt":"Use my currently open browser to go to Hacker News and extract the top 10 story titles and links."}'
Invoke-RestMethod -Method Post -Uri "http://127.0.0.1:8765/tasks/$($task.id)/run"
Start-Sleep -Seconds 5
Invoke-RestMethod -Uri "http://127.0.0.1:8765/tasks/$($task.id)/results"
```

## Safety boundary

This repo does not include CAPTCHA solving, CAPTCHA bypassing, anti-bot evasion, stealth automation, proxy rotation, fingerprint spoofing, credential theft, unauthorized scraping helpers, or hidden computer control.

