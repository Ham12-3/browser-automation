from typing import Any

from app.control.base import BrowserController


class ExtensionController(BrowserController):
    mode_name = "extension"

    async def observe(self) -> dict[str, Any]:
        return {"mode": self.mode_name, "available": False, "message": "Extension bridge scaffold is present but not connected."}

    async def navigate(self, url: str) -> dict[str, Any]:
        raise NotImplementedError("Extension bridge execution is planned for Phase 3.")

    async def click(self, target: dict[str, Any]) -> dict[str, Any]:
        raise NotImplementedError("Extension bridge execution is planned for Phase 3.")

    async def type(self, target: dict[str, Any], text: str) -> dict[str, Any]:
        raise NotImplementedError("Extension bridge execution is planned for Phase 3.")

    async def press(self, key: str) -> dict[str, Any]:
        raise NotImplementedError("Extension bridge execution is planned for Phase 3.")

    async def scroll(self, direction: str, amount: int) -> dict[str, Any]:
        raise NotImplementedError("Extension bridge execution is planned for Phase 3.")

    async def extract(self, schema: dict[str, Any]) -> dict[str, Any]:
        raise NotImplementedError("Extension bridge execution is planned for Phase 3.")

    async def screenshot(self) -> bytes:
        raise NotImplementedError("Extension bridge execution is planned for Phase 3.")

    async def wait(self, condition: dict[str, Any]) -> dict[str, Any]:
        raise NotImplementedError("Extension bridge execution is planned for Phase 3.")

    async def stop(self) -> None:
        return None

    async def resume(self) -> None:
        return None

