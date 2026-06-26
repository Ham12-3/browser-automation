from collections import defaultdict
from typing import Any

from fastapi import WebSocket


class EventHub:
    def __init__(self) -> None:
        self._connections: dict[int | str, set[WebSocket]] = defaultdict(set)

    async def connect(self, key: int | str, websocket: WebSocket) -> None:
        await websocket.accept()
        self._connections[key].add(websocket)

    def disconnect(self, key: int | str, websocket: WebSocket) -> None:
        self._connections[key].discard(websocket)

    async def publish(self, key: int | str, event: dict[str, Any]) -> None:
        dead: list[WebSocket] = []
        for websocket in list(self._connections.get(key, set())):
            try:
                await websocket.send_json(event)
            except RuntimeError:
                dead.append(websocket)
        for websocket in dead:
            self.disconnect(key, websocket)


event_hub = EventHub()

