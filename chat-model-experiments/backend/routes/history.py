from fastapi import WebSocket, APIRouter
from fastapi.responses import HTMLResponse

# History gathering chat ws

router = APIRouter()

@router.websocket("/history")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    while True:
        data = await websocket.receive_text()
        await websocket.send_text(f"Message text was: {data}")