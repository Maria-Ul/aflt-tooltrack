import pytest
from app.models import models

class TestAuth:
    def test_register_success(self, client):
        """Тест успешной регистрации пользователя"""
        response = client.post("/api/auth/register", json={
            "tab_number": "newuser001",
            "full_name": "New Test User",
            "password": "newpassword123",
            "role": models.Role.AVIATION_ENGINEER.value
        })
        
        assert response.status_code == 201
        data = response.json()
        assert data["tab_number"] == "newuser001"
        assert data["full_name"] == "New Test User"
        assert data["role"] == models.Role.AVIATION_ENGINEER.value
        assert "access_token" in data
        assert data["token_type"] == "bearer"

    def test_register_duplicate_tab_number(self, client, test_user):
        """Тест регистрации с существующим табельным номером"""
        response = client.post("/api/auth/register", json={
            "tab_number": test_user.tab_number,  # Уже существует
            "full_name": "Another User",
            "password": "password123",
            "role": models.Role.WAREHOUSE_EMPLOYEE.value
        })
        
        assert response.status_code == 400
        assert "already exists" in response.json()["detail"]

    def test_login_success(self, client, test_user):
        """Тест успешного входа в систему"""
        response = client.post("/api/auth/login", json={
            "tab_number": test_user.tab_number,
            "password": "secret"
        })
        
        assert response.status_code == 200
        data = response.json()
        assert data["tab_number"] == test_user.tab_number
        assert "access_token" in data
        assert data["token_type"] == "bearer"

    def test_login_wrong_password(self, client, test_user):
        """Тест входа с неправильным паролем"""
        response = client.post("/api/auth/login", json={
            "tab_number": test_user.tab_number,
            "password": "wrongpassword"
        })
        
        assert response.status_code == 401
        assert "Incorrect tab number or password" in response.json()["detail"]

    def test_login_nonexistent_user(self, client):
        """Тест входа несуществующего пользователя"""
        response = client.post("/api/auth/login", json={
            "tab_number": "nonexistent",
            "password": "password123"
        })
        
        assert response.status_code == 401
        assert "Incorrect tab number or password" in response.json()["detail"]

    def test_register_invalid_role(self, client):
        """Тест регистрации с невалидной ролью"""
        response = client.post("/api/auth/register", json={
            "tab_number": "user002",
            "full_name": "Test User",
            "password": "password123",
            "role": "invalid_role"
        })
        
        assert response.status_code == 422  # Validation error
