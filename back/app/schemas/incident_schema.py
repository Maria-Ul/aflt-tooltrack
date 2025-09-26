from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum

# Incident схемы
class IncidentStatus(str, Enum):
    OPEN = "OPEN"
    INVESTIGATING = "INVESTIGATING"
    RESOLVED = "RESOLVED"
    CLOSED = "CLOSED"

class IncidentBase(BaseModel):
    aviation_engineer_id: int = Field(..., description="ID авиационного инженера")
    quality_control_specialist_id: int = Field(..., description="ID специалиста по контролю качества")
    aircraft_id: int = Field(..., description="ID самолета")
    tool_set_id: int = Field(..., description="ID набора инструментов")
    annotated_image: Optional[str] = Field(None, description="Путь к аннотированному изображению")
    raw_image: Optional[str] = Field(None, description="Путь к исходному изображению")
    resolution_summary: Optional[str] = Field(None, description="Краткое описание решения")
    comments: Optional[str] = Field(None, description="Комментарии")
    maintenance_request_id: int = Field(..., description="ID заявки на ТО")

class IncidentCreate(BaseModel):
    resolution_summary: Optional[str] = Field(None, description="Краткое описание решения")
    comments: Optional[str] = Field(None, description="Комментарии")

class IncidentUpdate(BaseModel):
    status: Optional[IncidentStatus] = Field(None, description="Новый статус инцидента")
    resolution_summary: Optional[str] = Field(None, description="Обновленное описание решения")
    comments: Optional[str] = Field(None, description="Обновленные комментарии")
    annotated_image: Optional[str] = Field(None, description="Путь к аннотированному изображению")
    raw_image: Optional[str] = Field(None, description="Путь к исходному изображению")

class Incident(IncidentBase):
    id: int = Field(..., description="ID инцидента")
    status: IncidentStatus = Field(..., description="Статус инцидента")
    created_at: datetime = Field(..., description="Дата создания")
    
    class Config:
        from_attributes = True

# Расширенная схема с дополнительной информацией
class IncidentWithRelations(Incident):
    aviation_engineer: Optional['User'] = Field(None, description="Информация об инженере")
    quality_control_specialist: Optional['User'] = Field(None, description="Информация о специалисте КК")
    aircraft: Optional['Aircraft'] = Field(None, description="Информация о самолете")
    tool_set: Optional['ToolSet'] = Field(None, description="Информация о наборе инструментов")
    maintenance_request: Optional['MaintenanceRequest'] = Field(None, description="Информация о заявке")


# Схема для создания инцидента из заявки
class CreateIncidentFromRequest(BaseModel):
    comments: Optional[str] = Field(None, description="Комментарии к инциденту")

# Схема для закрытия инцидента
class CloseIncidentRequest(BaseModel):
    resolution_summary: str = Field(..., description="Описание решения инцидента")
    comments: Optional[str] = Field(None, description="Финальные комментарии")
