from sqlalchemy import Column, Integer, String, ForeignKey, Enum, DateTime, func, JSON, Boolean, Table
from sqlalchemy.orm import relationship
from ..database import Base
import enum
from enum import Enum as PyEnum


# Association table for many-to-many relationship between ToolSetType and ToolType
tool_set_type_tool_types = Table(
    'tool_set_type_tool_types',
    Base.metadata,
    Column('tool_set_type_id', Integer, ForeignKey('tool_set_types.id'), primary_key=True),
    Column('tool_type_id', Integer, ForeignKey('tool_types.id'), primary_key=True)
)

class Role(PyEnum):
    WAREHOUSE_EMPLOYEE = "warehouse_employee"
    AVIATION_ENGINEER = "aviation_engineer"
    CONVEYOR = "conveyor"
    ADMINISTRATOR = "administrator"
    QUALITY_CONTROL_SPECIALIST = "quality_control_specialist"
    
class MaintenanceRequestStatus(PyEnum):
    CREATED = "created"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    INCIDENT = "incident"

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    tab_number = Column(String, unique=True, nullable=False)
    full_name = Column(String, nullable=False)
    password = Column(String, nullable=False)
    role = Column(Enum(Role), nullable=False)
    created_at = Column(String, server_default=func.now())
    updated_at = Column(String, server_default=func.now(), onupdate=func.now())

class Aircraft(Base):
    __tablename__ = "aircrafts"
    id = Column(Integer, primary_key=True, index=True)
    tail_number = Column(String, unique=True, nullable=False)
    model = Column(String, nullable=False)
    year_of_manufacture = Column(Integer, nullable=False)
    description = Column(String)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())

    maintenance_requests = relationship("MaintenanceRequest", back_populates="aircraft")
    incidents = relationship("Incident", back_populates="aircraft")

class ToolCategory(Base):
    __tablename__ = "tool_categories"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False, unique=True)
    tool_types = relationship("ToolType", back_populates="category")

class ToolType(Base):
    __tablename__ = "tool_types"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False, unique=True)
    category_id = Column(Integer, ForeignKey('tool_categories.id'))
    is_item = Column(Boolean, nullable=False)

    category = relationship("ToolCategory", back_populates="tool_types")
    tool_set_types = relationship("ToolSetType", secondary=tool_set_type_tool_types, back_populates="tool_types")

class ToolSetType(Base):
    __tablename__ = "tool_set_types"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False, unique=True)
    description = Column(String)
    tool_type_ids = Column(JSON, nullable=False, default=list)

    tool_sets = relationship("ToolSet", back_populates="tool_set_type")
    tool_types = relationship("ToolType", secondary=tool_set_type_tool_types, back_populates="tool_set_types")

class ToolSet(Base):
    __tablename__ = "tool_sets"
    id = Column(Integer, primary_key=True, index=True)
    tool_set_type_id = Column(Integer, ForeignKey('tool_set_types.id'), nullable=False)
    batch_number = Column(String, nullable=False)
    description = Column(String)
    batch_map = Column(JSON, nullable=False, default=dict)

    tool_set_type = relationship("ToolSetType", back_populates="tool_sets")
    incidents = relationship("Incident", back_populates="tool_set")
    maintenance_requests = relationship("MaintenanceRequest", back_populates="tool_set")

class MaintenanceRequest(Base):
    __tablename__ = "maintenance_requests"
    id = Column(Integer, primary_key=True, index=True)
    aircraft_id = Column(Integer, ForeignKey('aircrafts.id'), nullable=False)
    created_at = Column(DateTime, server_default=func.now())
    warehouse_employee_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    description = Column(String, nullable=False)
    status = Column(Enum(MaintenanceRequestStatus), nullable=False, default=MaintenanceRequestStatus.CREATED)
    aviation_engineer_id = Column(Integer, ForeignKey('users.id'))
    tool_set_id = Column(Integer, ForeignKey('tool_sets.id'))

    aircraft = relationship("Aircraft", back_populates="maintenance_requests")
    warehouse_employee = relationship("User", foreign_keys=[warehouse_employee_id])
    aviation_engineer = relationship("User", foreign_keys=[aviation_engineer_id])
    tool_set = relationship("ToolSet", back_populates="maintenance_requests")
    incident = relationship("Incident", uselist=False, back_populates="maintenance_request")

class IncidentStatus(enum.Enum):
    OPEN = "open"
    INVESTIGATING = "investigating"
    RESOLVED = "resolved"
    CLOSED = "closed"

class Incident(Base):
    __tablename__ = "incidents"
    id = Column(Integer, primary_key=True, index=True)
    aviation_engineer_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    quality_control_specialist_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    aircraft_id = Column(Integer, ForeignKey('aircrafts.id'), nullable=False)
    created_at = Column(DateTime, server_default=func.now())
    tool_set_id = Column(Integer, ForeignKey('tool_sets.id'), nullable=False)
    annotated_image = Column(String)
    raw_image = Column(String)
    status = Column(Enum(IncidentStatus), nullable=False, default=IncidentStatus.OPEN)
    resolution_summary = Column(String)
    comments = Column(String)
    maintenance_request_id = Column(Integer, ForeignKey('maintenance_requests.id'), unique=True, nullable=False)

    aviation_engineer = relationship("User", foreign_keys=[aviation_engineer_id])
    quality_control_specialist = relationship("User", foreign_keys=[quality_control_specialist_id])
    aircraft = relationship("Aircraft", back_populates="incidents")
    tool_set = relationship("ToolSet", back_populates="incidents")
    maintenance_request = relationship("MaintenanceRequest", back_populates="incident")