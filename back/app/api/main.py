from fastapi import APIRouter
from . import auth, users, websocket

router = APIRouter()

# Подключаем все роутеры
router.include_router(auth.router)
router.include_router(users.router)
router.include_router(websocket.router)

# Основной эндпоинт для проверки работы API
@router.get("/")
async def root():
    return {"message": "Aviation Maintenance API is running"}
