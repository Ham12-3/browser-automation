from datetime import datetime

from sqlalchemy.orm import Session

from app.models import Approval


def create_pending_approval(db: Session, task_run_id: int, message: str, action_id: int | None = None) -> Approval:
    approval = Approval(task_run_id=task_run_id, action_id=action_id, message=message)
    db.add(approval)
    db.commit()
    db.refresh(approval)
    return approval


def resolve_approval(db: Session, approval: Approval, status: str) -> Approval:
    approval.approval_status = status
    approval.resolved_at = datetime.utcnow()
    db.commit()
    db.refresh(approval)
    return approval

