from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from typing import Dict, Optional
import time
import base64
import json
from datetime import datetime

router = APIRouter(prefix="/ws", tags=["WebSocket видео потоки"])

class ConnectionManager:
    def __init__(self):
        # Хранилище клиентов и их данных
        self.active_connections: Dict[str, Dict] = {}
        self.frames_history: Dict[str, list] = {}

    async def connect(self, websocket: WebSocket, client_id: str):
        """Подключение клиента"""
        await websocket.accept()
        self.active_connections[client_id] = {
            'websocket': websocket,
            'connected_at': time.time(),
            'last_frame_time': None,
            'frame_count': 0,
            'last_frame': None
        }
        print(f'📱 Клиент подключен: {client_id}')
        
        # Отправляем подтверждение подключения
        await self.send_message(client_id, {
            'type': 'connection_established',
            'client_id': client_id,
            'timestamp': time.time()
        })

    async def disconnect(self, client_id: str):
        """Отключение клиента"""
        if client_id in self.active_connections:
            client_data = self.active_connections[client_id]
            connection_time = time.time() - client_data['connected_at']
            frame_count = client_data['frame_count']
            print(f'🔌 Клиент отключен: {client_id} | Время: {connection_time:.1f}с | Кадров: {frame_count}')
            del self.active_connections[client_id]

    async def handle_video_frame(self, client_id: str, data: dict):
        """Обработка видео кадров от клиента"""
        if client_id not in self.active_connections:
            return False
        
        try:
            client_data = self.active_connections[client_id]
            
            # Увеличиваем счетчик кадров
            client_data['frame_count'] += 1
            client_data['last_frame_time'] = time.time()
            
            # Получаем данные кадра
            frame_data = data.get('frame', '')
            if not frame_data:
                return False
            
            # Убираем префикс data:image/jpeg;base64, если есть
            if ',' in frame_data:
                frame_data = frame_data.split(',')[1]
            
            # Сохраняем последний кадр
            client_data['last_frame'] = frame_data
            
            # Добавляем в историю (ограничиваем размер)
            if client_id not in self.frames_history:
                self.frames_history[client_id] = []
            
            self.frames_history[client_id].append({
                'frame': frame_data,
                'timestamp': data.get('timestamp', time.time()),
                'size': len(base64.b64decode(frame_data))
            })
            
            # Ограничиваем историю последними 100 кадрами
            if len(self.frames_history[client_id]) > 100:
                self.frames_history[client_id].pop(0)
            
            # Логируем статистику
            fps = self.calculate_fps(client_id)
            frame_size = len(base64.b64decode(frame_data))
            print(f'📹 Кадр от {client_id[:8]}... | FPS: {fps:.1f} | Размер: {frame_size} байт')
            
            # Транслируем другим клиентам
            # await self.broadcast_frame(client_id, frame_data, data.get('timestamp'))
            
            # Отправляем подтверждение клиенту
            await self.send_message(client_id, {
                'type': 'frame_received',
                'frame_number': client_data['frame_count'],
                'fps': fps,
                'timestamp': time.time(),
                'frame': "/9j/4AAQSkZJRgABAQEAYABgAAD/2wBDAAgGBgcGBQgHBwcJCQgKDBQNDAsLDBkSEw8UHRofHh0aHBwgJC4nICIsIxwcKDcpLDAxNDQ0Hyc5PTgyPC4zNDL/2wBDAQkJCQwLDBgNDRgyIRwhMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjL/wAARCAABAAEDASIAAhEBAxEB/8QAFQABAQAAAAAAAAAAAAAAAAAAAAv/xAAUEAEAAAAAAAAAAAAAAAAAAAAA/8QAFQEBAQAAAAAAAAAAAAAAAAAAAAX/xAAUEQEAAAAAAAAAAAAAAAAAAAAA/9oADAMBAAIRAxEAPwCwAAD/2Q=="
            })
            
            return True
            
        except Exception as e:
            print(f'❌ Ошибка обработки кадра от {client_id}: {e}')
            return False

    async def broadcast_frame(self, sender_id: str, frame_data: str, timestamp: Optional[float] = None):
        """Трансляция кадра другим клиентам"""
        try:
            message = {
                'type': 'video_stream',
                'sender_id': sender_id,
                'frame': frame_data,
                'timestamp': timestamp or time.time()
            }
            
            disconnected_clients = []
            for client_id, client_data in self.active_connections.items():
                if client_id != sender_id:  # Не отправляем отправителю
                    try:
                        await client_data['websocket'].send_text(json.dumps(message))
                    except Exception:
                        disconnected_clients.append(client_id)
            
            # Удаляем отключенных клиентов
            for client_id in disconnected_clients:
                await self.disconnect(client_id)
                
        except Exception as e:
            print(f'❌ Ошибка трансляции кадра: {e}')

    async def send_message(self, client_id: str, message: dict):
        """Отправка сообщения конкретному клиенту"""
        if client_id in self.active_connections:
            try:
                await self.active_connections[client_id]['websocket'].send_text(json.dumps(message))
            except Exception as e:
                print(f'❌ Ошибка отправки сообщения клиенту {client_id}: {e}')
                await self.disconnect(client_id)

    def calculate_fps(self, client_id: str) -> float:
        """Расчет FPS для клиента"""
        client_data = self.active_connections.get(client_id)
        if not client_data or not client_data.get('last_frame_time'):
            return 0.0
        
        frame_count = client_data['frame_count']
        connection_time = time.time() - client_data['connected_at']
        
        if connection_time > 0:
            return frame_count / connection_time
        return 0.0

    def get_client_stats(self, client_id: str) -> Optional[Dict]:
        """Получение статистики клиента"""
        if client_id in self.active_connections:
            client_data = self.active_connections[client_id]
            return {
                'client_id': client_id,
                'connected_at': client_data['connected_at'],
                'frame_count': client_data['frame_count'],
                'fps': self.calculate_fps(client_id),
                'connection_time': time.time() - client_data['connected_at'],
                'last_frame_time': client_data['last_frame_time']
            }
        return None

    def get_all_stats(self) -> Dict:
        """Получение статистики всех клиентов"""
        return {
            'clients_count': len(self.active_connections),
            'total_frames': sum(client['frame_count'] for client in self.active_connections.values()),
            'clients': [
                self.get_client_stats(client_id)
                for client_id in self.active_connections.keys()
            ]
        }

    def get_last_frame(self, client_id: str) -> Optional[str]:
        """Получение последнего кадра клиента"""
        if client_id in self.active_connections:
            return self.active_connections[client_id].get('last_frame')
        return None

# Глобальный менеджер соединений
manager = ConnectionManager()

@router.websocket("/video")
async def websocket_video_endpoint(websocket: WebSocket):
    """
    WebSocket endpoint для приема и трансляции видео потоков.
    
    **Протокол сообщений:**
    
    **От клиента:**
    ```json
    {
        "type": "video_frame",
        "frame": "base64_encoded_image_data",
        "timestamp": 1234567890.123
    }
    ```
    
    **Клиенту:**
    ```json
    {
        "type": "connection_established",
        "client_id": "unique_client_id",
        "timestamp": 1234567890.123
    }
    ```
    ```json
    {
        "type": "frame_received", 
        "frame_number": 150,
        "fps": 30.5,
        "timestamp": 1234567890.123
    }
    ```
    ```json
    {
        "type": "video_stream",
        "sender_id": "client_id",
        "frame": "base64_encoded_image_data", 
        "timestamp": 1234567890.123
    }
    ```
    
    **Возможные типы сообщений:**
    - `video_frame` - кадр видео от клиента
    - `connection_established` - подтверждение подключения
    - `frame_received` - подтверждение получения кадра
    - `video_stream` - трансляция кадра другим клиентам
    """
    # Генерируем уникальный ID клиента
    client_id = f"client_{int(time.time() * 1000)}_{id(websocket)}"
    
    await manager.connect(websocket, client_id)
    
    try:
        while True:
            # Ожидаем сообщение от клиента
            data = await websocket.receive_text()
            
            try:
                message = json.loads(data)
                message_type = message.get('type')
                
                if message_type == 'video_frame':
                    # Обработка видео кадра
                    await manager.handle_video_frame(client_id, message)
                    
                elif message_type == 'ping':
                    # Ответ на ping
                    await manager.send_message(client_id, {
                        'type': 'pong',
                        'timestamp': time.time()
                    })
                    
                else:
                    print(f'⚠️ Неизвестный тип сообщения от {client_id}: {message_type}')
                    
            except json.JSONDecodeError:
                print(f'❌ Ошибка декодирования JSON от {client_id}')
            except Exception as e:
                print(f'❌ Ошибка обработки сообщения от {client_id}: {e}')
                
    except WebSocketDisconnect:
        await manager.disconnect(client_id)

# HTTP endpoints для мониторинга (опционально)
@router.get("/status")
async def get_websocket_status():
    """
    Получение статуса WebSocket сервера.
    
    Возвращает статистику по подключенным клиентам и видео потокам.
    
    **Пример ответа:**
    ```json
    {
        "clients_count": 5,
        "total_frames": 1500,
        "clients": [
            {
                "client_id": "client_1234567890_12345",
                "connected_at": 1234567890.123,
                "frame_count": 500,
                "fps": 30.5,
                "connection_time": 60.5,
                "last_frame_time": 1234567950.123
            }
        ]
    }
    ```
    """
    return manager.get_all_stats()

@router.get("/clients/{client_id}")
async def get_client_status(client_id: str):
    """
    Получение статуса конкретного клиента.
    
    **Параметры:**
    - `client_id`: ID клиента
    
    **Пример ответа:**
    ```json
    {
        "client_id": "client_1234567890_12345",
        "connected_at": 1234567890.123,
        "frame_count": 500,
        "fps": 30.5,
        "connection_time": 60.5,
        "last_frame_time": 1234567950.123
    }
    ```
    """
    stats = manager.get_client_stats(client_id)
    if stats:
        return stats
    return {"error": "Client not found"}

@router.get("/frame/{client_id}")
async def get_client_last_frame(client_id: str):
    """
    Получение последнего кадра от клиента в формате base64.
    
    **Параметры:**
    - `client_id`: ID клиента
    
    **Пример ответа:**
    ```json
    {
        "client_id": "client_1234567890_12345",
        "frame": "base64_encoded_image_data",
        "timestamp": 1234567890.123,
        "frame_size": 15432
    }
    ```
    """
    frame_data = manager.get_last_frame(client_id)
    if frame_data:
        return {
            "client_id": client_id,
            "frame": frame_data,
            "timestamp": time.time(),
            "frame_size": len(base64.b64decode(frame_data))
        }
    return {"error": "Frame not found"}
