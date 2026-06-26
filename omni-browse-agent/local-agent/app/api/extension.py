from fastapi import APIRouter, HTTPException

from app.config import get_settings
from app.schemas import ExtensionMessage

router = APIRouter(prefix="/extension", tags=["extension"])


@router.post("/connect")
def connect_extension(message: ExtensionMessage) -> dict[str, str]:
    _validate_extension_message(message)
    return {"status": "connected"}


@router.post("/message")
def extension_message(message: ExtensionMessage) -> dict[str, object]:
    _validate_extension_message(message)
    return {"request_id": message.request_id, "accepted": True, "message": "Extension action routing is scaffolded for Phase 3."}


@router.get("/status")
def extension_status() -> dict[str, object]:
    return {"connected": False, "phase": 3}


@router.get("/install-instructions")
def install_instructions() -> dict[str, object]:
    return {
        "chrome_edge_brave": "Load browser-extension as an unpacked extension, then install the matching native messaging manifest from local-agent/app/extension_bridge/manifests.",
        "firefox": "Use manifest.firefox.json and install the Firefox native messaging manifest.",
    }


def _validate_extension_message(message: ExtensionMessage) -> None:
    settings = get_settings()
    if settings.allowed_extension_ids and message.extension_id not in settings.allowed_extension_ids:
        raise HTTPException(status_code=403, detail="Unknown extension ID")
    if settings.allowed_origins and not any(message.origin.startswith(origin) for origin in settings.allowed_origins):
        raise HTTPException(status_code=403, detail="Unknown origin")

