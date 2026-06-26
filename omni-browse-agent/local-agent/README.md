# OmniBrowse Local Agent

FastAPI backend for the local browser automation agent.

## Quick start

```powershell
cd omni-browse-agent/local-agent
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -e ".[test]"
playwright install chromium
uvicorn app.main:app --host 127.0.0.1 --port 8765
```

Ollama is the default local planner provider:

```powershell
ollama pull llama3.1
$env:OMNI_OLLAMA_MODEL="llama3.1"
```

The Phase 2 Hacker News demo does not require the LLM planner yet; it uses the same policy, CDP, logging, screenshot, and result pipeline that the planner will use.

## Launch a browser with CDP on Windows

Chrome:

```powershell
.\scripts\launch-chrome-cdp.ps1
```

Edge:

```powershell
.\scripts\launch-edge-cdp.ps1
```

Brave:

```powershell
.\scripts\launch-brave-cdp.ps1
```

Then create and run a task:

```powershell
$task = Invoke-RestMethod -Method Post -Uri http://127.0.0.1:8765/tasks -ContentType application/json -Body '{"user_prompt":"Use my currently open browser to go to Hacker News and extract the top 10 story titles and links."}'
Invoke-RestMethod -Method Post -Uri "http://127.0.0.1:8765/tasks/$($task.id)/run"
```

Results:

```powershell
Invoke-RestMethod -Uri "http://127.0.0.1:8765/tasks/$($task.id)/results"
```

## Safety

The backend blocks CAPTCHA solving/bypass, stealth automation, proxy rotation, fingerprint spoofing, credential theft, and login/access-control bypass attempts. If CAPTCHA is detected, the run pauses/blocks with `CAPTCHA_BLOCKED` and saves the current context instead of solving it.

