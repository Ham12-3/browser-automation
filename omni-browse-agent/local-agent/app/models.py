from datetime import datetime
from enum import StrEnum

from sqlalchemy import DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class TaskStatus(StrEnum):
    pending = "pending"
    running = "running"
    paused = "paused"
    waiting_for_human = "waiting_for_human"
    completed = "completed"
    failed = "failed"
    blocked = "blocked"
    stopped = "stopped"


def utcnow() -> datetime:
    return datetime.utcnow()


class Task(Base):
    __tablename__ = "tasks"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    title: Mapped[str] = mapped_column(String(255))
    user_prompt: Mapped[str] = mapped_column(Text)
    status: Mapped[str] = mapped_column(String(50), default=TaskStatus.pending.value, index=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=utcnow, onupdate=utcnow)

    runs: Mapped[list["TaskRun"]] = relationship(back_populates="task")


class TaskRun(Base):
    __tablename__ = "task_runs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    task_id: Mapped[int] = mapped_column(ForeignKey("tasks.id"), index=True)
    status: Mapped[str] = mapped_column(String(50), default=TaskStatus.pending.value, index=True)
    browser_name: Mapped[str | None] = mapped_column(String(100), nullable=True)
    control_mode: Mapped[str | None] = mapped_column(String(100), nullable=True)
    started_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    ended_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    blocked_reason: Mapped[str | None] = mapped_column(String(255), nullable=True)
    final_output_json: Mapped[str | None] = mapped_column(Text, nullable=True)

    task: Mapped[Task] = relationship(back_populates="runs")


class Action(Base):
    __tablename__ = "actions"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    task_run_id: Mapped[int] = mapped_column(ForeignKey("task_runs.id"), index=True)
    action_type: Mapped[str] = mapped_column(String(100), index=True)
    action_payload_json: Mapped[str] = mapped_column(Text)
    risk_level: Mapped[str] = mapped_column(String(50), default="low")
    policy_result_json: Mapped[str] = mapped_column(Text)
    status: Mapped[str] = mapped_column(String(50), default="pending")
    created_at: Mapped[datetime] = mapped_column(DateTime, default=utcnow)
    completed_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)


class ActionLog(Base):
    __tablename__ = "action_logs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    task_run_id: Mapped[int | None] = mapped_column(ForeignKey("task_runs.id"), nullable=True, index=True)
    level: Mapped[str] = mapped_column(String(20), default="info")
    message: Mapped[str] = mapped_column(Text)
    data_json: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=utcnow)


class Screenshot(Base):
    __tablename__ = "screenshots"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    task_run_id: Mapped[int] = mapped_column(ForeignKey("task_runs.id"), index=True)
    action_id: Mapped[int | None] = mapped_column(ForeignKey("actions.id"), nullable=True)
    file_path: Mapped[str] = mapped_column(Text)
    url: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=utcnow)


class Approval(Base):
    __tablename__ = "approvals"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    task_run_id: Mapped[int] = mapped_column(ForeignKey("task_runs.id"), index=True)
    action_id: Mapped[int | None] = mapped_column(ForeignKey("actions.id"), nullable=True)
    approval_status: Mapped[str] = mapped_column(String(50), default="pending")
    message: Mapped[str] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=utcnow)
    resolved_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)


class BlockedEvent(Base):
    __tablename__ = "blocked_events"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    task_run_id: Mapped[int] = mapped_column(ForeignKey("task_runs.id"), index=True)
    reason_code: Mapped[str] = mapped_column(String(100), index=True)
    message: Mapped[str] = mapped_column(Text)
    screenshot_id: Mapped[int | None] = mapped_column(ForeignKey("screenshots.id"), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=utcnow)


class ExtractedResult(Base):
    __tablename__ = "extracted_results"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    task_run_id: Mapped[int] = mapped_column(ForeignKey("task_runs.id"), index=True)
    schema_json: Mapped[str] = mapped_column(Text)
    data_json: Mapped[str] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=utcnow)


class Setting(Base):
    __tablename__ = "settings"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    key: Mapped[str] = mapped_column(String(255), unique=True, index=True)
    value_json: Mapped[str] = mapped_column(Text)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=utcnow, onupdate=utcnow)


class BrowserSession(Base):
    __tablename__ = "browser_sessions"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    browser_name: Mapped[str] = mapped_column(String(100))
    control_mode: Mapped[str] = mapped_column(String(100))
    endpoint_url: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=utcnow)


class BrowserWindow(Base):
    __tablename__ = "browser_windows"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    browser_name: Mapped[str] = mapped_column(String(100))
    process_name: Mapped[str] = mapped_column(String(100))
    window_title: Mapped[str | None] = mapped_column(Text, nullable=True)
    control_modes_json: Mapped[str] = mapped_column(Text, default="[]")
    created_at: Mapped[datetime] = mapped_column(DateTime, default=utcnow)


class ControlMode(Base):
    __tablename__ = "control_modes"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(100), unique=True)
    available: Mapped[int] = mapped_column(Integer, default=0)
    details_json: Mapped[str] = mapped_column(Text, default="{}")


class ExtensionConnection(Base):
    __tablename__ = "extension_connections"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    extension_id: Mapped[str] = mapped_column(String(255), index=True)
    browser_name: Mapped[str] = mapped_column(String(100))
    origin: Mapped[str | None] = mapped_column(Text, nullable=True)
    status: Mapped[str] = mapped_column(String(50), default="connected")
    created_at: Mapped[datetime] = mapped_column(DateTime, default=utcnow)


class SafetyEvent(Base):
    __tablename__ = "safety_events"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    task_run_id: Mapped[int | None] = mapped_column(ForeignKey("task_runs.id"), nullable=True, index=True)
    reason_code: Mapped[str] = mapped_column(String(100), index=True)
    message: Mapped[str] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=utcnow)

