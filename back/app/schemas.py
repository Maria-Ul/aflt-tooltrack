from pydantic import BaseModel
from typing import Optional
from .models import Role

class UserBase(BaseModel):
    tab_number: str
    full_name: str
    role: Role

class UserCreate(UserBase):
    password: str

class User(UserBase):
    id: int

    class Config:
        orm_mode = True
        from_attributes=True

class Token(BaseModel):
    access_token: str
    token_type: str

class UserLogin(BaseModel):
    tab_number: str
    password: str