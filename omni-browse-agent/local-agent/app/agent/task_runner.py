import json
import re
from datetime import datetime
from typing import Any

from sqlalchemy.orm import Session

from app.agent.memory import TaskMemory
from app.control.manager import BrowserControlManager
from app.models import Action, BlockedEvent, Task, TaskRun, TaskStatus
from app.safety.captcha_detector import CaptchaDetector
from app.safety.policy_checker import PolicyChecker
from app.schemas import AgentAction
from app.storage.result_store import save_result
from app.storage.screenshot_store import ScreenshotStore
from app.utils.events import event_hub
from app.utils.logger import log_event


class TaskRunner:
    def __init__(self, db: Session) -> None:
        self.db = db
        self.manager = BrowserControlManager()
        self.policy = PolicyChecker()
        self.captcha_detector = CaptchaDetector()
        self.screenshots = ScreenshotStore()

    async def run(self, task_id: int) -> None:
        task = self.db.get(Task, task_id)
        if not task:
            return
        run = TaskRun(task_id=task.id, status=TaskStatus.running.value, started_at=datetime.utcnow())
        task.status = TaskStatus.running.value
        self.db.add(run)
        self.db.commit()
        self.db.refresh(run)
        await self._publish(run.id, "run_started", {"task_id": task.id})

        try:
            controller = await self.manager.select_best()
            run.control_mode = controller.mode_name
            run.browser_name = self.manager.selected_browser.browser_name if self.manager.selected_browser else None
            self.db.commit()
            log_event(self.db, f"Selected {run.control_mode} control mode.", task_run_id=run.id)

            if self._is_hacker_news_task(task.user_prompt):
                await self._run_hacker_news_demo(task, run)
            else:
                await self._run_simple_web_extraction(task, run)

            task.status = TaskStatus.completed.value
            run.status = TaskStatus.completed.value
            run.ended_at = datetime.utcnow()
            self.db.commit()
            await self._publish(run.id, "run_completed", {})
        except Exception as exc:
            if run.status in {TaskStatus.blocked.value, TaskStatus.waiting_for_human.value, TaskStatus.stopped.value}:
                task.status = run.status
            else:
                task.status = TaskStatus.failed.value
                run.status = TaskStatus.failed.value
            run.ended_at = datetime.utcnow()
            run.blocked_reason = run.blocked_reason or str(exc)
            self.db.commit()
            log_event(self.db, f"Task failed: {exc}", task_run_id=run.id, level="error")
            await self._publish(run.id, "run_failed", {"error": str(exc)})

    async def _run_hacker_news_demo(self, task: Task, run: TaskRun) -> None:
        memory = TaskMemory(user_goal=task.user_prompt)

        await self._execute_action(
            run,
            AgentAction(
                type="navigate",
                payload={"url": "https://news.ycombinator.com/"},
                reason="Open Hacker News to extract the top stories.",
                risk_level="low",
            ),
        )

        observation = await self.manager.observe()
        memory.current_url = observation.get("url")
        await self._guard_captcha(run, observation)

        image = await self.manager.screenshot()
        screenshot = self.screenshots.save(self.db, run.id, image, url=memory.current_url)
        memory.screenshots.append(screenshot.file_path)
        await self._publish(run.id, "screenshot", {"path": screenshot.file_path})

        await self._execute_action(
            run,
            AgentAction(
                type="extract",
                payload={"schema": {"name": "hacker_news_top", "limit": 10}},
                reason="Extract top 10 Hacker News story titles and links.",
                risk_level="low",
            ),
        )
        extracted = await self.manager.extract({"name": "hacker_news_top", "limit": 10})
        data = extracted["data"]
        memory.extracted_data = data
        result = save_result(self.db, run.id, {"name": "hacker_news_top", "limit": 10}, data)
        run.final_output_json = result.data_json
        self.db.commit()
        log_event(self.db, "Extracted Hacker News top stories.", task_run_id=run.id, data={"count": len(data)})
        await self._publish(run.id, "result", {"data": data})

    async def _run_observe_only(self, task: Task, run: TaskRun) -> None:
        observation = await self.manager.observe()
        await self._guard_captcha(run, observation)
        log_event(self.db, "Observed current browser tab. Generic planner loop is scaffolded for Phase 6.", task_run_id=run.id)
        run.final_output_json = json.dumps({"observation": observation}, default=str)
        self.db.commit()

    async def _run_simple_web_extraction(self, task: Task, run: TaskRun) -> None:
        url = self._extract_url(task.user_prompt)
        if not url:
            await self._run_observe_only(task, run)
            return

        await self._execute_action(
            run,
            AgentAction(
                type="navigate",
                payload={"url": url},
                reason=f"Open {url} for the requested extraction.",
                risk_level="low",
            ),
        )

        observation = await self.manager.observe()
        await self._guard_captcha(run, observation)
        image = await self.manager.screenshot()
        screenshot = self.screenshots.save(self.db, run.id, image, url=observation.get("url"))
        await self._publish(run.id, "screenshot", {"path": screenshot.file_path})

        extracted = await self.manager.extract({"name": "links", "limit": 10})
        data = extracted["data"][:10]
        result = save_result(self.db, run.id, {"name": "links", "limit": 10}, data)
        run.final_output_json = result.data_json
        self.db.commit()
        log_event(self.db, "Extracted visible links from requested page.", task_run_id=run.id, data={"count": len(data)})
        await self._publish(run.id, "result", {"data": data})

    async def _execute_action(self, run: TaskRun, action: AgentAction) -> Action:
        observation_url = None
        try:
            observation_url = (await self.manager.observe()).get("url")
        except Exception:
            pass
        policy = self.policy.check(action, current_url=observation_url)
        db_action = Action(
            task_run_id=run.id,
            action_type=action.type,
            action_payload_json=action.model_dump_json(),
            risk_level=policy.risk_level,
            policy_result_json=policy.model_dump_json(),
            status="blocked" if not policy.allowed else "approved" if not policy.requires_approval else "pending_approval",
        )
        self.db.add(db_action)
        self.db.commit()
        self.db.refresh(db_action)
        log_event(self.db, f"Policy checked action {action.type}: {policy.reason}", task_run_id=run.id)
        await self._publish(run.id, "action_policy_checked", {"action": action.model_dump(), "policy": policy.model_dump()})

        if not policy.allowed:
            await self._block(run, "POLICY_BLOCKED", policy.reason)
            raise RuntimeError(policy.reason)
        if policy.requires_approval:
            await self._block(run, "APPROVAL_REQUIRED", policy.reason)
            raise RuntimeError(policy.reason)

        if action.type == "navigate":
            await self.manager.navigate(str(action.payload["url"]))
        elif action.type == "click" and action.target:
            await self.manager.click(action.target.model_dump())
        elif action.type == "type" and action.target:
            await self.manager.type(action.target.model_dump(), str(action.payload.get("text", "")))
        elif action.type == "press":
            await self.manager.press(str(action.payload.get("key", "")))
        elif action.type == "scroll":
            await self.manager.scroll(str(action.payload.get("direction", "down")), int(action.payload.get("amount", 600)))
        elif action.type == "wait":
            await self.manager.wait(action.payload)
        elif action.type == "screenshot":
            image = await self.manager.screenshot()
            self.screenshots.save(self.db, run.id, image, action_id=db_action.id, url=observation_url)
        elif action.type == "extract":
            pass

        db_action.status = "completed"
        db_action.completed_at = datetime.utcnow()
        self.db.commit()
        return db_action

    async def _guard_captcha(self, run: TaskRun, observation: dict[str, Any]) -> None:
        detected = self.captcha_detector.detect(observation)
        if not detected.detected:
            return
        screenshot_id = None
        try:
            image = await self.manager.screenshot()
            screenshot = self.screenshots.save(self.db, run.id, image, url=observation.get("url"))
            screenshot_id = screenshot.id
        except Exception:
            pass
        await self._block(run, "CAPTCHA_BLOCKED", "CAPTCHA detected. Please complete it manually.", screenshot_id=screenshot_id)
        raise RuntimeError("CAPTCHA_BLOCKED")

    async def _block(self, run: TaskRun, reason_code: str, message: str, screenshot_id: int | None = None) -> None:
        run.status = TaskStatus.waiting_for_human.value if reason_code == "CAPTCHA_BLOCKED" else TaskStatus.blocked.value
        run.blocked_reason = reason_code
        blocked = BlockedEvent(task_run_id=run.id, reason_code=reason_code, message=message, screenshot_id=screenshot_id)
        self.db.add(blocked)
        self.db.commit()
        log_event(self.db, message, task_run_id=run.id, level="warning", data={"reason_code": reason_code})
        await self._publish(run.id, "blocked", {"reason_code": reason_code, "message": message})

    async def _publish(self, run_id: int, event_type: str, payload: dict[str, Any]) -> None:
        await event_hub.publish(run_id, {"type": event_type, "payload": payload, "timestamp": datetime.utcnow().isoformat()})

    def _is_hacker_news_task(self, prompt: str) -> bool:
        lower = prompt.lower()
        return "hacker news" in lower or "news.ycombinator.com" in lower or re.search(r"\bhn\b", lower) is not None

    def _extract_url(self, prompt: str) -> str | None:
        match = re.search(r"https?://[^\s,]+", prompt, flags=re.IGNORECASE)
        if match:
            return match.group(0).rstrip(".")
        domain = re.search(r"\b([a-z0-9-]+(?:\.[a-z0-9-]+)+)(?:/[^\s,]*)?", prompt, flags=re.IGNORECASE)
        if domain:
            return f"https://{domain.group(0).rstrip('.')}"
        return None
