from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from datetime import timedelta
from .dependencies import get_db, authenticate_user, create_access_token, get_password_hash, ACCESS_TOKEN_EXPIRE_MINUTES
from .. import schemas, models

router = APIRouter(tags=["authentication"])

@router.post("/register", status_code=status.HTTP_201_CREATED)
def create_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
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
    access_token = create_access_token(
        data={"sub": user.tab_number}, 
        expires_delta=timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    )
    return {
        **schemas.User.from_orm(user).dict(),
        "access_token": access_token,
        "token_type": "bearer"
    }