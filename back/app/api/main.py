from fastapi import APIRouter
from . import auth,files,users, websocket, aircraft, tool_types, tool_set_types, tool_sets, maintenance_requests, incidents

router = APIRouter()

# Подключаем все роутеры
router.include_router(auth.router)
router.include_router(users.router)
router.include_router(aircraft.router)
router.include_router(tool_types.router)
router.include_router(tool_set_types.router)
router.include_router(tool_sets.router)
router.include_router(maintenance_requests.router)
router.include_router(incidents.router)  # добавляем incidents роутер
router.include_router(websocket.router)
router.include_router(files.router)

# Основной эндпоинт для проверки работы API
@router.get("/")
async def root():
    return {"message": "Aviation Maintenance API is running"}