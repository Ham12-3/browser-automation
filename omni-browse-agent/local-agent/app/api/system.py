from fastapi import APIRouter

from app.control.manager import BrowserControlManager

router = APIRouter(prefix="/system", tags=["system"])


@router.get("/browsers")
async def get_browsers() -> list[dict[str, object]]:
    browsers = await BrowserControlManager().detect_browsers()
    return [browser.model_dump() for browser in browsers]


@router.post("/select-browser")
async def select_browser() -> dict[str, object]:
    controller = await BrowserControlManager().select_best()
    return {"selected_control_mode": controller.mode_name}


@router.get("/control-modes")
def control_modes() -> list[dict[str, object]]:
    return [
        {"name": "cdp", "phase": 2, "available_when": "Chromium remote debugging endpoint is running."},
        {"name": "extension", "phase": 3, "available_when": "Browser extension and native messaging host are installed."},
        {"name": "accessibility", "phase": 4, "available_when": "Windows UI Automation is available."},
        {"name": "visual", "phase": 5, "available_when": "User selects/focuses a visible browser window."},
    ]


@router.post("/test-cdp")
async def test_cdp() -> dict[str, object]:
    browsers = [browser for browser in await BrowserControlManager().detect_browsers() if browser.cdp_available]
    return {"ok": bool(browsers), "browsers": [browser.model_dump() for browser in browsers]}


@router.post("/test-extension")
def test_extension() -> dict[str, object]:
    return {"ok": False, "message": "Extension bridge is scaffolded for Phase 3."}


@router.post("/test-accessibility")
def test_accessibility() -> dict[str, object]:
    return {"ok": False, "message": "Accessibility mode is scaffolded for Phase 4."}


@router.post("/test-visual-control")
def test_visual_control() -> dict[str, object]:
    return {"ok": False, "message": "Visual fallback mode is scaffolded for Phase 5."}


@router.post("/emergency-stop")
def emergency_stop() -> dict[str, str]:
    return {"status": "stop_requested"}

