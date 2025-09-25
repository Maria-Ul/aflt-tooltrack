from ..models import models
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from .dependencies import get_db, get_current_user
from app.schemas import user

router = APIRouter(prefix="/users", tags=["users"])

@router.get("/me", response_model=user.User)
async def read_users_me(current_user: models.User = Depends(get_current_user)):
    return current_user

# Дополнительные эндпоинты для пользователей можно добавить здесь
@router.get("/")
async def get_all_users(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    # Проверка прав доступа (только администратор может видеть всех пользователей)
    if current_user.role != models.Role.ADMINISTRATOR:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    
    users = db.query(models.User).all()
    return users