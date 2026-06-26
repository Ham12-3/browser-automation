from abc import ABC, abstractmethod
from typing import Any


class BrowserController(ABC):
    mode_name: str

    @abstractmethod
    async def observe(self) -> dict[str, Any]:
        raise NotImplementedError

    @abstractmethod
    async def navigate(self, url: str) -> dict[str, Any]:
        raise NotImplementedError

    @abstractmethod
    async def click(self, target: dict[str, Any]) -> dict[str, Any]:
        raise NotImplementedError

    @abstractmethod
    async def type(self, target: dict[str, Any], text: str) -> dict[str, Any]:
        raise NotImplementedError

    @abstractmethod
    async def press(self, key: str) -> dict[str, Any]:
        raise NotImplementedError

    @abstractmethod
    async def scroll(self, direction: str, amount: int) -> dict[str, Any]:
        raise NotImplementedError

    @abstractmethod
    async def extract(self, schema: dict[str, Any]) -> dict[str, Any]:
        raise NotImplementedError

    @abstractmethod
    async def screenshot(self) -> bytes:
        raise NotImplementedError

    @abstractmethod
    async def wait(self, condition: dict[str, Any]) -> dict[str, Any]:
        raise NotImplementedError

    @abstractmethod
    async def stop(self) -> None:
        raise NotImplementedError

    @abstractmethod
    async def resume(self) -> None:
        raise NotImplementedError

