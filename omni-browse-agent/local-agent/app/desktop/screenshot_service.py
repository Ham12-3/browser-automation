from pathlib import Path

from app.config import get_settings


def screenshot_path(filename: str) -> Path:
    path = get_settings().screenshot_dir / filename
    path.parent.mkdir(parents=True, exist_ok=True)
    return path

