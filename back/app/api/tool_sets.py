from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional, Dict
from .dependencies import get_db, get_current_user
from app.models import models
from app.schemas import tool_set_schema, tool_set_type_schema

router = APIRouter(prefix="/tool-sets", tags=["Набор инструментов"])

@router.post(
    "/", 
    response_model=tool_set_schema.ToolSet, 
    status_code=status.HTTP_201_CREATED,
    summary="Создать набор инструментов",
    description="Создает новый набор инструментов с указанием типа набора и партийных номеров"
)
def create_tool_set(
    tool_set: tool_set_schema.ToolSetCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    """
    Создание набора инструментов.
    
    - **tool_set_type_id**: ID типа набора инструментов
    - **batch_number**: Партийный номер набора (уникальный)
    - **description**: Описание набора (опционально)
    - **batch_map**: Мапа партийных номеров инструментов
    
    **Валидация:**
    - Проверяет существование tool_set_type_id
    - Проверяет уникальность batch_number
    - Проверяет, что batch_map соответствует tool_type_ids из типа набора
    """
    # Проверяем существование типа набора
    tool_set_type = db.query(models.ToolSetType).filter(
        models.ToolSetType.id == tool_set.tool_set_type_id
    ).first()
    
    if not tool_set_type:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Tool set type not found"
        )
    
    # Проверяем уникальность партийного номера
    existing_tool_set = db.query(models.ToolSet).filter(
        models.ToolSet.batch_number == tool_set.batch_number
    ).first()
    
    if existing_tool_set:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Tool set with this batch number already exists"
        )
    
    # Валидация batch_map
    if tool_set_type.tool_type_ids:
        # Проверяем, что все ключи в batch_map существуют в tool_type_ids
        for tool_type_id in tool_set.batch_map.keys():
            if int(tool_type_id) not in tool_set_type.tool_type_ids:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Tool type ID {tool_type_id} is not part of the selected tool set type"
                )
    
    db_tool_set = models.ToolSet(
        tool_set_type_id=tool_set.tool_set_type_id,
        batch_number=tool_set.batch_number,
        description=tool_set.description,
        batch_map=tool_set.batch_map or {}
    )
    
    db.add(db_tool_set)
    db.commit()
    db.refresh(db_tool_set)
    return db_tool_set

@router.get(
    "/", 
    response_model=List[tool_set_schema.ToolSet],
    summary="Получить все наборы инструментов",
    description="Возвращает список всех наборов инструментов"
)
def get_all_tool_sets(
    skip: int = 0,
    limit: int = 100,
    tool_set_type_id: Optional[int] = None,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    """
    Получение списка наборов инструментов.
    
    **Параметры запроса:**
    - **skip**: Пропуск записей
    - **limit**: Лимит записей
    - **tool_set_type_id**: Фильтр по типу набора
    
    Требуется аутентификация.
    """
    query = db.query(models.ToolSet)
    
    if tool_set_type_id is not None:
        query = query.filter(models.ToolSet.tool_set_type_id == tool_set_type_id)
    
    tool_sets = query.offset(skip).limit(limit).all()
    return tool_sets

@router.get(
    "/{tool_set_id}", 
    response_model=tool_set_schema.ToolSet,
    summary="Получить набор инструментов по ID",
    description="Возвращает информацию о наборе инструментов по его идентификатору"
)
def get_tool_set(
    tool_set_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    """
    Получение набора инструментов по ID.
    
    - **tool_set_id**: ID набора инструментов
    
    Требуется аутентификация.
    """
    tool_set = db.query(models.ToolSet).filter(models.ToolSet.id == tool_set_id).first()
    
    if not tool_set:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Tool set not found"
        )
    return tool_set

@router.get(
    "/batch/{batch_number}",
    response_model=tool_set_schema.ToolSet,
    summary="Получить набор инструментов по партийному номеру",
    description="Возвращает информацию о наборе инструментов по партийному номеру"
)
def get_tool_set_by_batch_number(
    batch_number: str,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    """
    Получение набора инструментов по партийному номеру.
    
    - **batch_number**: Партийный номер набора
    
    Требуется аутентификация.
    """
    tool_set = db.query(models.ToolSet).filter(
        models.ToolSet.batch_number == batch_number
    ).first()
    
    if not tool_set:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Tool set not found"
        )
    return tool_set

@router.get(
    "/{tool_set_id}/with-type",
    response_model=tool_set_schema.ToolSetWithType,
    summary="Получить набор с детальной информацией о типе",
    description="Возвращает набор инструментов с полной информацией о его типе"
)

def get_tool_set_with_type(
    tool_set_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    """
    Получение набора с детальной информацией о типе.
    """
    tool_set = db.query(models.ToolSet).filter(models.ToolSet.id == tool_set_id).first()
    
    if not tool_set:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Tool set not found"
        )
    
    # Создаем расширенный ответ
    tool_set_data = tool_set_schema.ToolSet.from_orm(tool_set)
    
    # Получаем информацию о типе набора
    tool_set_type_data = None
    if tool_set.tool_set_type:
        tool_set_type_data = tool_set_schema.ToolSetType.from_orm(tool_set.tool_set_type)
    
    # Создаем ответ вручную, чтобы избежать проблем с рекурсивными схемами
    response_data = tool_set_data.dict()
    response_data["tool_set_type"] = tool_set_type_data.dict() if tool_set_type_data else None
    
    return response_data

@router.put(
    "/{tool_set_id}", 
    response_model=tool_set_schema.ToolSet,
    summary="Обновить набор инструментов",
    description="Обновляет информацию о наборе инструментов"
)
def update_tool_set(
    tool_set_id: int,
    tool_set_update: tool_set_schema.ToolSetUpdate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    """
    Обновление набора инструментов.
    
    - **tool_set_id**: ID набора инструментов
    - **batch_number**: Новый партийный номер (опционально)
    - **description**: Новое описание (опционально)
    - **batch_map**: Новая мапа партийных номеров (опционально)
    
    **Валидация:**
    - Проверяет уникальность batch_number при изменении
    - Проверяет соответствие batch_map tool_type_ids типа набора
    
    Требуется аутентификация.
    """
    tool_set = db.query(models.ToolSet).filter(models.ToolSet.id == tool_set_id).first()
    
    if not tool_set:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Tool set not found"
        )
    
    update_data = tool_set_update.dict(exclude_unset=True)
    
    # Валидация уникальности batch_number
    if 'batch_number' in update_data and update_data['batch_number'] != tool_set.batch_number:
        existing_tool_set = db.query(models.ToolSet).filter(
            models.ToolSet.batch_number == update_data['batch_number']
        ).first()
        if existing_tool_set:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Tool set with this batch number already exists"
            )
    
    # Валидация batch_map
    if 'batch_map' in update_data:
        tool_set_type = tool_set.tool_set_type
        if tool_set_type and tool_set_type.tool_type_ids:
            # Проверяем, что все ключи в batch_map существуют в tool_type_ids
            for tool_type_id in update_data['batch_map'].keys():
                if int(tool_type_id) not in tool_set_type.tool_type_ids:
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail=f"Tool type ID {tool_type_id} is not part of the tool set type"
                    )
    
    # Применяем обновления
    for field, value in update_data.items():
        setattr(tool_set, field, value)
    
    db.commit()
    db.refresh(tool_set)
    return tool_set

@router.delete(
    "/{tool_set_id}", 
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Удалить набор инструментов",
    description="Удаляет набор инструментов из системы"
)
def delete_tool_set(
    tool_set_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    """
    Удаление набора инструментов.
    
    - **tool_set_id**: ID набора инструментов
    
    **Ограничения:**
    - Нельзя удалить набор, если он используется в заявках на ТО или инцидентах
    
    Требуется аутентификация.
    """
    tool_set = db.query(models.ToolSet).filter(models.ToolSet.id == tool_set_id).first()
    
    if not tool_set:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Tool set not found"
        )
    
    # Проверяем использование в maintenance requests
    maintenance_requests_count = db.query(models.MaintenanceRequest).filter(
        models.MaintenanceRequest.tool_set_id == tool_set_id
    ).count()
    
    # Проверяем использование в incidents
    incidents_count = db.query(models.Incident).filter(
        models.Incident.tool_set_id == tool_set_id
    ).count()
    
    if maintenance_requests_count > 0 or incidents_count > 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot delete tool set that is used in maintenance requests or incidents"
        )
    
    db.delete(tool_set)
    db.commit()
    return None

@router.post(
    "/validate",
    response_model=dict,
    summary="Валидировать набор инструментов",
    description="Проверяет корректность данных для набора инструментов без его создания"
)
def validate_tool_set(
    tool_set: tool_set_schema.ToolSetValidation,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    """
    Валидация данных набора инструментов.
    
    Проверяет:
    - Существование tool_set_type_id
    - Уникальность batch_number
    - Соответствие batch_map tool_type_ids типа набора
    
    Возвращает результат проверки.
    
    Требуется аутентификация.
    """
    validation_errors = []
    
    # Проверка существования типа набора
    tool_set_type = db.query(models.ToolSetType).filter(
        models.ToolSetType.id == tool_set.tool_set_type_id
    ).first()
    
    if not tool_set_type:
        validation_errors.append("Tool set type not found")
    else:
        # Проверка соответствия batch_map
        if tool_set_type.tool_type_ids and tool_set.batch_map:
            for tool_type_id in tool_set.batch_map.keys():
                if int(tool_type_id) not in tool_set_type.tool_type_ids:
                    validation_errors.append(f"Tool type ID {tool_type_id} is not part of the selected tool set type")
    
    # Проверка уникальности batch_number
    existing_tool_set = db.query(models.ToolSet).filter(
        models.ToolSet.batch_number == tool_set.batch_number
    ).first()
    
    if existing_tool_set:
        validation_errors.append("Tool set with this batch number already exists")
    
    is_valid = len(validation_errors) == 0
    
    return {
        "is_valid": is_valid,
        "errors": validation_errors,
        "checked_data": {
            "tool_set_type_id": tool_set.tool_set_type_id,
            "batch_number": tool_set.batch_number,
            "batch_map_keys_count": len(tool_set.batch_map) if tool_set.batch_map else 0
        }
    }
