from fastapi import APIRouter, WebSocket, WebSocketDisconnect

from app.utils.events import event_hub

router = APIRouter(tags=["websocket"])


@router.websocket("/ws/runs/{run_id}")
async def run_events(websocket: WebSocket, run_id: int) -> None:
    await event_hub.connect(run_id, websocket)
    try:
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        event_hub.disconnect(run_id, websocket)

