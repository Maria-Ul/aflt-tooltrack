from fastapi import FastAPI
from .database import database, engine
from app.models import models
from app.api.main import router as api_router
from fastapi.middleware.cors import CORSMiddleware
from fastapi import FastAPI
from app.api.main import router as api_router
from app.database import engine, Base

Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Aviation Maintenance API",
    description="""
    API системы управления техническим обслуживанием авиационной техники.
    
    ## Функциональность
    
    - **Аутентификация и авторизация**
    - **Управление самолетами** (CRUD операции)
    - **Управление пользователями**
    - **WebSocket для видео трансляции**
    - **Система заявок на техническое обслуживание**
    - **Учет инцидентов и инструментов**
    
    ## Роли пользователей
    
    1. **warehouse_employee** - Сотрудник склада
    2. **aviation_engineer** - Авиационный инженер  
    3. **conveyor** - Конвейерный работник
    4. **administrator** - Администратор системы
    5. **quality_control_specialist** - Специалист по контролю качества
    """,
    version="1.0.0",
    contact={
        "name": "Aviation Maintenance Team",
        "email": "support@aviation-maintenance.com",
    },
    license_info={
        "name": "MIT License",
        "url": "https://opensource.org/licenses/MIT",
    }
)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

models.Base.metadata.create_all(bind=engine)

# Подключаем основной роутер API
app.include_router(api_router, prefix="/api")

@app.get("/", summary="Корневой эндпоинт", description="Проверка работоспособности API")
async def root():
    return {
        "message": "Aviation Maintenance System API", 
        "version": "1.0.0",
        "docs": "/docs",
        "redoc": "/redoc"
    }

@app.get("/health", summary="Проверка здоровья системы", description="Проверяет статус работы API и базы данных")
async def health_check():
    return {"status": "healthy", "timestamp": "2024-01-01T10:00:00Z"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)