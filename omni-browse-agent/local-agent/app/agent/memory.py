from dataclasses import dataclass, field
from typing import Any


@dataclass
class TaskMemory:
    user_goal: str
    current_url: str | None = None
    completed_steps: list[str] = field(default_factory=list)
    current_step: str | None = None
    extracted_data: list[dict[str, Any]] = field(default_factory=list)
    failed_attempts: list[str] = field(default_factory=list)
    screenshots: list[str] = field(default_factory=list)
    blocked_reasons: list[str] = field(default_factory=list)
    approvals: list[dict[str, Any]] = field(default_factory=list)
    pending_user_input: str | None = None

