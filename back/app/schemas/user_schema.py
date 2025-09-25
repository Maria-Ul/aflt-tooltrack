from pydantic import BaseModel, Field
from typing import Optional
from app.models.models import Role

class UserBase(BaseModel):
    tab_number: str = Field(..., example="12345", description="Табельный номер сотрудника")
    full_name: str = Field(..., example="Иванов Иван Иванович", description="ФИО сотрудника")
    role: Role = Field(..., example=Role.AVIATION_ENGINEER, description="Роль сотрудника")

class UserCreate(UserBase):
    password: str = Field(..., example="securepassword123", description="Пароль сотрудника")

class UserLogin(BaseModel):
    tab_number: str = Field(..., example="12345", description="Табельный номер сотрудника")
    password: str = Field(..., example="securepassword123", description="Пароль сотрудника")

class User(UserBase):
    id: int = Field(..., example=1, description="ID пользователя в системе")
    created_at: str = Field(..., example="2024-01-01T10:00:00Z", description="Дата создания учетной записи")
    updated_at: str = Field(..., example="2024-01-01T10:00:00Z", description="Дата последнего обновления")

    class Config:
        orm_mode = True
        from_attributes=True

class Token(BaseModel):
    access_token: str = Field(..., description="JWT токен доступа")
    token_type: str = Field(..., example="bearer", description="Тип токена")

class UserWithToken(User):
    access_token: str = Field(..., description="JWT токен доступа")
    token_type: str = Field(..., example="bearer", description="Тип токена")