from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum

# MaintenanceRequest схемы
class MaintenanceRequestStatus(str, Enum):
    CREATED = "CREATED"
    IN_PROGRESS = "IN_PROGRESS"
    COMPLETED = "COMPLETED"
    INCIDENT = "INCIDENT"

class MaintenanceRequestBase(BaseModel):
    aircraft_id: int = Field(..., example=1, description="ID самолета")
    warehouse_employee_id: int = Field(..., example=1, description="ID сотрудника склада")
    description: str = Field(..., example="Плановое техническое обслуживание", description="Описание заявки")
    aviation_engineer_id: Optional[int] = Field(None, example=2, description="ID авиационного инженера (исполнителя)")
    tool_set_id: Optional[int] = Field(None, example=1, description="ID набора инструментов")

class MaintenanceRequestCreate(MaintenanceRequestBase):
    status: MaintenanceRequestStatus = Field(default=MaintenanceRequestStatus.CREATED, description="Статус заявки")

class MaintenanceRequestUpdate(BaseModel):
    status: Optional[MaintenanceRequestStatus] = Field(None, description="Новый статус заявки")
    aviation_engineer_id: Optional[int] = Field(None, description="ID назначенного инженера")
    tool_set_id: Optional[int] = Field(None, description="ID назначенного набора инструментов")
    description: Optional[str] = Field(None, description="Обновленное описание")

class MaintenanceRequest(MaintenanceRequestBase):
    id: int = Field(..., example=1, description="ID заявки на ТО")
    status: MaintenanceRequestStatus = Field(..., description="Статус заявки")
    
    class Config:
        orm_mode = True
        from_attributes=True
        

# Расширенные схемы с дополнительной информацией
class MaintenanceRequestWithRelations(MaintenanceRequest):
    aircraft: Optional['Aircraft'] = Field(None, description="Информация о самолете")
    warehouse_employee: Optional['User'] = Field(None, description="Информация о сотруднике склада")
    aviation_engineer: Optional['User'] = Field(None, description="Информация об инженере")
    tool_set: Optional['ToolSet'] = Field(None, description="Информация о наборе инструментов")

# Схема для фильтрации
class MaintenanceRequestFilter(BaseModel):
    status: Optional[MaintenanceRequestStatus] = Field(None, description="Фильтр по статусу")
    aircraft_id: Optional[int] = Field(None, description="Фильтр по самолету")
    aviation_engineer_id: Optional[int] = Field(None, description="Фильтр по инженеру")
    date_from: Optional[datetime] = Field(None, description="Фильтр по дате от")
    date_to: Optional[datetime] = Field(None, description="Фильтр по дате до")

# Схема для статистики
class MaintenanceRequestStats(BaseModel):
    total: int = Field(..., description="Общее количество заявок")
    by_status: Dict[MaintenanceRequestStatus, int] = Field(..., description="Количество заявок по статусам")
    recent_count: int = Field(..., description="Количество заявок за последние 7 дней")

# Схема для ответа при создании инцидента из заявки
class MaintenanceRequestWithIncidentInfo(MaintenanceRequest):
    incident_id: Optional[int] = Field(None, description="ID созданного инцидента")
    incident_created: bool = Field(..., description="Был ли создан инцидент")

    class Config:
        from_attributes = True