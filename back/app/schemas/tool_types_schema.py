from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
from enum import Enum

# ToolType схемы

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

class ToolTypeBase(BaseModel):
    name: str = Field(..., example="Отвертка крестовая", description="Название типа инструмента или категории")
    category_id: Optional[int] = Field(None, example=1, description="ID родительской категории (None для корневых элементов)")
    is_item: bool = Field(..., example=True, description="True если это конкретный инструмент, False если категория")
    tool_class: Optional[ToolClass] = Field(None, example=ToolClass.OTVERTKA_PLUS, description="Класс инструмента (только для инструментов)")

class ToolTypeCreate(ToolTypeBase):
    pass

class ToolType(ToolTypeBase):
    id: int = Field(..., example=1, description="ID типа инструмента")
    
    class Config:
        orm_mode = True
        from_attributes=True

# Схема для дерева категорий
class ToolTypeTree(BaseModel):
    id: int
    name: str
    is_item: bool
    children: List['ToolTypeTree'] = []

# Обновляем для рекурсии
ToolTypeTree.update_forward_refs()

# ToolCategory схемы (если нужно отдельное API для категорий)
class ToolCategoryBase(BaseModel):
    name: str = Field(..., example="Ручные инструменты", description="Название категории инструментов")

class ToolCategoryCreate(ToolCategoryBase):
    pass

class ToolCategory(ToolCategoryBase):
    id: int = Field(..., example=1, description="ID категории")
    tool_types: List[ToolType] = Field(default=[], description="Типы инструментов в категории")
    
    class Config:
        orm_mode = True


class ToolTypeUpdate(BaseModel):
    name: Optional[str] = Field(None, example="Отвертка крестовая улучшенная", description="Новое название", min_length=1, max_length=100)
    category_id: Optional[int] = Field(None, example=2, description="Новая родительская категория")
    is_item: Optional[bool] = Field(None, example=True, description="Изменение типа элемента")
    tool_class: Optional[ToolClass] = Field(None, example=ToolClass.OTVERTKA_PLUS, description="Новый класс инструмента")

# Остальные схемы остаются без изменений, но наследуют новое поле
class ToolTypeWithChildren(ToolType):
    children: List['ToolTypeWithChildren'] = Field(default=[], description="Дочерние элементы")
    category: Optional['ToolType'] = Field(None, description="Родительская категория")

ToolTypeWithChildren.update_forward_refs()