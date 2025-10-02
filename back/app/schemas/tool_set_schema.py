from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from enum import Enum
from datetime import datetime

class ToolClass(str, Enum):
    """Классы инструментов"""
    BOKOREZY = "BOKOREZY"
    KEY_ROZGKOVY_NAKIDNOY_3_4 = "KEY_ROZGKOVY_NAKIDNOY_3_4"
    KOLOVOROT = "KOLOVOROT"
    OTKRYVASHKA_OIL_CAN = "OTKRYVASHKA_OIL_CAN"
    OTVERTKA_MINUS = "OTVERTKA_MINUS"
    OTVERTKA_OFFSET_CROSS = "OTVERTKA_OFFSET_CROSS"
    OTVERTKA_PLUS = "OTVERTKA_PLUS"
    PASSATIGI = "PASSATIGI"
    PASSATIGI_CONTROVOCHNY = "PASSATIGI_CONTROVOCHNY"
    RAZVODNOY_KEY = "RAZVODNOY_KEY"
    SHARNITSA = "SHARNITSA"

# ToolSet схемы
class ToolTypeBase(BaseModel):
    name: str = Field(..., example="Отвертка крестовая", description="Название типа инструмента или категории")
    category_id: Optional[int] = Field(None, example=1, description="ID родительской категории")
    is_item: bool = Field(..., example=True, description="True если это конкретный инструмент, False если категория")
    tool_class: Optional[ToolClass] = Field(None, example=ToolClass.OTVERTKA_PLUS, description="Класс инструмента (только для инструментов)")

class ToolType(ToolTypeBase):
    id: int = Field(..., example=1, description="ID типа инструмента")
    
    class Config:
        orm_mode = True
        from_attributes=True

class ToolSetTypeBase(BaseModel):
    name: str = Field(..., example="Набор для ТО двигателя", description="Название типа набора инструментов")
    description: Optional[str] = Field(None, example="Полный набор для технического обслуживания двигателя", description="Описание типа набора")
    tool_type_ids: List[int] = Field(..., example=[1, 2, 3], description="Список ID типов инструментов, входящих в набор")

class ToolSetType(ToolSetTypeBase):
    id: int = Field(..., example=1, description="ID типа набора инструментов")
    tool_types: List[ToolType] = Field(default=[], description="Подробная информация о инструментах в наборе")
    
    class Config:
        orm_mode = True
        from_attributes=True

class ToolSetBase(BaseModel):
    tool_set_type_id: int = Field(..., example=1, description="ID типа набора инструментов")
    batch_number: str = Field(..., example="BATCH-001", description="Партийный номер набора")
    description: Optional[str] = Field(None, example="Набор для регулярного ТО", description="Описание набора")
    batch_map: Dict[str, str] = Field(..., example={"1": "SN-001", "2": "SN-002"}, description="Мапа партийных номеров инструментов")

class ToolSet(ToolSetBase):
    id: int = Field(..., example=1, description="ID набора инструментов")
    
    class Config:
        orm_mode = True
        from_attributes=True

# Упрощенная схема без рекурсивных ссылок
class ToolSetWithType(ToolSet):
    tool_set_type: Optional[ToolSetType] = Field(None, description="Информация о типе набора")

# Схема для валидации
class ToolSetValidation(BaseModel):
    tool_set_type_id: int
    batch_number: str
    description: Optional[str] = None
    batch_map: Dict[str, str]

class ToolSetCreate(ToolSetBase):
    pass

class ToolSetUpdate(BaseModel):
    batch_number: Optional[str] = Field(None, example="BATCH-001-UPDATED", description="Новый партийный номер")
    description: Optional[str] = Field(None, example="Обновленное описание", description="Новое описание")
    batch_map: Optional[Dict[str, str]] = Field(None, example={"1": "SN-001", "2": "SN-002", "3": "SN-003"}, description="Обновленная мапа партийных номеров")
