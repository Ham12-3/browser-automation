import json
from typing import Any

from sqlalchemy.orm import Session

from app.models import ExtractedResult


def save_result(db: Session, task_run_id: int, schema: dict[str, Any], data: Any) -> ExtractedResult:
    result = ExtractedResult(
        task_run_id=task_run_id,
        schema_json=json.dumps(schema, default=str),
        data_json=json.dumps(data, default=str),
    )
    db.add(result)
    db.commit()
    db.refresh(result)
    return result

