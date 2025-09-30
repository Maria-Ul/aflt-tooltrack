from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from datetime import timedelta
from .dependencies import get_db, authenticate_user, create_access_token, get_password_hash, ACCESS_TOKEN_EXPIRE_MINUTES
from app.schemas import user_schema
from app.models import models

router = APIRouter(prefix="/auth", tags=["Авторизация"])

@router.post(
    "/register", 
    response_model=user_schema.UserWithToken,
    status_code=status.HTTP_201_CREATED,
    summary="Регистрация нового пользователя",
    description="""
    Регистрирует нового пользователя в системе.
    
    **Роли пользователей:**
    - `warehouse_employee` - Сотрудник склада
    - `aviation_engineer` - Авиационный инженер
    - `conveyor` - Конвейерный работник
    - `administrator` - Администратор
    - `quality_control_specialist` - Специалист по контролю качества
    """
)
def create_user(user: user_schema.UserCreate, db: Session = Depends(get_db)):
    """
    Регистрация нового пользователя.
    
    - **tab_number**: Табельный номер (уникальный)
    - **full_name**: ФИО сотрудника
    - **password**: Пароль (минимум 6 символов)
    - **role**: Роль в системе
    """
    # Проверяем, существует ли пользователь с таким табельным номером
    existing_user = db.query(models.User).filter(models.User.tab_number == user.tab_number).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User with this tab number already exists"
        )
    
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
    
    access_token = create_access_token(
        data={"sub": new_user.tab_number}, 
        expires_delta=timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    )
    return {
        **user_schema.User.from_orm(new_user).dict(),
        "access_token": access_token,
        "token_type": "bearer"
    }

@router.post(
    "/login",
    response_model=user_schema.UserWithToken,
    summary="Аутентификация пользователя",
    description="Аутентифицирует пользователя и возвращает JWT токен"
)
def login_for_access_token(userLogin: user_schema.UserLogin, db: Session = Depends(get_db)):
    """
    Вход в систему.
    
    - **tab_number**: Табельный номер
    - **password**: Пароль
    
    Возвращает данные пользователя и JWT токен для доступа к API.
    """
    user = authenticate_user(db, userLogin.tab_number, userLogin.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect tab number or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token = create_access_token(
        data={"sub": user.tab_number}, 
        expires_delta=timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    )
    return {
        **user_schema.User.from_orm(user).dict(),
        "access_token": access_token,
        "token_type": "bearer"
    }
