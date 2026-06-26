import json
from pathlib import Path

from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException
from fastapi.responses import FileResponse
from sqlalchemy import desc
from sqlalchemy.orm import Session

from app.agent.task_runner import TaskRunner
from app.database import get_db
from app.models import ActionLog, ExtractedResult, Screenshot, Task, TaskRun, TaskStatus
from app.schemas import ApprovalDecision, TaskCreate, TaskRead, TaskRunRead

router = APIRouter(prefix="/tasks", tags=["tasks"])


@router.post("", response_model=TaskRead)
def create_task(payload: TaskCreate, db: Session = Depends(get_db)) -> Task:
    title = payload.title or payload.user_prompt[:80]
    task = Task(title=title, user_prompt=payload.user_prompt, status=TaskStatus.pending.value)
    db.add(task)
    db.commit()
    db.refresh(task)
    return task


@router.get("", response_model=list[TaskRead])
def list_tasks(db: Session = Depends(get_db)) -> list[Task]:
    return list(db.query(Task).order_by(desc(Task.created_at)).all())


@router.get("/{task_id}", response_model=TaskRead)
def get_task(task_id: int, db: Session = Depends(get_db)) -> Task:
    task = db.get(Task, task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    return task


@router.post("/{task_id}/run")
def run_task(task_id: int, background_tasks: BackgroundTasks, db: Session = Depends(get_db)) -> dict[str, object]:
    task = db.get(Task, task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    task.status = TaskStatus.pending.value
    db.commit()
    background_tasks.add_task(_run_task_background, task_id)
    return {"task_id": task_id, "status": "queued"}


def _run_task_background(task_id: int) -> None:
    from app.database import SessionLocal
    import asyncio

    db = SessionLocal()
    try:
        asyncio.run(TaskRunner(db).run(task_id))
    finally:
        db.close()


@router.post("/{task_id}/stop")
def stop_task(task_id: int, db: Session = Depends(get_db)) -> dict[str, str]:
    task = db.get(Task, task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    task.status = TaskStatus.stopped.value
    latest_run = _latest_run(db, task_id)
    if latest_run:
        latest_run.status = TaskStatus.stopped.value
    db.commit()
    return {"status": "stopped"}


@router.post("/{task_id}/pause")
def pause_task(task_id: int, db: Session = Depends(get_db)) -> dict[str, str]:
    return _set_task_status(db, task_id, TaskStatus.paused.value)


@router.post("/{task_id}/resume")
def resume_task(task_id: int, db: Session = Depends(get_db)) -> dict[str, str]:
    return _set_task_status(db, task_id, TaskStatus.running.value)


@router.post("/{task_id}/approve")
def approve_task(task_id: int, decision: ApprovalDecision, db: Session = Depends(get_db)) -> dict[str, str]:
    task = db.get(Task, task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    return {"status": decision.decision}


@router.post("/{task_id}/reject")
def reject_task(task_id: int, decision: ApprovalDecision, db: Session = Depends(get_db)) -> dict[str, str]:
    task = db.get(Task, task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    task.status = TaskStatus.blocked.value
    db.commit()
    return {"status": decision.decision}


@router.get("/{task_id}/logs")
def get_logs(task_id: int, db: Session = Depends(get_db)) -> list[dict[str, object]]:
    run = _latest_run(db, task_id)
    if not run:
        return []
    logs = db.query(ActionLog).filter(ActionLog.task_run_id == run.id).order_by(ActionLog.created_at).all()
    return [
        {"id": log.id, "level": log.level, "message": log.message, "data": json.loads(log.data_json) if log.data_json else None, "created_at": log.created_at}
        for log in logs
    ]


@router.get("/{task_id}/screenshots")
def get_screenshots(task_id: int, db: Session = Depends(get_db)) -> list[dict[str, object]]:
    run = _latest_run(db, task_id)
    if not run:
        return []
    rows = db.query(Screenshot).filter(Screenshot.task_run_id == run.id).order_by(Screenshot.created_at).all()
    return [{"id": row.id, "file_path": row.file_path, "url": row.url, "created_at": row.created_at} for row in rows]


@router.get("/{task_id}/screenshots/{screenshot_id}")
def get_screenshot_file(task_id: int, screenshot_id: int, db: Session = Depends(get_db)) -> FileResponse:
    row = db.get(Screenshot, screenshot_id)
    if not row or not Path(row.file_path).exists():
        raise HTTPException(status_code=404, detail="Screenshot not found")
    return FileResponse(row.file_path, media_type="image/png")


@router.get("/{task_id}/results")
def get_results(task_id: int, db: Session = Depends(get_db)) -> list[dict[str, object]]:
    run = _latest_run(db, task_id)
    if not run:
        return []
    rows = db.query(ExtractedResult).filter(ExtractedResult.task_run_id == run.id).order_by(desc(ExtractedResult.created_at)).all()
    return [
        {
            "id": row.id,
            "schema": json.loads(row.schema_json),
            "data": json.loads(row.data_json),
            "created_at": row.created_at,
        }
        for row in rows
    ]


def _latest_run(db: Session, task_id: int) -> TaskRun | None:
    return db.query(TaskRun).filter(TaskRun.task_id == task_id).order_by(desc(TaskRun.started_at), desc(TaskRun.id)).first()


def _set_task_status(db: Session, task_id: int, status: str) -> dict[str, str]:
    task = db.get(Task, task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    task.status = status
    latest_run = _latest_run(db, task_id)
    if latest_run:
        latest_run.status = status
    db.commit()
    return {"status": status}
