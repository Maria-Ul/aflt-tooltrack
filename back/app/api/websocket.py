from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from typing import List
import asyncio

router = APIRouter()

class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)

    async def send_personal_message(self, message, websocket: WebSocket):
        await websocket.send_text(message)

manager = ConnectionManager()

@router.websocket("/ws/video")
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        while True:
            data = await websocket.receive_bytes()
            print(f"Received video chunk of size: {len(data)} bytes")
            await websocket.send_text(f"Chunk of size {len(data)} received")
    except WebSocketDisconnect:
        manager.disconnect(websocket)
        print("Client disconnected")

@router.websocket("/ws/video/stream")
async def video_stream(websocket: WebSocket):
    await websocket.accept()
    try:
        chunk_size = 1024 * 32
        with open("/app/app/video.mov", "rb") as video_file:
            while True:
                chunk = video_file.read(chunk_size)
                if not chunk:
                    break
                await websocket.send_bytes(chunk)
                await asyncio.sleep(0.03)
        await websocket.close()
    except WebSocketDisconnect:
        print("Клиент отключился")
