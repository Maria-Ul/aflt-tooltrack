from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from .dependencies import get_db, get_current_user
from app.schemas import aircraft
from app.models import models

router = APIRouter(prefix="/aircraft", tags=["aircraft"])

@router.post("/", response_model=aircraft.Aircraft, status_code=status.HTTP_201_CREATED)
def create_aircraft(
    aircraft: aircraft.AircraftCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    # Проверяем, существует ли самолет с таким бортовым номером
    existing_aircraft = db.query(models.Aircraft).filter(
        models.Aircraft.tail_number == aircraft.tail_number
    ).first()
    
    if existing_aircraft:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Aircraft with this tail number already exists"
        )
    
    db_aircraft = models.Aircraft(
        tail_number=aircraft.tail_number,
        model=aircraft.model,
        year_of_manufacture=aircraft.year_of_manufacture,
        description=aircraft.description
    )
    
    db.add(db_aircraft)
    db.commit()
    db.refresh(db_aircraft)
    return db_aircraft

@router.get("/", response_model=List[aircraft.Aircraft])
def get_all_aircrafts(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    aircrafts = db.query(models.Aircraft).offset(skip).limit(limit).all()
    return aircrafts

@router.get("/{aircraft_id}", response_model=aircraft.Aircraft)
def get_aircraft(
    aircraft_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    aircraft = db.query(models.Aircraft).filter(models.Aircraft.id == aircraft_id).first()
    if not aircraft:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Aircraft not found"
        )
    return aircraft

@router.get("/tail/{tail_number}", response_model=aircraft.Aircraft)
def get_aircraft_by_tail_number(
    tail_number: str,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    aircraft = db.query(models.Aircraft).filter(models.Aircraft.tail_number == tail_number).first()
    if not aircraft:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Aircraft not found"
        )
    return aircraft

@router.put("/{aircraft_id}", response_model=aircraft.Aircraft)
def update_aircraft(
    aircraft_id: int,
    aircraft_update: aircraft.AircraftUpdate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    aircraft = db.query(models.Aircraft).filter(models.Aircraft.id == aircraft_id).first()
    if not aircraft:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Aircraft not found"
        )
    
    # Обновляем только переданные поля
    update_data = aircraft_update.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(aircraft, field, value)
    
    db.commit()
    db.refresh(aircraft)
    return aircraft

@router.delete("/{aircraft_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_aircraft(
    aircraft_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    aircraft = db.query(models.Aircraft).filter(models.Aircraft.id == aircraft_id).first()
    if not aircraft:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Aircraft not found"
        )
    
    # Проверяем, есть ли связанные записи (опционально - для безопасности)
    maintenance_requests = db.query(models.MaintenanceRequest).filter(
        models.MaintenanceRequest.aircraft_id == aircraft_id
    ).first()
    
    incidents = db.query(models.Incident).filter(
        models.Incident.aircraft_id == aircraft_id
    ).first()
    
    if maintenance_requests or incidents:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot delete aircraft with existing maintenance requests or incidents"
        )
    
    db.delete(aircraft)
    db.commit()
    return None