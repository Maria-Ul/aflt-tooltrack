import pytest

class TestAircraft:
    def test_create_aircraft_success(self, client, auth_headers):
        """Тест успешного создания самолета"""
        aircraft_data = {
            "tail_number": "RA-12345",
            "model": "Boeing 737-800",
            "year_of_manufacture": 2018,
            "description": "Test aircraft"
        }
        
        response = client.post("/api/aircraft/", json=aircraft_data, headers=auth_headers)
        
        assert response.status_code == 201
        data = response.json()
        assert data["tail_number"] == aircraft_data["tail_number"]
        assert data["model"] == aircraft_data["model"]
        assert data["year_of_manufacture"] == aircraft_data["year_of_manufacture"]
        assert data["description"] == aircraft_data["description"]
        assert "id" in data
        assert "created_at" in data

    def test_create_aircraft_duplicate_tail_number(self, client, auth_headers):
        """Тест создания самолета с существующим бортовым номером"""
        # Первый самолет
        aircraft_data = {
            "tail_number": "RA-67890",
            "model": "Airbus A320",
            "year_of_manufacture": 2020,
            "description": "First aircraft"
        }
        client.post("/api/aircraft/", json=aircraft_data, headers=auth_headers)
        
        # Второй самолет с тем же бортовым номером
        response = client.post("/api/aircraft/", json=aircraft_data, headers=auth_headers)
        
        assert response.status_code == 400
        assert "already exists" in response.json()["detail"]

    def test_get_all_aircrafts(self, client, auth_headers):
        """Тест получения списка самолетов"""
        # Создаем несколько самолетов
        aircrafts_data = [
            {
                "tail_number": "RA-11111",
                "model": "Boeing 747",
                "year_of_manufacture": 2015,
                "description": "First test aircraft"
            },
            {
                "tail_number": "RA-22222",
                "model": "Airbus A380",
                "year_of_manufacture": 2019,
                "description": "Second test aircraft"
            }
        ]
        
        for aircraft_data in aircrafts_data:
            client.post("/api/aircraft/", json=aircraft_data, headers=auth_headers)
        
        response = client.get("/api/aircraft/", headers=auth_headers)
        
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) >= 2

    def test_get_aircraft_by_id(self, client, auth_headers):
        """Тест получения самолета по ID"""
        # Создаем самолет
        aircraft_data = {
            "tail_number": "RA-33333",
            "model": "Boeing 777",
            "year_of_manufacture": 2017,
            "description": "Test aircraft for get by ID"
        }
        create_response = client.post("/api/aircraft/", json=aircraft_data, headers=auth_headers)
        aircraft_id = create_response.json()["id"]
        
        # Получаем самолет по ID
        response = client.get(f"/api/aircraft/{aircraft_id}", headers=auth_headers)
        
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == aircraft_id
        assert data["tail_number"] == aircraft_data["tail_number"]

    def test_get_aircraft_by_tail_number(self, client, auth_headers):
        """Тест получения самолета по бортовому номеру"""
        aircraft_data = {
            "tail_number": "RA-44444",
            "model": "Airbus A350",
            "year_of_manufacture": 2021,
            "description": "Test aircraft for get by tail number"
        }
        client.post("/api/aircraft/", json=aircraft_data, headers=auth_headers)
        
        response = client.get(f"/api/aircraft/tail/{aircraft_data['tail_number']}", headers=auth_headers)
        
        assert response.status_code == 200
        data = response.json()
        assert data["tail_number"] == aircraft_data["tail_number"]

    def test_update_aircraft(self, client, auth_headers):
        """Тест обновления самолета"""
        # Создаем самолет
        aircraft_data = {
            "tail_number": "RA-55555",
            "model": "Boeing 737",
            "year_of_manufacture": 2016,
            "description": "Original description"
        }
        create_response = client.post("/api/aircraft/", json=aircraft_data, headers=auth_headers)
        aircraft_id = create_response.json()["id"]
        
        # Обновляем самолет
        update_data = {
            "model": "Boeing 737 MAX",
            "description": "Updated description"
        }
        response = client.put(f"/api/aircraft/{aircraft_id}", json=update_data, headers=auth_headers)
        
        assert response.status_code == 200
        data = response.json()
        assert data["model"] == update_data["model"]
        assert data["description"] == update_data["description"]
        assert data["year_of_manufacture"] == aircraft_data["year_of_manufacture"]  # Не изменилось

    def test_delete_aircraft(self, client, auth_headers):
        """Тест удаления самолета"""
        # Создаем самолет
        aircraft_data = {
            "tail_number": "RA-66666",
            "model": "Airbus A220",
            "year_of_manufacture": 2022,
            "description": "Aircraft to delete"
        }
        create_response = client.post("/api/aircraft/", json=aircraft_data, headers=auth_headers)
        aircraft_id = create_response.json()["id"]
        
        # Удаляем самолет
        response = client.delete(f"/api/aircraft/{aircraft_id}", headers=auth_headers)
        
        assert response.status_code == 204
        
        # Проверяем, что самолет удален
        get_response = client.get(f"/api/aircraft/{aircraft_id}", headers=auth_headers)
        assert get_response.status_code == 404

    def test_aircraft_unauthorized_access(self, client):
        """Тест доступа к API самолетов без аутентификации"""
        # Все операции без токена должны возвращать 401
        responses = [
            client.post("/api/aircraft/", json={}),
            client.get("/api/aircraft/"),
            client.get("/api/aircraft/1"),
            client.put("/api/aircraft/1", json={}),
            client.delete("/api/aircraft/1")
        ]
        
        for response in responses:
            assert response.status_code == 401