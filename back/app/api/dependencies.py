from fastapi import Depends, HTTPException, status
from sqlalchemy.orm import Session
from jose import JWTError, jwt
from datetime import datetime, timedelta
from passlib.context import CryptContext
from fastapi.security import OAuth2PasswordBearer
import hashlib
from app.database import SessionLocal
from app.models import models
import bcrypt

SECRET_KEY = "your_secret_key_here"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60

# Настройка bcrypt
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Dependency для БД
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="api/auth/login")

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Проверка пароля с двойным хэшированием"""
    try:
        # Всегда сначала хэшируем пароль через SHA-256
        # sha256_hash = hashlib.sha256(plain_password.encode()).hexdigest()
        # Затем проверяем через bcrypt
        return bcrypt.checkpw(plain_password.encode('utf-8'), hashed_password.encode('ascii'))
    except Exception:
        return False

def get_password_hash(password: str) -> str:
    """Хэширование пароля с двойным хэшированием"""
    # Всегда сначала хэшируем пароль через SHA-256
    # sha256_hash = hashlib.sha256(password.encode()).hexdigest()
    # Затем хэшируем через bcrypt

    hashed = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
    return hashed.decode('ascii')
    # print(password[:72])
    # return pwd_context.hash(password[:72])

def create_access_token(data: dict, expires_delta: timedelta = None):
    """Создание JWT токена"""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def authenticate_user(db: Session, tab_number: str, password: str):
    """Аутентификация пользователя"""
    user = db.query(models.User).filter(models.User.tab_number == tab_number).first()
    if not user:
        return False
    if not verify_password(password, user.password):
        return False
    return user

async def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    """Получение текущего пользователя из JWT токена"""
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

async def get_current_active_user(current_user: models.User = Depends(get_current_user)):
    """Проверка что пользователь активен"""
    return current_user