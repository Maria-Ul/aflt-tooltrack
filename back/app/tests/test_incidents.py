class TestIncidents:
    def test_mark_request_as_incident(self, client, auth_headers, test_maintenance_request_with_relations):
        """Тест пометки заявки как инцидента через API заявок"""
        incident_data = {
            "comments": "Проблема с качеством инструментов"
        }
        
        response = client.put(
            f"/api/maintenance-requests/{test_maintenance_request_with_relations.id}/mark-incident",
            json=incident_data,
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        
        # Проверяем основные поля
        assert data["status"] == "INCIDENT"
        assert data["id"] == test_maintenance_request_with_relations.id
        
        # Проверяем, что вернулся ID инцидента
        assert "incident_id" in data
        assert isinstance(data["incident_id"], int)
        assert data["incident_id"] > 0
        
        # Можно дополнительно проверить, что инцидент действительно создан
        incident_response = client.get(
            f"/api/incidents/{data['incident_id']}",
            headers=auth_headers
        )
        assert incident_response.status_code == 200
        incident_data = incident_response.json()
        assert incident_data["maintenance_request_id"] == test_maintenance_request_with_relations.id

    def test_create_incident_from_request_already_has_incident(self, client, auth_headers, test_maintenance_request_with_incident):
        """Тест создания инцидента для заявки, у которой уже есть инцидент"""
        incident_data = {"comments": "Тестовый комментарий"}
        
        response = client.put(
            f"/api/maintenance-requests/{test_maintenance_request_with_incident.id}/mark-incident",
            json=incident_data,
            headers=auth_headers
        )
        
        assert response.status_code == 400
        assert "already has an associated incident" in response.json()["detail"]

    def test_create_incident_from_request_missing_engineer(self, client, auth_headers, test_maintenance_request):
        """Тест создания инцидента для заявки без инженера"""
        incident_data = {"comments": "Тестовый комментарий"}
        
        response = client.put(
            f"/api/maintenance-requests/{test_maintenance_request.id}/mark-incident",
            json=incident_data,
            headers=auth_headers
        )
        
        assert response.status_code == 400
        assert "must have an assigned aviation engineer" in response.json()["detail"]

    def test_get_all_incidents(self, client, auth_headers, test_incident):
        """Тест получения всех инцидентов"""
        response = client.get("/api/incidents/", headers=auth_headers)
        
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) >= 1

    def test_get_incident_by_id(self, client, auth_headers, test_incident):
        """Тест получения инцидента по ID"""
        response = client.get(f"/api/incidents/{test_incident.id}", headers=auth_headers)
        
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == test_incident.id
        assert data["status"] == test_incident.status.value

    def test_get_incident_with_relations(self, client, auth_headers, test_incident_with_relations):
        """Тест получения инцидента с полной информацией"""
        response = client.get(
            f"/api/incidents/{test_incident_with_relations.id}/with-relations", 
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == test_incident_with_relations.id
        assert "aviation_engineer" in data
        assert "quality_control_specialist" in data
        assert "aircraft" in data
        assert "tool_set" in data
        assert "maintenance_request" in data

    def test_update_incident(self, client, auth_headers, test_incident):
        """Тест обновления инцидента"""
        update_data = {
            "status": "INVESTIGATING",
            "comments": "Начато расследование инцидента",
            "resolution_summary": "Предварительный анализ"
        }
        
        response = client.put(
            f"/api/incidents/{test_incident.id}", 
            json=update_data, 
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == update_data["status"]
        assert data["comments"] == update_data["comments"]
        assert data["resolution_summary"] == update_data["resolution_summary"]

    def test_resolve_incident(self, client, auth_headers, test_incident):
        """Тест разрешения инцидента"""
        resolve_data = {
            "resolution_summary": "Проблема решена заменой инструментов",
            "comments": "Инцидент успешно разрешен"
        }
        
        response = client.put(
            f"/api/incidents/{test_incident.id}/resolve", 
            json=resolve_data, 
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "RESOLVED"
        assert data["resolution_summary"] == resolve_data["resolution_summary"]
        
        # Проверяем, что заявка переведена в статус COMPLETED
        maintenance_request_response = client.get(
            f"/api/maintenance-requests/{test_incident.maintenance_request_id}", 
            headers=auth_headers
        )
        maintenance_request_data = maintenance_request_response.json()
        assert maintenance_request_data["status"] == "COMPLETED"

    def test_close_incident(self, client, auth_headers, test_incident):
        """Тест закрытия инцидента"""
        close_data = {
            "resolution_summary": "Инцидент закрыт после проверки",
            "comments": "Все проблемы устранены"
        }
        
        response = client.put(
            f"/api/incidents/{test_incident.id}/close", 
            json=close_data, 
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "CLOSED"
        assert data["resolution_summary"] == close_data["resolution_summary"]

    def test_get_incidents_stats(self, client, auth_headers, test_incident):
        """Тест получения статистики по инцидентам"""
        response = client.get("/api/incidents/stats/summary", headers=auth_headers)
        
        assert response.status_code == 200
        data = response.json()
        assert "total" in data
        assert "by_status" in data
        assert "recent_count" in data
        assert isinstance(data["by_status"], dict)

    def test_incidents_unauthorized_access(self, client):
        """Тест доступа к API без аутентификации"""
        responses = [
            client.get("/api/incidents/"),
            client.get("/api/incidents/1"),
            client.get("/api/incidents/1/with-relations"),
            client.put("/api/incidents/1", json={}),
            client.put("/api/incidents/1/resolve", json={}),
            client.put("/api/incidents/1/close", json={}),
            client.get("/api/incidents/stats/summary"),
            client.delete("/api/incidents/1")
        ]
        
        for response in responses:
            assert response.status_code == 401
    