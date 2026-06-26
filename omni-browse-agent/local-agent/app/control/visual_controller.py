from typing import Any

from app.control.base import BrowserController


class VisualController(BrowserController):
    mode_name = "visual"

    async def observe(self) -> dict[str, Any]:
        return {"mode": self.mode_name, "available": False, "message": "PyAutoGUI visual fallback is scaffolded for Phase 5."}

    async def navigate(self, url: str) -> dict[str, Any]:
        raise NotImplementedError("Visual fallback execution is planned for Phase 5.")

    async def click(self, target: dict[str, Any]) -> dict[str, Any]:
        raise NotImplementedError("Visual fallback execution is planned for Phase 5.")

    async def type(self, target: dict[str, Any], text: str) -> dict[str, Any]:
        raise NotImplementedError("Visual fallback execution is planned for Phase 5.")

    async def press(self, key: str) -> dict[str, Any]:
        raise NotImplementedError("Visual fallback execution is planned for Phase 5.")

    async def scroll(self, direction: str, amount: int) -> dict[str, Any]:
        raise NotImplementedError("Visual fallback execution is planned for Phase 5.")

    async def extract(self, schema: dict[str, Any]) -> dict[str, Any]:
        raise NotImplementedError("Visual fallback execution is planned for Phase 5.")

    async def screenshot(self) -> bytes:
        raise NotImplementedError("Visual fallback execution is planned for Phase 5.")

    async def wait(self, condition: dict[str, Any]) -> dict[str, Any]:
        raise NotImplementedError("Visual fallback execution is planned for Phase 5.")

    async def stop(self) -> None:
        return None

    async def resume(self) -> None:
        return None

