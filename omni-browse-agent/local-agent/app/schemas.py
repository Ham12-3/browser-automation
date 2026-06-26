from datetime import datetime
from typing import Any, Literal

from pydantic import BaseModel, Field


class TaskCreate(BaseModel):
    title: str | None = None
    user_prompt: str = Field(min_length=1)


class TaskRead(BaseModel):
    id: int
    title: str
    user_prompt: str
    status: str
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class TaskRunRead(BaseModel):
    id: int
    task_id: int
    status: str
    browser_name: str | None
    control_mode: str | None
    started_at: datetime | None
    ended_at: datetime | None
    blocked_reason: str | None
    final_output_json: str | None

    model_config = {"from_attributes": True}


class BrowserInfo(BaseModel):
    browser_name: str
    process_name: str | None = None
    window_title: str | None = None
    cdp_available: bool = False
    extension_available: bool = False
    accessibility_available: bool = False
    visual_fallback_available: bool = True
    endpoint_url: str | None = None
    tabs: list[dict[str, Any]] = Field(default_factory=list)


class ActionTarget(BaseModel):
    kind: str
    value: str


class AgentAction(BaseModel):
    type: Literal[
        "navigate",
        "click",
        "type",
        "press",
        "scroll",
        "wait",
        "extract",
        "screenshot",
        "ask_user",
        "pause",
        "stop",
        "resume",
    ]
    target: ActionTarget | None = None
    payload: dict[str, Any] = Field(default_factory=dict)
    reason: str = ""
    risk_level: Literal["low", "medium", "high", "blocked"] = "low"


class PolicyResult(BaseModel):
    allowed: bool
    requires_approval: bool = False
    reason: str
    risk_level: Literal["low", "medium", "high", "blocked"] = "low"


class ApprovalDecision(BaseModel):
    decision: Literal["approve_once", "reject", "stop_task", "edit_action", "continue_manually", "mark_blocked"]
    edited_action: AgentAction | None = None
    message: str | None = None


class ExtensionMessage(BaseModel):
    request_id: str
    tab_id: int | str | None = None
    browser_name: str
    origin: str
    extension_id: str | None = None
    action_type: str
    payload: dict[str, Any] = Field(default_factory=dict)
    timestamp: str

