import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.main import app, database
from app.database import Base
from app.api.dependencies import get_db
from app.models import models

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
    user = models.User(
        tab_number="12345",
        full_name="Test User",
        password="$2b$12$EixZaYVK1fsbw1ZfbX3OXePaWxn96p36WQoeG6Lruj3vjPGga31lW",  # password: secret
        role=models.Role.AVIATION_ENGINEER
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user

@pytest.fixture
def test_admin(db_session):
    """Создает тестового администратора"""
    admin = models.User(
        tab_number="admin001",
        full_name="Admin User",
        password="$2b$12$EixZaYVK1fsbw1ZfbX3OXePaWxn96p36WQoeG6Lruj3vjPGga31lW",  # password: secret
        role=models.Role.ADMINISTRATOR
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