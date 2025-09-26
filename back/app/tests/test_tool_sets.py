import pytest

class TestToolSets:
    def test_create_tool_set_success(self, client, auth_headers, test_tool_set_type):
        """Тест успешного создания набора инструментов"""
        tool_set_data = {
            "tool_set_type_id": test_tool_set_type.id,
            "batch_number": "BATCH-001",
            "description": "Тестовый набор инструментов",
            "batch_map": {"1": "SN-001", "2": "SN-002"}
        }
        
        response = client.post("/api/tool-sets/", json=tool_set_data, headers=auth_headers)
        
        assert response.status_code == 201
        data = response.json()
        assert data["batch_number"] == tool_set_data["batch_number"]
        assert data["description"] == tool_set_data["description"]
        assert data["batch_map"] == tool_set_data["batch_map"]
        assert "id" in data

    def test_create_tool_set_duplicate_batch_number(self, client, auth_headers, test_tool_set):
        """Тест создания с дублирующимся партийным номером"""
        tool_set_data = {
            "tool_set_type_id": test_tool_set.tool_set_type_id,
            "batch_number": test_tool_set.batch_number,  # Существующий номер
            "description": "Новое описание",
            "batch_map": {}
        }
        
        response = client.post("/api/tool-sets/", json=tool_set_data, headers=auth_headers)
        
        assert response.status_code == 400
        assert "already exists" in response.json()["detail"]

    def test_create_tool_set_invalid_tool_set_type(self, client, auth_headers):
        """Тест создания с несуществующим типом набора"""
        tool_set_data = {
            "tool_set_type_id": 9999,  # Несуществующий ID
            "batch_number": "BATCH-002",
            "description": "Набор с невалидным типом",
            "batch_map": {}
        }
        
        response = client.post("/api/tool-sets/", json=tool_set_data, headers=auth_headers)
        
        assert response.status_code == 400
        assert "not found" in response.json()["detail"]

    def test_create_tool_set_invalid_batch_map(self, client, auth_headers, test_tool_set_type):
        """Тест создания с невалидной мапой партийных номеров"""
        tool_set_data = {
            "tool_set_type_id": test_tool_set_type.id,
            "batch_number": "BATCH-003",
            "description": "Набор с невалидной мапой",
            "batch_map": {"9999": "SN-001"}  # Несуществующий tool_type_id
        }
        
        response = client.post("/api/tool-sets/", json=tool_set_data, headers=auth_headers)
        
        assert response.status_code == 400
        assert "is not part of the selected tool set type" in response.json()["detail"]

    def test_get_all_tool_sets(self, client, auth_headers, test_tool_set):
        """Тест получения всех наборов инструментов"""
        response = client.get("/api/tool-sets/", headers=auth_headers)
        
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) >= 1

    def test_get_tool_sets_with_filter(self, client, auth_headers, test_tool_set):
        """Тест получения наборов с фильтром по типу"""
        response = client.get(
            f"/api/tool-sets/?tool_set_type_id={test_tool_set.tool_set_type_id}", 
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert all(item["tool_set_type_id"] == test_tool_set.tool_set_type_id for item in data)

    def test_get_tool_set_by_id(self, client, auth_headers, test_tool_set):
        """Тест получения набора по ID"""
        response = client.get(f"/api/tool-sets/{test_tool_set.id}", headers=auth_headers)
        
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == test_tool_set.id
        assert data["batch_number"] == test_tool_set.batch_number

    def test_get_tool_set_by_batch_number(self, client, auth_headers, test_tool_set):
        """Тест получения набора по партийному номеру"""
        response = client.get(
            f"/api/tool-sets/batch/{test_tool_set.batch_number}", 
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["batch_number"] == test_tool_set.batch_number

    def test_get_tool_set_with_type(self, client, auth_headers, test_tool_set):
        """Тест получения набора с информацией о типе"""
        response = client.get(
            f"/api/tool-sets/{test_tool_set.id}/with-type", 
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == test_tool_set.id
        assert "tool_set_type" in data
        # Проверяем, что есть информация о типе набора
        assert data["tool_set_type"] is not None
        assert data["tool_set_type"]["id"] == test_tool_set.tool_set_type_id

    def test_update_tool_set_success(self, client, auth_headers, test_tool_set):
        """Тест успешного обновления набора"""
        update_data = {
            "batch_number": "BATCH-UPDATED",
            "description": "Обновленное описание",
            "batch_map": {"1": "SN-UPDATED"}
        }
        
        response = client.put(
            f"/api/tool-sets/{test_tool_set.id}", 
            json=update_data, 
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["batch_number"] == update_data["batch_number"]
        assert data["description"] == update_data["description"]
        assert data["batch_map"] == update_data["batch_map"]

    def test_update_tool_set_duplicate_batch_number(self, client, auth_headers, test_tool_set, test_tool_set_2):
        """Тест обновления с дублирующимся партийным номером"""
        update_data = {
            "batch_number": test_tool_set_2.batch_number  # Номер другого набора
        }
        
        response = client.put(
            f"/api/tool-sets/{test_tool_set.id}", 
            json=update_data, 
            headers=auth_headers
        )
        
        assert response.status_code == 400
        assert "already exists" in response.json()["detail"]

    def test_delete_tool_set_success(self, client, auth_headers, test_tool_set):
        """Тест успешного удаления набора"""
        response = client.delete(f"/api/tool-sets/{test_tool_set.id}", headers=auth_headers)
        
        assert response.status_code == 204
        
        # Проверяем, что удален
        get_response = client.get(f"/api/tool-sets/{test_tool_set.id}", headers=auth_headers)
        assert get_response.status_code == 404

    def test_delete_tool_set_used_in_maintenance_request(self, client, auth_headers, test_tool_set_with_maintenance):
        """Тест удаления набора, используемого в заявке на ТО"""
        response = client.delete(
            f"/api/tool-sets/{test_tool_set_with_maintenance.id}", 
            headers=auth_headers
        )
        
        assert response.status_code == 400
        assert "used in maintenance requests" in response.json()["detail"]

    def test_validate_tool_set_success(self, client, auth_headers, test_tool_set_type):
        """Тест успешной валидации набора"""
        validation_data = {
            "tool_set_type_id": test_tool_set_type.id,
            "batch_number": "NEW-BATCH-001",
            "description": "Валидный набор",
            "batch_map": {"1": "SN-001"}
        }
        
        response = client.post("/api/tool-sets/validate", json=validation_data, headers=auth_headers)
        
        assert response.status_code == 200
        data = response.json()
        assert data["is_valid"] == True
        assert len(data["errors"]) == 0

    def test_tool_sets_unauthorized_access(self, client):
        """Тест доступа к API без аутентификации"""
        responses = [
            client.post("/api/tool-sets/", json={}),
            client.get("/api/tool-sets/"),
            client.get("/api/tool-sets/1"),
            client.get("/api/tool-sets/batch/123"),
            client.get("/api/tool-sets/1/with-type"),
            client.put("/api/tool-sets/1", json={}),
            client.delete("/api/tool-sets/1"),
            client.post("/api/tool-sets/validate", json={})
        ]
        
        for response in responses:
            assert response.status_code == 401

    def test_pagination(self, client, auth_headers, test_tool_set_type):
        """Тест пагинации"""
        # Создаем несколько наборов
        for i in range(10):
            tool_set_data = {
                "tool_set_type_id": test_tool_set_type.id,
                "batch_number": f"BATCH-PAG-{i}",
                "batch_map": {}
            }
            client.post("/api/tool-sets/", json=tool_set_data, headers=auth_headers)
        
        response = client.get("/api/tool-sets/?skip=2&limit=5", headers=auth_headers)
        
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 5