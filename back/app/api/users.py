from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from .dependencies import get_db, get_current_user
from app.schemas import user_schema
from app.models import models

router = APIRouter(prefix="/users", tags=["Пользователь"])

@router.get(
    "/me", 
    response_model=user_schema.User,
    summary="Получить текущего пользователя",
    description="Возвращает информацию о текущем аутентифицированном пользователе"
)
async def read_users_me(current_user: models.User = Depends(get_current_user)):
    """
    Получение данных текущего пользователя.
    
    Требуется аутентификация. Возвращает данные пользователя из JWT токена.
    """
    return current_user

@router.get(
    "/",
    response_model=List[user_schema.User],
    summary="Получить всех пользователей",
    description="Возвращает список всех пользователей системы (только для администраторов)"
)
async def get_all_users(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    """
    Получение списка всех пользователей.
    
    
    - Возвращает полный список пользователей системы
    """
    users = db.query(models.User).all()
    return users