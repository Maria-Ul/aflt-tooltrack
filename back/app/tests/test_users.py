import pytest

class TestUsers:
    def test_get_current_user_success(self, client, auth_headers):
        """Тест получения данных текущего пользователя"""
        response = client.get("/api/users/me", headers=auth_headers)
        
        assert response.status_code == 200
        data = response.json()
        assert "tab_number" in data
        assert "full_name" in data
        assert "role" in data
        assert "id" in data

    def test_get_current_user_unauthorized(self, client):
        """Тест получения данных без аутентификации"""
        response = client.get("/api/users/me")
        
        assert response.status_code == 401
        assert "Not authenticated" in response.json()["detail"]

    def test_get_all_users_as_admin(self, client, admin_headers, test_user):
        """Тест получения всех пользователей администратором"""
        response = client.get("/api/users/", headers=admin_headers)
        
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) >= 1  # Как минимум админ и тестовый пользователь

    def test_get_all_users_as_regular_user(self, client, auth_headers):
        """Тест получения всех пользователей обычным пользователем"""
        response = client.get("/api/users/", headers=auth_headers)
        
        assert response.status_code == 403
        assert "Not enough permissions" in response.json()["detail"]

    def test_invalid_token(self, client):
        """Тест с невалидным токеном"""
        response = client.get("/api/users/me", headers={
            "Authorization": "Bearer invalid_token"
        })
        
        assert response.status_code == 401
        assert "Could not validate credentials" in response.json()["detail"]