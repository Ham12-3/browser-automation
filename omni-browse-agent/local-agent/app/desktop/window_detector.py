from app.schemas import BrowserInfo


BROWSER_PROCESSES = {
    "chrome.exe": "Chrome",
    "msedge.exe": "Microsoft Edge",
    "brave.exe": "Brave",
    "firefox.exe": "Firefox",
    "opera.exe": "Opera",
    "vivaldi.exe": "Vivaldi",
}


def detect_browser_processes() -> list[BrowserInfo]:
    try:
        import psutil
    except Exception:
        return []

    browsers: list[BrowserInfo] = []
    for proc in psutil.process_iter(["name", "pid"]):
        name = (proc.info.get("name") or "").lower()
        if name in BROWSER_PROCESSES:
            browsers.append(
                BrowserInfo(
                    browser_name=BROWSER_PROCESSES[name],
                    process_name=name,
                    accessibility_available=True,
                    visual_fallback_available=True,
                )
            )
    return browsers

