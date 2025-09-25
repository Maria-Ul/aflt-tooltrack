from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime

# Aircraft схемы
class AircraftBase(BaseModel):
    tail_number: str = Field(..., example="RA-12345", description="Бортовой номер самолета")
    model: str = Field(..., example="Boeing 737-800", description="Модель самолета")
    year_of_manufacture: int = Field(..., example=2018, description="Год выпуска")
    description: Optional[str] = Field(None, example="Регулярный рейс Москва-Сочи", description="Описание самолета")

class AircraftCreate(AircraftBase):
    pass

class AircraftUpdate(BaseModel):
    model: Optional[str] = Field(None, example="Boeing 737-900", description="Модель самолета")
    year_of_manufacture: Optional[int] = Field(None, example=2019, description="Год выпуска")
    description: Optional[str] = Field(None, example="Обновленное описание", description="Описание самолета")

class Aircraft(AircraftBase):
    id: int = Field(..., example=1, description="ID самолета в системе")
    created_at: datetime = Field(..., example="2024-01-01T10:00:00Z", description="Дата создания записи")
    updated_at: datetime = Field(..., example="2024-01-01T10:00:00Z", description="Дата последнего обновления")

    class Config:
        orm_mode = True