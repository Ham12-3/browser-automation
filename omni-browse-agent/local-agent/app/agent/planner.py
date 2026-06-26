import json
from typing import Any

import httpx

from app.agent.prompts import PLANNER_SYSTEM_PROMPT
from app.config import Settings, get_settings
from app.schemas import AgentAction


class OllamaPlanner:
    def __init__(self, settings: Settings | None = None) -> None:
        self.settings = settings or get_settings()

    async def next_action(self, user_task: str, observation: dict[str, Any], memory: dict[str, Any] | None = None) -> AgentAction:
        payload = {
            "model": self.settings.ollama_model,
            "stream": False,
            "format": "json",
            "messages": [
                {"role": "system", "content": PLANNER_SYSTEM_PROMPT},
                {
                    "role": "user",
                    "content": json.dumps(
                        {
                            "task": user_task,
                            "observation": _compact_observation(observation),
                            "memory": memory or {},
                        },
                        default=str,
                    ),
                },
            ],
        }
        async with httpx.AsyncClient(timeout=45) as client:
            response = await client.post(f"{self.settings.ollama_base_url}/api/chat", json=payload)
            response.raise_for_status()
            content = response.json()["message"]["content"]
        return AgentAction.model_validate_json(content)


def _compact_observation(observation: dict[str, Any]) -> dict[str, Any]:
    compact = dict(observation)
    if isinstance(compact.get("visible_text"), str):
        compact["visible_text"] = compact["visible_text"][:4000]
    for key in ("links", "buttons", "inputs", "headings"):
        if isinstance(compact.get(key), list):
            compact[key] = compact[key][:30]
    return compact

