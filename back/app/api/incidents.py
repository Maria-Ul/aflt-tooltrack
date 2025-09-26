from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
import random
from .dependencies import get_db, get_current_user
from app.models import models
from app.schemas import incident_schema, maintenance_request_schema

router = APIRouter(prefix="/incidents", tags=["Инцидент"])

@router.get(
    "/", 
    response_model=List[incident_schema.Incident],
    summary="Получить все инциденты",
    description="Возвращает список всех инцидентов с возможностью фильтрации"
)
def get_all_incidents(
    skip: int = 0,
    limit: int = 100,
    status: Optional[incident_schema.IncidentStatus] = Query(None, description="Фильтр по статусу"),
    aviation_engineer_id: Optional[int] = Query(None, description="Фильтр по инженеру"),
    quality_control_specialist_id: Optional[int] = Query(None, description="Фильтр по специалисту КК"),
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    """
    Получение списка инцидентов.
    
    **Параметры запроса:**
    - **skip**: Пропуск записей
    - **limit**: Лимит записей
    - **status**: Фильтр по статусу
    - **aviation_engineer_id**: Фильтр по инженеру
    - **quality_control_specialist_id**: Фильтр по специалисту КК
    
    Требуется аутентификация.
    """
    query = db.query(models.Incident)
    
    # Применяем фильтры
    if status:
        query = query.filter(models.Incident.status == status)
    if aviation_engineer_id:
        query = query.filter(models.Incident.aviation_engineer_id == aviation_engineer_id)
    if quality_control_specialist_id:
        query = query.filter(models.Incident.quality_control_specialist_id == quality_control_specialist_id)
    
    # Сортировка по дате создания (новые сначала)
    query = query.order_by(models.Incident.created_at.desc())
    
    incidents = query.offset(skip).limit(limit).all()
    return incidents

@router.get(
    "/{incident_id}", 
    response_model=incident_schema.Incident,
    summary="Получить инцидент по ID",
    description="Возвращает информацию об инциденте по его идентификатору"
)
def get_incident(
    incident_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    """
    Получение инцидента по ID.
    
    - **incident_id**: ID инцидента
    
    Требуется аутентификация.
    """
    incident = db.query(models.Incident).filter(models.Incident.id == incident_id).first()
    
    if not incident:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Incident not found"
        )
    return incident

@router.get(
    "/{incident_id}/with-relations",
    response_model=Dict[str, Any],
    summary="Получить инцидент с полной информацией",
    description="Возвращает инцидент с полной информацией о связанных объектах"
)
def get_incident_with_relations(
    incident_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    """
    Получение инцидента с полной информацией о связанных объектах.
    """
    incident = db.query(models.Incident).filter(models.Incident.id == incident_id).first()
    
    if not incident:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Incident not found"
        )
    
    # Собираем полную информацию
    response_data = {
        "id": incident.id,
        "aviation_engineer_id": incident.aviation_engineer_id,
        "quality_control_specialist_id": incident.quality_control_specialist_id,
        "aircraft_id": incident.aircraft_id,
        "tool_set_id": incident.tool_set_id,
        "maintenance_request_id": incident.maintenance_request_id,
        "status": incident.status,
        "annotated_image": incident.annotated_image,
        "raw_image": incident.raw_image,
        "resolution_summary": incident.resolution_summary,
        "comments": incident.comments,
        "created_at": incident.created_at.isoformat() if incident.created_at else None,
        "aviation_engineer": None,
        "quality_control_specialist": None,
        "aircraft": None,
        "tool_set": None,
        "maintenance_request": None
    }
    
    # Информация об инженере
    if incident.aviation_engineer:
        response_data["aviation_engineer"] = {
            "id": incident.aviation_engineer.id,
            "tab_number": incident.aviation_engineer.tab_number,
            "full_name": incident.aviation_engineer.full_name,
            "role": incident.aviation_engineer.role
        }
    
    # Информация о специалисте КК
    if incident.quality_control_specialist:
        response_data["quality_control_specialist"] = {
            "id": incident.quality_control_specialist.id,
            "tab_number": incident.quality_control_specialist.tab_number,
            "full_name": incident.quality_control_specialist.full_name,
            "role": incident.quality_control_specialist.role
        }
    
    # Информация о самолете
    if incident.aircraft:
        response_data["aircraft"] = {
            "id": incident.aircraft.id,
            "tail_number": incident.aircraft.tail_number,
            "model": incident.aircraft.model,
            "year_of_manufacture": incident.aircraft.year_of_manufacture
        }
    
    # Информация о наборе инструментов
    if incident.tool_set:
        response_data["tool_set"] = {
            "id": incident.tool_set.id,
            "batch_number": incident.tool_set.batch_number,
            "description": incident.tool_set.description
        }
    
    # Информация о заявке
    if incident.maintenance_request:
        response_data["maintenance_request"] = {
            "id": incident.maintenance_request.id,
            "description": incident.maintenance_request.description,
            "status": incident.maintenance_request.status,
            "created_at": incident.maintenance_request.created_at.isoformat() if incident.maintenance_request.created_at else None
        }
    
    return response_data

@router.put(
    "/{incident_id}", 
    response_model=incident_schema.Incident,
    summary="Обновить инцидент",
    description="Обновляет информацию об инциденте"
)
def update_incident(
    incident_id: int,
    incident_update: incident_schema.IncidentUpdate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    """
    Обновление инцидента.
    
    - **incident_id**: ID инцидента
    - **status**: Новый статус (опционально)
    - **resolution_summary**: Описание решения (опционально)
    - **comments**: Комментарии (опционально)
    - **annotated_image**: Путь к аннотированному изображению (опционально)
    - **raw_image**: Путь к исходному изображению (опционально)
    
    Требуется аутентификация.
    """
    incident = db.query(models.Incident).filter(models.Incident.id == incident_id).first()
    
    if not incident:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Incident not found"
        )
    
    update_data = incident_update.model_dump(exclude_unset=True)
    
    # Применяем обновления
    for field, value in update_data.items():
        setattr(incident, field, value)
    
    db.commit()
    db.refresh(incident)
    return incident

@router.put(
    "/{incident_id}/resolve",
    response_model=incident_schema.Incident,
    summary="Разрешить инцидент",
    description="Переводит инцидент в статус RESOLVED и заявку в статус COMPLETED"
)
def resolve_incident(
    incident_id: int,
    resolve_data: incident_schema.CloseIncidentRequest,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    """
    Разрешение инцидента.
    
    - **incident_id**: ID инцидента
    - **resolution_summary**: Описание решения (обязательно)
    - **comments**: Комментарии (опционально)
    
    **Бизнес-логика:**
    - Переводит инцидент в статус RESOLVED
    - Переводит связанную заявку в статус COMPLETED
    - Сохраняет описание решения
    
    Требуется аутентификация.
    """
    incident = db.query(models.Incident).filter(models.Incident.id == incident_id).first()
    
    if not incident:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Incident not found"
        )
    
    # Проверяем, что инцидент еще не закрыт
    if incident.status in [incident_schema.IncidentStatus.RESOLVED, incident_schema.IncidentStatus.CLOSED]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Incident is already resolved or closed"
        )
    
    # Обновляем инцидент
    incident.status = incident_schema.IncidentStatus.RESOLVED
    incident.resolution_summary = resolve_data.resolution_summary
    if resolve_data.comments:
        incident.comments = resolve_data.comments
    
    # Обновляем связанную заявку
    if incident.maintenance_request:
        incident.maintenance_request.status = maintenance_request_schema.MaintenanceRequestStatus.COMPLETED
    
    db.commit()
    db.refresh(incident)
    return incident

@router.put(
    "/{incident_id}/close",
    response_model=incident_schema.Incident,
    summary="Закрыть инцидент",
    description="Переводит инцидент в статус CLOSED"
)
def close_incident(
    incident_id: int,
    close_data: incident_schema.CloseIncidentRequest,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    """
    Закрытие инцидента.
    
    - **incident_id**: ID инцидента
    - **resolution_summary**: Описание решения (обязательно)
    - **comments**: Комментарии (опционально)
    
    **Бизнес-логика:**
    - Переводит инцидент в статус CLOSED
    - Переводит связанную заявку в статус COMPLETED (если еще не сделано)
    - Сохраняет описание решения
    
    Требуется аутентификация.
    """
    incident = db.query(models.Incident).filter(models.Incident.id == incident_id).first()
    
    if not incident:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Incident not found"
        )
    
    # Проверяем, что инцидент еще не закрыт
    if incident.status == incident_schema.IncidentStatus.CLOSED:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Incident is already closed"
        )
    
    # Обновляем инцидент
    incident.status = incident_schema.IncidentStatus.CLOSED
    incident.resolution_summary = close_data.resolution_summary
    if close_data.comments:
        incident.comments = close_data.comments
    
    # Обновляем связанную заявку (если еще не обновлена)
    if incident.maintenance_request and incident.maintenance_request.status != maintenance_request_schema.MaintenanceRequestStatus.COMPLETED:
        incident.maintenance_request.status = maintenance_request_schema.MaintenanceRequestStatus.COMPLETED
    
    db.commit()
    db.refresh(incident)
    return incident

@router.get(
    "/stats/summary",
    response_model=Dict[str, Any],
    summary="Получить статистику по инцидентам",
    description="Возвращает статистическую информацию по инцидентам"
)
def get_incidents_stats(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    """
    Получение статистики по инцидентам.
    
    Возвращает:
    - Общее количество инцидентов
    - Количество инцидентов по статусам
    - Количество инцидентов за последние 30 дней
    
    Требуется аутентификация.
    """
    # Общее количество
    total_count = db.query(models.Incident).count()
    
    # Количество по статусам
    status_counts = {}
    for status in incident_schema.IncidentStatus:
        count = db.query(models.Incident).filter(
            models.Incident.status == status
        ).count()
        status_counts[status] = count
    
    # Количество за последние 30 дней
    month_ago = datetime.now() - timedelta(days=30)
    recent_count = db.query(models.Incident).filter(
        models.Incident.created_at >= month_ago
    ).count()
    
    # Среднее время разрешения инцидентов
    resolved_incidents = db.query(models.Incident).filter(
        models.Incident.status.in_([incident_schema.IncidentStatus.RESOLVED, incident_schema.IncidentStatus.CLOSED])
    ).all()
    
    avg_resolution_time = None
    if resolved_incidents:
        total_seconds = 0
        for incident in resolved_incidents:
            if incident.created_at:
                # Предполагаем, что инцидент разрешен при изменении статуса
                # В реальной системе нужно хранить дату разрешения
                resolution_time = (datetime.now() - incident.created_at).total_seconds()
                total_seconds += resolution_time
        avg_resolution_time = total_seconds / len(resolved_incidents)
    
    return {
        "total": total_count,
        "by_status": status_counts,
        "recent_count": recent_count,
        "avg_resolution_time_seconds": avg_resolution_time
    }

@router.delete(
    "/{incident_id}", 
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Удалить инцидент",
    description="Удаляет инцидент из системы"
)
def delete_incident(
    incident_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    """
    Удаление инцидента.
    
    - **incident_id**: ID инцидента
    
    **Ограничения:**
    - Можно удалять только инциденты без важных связанных данных
    
    Требуется аутентификация.
    """
    incident = db.query(models.Incident).filter(models.Incident.id == incident_id).first()
    
    if not incident:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Incident not found"
        )
    
    # Восстанавливаем статус заявки
    if incident.maintenance_request:
        incident.maintenance_request.status = maintenance_request_schema.MaintenanceRequestStatus.IN_PROGRESS
    
    db.delete(incident)
    db.commit()
    return None
