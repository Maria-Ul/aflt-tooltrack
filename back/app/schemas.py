from pydantic import BaseModel, Field
from typing import Optional
from .models import Role

class UserCreate(BaseModel):
    tab_number: str = Field(..., min_length=1, max_length=10)
    full_name: str = Field(..., min_length=2)
    password: str = Field(..., min_length=8)
    role: Role


class UserLogin(BaseModel):
    tab_number: str = Field(..., min_length=1, max_length=10)
    password: str = Field(..., min_length=8)


class User(BaseModel):
    id: int
    tab_number: str
    full_name: str
    role: Role
    created_at: str
    updated_at: str

    class Config:
        orm_mode = True
