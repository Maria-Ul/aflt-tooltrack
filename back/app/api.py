from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from .database import SessionLocal
from . import models, rabbitmq
from pydantic import BaseModel
from typing import Optional
from fastapi.responses import JSONResponse
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from jose import JWTError, jwt
from datetime import datetime, timedelta
from passlib.context import CryptContext
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from . import models, schemas
import bcrypt
from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Depends
from fastapi.responses import HTMLResponse
from typing import List
import asyncio

router = APIRouter()

# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

SECRET_KEY = "your_secret_key_here"  # Секретный ключ, храните в .env!
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60  # Время жизни токена

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password):
    return pwd_context.hash(password)

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta if expires_delta else timedelta(minutes=15))
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def authenticate_user(db: Session, tab_number: str, password: str):
    user = db.query(models.User).filter(models.User.tab_number == tab_number).first()
    if not user:
        return False
    if not verify_password(password, user.password):
        return False
    return user

@router.post("/register", status_code=status.HTTP_201_CREATED)
def create_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
    hashed_password = get_password_hash(user.password)
    new_user = models.User(
        tab_number=user.tab_number,
        full_name=user.full_name,
        password=hashed_password,
        role=user.role
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    access_token = create_access_token(data={"sub": new_user.tab_number})
    return {
        **schemas.User.from_orm(new_user).dict(),
        "access_token": access_token,
        "token_type": "bearer"
    }

@router.post("/login")
def login_for_access_token(userLogin: schemas.UserLogin, db: Session = Depends(get_db)):
    user = authenticate_user(db, userLogin.tab_number, userLogin.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect tab number or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token = create_access_token(data={"sub": user.tab_number}, expires_delta=timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
    return {
        **schemas.User.from_orm(user).dict(),
        "access_token": access_token,
        "token_type": "bearer"
    }

async def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        tab_number: str = payload.get("sub")
        if tab_number is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    user = db.query(models.User).filter(models.User.tab_number == tab_number).first()
    if user is None:
        raise credentials_exception
    return user

# Пример защищенного эндпоинта
@router.get("/users/me", response_model=schemas.User)
async def read_users_me(current_user: models.User = Depends(get_current_user)):
    return current_user


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
            data = await websocket.receive_bytes()  # Получаем бинарные данные (чанки видео)
            # Здесь можно сохранить chunk в файл, базу или передать в обработчик
            # Для примера просто печатаем размер данных
            print(f"Received video chunk of size: {len(data)} bytes")

            # Можно отправить подтверждение клиенту
            await websocket.send_text(f"Chunk of size {len(data)} received")
    except WebSocketDisconnect:
        manager.disconnect(websocket)
        print("Client disconnected")

@router.websocket("/ws/video/stream")
async def video_stream(websocket: WebSocket):
    await websocket.accept()
    try:
        # Пример: читаем видеофайл по частям и отправляем чанки клиенту
        # В реальном приложении можно стримить с камеры или из другого источника
        
        chunk_size = 1024 * 32  # 32 Кб
        with open("/app/app/video.mov", "rb") as video_file:
            while True:
                chunk = video_file.read(chunk_size)
                if not chunk:
                    break
                await websocket.send_bytes(chunk)
                await asyncio.sleep(0.03)  # небольшой таймаут для имитации реального стрима (~30 fps)

        await websocket.close()
    except WebSocketDisconnect:
        print("Клиент отключился")