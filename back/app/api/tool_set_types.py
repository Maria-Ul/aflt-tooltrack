from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional
from .dependencies import get_db, get_current_user
from app.models import models
from app.schemas import tool_set_type_schema

router = APIRouter(prefix="/tool-set-types", tags=["Тип набора инструментов"])

@router.post(
    "/", 
    response_model=tool_set_type_schema.ToolSetType, 
    status_code=status.HTTP_201_CREATED,
    summary="Создать тип набора инструментов",
    description="Создает новый тип набора инструментов с указанием входящих в него инструментов"
)
def create_tool_set_type(
    tool_set_type: tool_set_type_schema.ToolSetTypeCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    """
    Создание типа набора инструментов.
    
    - **name**: Название типа набора (уникальное)
    - **description**: Описание набора (опционально)
    - **tool_type_ids**: Список ID типов инструментов
    
    **Валидация:**
    - Проверяет существование всех указанных tool_type_ids
    - Проверяет уникальность имени
    """
    # Проверяем уникальность имени
    existing_tool_set_type = db.query(models.ToolSetType).filter(
        models.ToolSetType.name == tool_set_type.name
    ).first()
    
    if existing_tool_set_type:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Tool set type with this name already exists"
        )
    
    # Валидируем существование всех tool_type_ids
    if tool_set_type.tool_type_ids:
        existing_tool_types_count = db.query(models.ToolType).filter(
            models.ToolType.id.in_(tool_set_type.tool_type_ids)
        ).count()
        
        if existing_tool_types_count != len(tool_set_type.tool_type_ids):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="One or more tool type IDs not found"
            )
    
    db_tool_set_type = models.ToolSetType(
        name=tool_set_type.name,
        description=tool_set_type.description,
        tool_type_ids=tool_set_type.tool_type_ids
    )
    
    db.add(db_tool_set_type)
    db.commit()
    db.refresh(db_tool_set_type)
    return db_tool_set_type

@router.get(
    "/", 
    response_model=List[tool_set_type_schema.ToolSetType],
    summary="Получить все типы наборов инструментов",
    description="Возвращает список всех типов наборов инструментов"
)
def get_all_tool_set_types(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    """
    Получение списка типов наборов инструментов.
    
    **Параметры запроса:**
    - **skip**: Пропуск записей
    - **limit**: Лимит записей
    
    Требуется аутентификация.
    """
    tool_set_types = db.query(models.ToolSetType).offset(skip).limit(limit).all()
    return tool_set_types

@router.get(
    "/{tool_set_type_id}", 
    response_model=tool_set_type_schema.ToolSetType,
    summary="Получить тип набора инструментов по ID",
    description="Возвращает информацию о типе набора инструментов по его идентификатору"
)
def get_tool_set_type(
    tool_set_type_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    """
    Получение типа набора инструментов по ID.
    
    - **tool_set_type_id**: ID типа набора инструментов
    
    Требуется аутентификация.
    """
    tool_set_type = db.query(models.ToolSetType).filter(
        models.ToolSetType.id == tool_set_type_id
    ).first()
    
    if not tool_set_type:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Tool set type not found"
        )
    return tool_set_type

@router.get(
    "/{tool_set_type_id}/with-tools",
    response_model=tool_set_type_schema.ToolSetTypeWithTools,
    summary="Получить тип набора с детальной информацией об инструментах",
    description="Возвращает тип набора инструментов с полной информацией о входящих в него инструментах"
)
def get_tool_set_type_with_tools(
    tool_set_type_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    """
    Получение типа набора с детальной информацией об инструментах.
    
    - **tool_set_type_id**: ID типа набора инструментов
    
    Возвращает расширенную информацию с деталями о каждом инструменте в наборе.
    
    Требуется аутентификация.
    """
    tool_set_type = db.query(models.ToolSetType).filter(
        models.ToolSetType.id == tool_set_type_id
    ).first()
    
    if not tool_set_type:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Tool set type not found"
        )
    
    # Получаем детальную информацию об инструментах
    tool_types = []
    if tool_set_type.tool_type_ids:
        tool_types = db.query(models.ToolType).filter(
            models.ToolType.id.in_(tool_set_type.tool_type_ids)
        ).all()
    
    # Создаем расширенный ответ
    tool_set_type_data = tool_set_type_schema.ToolSetType.from_orm(tool_set_type)
    return tool_set_type_schema.ToolSetTypeWithTools(
        **tool_set_type_data.dict(),
        tool_types=tool_types
    )

@router.get(
    "/search/by-tool-type/{tool_type_id}",
    response_model=List[tool_set_type_schema.ToolSetType],
    summary="Найти наборы по типу инструмента",
    description="Возвращает список наборов инструментов, содержащих указанный тип инструмента"
)
def get_tool_set_types_by_tool_type(
    tool_type_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    """
    Поиск наборов по типу инструмента.
    
    - **tool_type_id**: ID типа инструмента для поиска
    
    Возвращает все наборы, которые содержат указанный тип инструмента.
    
    Требуется аутентификация.
    """
    # Проверяем существование типа инструмента
    tool_type = db.query(models.ToolType).filter(models.ToolType.id == tool_type_id).first()
    if not tool_type:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Tool type not found"
        )
    
    # Получаем все типы наборов
    all_tool_set_types = db.query(models.ToolSetType).all()
    
    # Фильтруем вручную те наборы, которые содержат нужный tool_type_id
    matching_tool_set_types = []
    for tool_set_type in all_tool_set_types:
        if tool_set_type.tool_type_ids and tool_type_id in tool_set_type.tool_type_ids:
            matching_tool_set_types.append(tool_set_type)
    
    return matching_tool_set_types

@router.put(
    "/{tool_set_type_id}", 
    response_model=tool_set_type_schema.ToolSetType,
    summary="Обновить тип набора инструментов",
    description="Обновляет информацию о типе набора инструментов"
)
def update_tool_set_type(
    tool_set_type_id: int,
    tool_set_type_update: tool_set_type_schema.ToolSetTypeUpdate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    """
    Обновление типа набора инструментов.
    
    - **tool_set_type_id**: ID типа набора инструментов
    - **name**: Новое название (опционально)
    - **description**: Новое описание (опционально)
    - **tool_type_ids**: Новый список ID типов инструментов (опционально)
    
    **Валидация:**
    - Проверяет существование всех указанных tool_type_ids
    - Проверяет уникальность имени при изменении
    
    Требуется аутентификация.
    """
    tool_set_type = db.query(models.ToolSetType).filter(
        models.ToolSetType.id == tool_set_type_id
    ).first()
    
    if not tool_set_type:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Tool set type not found"
        )
    
    update_data = tool_set_type_update.dict(exclude_unset=True)
    
    # Валидация уникальности имени
    if 'name' in update_data and update_data['name'] != tool_set_type.name:
        existing_tool_set_type = db.query(models.ToolSetType).filter(
            models.ToolSetType.name == update_data['name']
        ).first()
        if existing_tool_set_type:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Tool set type with this name already exists"
            )
    
    # Валидация tool_type_ids
    if 'tool_type_ids' in update_data:
        tool_type_ids = update_data['tool_type_ids']
        if tool_type_ids:
            existing_tool_types_count = db.query(models.ToolType).filter(
                models.ToolType.id.in_(tool_type_ids)
            ).count()
            
            if existing_tool_types_count != len(tool_type_ids):
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="One or more tool type IDs not found"
                )
    
    # Применяем обновления
    for field, value in update_data.items():
        setattr(tool_set_type, field, value)
    
    db.commit()
    db.refresh(tool_set_type)
    return tool_set_type

@router.delete(
    "/{tool_set_type_id}", 
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Удалить тип набора инструментов",
    description="Удаляет тип набора инструментов из системы"
)
def delete_tool_set_type(
    tool_set_type_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    """
    Удаление типа набора инструментов.
    
    - **tool_set_type_id**: ID типа набора инструментов
    
    **Ограничения:**
    - Нельзя удалить тип набора, если он используется в наборах инструментов (ToolSet)
    
    Требуется аутентификация.
    """
    tool_set_type = db.query(models.ToolSetType).filter(
        models.ToolSetType.id == tool_set_type_id
    ).first()
    
    if not tool_set_type:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Tool set type not found"
        )
    
    # Проверяем, используется ли тип набора в каких-либо наборах инструментов
    tool_sets_count = db.query(models.ToolSet).filter(
        models.ToolSet.tool_set_type_id == tool_set_type_id
    ).count()
    
    if tool_sets_count > 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot delete tool set type that is used in tool sets"
        )
    
    db.delete(tool_set_type)
    db.commit()
    return None

@router.post(
    "/validate",
    response_model=dict,
    summary="Валидировать тип набора инструментов",
    description="Проверяет корректность данных для типа набора инструментов без его создания"
)
def validate_tool_set_type(
    tool_set_type: tool_set_type_schema.ToolSetTypeValidation,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    """
    Валидация данных типа набора инструментов.
    
    Проверяет:
    - Уникальность имени
    - Существование tool_type_ids
    
    Возвращает результат проверки.
    
    Требуется аутентификация.
    """
    validation_errors = []
    
    # Проверка уникальности имени
    existing_tool_set_type = db.query(models.ToolSetType).filter(
        models.ToolSetType.name == tool_set_type.name
    ).first()
    
    if existing_tool_set_type:
        validation_errors.append("Tool set type with this name already exists")
    
    # Проверка существования tool_type_ids
    if tool_set_type.tool_type_ids:
        existing_tool_types_count = db.query(models.ToolType).filter(
            models.ToolType.id.in_(tool_set_type.tool_type_ids)
        ).count()
        
        if existing_tool_types_count != len(tool_set_type.tool_type_ids):
            validation_errors.append("One or more tool type IDs not found")
    
    is_valid = len(validation_errors) == 0
    
    return {
        "is_valid": is_valid,
        "errors": validation_errors,
        "checked_data": {
            "name": tool_set_type.name,
            "tool_type_ids_count": len(tool_set_type.tool_type_ids) if tool_set_type.tool_type_ids else 0
        }
    }


@router.get(
    "/{tool_set_type_id}/with-tools",
    response_model=tool_set_type_schema.ToolSetTypeWithTools,
    summary="Получить тип набора с детальной информацией об инструментах",
    description="Возвращает тип набора инструментов с полной информацией о входящих в него инструментах"
)
def get_tool_set_type_with_tools(
    tool_set_type_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    tool_set_type = db.query(models.ToolSetType).filter(
        models.ToolSetType.id == tool_set_type_id
    ).first()
    
    if not tool_set_type:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Tool set type not found"
        )
    
    # Получаем детальную информацию об инструментах
    tool_types = []
    if tool_set_type.tool_type_ids:
        tool_types = db.query(models.ToolType).filter(
            models.ToolType.id.in_(tool_set_type.tool_type_ids)
        ).all()
    
    # Создаем расширенный ответ
    tool_set_type_data = tool_set_type_schema.ToolSetType.from_orm(tool_set_type)
    
    # Конвертируем ToolType объекты в схемы
    tool_type_schemas = [tool_set_type_schema.ToolType.from_orm(tool_type) for tool_type in tool_types]
    
    return tool_set_type_schema.ToolSetTypeWithTools(
        **tool_set_type_data.dict(),
        tool_types=tool_type_schemas
    )

# ... остальной код без изменений ...