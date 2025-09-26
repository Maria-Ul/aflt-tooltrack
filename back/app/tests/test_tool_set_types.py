import pytest

class TestToolSetTypes:
    def test_create_tool_set_type_success(self, client, auth_headers, test_tool_type_item):
        """Тест успешного создания типа набора инструментов"""
        tool_set_type_data = {
            "name": "Набор для ТО двигателя",
            "description": "Полный набор для технического обслуживания авиационного двигателя",
            "tool_type_ids": [test_tool_type_item.id]
        }
        
        response = client.post("/api/tool-set-types/", json=tool_set_type_data, headers=auth_headers)
        
        assert response.status_code == 201
        data = response.json()
        assert data["name"] == tool_set_type_data["name"]
        assert data["description"] == tool_set_type_data["description"]
        assert data["tool_type_ids"] == tool_set_type_data["tool_type_ids"]
        assert "id" in data

    def test_create_tool_set_type_duplicate_name(self, client, auth_headers, test_tool_set_type):
        """Тест создания с дублирующимся именем"""
        tool_set_type_data = {
            "name": test_tool_set_type.name,  # Существующее имя
            "description": "Новое описание",
            "tool_type_ids": []
        }
        
        response = client.post("/api/tool-set-types/", json=tool_set_type_data, headers=auth_headers)
        
        assert response.status_code == 400
        assert "already exists" in response.json()["detail"]

    def test_create_tool_set_type_with_invalid_tool_type_ids(self, client, auth_headers):
        """Тест создания с несуществующими tool_type_ids"""
        tool_set_type_data = {
            "name": "Набор с невалидными инструментами",
            "description": "Набор с несуществующими инструментами",
            "tool_type_ids": [9999, 8888]  # Несуществующие ID
        }
        
        response = client.post("/api/tool-set-types/", json=tool_set_type_data, headers=auth_headers)
        
        assert response.status_code == 400
        assert "not found" in response.json()["detail"]

    def test_get_all_tool_set_types(self, client, auth_headers, test_tool_set_type):
        """Тест получения всех типов наборов"""
        response = client.get("/api/tool-set-types/", headers=auth_headers)
        
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) >= 1

    def test_get_tool_set_type_by_id(self, client, auth_headers, test_tool_set_type):
        """Тест получения типа набора по ID"""
        response = client.get(f"/api/tool-set-types/{test_tool_set_type.id}", headers=auth_headers)
        
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == test_tool_set_type.id
        assert data["name"] == test_tool_set_type.name

    def test_get_tool_set_type_with_tools(self, client, auth_headers, test_tool_set_type_with_tools):
        """Тест получения типа набора с детальной информацией об инструментах"""
        response = client.get(
            f"/api/tool-set-types/{test_tool_set_type_with_tools.id}/with-tools", 
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == test_tool_set_type_with_tools.id
        assert "tool_types" in data
        # Проверяем, что tool_types - это список
        assert isinstance(data["tool_types"], list)

    def test_search_tool_set_types_by_tool_type(self, client, auth_headers, test_tool_set_type_with_tools):
        """Тест поиска наборов по типу инструмента"""
        # Берем первый tool_type_id из тестового набора
        tool_type_id = test_tool_set_type_with_tools.tool_type_ids[0]
        
        response = client.get(
            f"/api/tool-set-types/search/by-tool-type/{tool_type_id}", 
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        # Должен найти хотя бы один набор
        assert len(data) >= 1
        # Проверяем, что tool_type_id есть в tool_type_ids найденного набора
        assert tool_type_id in data[0]["tool_type_ids"]

    def test_search_by_nonexistent_tool_type(self, client, auth_headers):
        """Тест поиска по несуществующему типу инструмента"""
        response = client.get("/api/tool-set-types/search/by-tool-type/9999", headers=auth_headers)
        
        assert response.status_code == 404
        assert "not found" in response.json()["detail"]

    def test_update_tool_set_type_success(self, client, auth_headers, test_tool_set_type, test_tool_type_item):
        """Тест успешного обновления типа набора"""
        update_data = {
            "name": "Обновленное название",
            "description": "Обновленное описание",
            "tool_type_ids": [test_tool_type_item.id]
        }
        
        response = client.put(
            f"/api/tool-set-types/{test_tool_set_type.id}", 
            json=update_data, 
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == update_data["name"]
        assert data["description"] == update_data["description"]
        assert data["tool_type_ids"] == update_data["tool_type_ids"]

    def test_delete_tool_set_type_success(self, client, auth_headers, test_tool_set_type):
        """Тест успешного удаления типа набора"""
        response = client.delete(f"/api/tool-set-types/{test_tool_set_type.id}", headers=auth_headers)
        
        assert response.status_code == 204
        
        # Проверяем, что удален
        get_response = client.get(f"/api/tool-set-types/{test_tool_set_type.id}", headers=auth_headers)
        assert get_response.status_code == 404

    def test_validate_tool_set_type_success(self, client, auth_headers, test_tool_type_item):
        """Тест успешной валидации типа набора"""
        validation_data = {
            "name": "Новое валидное имя",
            "description": "Описание",
            "tool_type_ids": [test_tool_type_item.id]
        }
        
        response = client.post("/api/tool-set-types/validate", json=validation_data, headers=auth_headers)
        
        assert response.status_code == 200
        data = response.json()
        assert data["is_valid"] == True
        assert len(data["errors"]) == 0

    def test_tool_set_types_unauthorized_access(self, client):
        """Тест доступа к API без аутентификации"""
        responses = [
            client.post("/api/tool-set-types/", json={}),
            client.get("/api/tool-set-types/"),
            client.get("/api/tool-set-types/1"),
            client.get("/api/tool-set-types/1/with-tools"),
            client.get("/api/tool-set-types/search/by-tool-type/1"),
            client.put("/api/tool-set-types/1", json={}),
            client.delete("/api/tool-set-types/1"),
            client.post("/api/tool-set-types/validate", json={})
        ]
        
        for response in responses:
            assert response.status_code == 401

    # Упрощенные тесты без сложных зависимостей
    def test_create_minimal_tool_set_type(self, client, auth_headers):
        """Тест создания минимального типа набора"""
        tool_set_type_data = {
            "name": "Минимальный набор",
            "tool_type_ids": []
        }
        
        response = client.post("/api/tool-set-types/", json=tool_set_type_data, headers=auth_headers)
        
        assert response.status_code == 201
        data = response.json()
        assert data["name"] == "Минимальный набор"
        assert data["tool_type_ids"] == []

    def test_update_partial_data(self, client, auth_headers, test_tool_set_type):
        """Тест частичного обновления"""
        update_data = {
            "name": "Только имя обновлено"
        }
        
        response = client.put(
            f"/api/tool-set-types/{test_tool_set_type.id}", 
            json=update_data, 
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "Только имя обновлено"
        # Описание должно остаться прежним
        assert data["description"] == test_tool_set_type.description