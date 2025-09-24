from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from .database import SessionLocal
from . import models, rabbitmq
from pydantic import BaseModel
from typing import Optional
from fastapi.responses import JSONResponse
from .schemas import UserCreate, UserLogin, User  #Создайте схемы для валидации
import bcrypt

router = APIRouter()

# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.get("/api")
async def read_api():
    return JSONResponse({"message": "Hello from backend!"})

@router.post("/register", response_model=User, status_code=status.HTTP_201_CREATED)
def create_user(user: UserCreate, db: Session = Depends(get_db)):
    hashed_password = bcrypt.hashpw(user.password.encode('utf-8'), bcrypt.gensalt())
    new_user = models.User(tab_number=user.tab_number, full_name=user.full_name, password=hashed_password.decode(), role=user.role)
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user


@router.post("/login", response_model=User)
def login_user(user: UserLogin, db: Session = Depends(get_db)):
    db_user = db.query(models.User).filter(models.User.tab_number == user.tab_number).first()
    if not db_user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"User with tab number {user.tab_number} not found")
    if not bcrypt.checkpw(user.password.encode('utf-8'), db_user.password.encode('utf-8')):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Incorrect password")
    return db_user
