import pytest

class TestMaintenanceRequests:
    def test_create_maintenance_request_success(self, client, auth_headers, test_aircraft, test_warehouse_employee):
        """Тест успешного создания заявки на ТО"""
        maintenance_request_data = {
            "aircraft_id": test_aircraft.id,
            "warehouse_employee_id": test_warehouse_employee.id,
            "description": "Плановое техническое обслуживание",
            "status": "CREATED"
        }
        
        response = client.post("/api/maintenance-requests/", json=maintenance_request_data, headers=auth_headers)
        
        assert response.status_code == 201
        data = response.json()
        assert data["aircraft_id"] == maintenance_request_data["aircraft_id"]
        assert data["description"] == maintenance_request_data["description"]
        assert data["status"] == maintenance_request_data["status"]
        assert "id" in data

    def test_create_maintenance_request_with_engineer_and_toolset(self, client, auth_headers, test_aircraft, test_warehouse_employee, test_aviation_engineer, test_tool_set):
        """Тест создания заявки с инженером и набором инструментов"""
        maintenance_request_data = {
            "aircraft_id": test_aircraft.id,
            "warehouse_employee_id": test_warehouse_employee.id,
            "aviation_engineer_id": test_aviation_engineer.id,
            "tool_set_id": test_tool_set.id,
            "description": "ТО с назначенными ресурсами",
            "status": "CREATED"
        }
        
        response = client.post("/api/maintenance-requests/", json=maintenance_request_data, headers=auth_headers)
        
        assert response.status_code == 201
        data = response.json()
        assert data["aviation_engineer_id"] == test_aviation_engineer.id
        assert data["tool_set_id"] == test_tool_set.id

    def test_create_maintenance_request_invalid_aircraft(self, client, auth_headers, test_warehouse_employee):
        """Тест создания заявки с несуществующим самолетом"""
        maintenance_request_data = {
            "aircraft_id": 9999,
            "warehouse_employee_id": test_warehouse_employee.id,
            "description": "Заявка с невалидным самолетом",
            "status": "CREATED"
        }
        
        response = client.post("/api/maintenance-requests/", json=maintenance_request_data, headers=auth_headers)
        
        assert response.status_code == 400
        assert "Aircraft not found" in response.json()["detail"]

    def test_create_maintenance_request_invalid_engineer_role(self, client, auth_headers, test_aircraft, test_warehouse_employee, test_warehouse_employee_2):
        """Тест создания заявки с пользователем не в роли инженера"""
        maintenance_request_data = {
            "aircraft_id": test_aircraft.id,
            "warehouse_employee_id": test_warehouse_employee.id,
            "aviation_engineer_id": test_warehouse_employee_2.id,  # Не инженер
            "description": "Заявка с невалидным инженером",
            "status": "CREATED"
        }
        
        response = client.post("/api/maintenance-requests/", json=maintenance_request_data, headers=auth_headers)
        
        assert response.status_code == 400
        assert "not an aviation engineer" in response.json()["detail"]

    def test_get_all_maintenance_requests(self, client, auth_headers, test_maintenance_request):
        """Тест получения всех заявок на ТО"""
        response = client.get("/api/maintenance-requests/", headers=auth_headers)
        
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) >= 1

    def test_get_maintenance_requests_with_filters(self, client, auth_headers, test_maintenance_request):
        """Тест получения заявок с фильтрами"""
        # Фильтр по статусу - используем строковое значение enum
        response_status = client.get(
            f"/api/maintenance-requests/?status={test_maintenance_request.status.value}",  # Используем .value
            headers=auth_headers
        )
        assert response_status.status_code == 200
        data_status = response_status.json()
        if data_status:  # Проверяем, если есть результаты
            assert all(item["status"] == test_maintenance_request.status.value for item in data_status)
        
        # Фильтр по самолету
        response_aircraft = client.get(
            f"/api/maintenance-requests/?aircraft_id={test_maintenance_request.aircraft_id}", 
            headers=auth_headers
        )
        assert response_aircraft.status_code == 200
        data_aircraft = response_aircraft.json()
        if data_aircraft:  # Проверяем, если есть результаты
            assert all(item["aircraft_id"] == test_maintenance_request.aircraft_id for item in data_aircraft)
            
    def test_get_maintenance_request_by_id(self, client, auth_headers, test_maintenance_request):
        """Тест получения заявки по ID"""
        response = client.get(f"/api/maintenance-requests/{test_maintenance_request.id}", headers=auth_headers)
        
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == test_maintenance_request.id
        assert data["description"] == test_maintenance_request.description

    def test_get_maintenance_request_with_relations(self, client, auth_headers, test_maintenance_request_with_relations):
        """Тест получения заявки с полной информацией"""
        response = client.get(
            f"/api/maintenance-requests/{test_maintenance_request_with_relations.id}/with-relations", 
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == test_maintenance_request_with_relations.id
        assert "aircraft" in data
        assert "warehouse_employee" in data
        assert data["aircraft"] is not None
        assert data["warehouse_employee"] is not None

    def test_update_maintenance_request(self, client, auth_headers, test_maintenance_request, test_aviation_engineer, test_tool_set):
        """Тест обновления заявки"""
        update_data = {
            "status": "IN_PROGRESS",
            "aviation_engineer_id": test_aviation_engineer.id,
            "tool_set_id": test_tool_set.id,
            "description": "Обновленное описание"
        }
        
        response = client.put(
            f"/api/maintenance-requests/{test_maintenance_request.id}", 
            json=update_data, 
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == update_data["status"]
        assert data["aviation_engineer_id"] == update_data["aviation_engineer_id"]
        assert data["tool_set_id"] == update_data["tool_set_id"]
        assert data["description"] == update_data["description"]

    def test_assign_engineer_to_request(self, client, auth_headers, test_maintenance_request, test_aviation_engineer):
        """Тест назначения инженера на заявку"""
        assign_data = {
            "aviation_engineer_id": test_aviation_engineer.id,
            "status": "IN_PROGRESS"
        }
        
        response = client.put(
            f"/api/maintenance-requests/{test_maintenance_request.id}/assign-engineer", 
            json=assign_data, 
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["aviation_engineer_id"] == test_aviation_engineer.id
        assert data["status"] == "IN_PROGRESS"

    def test_complete_maintenance_request(self, client, auth_headers, test_maintenance_request):
        """Тест завершения заявки"""
        response = client.put(
            f"/api/maintenance-requests/{test_maintenance_request.id}/complete", 
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "COMPLETED"

    def test_get_maintenance_requests_stats(self, client, auth_headers, test_maintenance_request):
        """Тест получения статистики по заявкам"""
        response = client.get("/api/maintenance-requests/stats/summary", headers=auth_headers)
        
        assert response.status_code == 200
        data = response.json()
        assert "total" in data
        assert "by_status" in data
        assert "recent_count" in data
        assert isinstance(data["by_status"], dict)
        assert data["total"] >= 1

    def test_delete_maintenance_request_success(self, client, auth_headers, test_maintenance_request):
        """Тест успешного удаления заявки"""
        response = client.delete(f"/api/maintenance-requests/{test_maintenance_request.id}", headers=auth_headers)
        
        assert response.status_code == 204
        
        # Проверяем, что удалена
        get_response = client.get(f"/api/maintenance-requests/{test_maintenance_request.id}", headers=auth_headers)
        assert get_response.status_code == 404

    def test_delete_maintenance_request_with_incident(self, client, auth_headers, test_maintenance_request_with_incident):
        """Тест удаления заявки с связанным инцидентом"""
        response = client.delete(
            f"/api/maintenance-requests/{test_maintenance_request_with_incident.id}", 
            headers=auth_headers
        )
        
        assert response.status_code == 400
        assert "associated incident" in response.json()["detail"]

    def test_maintenance_requests_unauthorized_access(self, client):
        """Тест доступа к API без аутентификации"""
        responses = [
            client.post("/api/maintenance-requests/", json={}),
            client.get("/api/maintenance-requests/"),
            client.get("/api/maintenance-requests/1"),
            client.get("/api/maintenance-requests/1/with-relations"),
            client.put("/api/maintenance-requests/1", json={}),
            client.put("/api/maintenance-requests/1/assign-engineer", json={}),
            client.put("/api/maintenance-requests/1/complete"),
            client.get("/api/maintenance-requests/stats/summary"),
            client.delete("/api/maintenance-requests/1")
        ]
        
        for response in responses:
            assert response.status_code == 401