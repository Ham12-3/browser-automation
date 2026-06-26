from datetime import datetime
from pathlib import Path

from sqlalchemy.orm import Session

from app.config import get_settings
from app.models import Screenshot


class ScreenshotStore:
    def __init__(self) -> None:
        self.base_dir = get_settings().screenshot_dir
        self.base_dir.mkdir(parents=True, exist_ok=True)

    def save(self, db: Session, task_run_id: int, image: bytes, *, action_id: int | None = None, url: str | None = None) -> Screenshot:
        timestamp = datetime.utcnow().strftime("%Y%m%d-%H%M%S-%f")
        path = Path(self.base_dir) / f"run-{task_run_id}" / f"{timestamp}.png"
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(image)
        screenshot = Screenshot(task_run_id=task_run_id, action_id=action_id, file_path=str(path), url=url)
        db.add(screenshot)
        db.commit()
        db.refresh(screenshot)
        return screenshot

