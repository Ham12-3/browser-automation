import json
from typing import Any

from sqlalchemy.orm import Session

from app.models import ActionLog


def log_event(db: Session, message: str, *, task_run_id: int | None = None, level: str = "info", data: Any = None) -> ActionLog:
    entry = ActionLog(
        task_run_id=task_run_id,
        level=level,
        message=message,
        data_json=json.dumps(data, default=str) if data is not None else None,
    )
    db.add(entry)
    db.commit()
    db.refresh(entry)
    return entry

