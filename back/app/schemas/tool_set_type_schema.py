from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime


# Сначала определяем базовые схемы без рекурсивных ссылок
class ToolTypeBase(BaseModel):
    name: str = Field(..., example="Отвертка крестовая", description="Название типа инструмента или категории")
    category_id: Optional[int] = Field(None, example=1, description="ID родительской категории")
    is_item: bool = Field(..., example=True, description="True если это конкретный инструмент, False если категория")

class ToolType(ToolTypeBase):
    id: int = Field(..., example=1, description="ID типа инструмента")
    
    class Config:
        orm_mode = True
        from_attributes=True

# ToolSetType схемы
class ToolSetTypeBase(BaseModel):
    name: str = Field(..., example="Набор для ТО двигателя", description="Название типа набора инструментов")
    description: Optional[str] = Field(None, example="Полный набор для технического обслуживания двигателя", description="Описание типа набора")
    tool_type_ids: List[int] = Field(..., example=[1, 2, 3], description="Список ID типов инструментов, входящих в набор")

class ToolSetTypeCreate(ToolSetTypeBase):
    pass

class ToolSetTypeUpdate(BaseModel):
    name: Optional[str] = Field(None, example="Обновленное название набора", description="Новое название")
    description: Optional[str] = Field(None, example="Обновленное описание", description="Новое описание")
    tool_type_ids: Optional[List[int]] = Field(None, example=[1, 2, 3, 4], description="Обновленный список ID типов инструментов")

class ToolSetType(ToolSetTypeBase):
    id: int = Field(..., example=1, description="ID типа набора инструментов")
    
    class Config:
        orm_mode = True
        from_attributes=True

# Упрощенная схема без рекурсивных ссылок
class ToolSetTypeWithTools(ToolSetType):
    tool_types: List[ToolType] = Field(default=[], description="Подробная информация о инструментах в наборе")

# Схема для валидации существования инструментов
class ToolSetTypeValidation(BaseModel):
    name: str
    description: Optional[str] = None
    tool_type_ids: List[int]

# Убираем рекурсивные схемы для ToolType, так как они не нужны для ToolSetType API