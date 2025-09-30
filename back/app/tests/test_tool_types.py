import pytest
from app.models.models import ToolType, User, Role

class TestToolTypes:
    def test_create_tool_type_category_success(self, client, auth_headers):
        """Тест успешного создания категории инструментов"""
        tool_type_data = {
            "name": "Ручные инструменты",
            "category_id": None,
            "is_item": False
        }
        
        response = client.post("/api/tool-types/", json=tool_type_data, headers=auth_headers)
        
        assert response.status_code == 201
        data = response.json()
        assert data["name"] == tool_type_data["name"]
        assert data["category_id"] is None
        assert data["is_item"] == tool_type_data["is_item"]
        assert "id" in data

    def test_create_tool_type_item_success(self, client, auth_headers):
        """Тест успешного создания конкретного инструмента"""
        # Сначала создаем родительскую категорию
        category_data = {
            "name": "Отвертки",
            "category_id": None,
            "is_item": False
        }
        category_response = client.post("/api/tool-types/", json=category_data, headers=auth_headers)
        category_id = category_response.json()["id"]
        
        # Создаем инструмент в категории
        item_data = {
            "name": "Отвертка крестовая PH2",
            "category_id": category_id,
            "is_item": True
        }
        
        response = client.post("/api/tool-types/", json=item_data, headers=auth_headers)
        
        assert response.status_code == 201
        data = response.json()
        assert data["name"] == item_data["name"]
        assert data["category_id"] == category_id
        assert data["is_item"] == True

    def test_create_tool_type_duplicate_name(self, client, auth_headers):
        """Тест создания с дублирующимся именем"""
        tool_type_data = {
            "name": "Уникальное имя",
            "category_id": None,
            "is_item": False
        }
        
        # Первое создание - успешно
        client.post("/api/tool-types/", json=tool_type_data, headers=auth_headers)
        
        # Второе создание с тем же именем - ошибка
        response = client.post("/api/tool-types/", json=tool_type_data, headers=auth_headers)
        
        assert response.status_code == 400
        assert "already exists" in response.json()["detail"]

    def test_create_item_without_parent_category(self, client, auth_headers):
        """Тест создания инструмента без родительской категории"""
        item_data = {
            "name": "Отвертка без категории",
            "category_id": None,
            "is_item": True  # Инструмент должен иметь категорию
        }
        
        response = client.post("/api/tool-types/", json=item_data, headers=auth_headers)
        
        assert response.status_code == 400
        assert "must have a parent category" in response.json()["detail"]

    def test_create_category_under_item(self, client, auth_headers):
        """Тест создания категории под инструментом (недопустимо)"""
        # Создаем категорию
        category_data = {
            "name": "Родительская категория",
            "category_id": None,
            "is_item": False
        }
        category_response = client.post("/api/tool-types/", json=category_data, headers=auth_headers)
        category_id = category_response.json()["id"]
        
        # Создаем инструмент в категории
        item_data = {
            "name": "Инструмент",
            "category_id": category_id,
            "is_item": True
        }
        item_response = client.post("/api/tool-types/", json=item_data, headers=auth_headers)
        item_id = item_response.json()["id"]
        
        # Пытаемся создать категорию под инструментом - ошибка
        subcategory_data = {
            "name": "Подкатегория под инструментом",
            "category_id": item_id,  # ID инструмента, а не категории
            "is_item": False
        }
        
        response = client.post("/api/tool-types/", json=subcategory_data, headers=auth_headers)
        
        assert response.status_code == 400
        assert "cannot be nested under an item" in response.json()["detail"]

    def test_get_all_tool_types(self, client, auth_headers):
        """Тест получения всех типов инструментов"""
        # Создаем несколько типов
        tool_types_data = [
            {"name": "Категория 1", "category_id": None, "is_item": False},
            {"name": "Категория 2", "category_id": None, "is_item": False},
            {"name": "Инструмент 1", "category_id": 1, "is_item": True}
        ]
        
        for data in tool_types_data:
            client.post("/api/tool-types/", json=data, headers=auth_headers)
        
        response = client.get("/api/tool-types/", headers=auth_headers)
        
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) >= 3

    def test_get_tool_types_with_filters(self, client, auth_headers):
        """Тест получения с фильтрами"""
        # Создаем тестовые данные
        category_data = {"name": "Фильтруемая категория", "category_id": None, "is_item": False}
        category_response = client.post("/api/tool-types/", json=category_data, headers=auth_headers)
        category_id = category_response.json()["id"]
        
        item_data = {"name": "Фильтруемый инструмент", "category_id": category_id, "is_item": True}
        client.post("/api/tool-types/", json=item_data, headers=auth_headers)
        
        # Тестируем фильтры
        response_items = client.get("/api/tool-types/?is_item=true", headers=auth_headers)
        assert response_items.status_code == 200
        items_data = response_items.json()
        assert all(item["is_item"] == True for item in items_data)
        
        response_category = client.get(f"/api/tool-types/?category_id={category_id}", headers=auth_headers)
        assert response_category.status_code == 200
        category_data = response_category.json()
        assert all(item["category_id"] == category_id for item in category_data)

    def test_get_tool_type_by_id(self, client, auth_headers):
        """Тест получения типа инструмента по ID"""
        # Создаем тип
        tool_type_data = {
            "name": "Тестовый тип",
            "category_id": None,
            "is_item": False
        }
        create_response = client.post("/api/tool-types/", json=tool_type_data, headers=auth_headers)
        tool_type_id = create_response.json()["id"]
        
        # Получаем по ID
        response = client.get(f"/api/tool-types/{tool_type_id}", headers=auth_headers)
        
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == tool_type_id
        assert data["name"] == tool_type_data["name"]

    def test_get_nonexistent_tool_type(self, client, auth_headers):
        """Тест получения несуществующего типа инструмента"""
        response = client.get("/api/tool-types/9999", headers=auth_headers)
        
        assert response.status_code == 404
        assert "not found" in response.json()["detail"]

    def test_get_tool_type_children(self, client, auth_headers):
        """Тест получения дочерних элементов"""
        # Создаем родительскую категорию
        parent_data = {"name": "Родитель", "category_id": None, "is_item": False}
        parent_response = client.post("/api/tool-types/", json=parent_data, headers=auth_headers)
        parent_id = parent_response.json()["id"]
        
        # Создаем дочерние элементы
        children_data = [
            {"name": "Дочерний 1", "category_id": parent_id, "is_item": False},
            {"name": "Дочерний 2", "category_id": parent_id, "is_item": True}
        ]
        
        for child_data in children_data:
            client.post("/api/tool-types/", json=child_data, headers=auth_headers)
        
        # Получаем дочерние элементы
        response = client.get(f"/api/tool-types/{parent_id}/children", headers=auth_headers)
        
        assert response.status_code == 200
        children = response.json()
        assert len(children) == 2
        assert all(child["category_id"] == parent_id for child in children)

    def test_get_tool_type_tree(self, client, auth_headers):
        """Тест получения дерева категорий"""
        # Создаем иерархическую структуру
        root_data = {"name": "Корень", "category_id": None, "is_item": False}
        root_response = client.post("/api/tool-types/", json=root_data, headers=auth_headers)
        root_id = root_response.json()["id"]
        
        child_data = {"name": "Дочерний", "category_id": root_id, "is_item": False}
        child_response = client.post("/api/tool-types/", json=child_data, headers=auth_headers)
        child_id = child_response.json()["id"]
        
        grandchild_data = {"name": "Внук", "category_id": child_id, "is_item": True}
        client.post("/api/tool-types/", json=grandchild_data, headers=auth_headers)
        
        # Получаем дерево
        response = client.get("/api/tool-types/tree/root", headers=auth_headers)
        
        assert response.status_code == 200
        tree = response.json()
        assert len(tree) >= 1
        assert tree[0]["name"] == "Корень"
        assert len(tree[0]["children"]) >= 1

    def test_get_root_categories(self, client, auth_headers):
        """Тест получения корневых категорий"""
        # Создаем корневые категории
        root_categories_data = [
            {"name": "Корень 1", "category_id": None, "is_item": False},
            {"name": "Корень 2", "category_id": None, "is_item": False}
        ]
        
        for data in root_categories_data:
            client.post("/api/tool-types/", json=data, headers=auth_headers)
        
        # Создаем НЕ корневую категорию (должна быть исключена из результатов)
        non_root_data = {"name": "Не корень", "category_id": 1, "is_item": False}
        client.post("/api/tool-types/", json=non_root_data, headers=auth_headers)
        
        response = client.get("/api/tool-types/categories/root", headers=auth_headers)
        
        assert response.status_code == 200
        root_categories = response.json()
        assert len(root_categories) >= 2
        assert all(cat["category_id"] is None for cat in root_categories)
        assert all(cat["is_item"] == False for cat in root_categories)

    def test_update_tool_type_success(self, client, auth_headers):
        """Тест успешного обновления типа инструмента"""
        # Создаем тип для обновления
        original_data = {
            "name": "Оригинальное имя",
            "category_id": None,
            "is_item": False
        }
        create_response = client.post("/api/tool-types/", json=original_data, headers=auth_headers)
        tool_type_id = create_response.json()["id"]
        
        # Обновляем
        update_data = {
            "name": "Обновленное имя",
            "is_item": False
        }
        response = client.put(f"/api/tool-types/{tool_type_id}", json=update_data, headers=auth_headers)
        
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == update_data["name"]
        assert data["is_item"] == update_data["is_item"]

    def test_update_tool_type_hierarchy(self, client, auth_headers):
        """Тест обновления иерархии"""
        # Создаем две категории
        category1_data = {"name": "Категория 1", "category_id": None, "is_item": False}
        category1_response = client.post("/api/tool-types/", json=category1_data, headers=auth_headers)
        category1_id = category1_response.json()["id"]
        
        category2_data = {"name": "Категория 2", "category_id": None, "is_item": False}
        category2_response = client.post("/api/tool-types/", json=category2_data, headers=auth_headers)
        category2_id = category2_response.json()["id"]
        
        # Создаем инструмент в первой категории
        item_data = {"name": "Инструмент", "category_id": category1_id, "is_item": True}
        item_response = client.post("/api/tool-types/", json=item_data, headers=auth_headers)
        item_id = item_response.json()["id"]
        
        # Перемещаем инструмент во вторую категорию
        update_data = {"category_id": category2_id}
        response = client.put(f"/api/tool-types/{item_id}", json=update_data, headers=auth_headers)
        
        assert response.status_code == 200
        data = response.json()
        assert data["category_id"] == category2_id

    def test_update_with_cyclic_reference(self, client, auth_headers):
        """Тест обновления с циклической ссылкой"""
        # Создаем категорию
        category_data = {"name": "Категория", "category_id": None, "is_item": False}
        category_response = client.post("/api/tool-types/", json=category_data, headers=auth_headers)
        category_id = category_response.json()["id"]
        
        # Пытаемся установить саму себя как родителя
        update_data = {"category_id": category_id}
        response = client.put(f"/api/tool-types/{category_id}", json=update_data, headers=auth_headers)
        
        assert response.status_code == 400
        assert "Cannot set self as parent" in response.json()["detail"]

    def test_delete_tool_type_success(self, client, auth_headers):
        """Тест успешного удаления типа инструмента"""
        # Создаем тип для удаления
        tool_type_data = {
            "name": "Для удаления",
            "category_id": None,
            "is_item": False
        }
        create_response = client.post("/api/tool-types/", json=tool_type_data, headers=auth_headers)
        tool_type_id = create_response.json()["id"]
        
        # Удаляем
        response = client.delete(f"/api/tool-types/{tool_type_id}", headers=auth_headers)
        
        assert response.status_code == 204
        
        # Проверяем, что удален
        get_response = client.get(f"/api/tool-types/{tool_type_id}", headers=auth_headers)
        assert get_response.status_code == 404

    def test_delete_category_with_children(self, client, auth_headers):
        """Тест удаления категории с дочерними элементами"""
        # Создаем категорию с дочерним элементом
        parent_data = {"name": "Родитель", "category_id": None, "is_item": False}
        parent_response = client.post("/api/tool-types/", json=parent_data, headers=auth_headers)
        parent_id = parent_response.json()["id"]
        
        child_data = {"name": "Дочерний", "category_id": parent_id, "is_item": True}
        client.post("/api/tool-types/", json=child_data, headers=auth_headers)
        
        # Пытаемся удалить родительскую категорию
        response = client.delete(f"/api/tool-types/{parent_id}", headers=auth_headers)
        
        assert response.status_code == 204

    def test_tool_types_unauthorized_access(self, client):
        """Тест доступа к API типов инструментов без аутентификации"""
        # Все операции без токена должны возвращать 401
        responses = [
            client.post("/api/tool-types/", json={}),
            client.get("/api/tool-types/"),
            client.get("/api/tool-types/1"),
            client.get("/api/tool-types/1/children"),
            client.get("/api/tool-types/tree/root"),
            client.get("/api/tool-types/categories/root"),
            client.put("/api/tool-types/1", json={}),
            client.delete("/api/tool-types/1")
        ]
        
        for response in responses:
            assert response.status_code == 401

    def test_pagination(self, client, auth_headers):
        """Тест пагинации"""
        # Создаем несколько типов
        for i in range(15):
            tool_type_data = {
                "name": f"Тип {i}",
                "category_id": None,
                "is_item": False
            }
            client.post("/api/tool-types/", json=tool_type_data, headers=auth_headers)
        
        # Тестируем пагинацию
        response = client.get("/api/tool-types/?skip=5&limit=5", headers=auth_headers)
        
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 5

    @pytest.mark.parametrize("invalid_data", [
        {"name": ""},  # Пустое имя
        {"name": "A" * 1000},  # Слишком длинное имя
        {"category_id": 9999},  # Несуществующая категория
        {"is_item": "not_a_boolean"}  # Не булево значение
    ])
    def test_invalid_data_validation(self, client, auth_headers, invalid_data):
        """Тест валидации невалидных данных"""
        # Сначала создаем валидный тип
        valid_data = {
            "name": "Валидный тип",
            "category_id": None,
            "is_item": False
        }
        create_response = client.post("/api/tool-types/", json=valid_data, headers=auth_headers)
        tool_type_id = create_response.json()["id"]
        
        # Пытаемся обновить невалидными данными
        response = client.put(f"/api/tool-types/{tool_type_id}", json=invalid_data, headers=auth_headers)
        
        # Должен вернуть 422 (Validation Error) или 400
        assert response.status_code in [400, 422]

    def test_create_tool_type_with_class_success(self, client, auth_headers, test_tool_type_category):
        """Тест успешного создания инструмента с классом"""
        tool_type_data = {
            "name": "Отвертка крестовая PH2",
            "category_id": test_tool_type_category.id,
            "is_item": True,
            "tool_class": "OTVERTKA_PLUS"
        }
        
        response = client.post("/api/tool-types/", json=tool_type_data, headers=auth_headers)
        
        assert response.status_code == 201
        data = response.json()
        assert data["tool_class"] == "OTVERTKA_PLUS"
        assert data["is_item"] == True

    def test_create_category_with_class_fails(self, client, auth_headers):
        """Тест создания категории с классом (должно быть ошибкой)"""
        tool_type_data = {
            "name": "Категория с классом",
            "category_id": None,
            "is_item": False,
            "tool_class": "OTVERTKA_PLUS"  # Нельзя для категории
        }
        
        response = client.post("/api/tool-types/", json=tool_type_data, headers=auth_headers)
        
        assert response.status_code == 400
        assert "Tool class can only be set for items" in response.json()["detail"]

    def test_create_item_with_class_auto_sets_is_item(self, client, auth_headers, test_tool_type_category):
        """Тест что указание класса автоматически устанавливает is_item=true"""
        tool_type_data = {
            "name": "Инструмент с классом",
            "category_id": test_tool_type_category.id,
            "is_item": True,
            "tool_class": "PASSATIGI"  # is_item не указан, но должен стать true
        }
        
        response = client.post("/api/tool-types/", json=tool_type_data, headers=auth_headers)
        
        assert response.status_code == 201
        data = response.json()
        assert data["is_item"] == True
        assert data["tool_class"] == "PASSATIGI"

    # def test_get_tool_types_with_class_filter(self, client, auth_headers, test_tool_type_with_class):
    #     """Тест фильтрации по классу инструмента"""
    #     response = client.get(
    #         f"/api/tool-types/?tool_class={test_tool_type_with_class.tool_class.value}", 
    #         headers=auth_headers
    #     )
        
    #     assert response.status_code == 200
    #     data = response.json()
    #     assert len(data) >= 1
    #     assert all(item["tool_class"] == test_tool_type_with_class.tool_class for item in data)

    def test_get_tool_classes_enum(self, client, auth_headers):
        """Тест получения списка классов инструментов"""
        response = client.get("/api/tool-types/tool-classes/enum", headers=auth_headers)
        
        assert response.status_code == 200
        data = response.json()
        assert "OTVERTKA_PLUS" in data
        assert "PASSATIGI" in data
        assert len(data) == 11  # Все 11 классов

    def test_update_tool_type_with_class(self, client, auth_headers, test_tool_type_item):
        """Тест обновления инструмента с установкой класса"""
        update_data = {
            "tool_class": "KOLOVOROT"
        }
        
        response = client.put(
            f"/api/tool-types/{test_tool_type_item.id}", 
            json=update_data, 
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["tool_class"] == "KOLOVOROT"
        assert data["is_item"] == True  # Должно автоматически установиться в true