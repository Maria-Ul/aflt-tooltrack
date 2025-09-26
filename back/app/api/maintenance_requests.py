from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
from .dependencies import get_db, get_current_user
from app.models import models
from app.schemas import maintenance_request_schema, incident_schema

router = APIRouter(prefix="/maintenance-requests", tags=["Заявки на выполнение тех. обслуживания"])

@router.post(
    "/", 
    response_model=maintenance_request_schema.MaintenanceRequest, 
    status_code=status.HTTP_201_CREATED,
    summary="Создать заявку на техническое обслуживание",
    description="Создает новую заявку на техническое обслуживание самолета"
)
def create_maintenance_request(
    maintenance_request: maintenance_request_schema.MaintenanceRequestCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    """
    Создание заявки на техническое обслуживание.
    
    - **aircraft_id**: ID самолета (обязательно)
    - **warehouse_employee_id**: ID сотрудника склада (обязательно)
    - **description**: Описание заявки (обязательно)
    - **aviation_engineer_id**: ID инженера (опционально)
    - **tool_set_id**: ID набора инструментов (опционально)
    - **status**: Статус заявки (по умолчанию: created)
    
    **Валидация:**
    - Проверяет существование aircraft_id
    - Проверяет существование warehouse_employee_id
    - Проверяет существование aviation_engineer_id (если указан)
    - Проверяет существование tool_set_id (если указан)
    - Проверяет, что aviation_engineer имеет соответствующую роль
    """
    # Проверяем существование самолета
    aircraft = db.query(models.Aircraft).filter(
        models.Aircraft.id == maintenance_request.aircraft_id
    ).first()
    if not aircraft:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Aircraft not found"
        )
    
    # Проверяем существование сотрудника склада
    warehouse_employee = db.query(models.User).filter(
        models.User.id == maintenance_request.warehouse_employee_id
    ).first()
    if not warehouse_employee:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Warehouse employee not found"
        )
    
    # Проверяем существование инженера (если указан)
    if maintenance_request.aviation_engineer_id:
        aviation_engineer = db.query(models.User).filter(
            models.User.id == maintenance_request.aviation_engineer_id
        ).first()
        if not aviation_engineer:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Aviation engineer not found"
            )
        # Проверяем роль инженера
        if aviation_engineer.role != models.Role.AVIATION_ENGINEER:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Specified user is not an aviation engineer"
            )
    
    # Проверяем существование набора инструментов (если указан)
    if maintenance_request.tool_set_id:
        tool_set = db.query(models.ToolSet).filter(
            models.ToolSet.id == maintenance_request.tool_set_id
        ).first()
        if not tool_set:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Tool set not found"
            )
    
    db_maintenance_request = models.MaintenanceRequest(
        aircraft_id=maintenance_request.aircraft_id,
        warehouse_employee_id=maintenance_request.warehouse_employee_id,
        description=maintenance_request.description,
        status=maintenance_request.status,
        aviation_engineer_id=maintenance_request.aviation_engineer_id,
        tool_set_id=maintenance_request.tool_set_id
    )
    
    db.add(db_maintenance_request)
    db.commit()
    db.refresh(db_maintenance_request)
    return db_maintenance_request

@router.get(
    "/", 
    response_model=List[maintenance_request_schema.MaintenanceRequest],
    summary="Получить все заявки на ТО",
    description="Возвращает список всех заявок на техническое обслуживание с возможностью фильтрации"
)
def get_all_maintenance_requests(
    skip: int = 0,
    limit: int = 100,
    status: Optional[maintenance_request_schema.MaintenanceRequestStatus] = Query(None, description="Фильтр по статусу"),
    aircraft_id: Optional[int] = Query(None, description="Фильтр по самолету"),
    aviation_engineer_id: Optional[int] = Query(None, description="Фильтр по инженеру"),
    date_from: Optional[datetime] = Query(None, description="Дата от (создания заявки)"),
    date_to: Optional[datetime] = Query(None, description="Дата до (создания заявки)"),
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    """
    Получение списка заявок на техническое обслуживание.
    
    **Параметры запроса:**
    - **skip**: Пропуск записей
    - **limit**: Лимит записей
    - **status**: Фильтр по статусу
    - **aircraft_id**: Фильтр по самолету
    - **aviation_engineer_id**: Фильтр по инженеру
    - **date_from**: Фильтр по дате от
    - **date_to**: Фильтр по дате до
    
    Требуется аутентификация.
    """
    query = db.query(models.MaintenanceRequest)
    
    # Применяем фильтры
    if status:
        query = query.filter(models.MaintenanceRequest.status == status)
    if aircraft_id:
        query = query.filter(models.MaintenanceRequest.aircraft_id == aircraft_id)
    if aviation_engineer_id:
        query = query.filter(models.MaintenanceRequest.aviation_engineer_id == aviation_engineer_id)
    if date_from:
        query = query.filter(models.MaintenanceRequest.created_at >= date_from)
    if date_to:
        # Добавляем 1 день чтобы включить всю указанную дату
        date_to_end = date_to.replace(hour=23, minute=59, second=59)
        query = query.filter(models.MaintenanceRequest.created_at <= date_to_end)
    
    # Сортировка по дате создания (новые сначала)
    query = query.order_by(models.MaintenanceRequest.created_at.desc())
    
    maintenance_requests = query.offset(skip).limit(limit).all()
    return maintenance_requests

@router.get(
    "/{request_id}", 
    response_model=maintenance_request_schema.MaintenanceRequest,
    summary="Получить заявку на ТО по ID",
    description="Возвращает информацию о заявке на техническое обслуживание по ее идентификатору"
)
def get_maintenance_request(
    request_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    """
    Получение заявки на ТО по ID.
    
    - **request_id**: ID заявки на техническое обслуживание
    
    Требуется аутентификация.
    """
    maintenance_request = db.query(models.MaintenanceRequest).filter(
        models.MaintenanceRequest.id == request_id
    ).first()
    
    if not maintenance_request:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Maintenance request not found"
        )
    return maintenance_request

@router.get(
    "/{request_id}/with-relations",
    response_model=Dict[str, Any],
    summary="Получить заявку с полной информацией",
    description="Возвращает заявку на ТО с полной информацией о связанных объектах"
)
def get_maintenance_request_with_relations(
    request_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    """
    Получение заявки с полной информацией о связанных объектах.
    
    - **request_id**: ID заявки на техническое обслуживание
    
    Возвращает расширенную информацию с деталями о самолете, сотрудниках и наборе инструментов.
    
    Требуется аутентификация.
    """
    maintenance_request = db.query(models.MaintenanceRequest).filter(
        models.MaintenanceRequest.id == request_id
    ).first()
    
    if not maintenance_request:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Maintenance request not found"
        )
    
    # Собираем полную информацию
    response_data = {
        "id": maintenance_request.id,
        "aircraft_id": maintenance_request.aircraft_id,
        "warehouse_employee_id": maintenance_request.warehouse_employee_id,
        "aviation_engineer_id": maintenance_request.aviation_engineer_id,
        "tool_set_id": maintenance_request.tool_set_id,
        "description": maintenance_request.description,
        "status": maintenance_request.status,
        "created_at": maintenance_request.created_at.isoformat() if maintenance_request.created_at else None,
        "aircraft": None,
        "warehouse_employee": None,
        "aviation_engineer": None,
        "tool_set": None
    }
    
    # Информация о самолете
    if maintenance_request.aircraft:
        response_data["aircraft"] = {
            "id": maintenance_request.aircraft.id,
            "tail_number": maintenance_request.aircraft.tail_number,
            "model": maintenance_request.aircraft.model,
            "year_of_manufacture": maintenance_request.aircraft.year_of_manufacture
        }
    
    # Информация о сотруднике склада
    if maintenance_request.warehouse_employee:
        response_data["warehouse_employee"] = {
            "id": maintenance_request.warehouse_employee.id,
            "tab_number": maintenance_request.warehouse_employee.tab_number,
            "full_name": maintenance_request.warehouse_employee.full_name,
            "role": maintenance_request.warehouse_employee.role
        }
    
    # Информация об инженере (если назначен)
    if maintenance_request.aviation_engineer:
        response_data["aviation_engineer"] = {
            "id": maintenance_request.aviation_engineer.id,
            "tab_number": maintenance_request.aviation_engineer.tab_number,
            "full_name": maintenance_request.aviation_engineer.full_name,
            "role": maintenance_request.aviation_engineer.role
        }
    
    # Информация о наборе инструментов (если назначен)
    if maintenance_request.tool_set:
        response_data["tool_set"] = {
            "id": maintenance_request.tool_set.id,
            "batch_number": maintenance_request.tool_set.batch_number,
            "description": maintenance_request.tool_set.description
        }
    
    return response_data

@router.put(
    "/{request_id}", 
    response_model=maintenance_request_schema.MaintenanceRequest,
    summary="Обновить заявку на ТО",
    description="Обновляет информацию о заявке на техническое обслуживание"
)
def update_maintenance_request(
    request_id: int,
    maintenance_request_update: maintenance_request_schema.MaintenanceRequestUpdate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    """
    Обновление заявки на техническое обслуживание.
    
    - **request_id**: ID заявки на ТО
    - **status**: Новый статус заявки (опционально)
    - **aviation_engineer_id**: ID назначенного инженера (опционально)
    - **tool_set_id**: ID назначенного набора инструментов (опционально)
    - **description**: Обновленное описание (опционально)
    
    **Валидация:**
    - Проверяет существование aviation_engineer_id (если указан)
    - Проверяет существование tool_set_id (если указан)
    - Проверяет, что aviation_engineer имеет соответствующую роль
    
    Требуется аутентификация.
    """
    maintenance_request = db.query(models.MaintenanceRequest).filter(
        models.MaintenanceRequest.id == request_id
    ).first()
    
    if not maintenance_request:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Maintenance request not found"
        )
    
    update_data = maintenance_request_update.dict(exclude_unset=True)
    
    # Валидация aviation_engineer_id
    if 'aviation_engineer_id' in update_data:
        aviation_engineer_id = update_data['aviation_engineer_id']
        if aviation_engineer_id:
            aviation_engineer = db.query(models.User).filter(
                models.User.id == aviation_engineer_id
            ).first()
            if not aviation_engineer:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Aviation engineer not found"
                )
            if aviation_engineer.role != models.Role.AVIATION_ENGINEER:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Specified user is not an aviation engineer"
                )
    
    # Валидация tool_set_id
    if 'tool_set_id' in update_data:
        tool_set_id = update_data['tool_set_id']
        if tool_set_id:
            tool_set = db.query(models.ToolSet).filter(
                models.ToolSet.id == tool_set_id
            ).first()
            if not tool_set:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Tool set not found"
                )
    
    # Применяем обновления
    for field, value in update_data.items():
        setattr(maintenance_request, field, value)
    
    db.commit()
    db.refresh(maintenance_request)
    return maintenance_request

@router.put(
    "/{request_id}/assign-engineer",
    response_model=maintenance_request_schema.MaintenanceRequest,
    summary="Назначить инженера на заявку",
    description="Назначает авиационного инженера на заявку технического обслуживания"
)
def assign_engineer_to_request(
    request_id: int,
    engineer_data: maintenance_request_schema.MaintenanceRequestUpdate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    """
    Назначение инженера на заявку.
    
    - **request_id**: ID заявки на ТО
    - **aviation_engineer_id**: ID инженера для назначения
    
    Также может обновлять статус заявки на 'in_progress'.
    
    Требуется аутентификация.
    """
    return update_maintenance_request(request_id, engineer_data, db, current_user)

@router.put(
    "/{request_id}/complete",
    response_model=maintenance_request_schema.MaintenanceRequest,
    summary="Завершить заявку на ТО",
    description="Отмечает заявку на техническое обслуживание как завершенную"
)
def complete_maintenance_request(
    request_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    """
    Завершение заявки на техническое обслуживание.
    
    - **request_id**: ID заявки на ТО
    
    Устанавливает статус заявки в 'completed'.
    
    Требуется аутентификация.
    """
    maintenance_request = db.query(models.MaintenanceRequest).filter(
        models.MaintenanceRequest.id == request_id
    ).first()
    
    if not maintenance_request:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Maintenance request not found"
        )
    
    maintenance_request.status = maintenance_request_schema.MaintenanceRequestStatus.COMPLETED.value
    db.commit()
    db.refresh(maintenance_request)
    return maintenance_request

@router.get(
    "/stats/summary",
    response_model=maintenance_request_schema.MaintenanceRequestStats,
    summary="Получить статистику по заявкам",
    description="Возвращает статистическую информацию по заявкам на техническое обслуживание"
)
def get_maintenance_requests_stats(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    """
    Получение статистики по заявкам на ТО.
    
    Возвращает:
    - Общее количество заявок
    - Количество заявок по статусам
    - Количество заявок за последние 7 дней
    
    Требуется аутентификация.
    """
    # Общее количество
    total_count = db.query(models.MaintenanceRequest).count()
    
    # Количество по статусам
    status_counts = {}
    for status in maintenance_request_schema.MaintenanceRequestStatus:
        count = db.query(models.MaintenanceRequest).filter(
            models.MaintenanceRequest.status == status
        ).count()
        status_counts[status] = count
    
    # Количество за последние 7 дней
    week_ago = datetime.now() - timedelta(days=7)
    recent_count = db.query(models.MaintenanceRequest).filter(
        models.MaintenanceRequest.created_at >= week_ago
    ).count()
    
    return {
        "total": total_count,
        "by_status": status_counts,
        "recent_count": recent_count
    }

@router.delete(
    "/{request_id}", 
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Удалить заявку на ТО",
    description="Удаляет заявку на техническое обслуживание из системы"
)
def delete_maintenance_request(
    request_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    """
    Удаление заявки на техническое обслуживание.
    
    - **request_id**: ID заявки на ТО
    
    **Ограничения:**
    - Нельзя удалить заявку, если с ней связан инцидент
    
    Требуется аутентификация.
    """
    maintenance_request = db.query(models.MaintenanceRequest).filter(
        models.MaintenanceRequest.id == request_id
    ).first()
    
    if not maintenance_request:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Maintenance request not found"
        )
    
    # Проверяем, есть ли связанный инцидент
    if maintenance_request.incident:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot delete maintenance request that has an associated incident"
        )
    
    db.delete(maintenance_request)
    db.commit()
    return None

@router.put(
    "/{request_id}/mark-incident",
    response_model=maintenance_request_schema.MaintenanceRequestWithIncidentInfo,  # Новая схема ответа
    summary="Пометить заявку как инцидент",
    description="Переводит заявку в статус INCIDENT и создает связанный инцидент. Возвращает заявку с информацией об инциденте."
)
def mark_request_as_incident(
    request_id: int,
    incident_data: incident_schema.CreateIncidentFromRequest,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    """
    Пометка заявки как инцидента.
    
    Возвращает:
    - Обновленную заявку
    - ID созданного инцидента
    - Флаг создания инцидента
    """
    # Находим заявку
    maintenance_request = db.query(models.MaintenanceRequest).filter(
        models.MaintenanceRequest.id == request_id
    ).first()
    
    if not maintenance_request:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Maintenance request not found"
        )
    
    # Проверяем, что заявка еще не имеет инцидента
    if maintenance_request.incident:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Maintenance request already has an associated incident"
        )
    
    # Проверяем, что у заявки есть назначенный инженер
    if not maintenance_request.aviation_engineer_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Maintenance request must have an assigned aviation engineer"
        )
    
    # Проверяем, что у заявки есть назначенный набор инструментов
    if not maintenance_request.tool_set_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Maintenance request must have an assigned tool set"
        )
    
    # Находим случайного специалиста по контролю качества
    quality_control_specialists = db.query(models.User).filter(
        models.User.role == models.Role.QUALITY_CONTROL_SPECIALIST
    ).all()
    
    if not quality_control_specialists:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No quality control specialists found in the system"
        )
    
    # Выбираем случайного специалиста
    import random
    random_specialist = random.choice(quality_control_specialists)
    
    # Генерируем моковые пути к изображениям
    from datetime import datetime
    timestamp = int(datetime.now().timestamp())
    raw_image_path = f"/uploads/incidents/{timestamp}_raw.jpg"
    annotated_image_path = f"/uploads/incidents/{timestamp}_annotated.jpg"
    
    # Создаем инцидент
    incident = models.Incident(
        aviation_engineer_id=maintenance_request.aviation_engineer_id,
        quality_control_specialist_id=random_specialist.id,
        aircraft_id=maintenance_request.aircraft_id,
        tool_set_id=maintenance_request.tool_set_id,
        maintenance_request_id=maintenance_request.id,
        raw_image=raw_image_path,
        annotated_image=annotated_image_path,
        status=incident_schema.IncidentStatus.OPEN,
        comments=incident_data.comments
    )
    
    # Обновляем статус заявки
    maintenance_request.status = maintenance_request_schema.MaintenanceRequestStatus.INCIDENT
    
    db.add(incident)
    db.commit()
    db.refresh(maintenance_request)
    db.refresh(incident)  # Обновляем инцидент чтобы получить ID
    
    # Создаем расширенный ответ
    response_data = maintenance_request_schema.MaintenanceRequest.from_orm(maintenance_request).dict()
    response_data["incident_id"] = incident.id
    response_data["incident_created"] = True
    
    return response_data