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

@router.websocket(
    "/ws/video",
    # summary="WebSocket для передачи видео",
    # description="WebSocket endpoint для передачи видео чанков в реальном времени"
)
async def websocket_endpoint(websocket: WebSocket):
    """
    WebSocket для передачи видео.
    
    Принимает бинарные данные (чанки видео) и отправляет подтверждения.
    Используется для загрузки видео с камеры или устройств.
    """
    await manager.connect(websocket)
    try:
        while True:
            data = await websocket.receive_bytes()
            print(f"Received video chunk of size: {len(data)} bytes")
            await websocket.send_text(f"Chunk of size {len(data)} received")
    except WebSocketDisconnect:
        manager.disconnect(websocket)
        print("Client disconnected")

@router.websocket(
    "/ws/video/stream",
    # summary="WebSocket для стриминга видео",
    # description="WebSocket endpoint для потоковой передачи видео клиенту"
)
async def video_stream(websocket: WebSocket):
    """
    WebSocket для стриминга видео.
    
    Передает видеофайл клиенту чанками в реальном времени.
    В реальной системе может использоваться для трансляции с камер.
    """
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