import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.main import app, database
from app.database import Base
from app.api.dependencies import get_db
from app.models.models import User, Role, ToolType, ToolSet, ToolSetType, ToolType, User, Role, Aircraft, MaintenanceRequest, Incident

# Тестовая база данных в памяти
SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)

TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

@pytest.fixture(scope="function")
def db_session():
    # Создаем таблицы
    Base.metadata.create_all(bind=engine)
    
    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.close()
    Base.metadata.drop_all(bind=engine)

@pytest.fixture(scope="function")
def client(db_session):
    # Переопределяем зависимость базы данных
    def override_get_db():
        try:
            yield db_session
        finally:
            pass
    
    app.dependency_overrides[get_db] = override_get_db
    client = TestClient(app)
    return client

@pytest.fixture
def test_user(db_session):
    """Создает тестового пользователя"""
    user = User(
        tab_number="12345",
        full_name="Test User",
        password="$2b$12$EixZaYVK1fsbw1ZfbX3OXePaWxn96p36WQoeG6Lruj3vjPGga31lW",  # password: secret
        role=Role.AVIATION_ENGINEER
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user

@pytest.fixture
def test_admin(db_session):
    """Создает тестового администратора"""
    admin = User(
        tab_number="admin001",
        full_name="Admin User",
        password="$2b$12$EixZaYVK1fsbw1ZfbX3OXePaWxn96p36WQoeG6Lruj3vjPGga31lW",  # password: secret
        role=Role.ADMINISTRATOR
    )
    db_session.add(admin)
    db_session.commit()
    db_session.refresh(admin)
    return admin

@pytest.fixture
def auth_headers(client, test_user):
    """Получает токен аутентификации"""
    response = client.post("/api/auth/login", json={
        "tab_number": test_user.tab_number,
        "password": "secret"
    })
    token = response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}

@pytest.fixture
def admin_headers(client, test_admin):
    """Получает токен аутентификации для администратора"""
    response = client.post("/api/auth/login", json={
        "tab_number": test_admin.tab_number,
        "password": "secret"
    })
    token = response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}

@pytest.fixture
def test_tool_type_category(db_session):
    """Создает тестовую категорию инструментов"""
    category = ToolType(
        name="Тестовая категория",
        category_id=None,
        is_item=False
    )
    db_session.add(category)
    db_session.commit()
    db_session.refresh(category)
    return category

@pytest.fixture
def test_tool_type_item(db_session, test_tool_type_category):
    """Создает тестовый инструмент в категории"""
    item = ToolType(
        name="Тестовый инструмент",
        category_id=test_tool_type_category.id,
        is_item=True,
        tool_class="OTVERTKA_PLUS"
    )
    db_session.add(item)
    db_session.commit()
    db_session.refresh(item)
    return item

@pytest.fixture
def test_tool_type_hierarchy(db_session):
    """Создает тестовую иерархию категорий и инструментов"""
    # Корневая категория
    root_category = ToolType(name="Корневая категория", category_id=None, is_item=False)
    db_session.add(root_category)
    db_session.commit()
    db_session.refresh(root_category)
    
    # Подкатегория
    subcategory = ToolType(name="Подкатегория", category_id=root_category.id, is_item=False)
    db_session.add(subcategory)
    db_session.commit()
    db_session.refresh(subcategory)
    
    # Инструмент
    tool = ToolType(
        name="Инструмент",
        category_id=subcategory.id,
        is_item=True,
        tool_class="OTVERTKA_PLUS"
    )
    db_session.add(tool)
    db_session.commit()
    db_session.refresh(tool)
    
    return {
        "root": root_category,
        "subcategory": subcategory,
        "tool": tool
    }

@pytest.fixture
def test_tool_set_type_with_tools(db_session):
    """Создает тестовый тип набора с несколькими инструментами"""
    # Создаем несколько инструментов
    tool_types = []
    for i in range(3):
        tool_type = ToolType(
            name=f"Инструмент {i}",
            category_id=None,
            is_item=True,
            tool_class="OTVERTKA_PLUS"
        )
        db_session.add(tool_type)
        tool_types.append(tool_type)
    
    db_session.commit()
    for tool_type in tool_types:
        db_session.refresh(tool_type)
    
    # Создаем тип набора с этими инструментами
    tool_type_ids = [tool_type.id for tool_type in tool_types]
    tool_set_type = ToolSetType(
        name="Набор с инструментами",
        description="Набор с несколькими инструментами",
        tool_type_ids=tool_type_ids
    )
    db_session.add(tool_set_type)
    db_session.commit()
    db_session.refresh(tool_set_type)
    return tool_set_type

@pytest.fixture
def test_tool_set_type_with_tool_set(db_session, test_tool_set_type):
    """Создает тестовый тип набора, используемый в наборе инструментов"""
    # Создаем ToolSet, который использует этот ToolSetType
    tool_set = ToolSet(
        tool_set_type_id=test_tool_set_type.id,
        batch_number="TEST-001",
        description="Тестовый набор инструментов",
        batch_map={}
    )
    db_session.add(tool_set)
    db_session.commit()
    db_session.refresh(tool_set)
    return test_tool_set_type


@pytest.fixture
def test_tool_set(db_session, test_tool_set_type):
    """Создает тестовый набор инструментов"""
    tool_set = ToolSet(
        tool_set_type_id=test_tool_set_type.id,
        batch_number="TEST-BATCH-001",
        description="Тестовый набор инструментов",
        batch_map={"1": "SN-001", "2": "SN-002"}
    )
    db_session.add(tool_set)
    db_session.commit()
    db_session.refresh(tool_set)
    return tool_set

@pytest.fixture
def test_tool_set_2(db_session, test_tool_set_type):
    """Создает второй тестовый набор инструментов"""
    tool_set = ToolSet(
        tool_set_type_id=test_tool_set_type.id,
        batch_number="TEST-BATCH-002",
        description="Второй тестовый набор",
        batch_map={"1": "SN-003"}
    )
    db_session.add(tool_set)
    db_session.commit()
    db_session.refresh(tool_set)
    return tool_set

@pytest.fixture
def test_tool_set_with_maintenance(db_session, test_tool_set, test_aircraft, test_user):
    """Создает тестовый набор, используемый в заявке на ТО"""
    # Создаем заявку на ТО, которая использует этот набор
    maintenance_request = MaintenanceRequest(
        aircraft_id=test_aircraft.id,
        warehouse_employee_id=test_user.id,
        description="Тестовая заявка",
        status="CREATED",
        tool_set_id=test_tool_set.id
    )
    db_session.add(maintenance_request)
    db_session.commit()
    return test_tool_set

@pytest.fixture
def test_aircraft(db_session):
    """Создает тестовый самолет"""
    aircraft = Aircraft(
        tail_number="TEST-001",
        model="Test Model",
        year_of_manufacture=2020,
        description="Тестовый самолет"
    )
    db_session.add(aircraft)
    db_session.commit()
    db_session.refresh(aircraft)
    return aircraft

@pytest.fixture
def test_tool_set_type(db_session):
    """Создает тестовый тип набора инструментов"""
    # Сначала создаем инструменты
    tool_types = []
    for i in range(1, 3):  # Создаем 2 инструмента с ID 1 и 2
        tool_type = ToolType(
            name=f"Тестовый инструмент {i}",
            category_id=None,
            is_item=True,
            tool_class="OTVERTKA_PLUS"
        )
        db_session.add(tool_type)
        tool_types.append(tool_type)
    
    db_session.commit()
    for tool_type in tool_types:
        db_session.refresh(tool_type)
    
    # Создаем тип набора с этими инструментами
    tool_set_type = ToolSetType(
        name="Тестовый тип набора",
        description="Тестовое описание типа набора",
        tool_type_ids=[tool_type.id for tool_type in tool_types]  # [1, 2]
    )
    db_session.add(tool_set_type)
    db_session.commit()
    db_session.refresh(tool_set_type)
    return tool_set_type

@pytest.fixture
def test_warehouse_employee(db_session):
    """Создает тестового сотрудника склада"""
    employee = User(
        tab_number="WH001",
        full_name="Сотрудник склада Тестовый",
        password="password",
        role=Role.WAREHOUSE_EMPLOYEE
    )
    db_session.add(employee)
    db_session.commit()
    db_session.refresh(employee)
    return employee

@pytest.fixture
def test_warehouse_employee_2(db_session):
    """Создает второго тестового сотрудника склада"""
    employee = User(
        tab_number="WH002",
        full_name="Сотрудник склада Тестовый 2",
        password="password",
        role=Role.WAREHOUSE_EMPLOYEE
    )
    db_session.add(employee)
    db_session.commit()
    db_session.refresh(employee)
    return employee

@pytest.fixture
def test_aviation_engineer(db_session):
    """Создает тестового авиационного инженера"""
    engineer = User(
        tab_number="ENG001",
        full_name="Авиационный инженер Тестовый",
        password="password",
        role=Role.AVIATION_ENGINEER
    )
    db_session.add(engineer)
    db_session.commit()
    db_session.refresh(engineer)
    return engineer

@pytest.fixture
def test_maintenance_request(db_session, test_aircraft, test_warehouse_employee):
    """Создает тестовую заявку на ТО"""
    maintenance_request = MaintenanceRequest(
        aircraft_id=test_aircraft.id,
        warehouse_employee_id=test_warehouse_employee.id,
        description="Тестовая заявка на техническое обслуживание",
        status="CREATED"
    )
    db_session.add(maintenance_request)
    db_session.commit()
    db_session.refresh(maintenance_request)
    return maintenance_request

@pytest.fixture
def test_maintenance_request_with_relations(db_session, test_aircraft, test_warehouse_employee, test_aviation_engineer, test_tool_set):
    """Создает тестовую заявку на ТО со всеми связями"""
    # Сначала создаем специалиста КК если его нет
    qc_specialist = db_session.query(User).filter(
        User.role == Role.QUALITY_CONTROL_SPECIALIST
    ).first()
    
    if not qc_specialist:
        qc_specialist = User(
            tab_number="QC002",
            full_name="Тестовый специалист КК",
            password="password",
            role=Role.QUALITY_CONTROL_SPECIALIST
        )
        db_session.add(qc_specialist)
        db_session.commit()
        db_session.refresh(qc_specialist)

    maintenance_request = MaintenanceRequest(
        aircraft_id=test_aircraft.id,
        warehouse_employee_id=test_warehouse_employee.id,
        aviation_engineer_id=test_aviation_engineer.id,
        tool_set_id=test_tool_set.id,
        description="Тестовая заявка со всеми связями",
        status="IN_PROGRESS"
    )
    db_session.add(maintenance_request)
    db_session.commit()
    db_session.refresh(maintenance_request)
    return maintenance_request

@pytest.fixture
def test_maintenance_request_with_incident(db_session, test_maintenance_request):
    """Создает тестовую заявку на ТО с связанным инцидентом"""
    incident = Incident(
        maintenance_request_id=test_maintenance_request.id,
        aviation_engineer_id=1,  # Заглушка
        quality_control_specialist_id=1,  # Заглушка
        aircraft_id=test_maintenance_request.aircraft_id,
        tool_set_id=1,  # Заглушка
        status="OPEN"
    )
    db_session.add(incident)
    db_session.commit()
    return test_maintenance_request

@pytest.fixture
def test_quality_control_specialist(db_session):
    """Создает тестового специалиста по контролю качества"""
    specialist = User(
        tab_number="QC001",
        full_name="Специалист КК Тестовый",
        password="password",
        role=Role.QUALITY_CONTROL_SPECIALIST
    )
    db_session.add(specialist)
    db_session.commit()
    db_session.refresh(specialist)
    return specialist

@pytest.fixture
def test_incident(db_session, test_maintenance_request_with_relations, test_quality_control_specialist):
    """Создает тестовый инцидент"""
    incident = Incident(
        aviation_engineer_id=test_maintenance_request_with_relations.aviation_engineer_id,
        quality_control_specialist_id=test_quality_control_specialist.id,
        aircraft_id=test_maintenance_request_with_relations.aircraft_id,
        tool_set_id=test_maintenance_request_with_relations.tool_set_id,
        maintenance_request_id=test_maintenance_request_with_relations.id,
        raw_image="/uploads/incidents/123_raw.jpg",
        annotated_image="/uploads/incidents/123_annotated.jpg",
        status="OPEN",
        comments="Тестовый инцидент"
    )
    db_session.add(incident)
    db_session.commit()
    db_session.refresh(incident)
    return incident

@pytest.fixture
def test_incident_with_relations(db_session, test_maintenance_request_with_relations, test_aviation_engineer, test_quality_control_specialist, test_aircraft, test_tool_set):
    """Создает тестовый инцидент со всеми связями"""
    incident = Incident(
        aviation_engineer_id=test_aviation_engineer.id,
        quality_control_specialist_id=test_quality_control_specialist.id,
        aircraft_id=test_aircraft.id,
        tool_set_id=test_tool_set.id,
        maintenance_request_id=test_maintenance_request_with_relations.id,
        raw_image="/uploads/incidents/123_raw.jpg",
        annotated_image="/uploads/incidents/123_annotated.jpg",
        status="OPEN",
        comments="Тестовый инцидент со связями"
    )
    db_session.add(incident)
    db_session.commit()
    db_session.refresh(incident)
    return incident

@pytest.fixture
def test_tool_type_with_class(db_session, test_tool_type_category):
    """Создает тестовый инструмент с классом"""
    tool_type = ToolType(
        name="Тестовый инструмент с классом",
        category_id=test_tool_type_category.id,
        is_item=True,
        tool_class="OTVERTKA_PLUS"
    )
    db_session.add(tool_type)
    db_session.commit()
    db_session.refresh(tool_type)

    return tool_type
