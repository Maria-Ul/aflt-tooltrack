from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from .database import SessionLocal
from . import models, rabbitmq
from pydantic import BaseModel
from typing import Optional
from fastapi.responses import JSONResponse

router = APIRouter()

# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

class ItemCreate(BaseModel):
    name: str
    description: Optional[str] = None

@router.get("/api")
async def read_api():
    return JSONResponse({"message": "Hello from backend!"})

@router.post("/items/")
async def create_item(item: ItemCreate, db: Session = Depends(get_db)):
    db_item = models.Item(name=item.name, description=item.description)
    db.add(db_item)
    db.commit()
    db.refresh(db_item)
    rabbitmq.send_message(f"New item created: {item.name}")  # Отправка сообщения в RabbitMQ
    return db_item
