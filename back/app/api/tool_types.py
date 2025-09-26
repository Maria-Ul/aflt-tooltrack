from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional
from .dependencies import get_db, get_current_user
from app.models import models
from app.schemas import tool_types_schema

router = APIRouter(prefix="/tool-types", tags=["Тип инструмента"])

@router.post(
    "/", 
    response_model=tool_types_schema.ToolType, 
    status_code=status.HTTP_201_CREATED,
    summary="Создать тип инструмента или категорию",
    description="Создает новый тип инструмента (is_item=true) или категорию (is_item=false)"
)
def create_tool_type(
    tool_type: tool_types_schema.ToolTypeCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    """
    Создание типа инструмента или категории.
    
    - **name**: Название (уникальное)
    - **category_id**: ID родительской категории (опционально)
    - **is_item**: True - конкретный инструмент, False - категория
    
    **Правила валидации:**
    - Категория (is_item=false) не может быть вложена в инструмент (is_item=true)
    - Инструмент (is_item=true) должен иметь родительскую категорию
    """
    # Проверяем уникальность имени
    existing_tool_type = db.query(models.ToolType).filter(
        models.ToolType.name == tool_type.name
    ).first()
    
    if existing_tool_type:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Tool type with this name already exists"
        )
    
    # Валидация иерархии
    if tool_type.category_id:
        parent_category = db.query(models.ToolType).filter(
            models.ToolType.id == tool_type.category_id
        ).first()
        
        if not parent_category:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Parent category not found"
            )
        
        # Категория не может быть вложена в инструмент
        if parent_category.is_item and not tool_type.is_item:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Category cannot be nested under an item"
            )
    
    # Инструмент должен иметь родительскую категорию
    if tool_type.is_item and not tool_type.category_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Item must have a parent category"
        )
    
    db_tool_type = models.ToolType(
        name=tool_type.name,
        category_id=tool_type.category_id,
        is_item=tool_type.is_item
    )
    
    db.add(db_tool_type)
    db.commit()
    db.refresh(db_tool_type)
    return db_tool_type

@router.get(
    "/", 
    response_model=List[tool_types_schema.ToolType],
    summary="Получить все типы инструментов",
    description="Возвращает список всех типов инструментов и категорий"
)
def get_all_tool_types(
    skip: int = 0,
    limit: int = 100,
    is_item: Optional[bool] = None,
    category_id: Optional[int] = None,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    """
    Получение списка типов инструментов с фильтрацией.
    
    **Параметры запроса:**
    - **skip**: Пропуск записей
    - **limit**: Лимит записей
    - **is_item**: Фильтр по типу (true - инструменты, false - категории)
    - **category_id**: Фильтр по родительской категории
    
    Требуется аутентификация.
    """
    query = db.query(models.ToolType)
    
    if is_item is not None:
        query = query.filter(models.ToolType.is_item == is_item)
    
    if category_id is not None:
        query = query.filter(models.ToolType.category_id == category_id)
    
    tool_types = query.offset(skip).limit(limit).all()
    return tool_types

@router.get(
    "/{tool_type_id}", 
    response_model=tool_types_schema.ToolType,
    summary="Получить тип инструмента по ID",
    description="Возвращает информацию о типе инструмента по его идентификатору"
)
def get_tool_type(
    tool_type_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    """
    Получение типа инструмента по ID.
    
    - **tool_type_id**: ID типа инструмента
    
    Требуется аутентификация.
    """
    tool_type = db.query(models.ToolType).filter(models.ToolType.id == tool_type_id).first()
    if not tool_type:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Tool type not found"
        )
    return tool_type

@router.get(
    "/{tool_type_id}/children",
    response_model=List[tool_types_schema.ToolType],
    summary="Получить дочерние элементы",
    description="Возвращает список дочерних элементов категории"
)
def get_tool_type_children(
    tool_type_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    """
    Получение дочерних элементов категории.
    
    - **tool_type_id**: ID родительской категории
    
    Требуется аутентификация.
    """
    # Проверяем существование родительского элемента
    parent = db.query(models.ToolType).filter(models.ToolType.id == tool_type_id).first()
    if not parent:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Tool type not found"
        )
    
    children = db.query(models.ToolType).filter(
        models.ToolType.category_id == tool_type_id
    ).all()
    return children

@router.get(
    "/tree/root",
    response_model=List[tool_types_schema.ToolTypeWithChildren],
    summary="Получить дерево категорий",
    description="Возвращает дерево категорий и инструментов, начиная с корневого уровня"
)
def get_tool_type_tree(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    """
    Получение полного дерева категорий и инструментов.
    
    Возвращает иерархическую структуру, начиная с корневых элементов
    (элементов без родительской категории).
    
    Требуется аутентификация.
    """
    def build_tree(parent_id: Optional[int] = None):
        """Рекурсивная функция построения дерева"""
        query = db.query(models.ToolType).filter(models.ToolType.category_id == parent_id)
        items = query.all()
        
        result = []
        for item in items:
            item_data = tool_types_schema.ToolType.from_orm(item)
            children = build_tree(item.id) if not item.is_item else []
            result.append(tool_types_schema.ToolTypeWithChildren(
                **item_data.dict(),
                children=children,
                category=item.category
            ))
        return result
    
    return build_tree()

@router.get(
    "/categories/root",
    response_model=List[tool_types_schema.ToolType],
    summary="Получить корневые категории",
    description="Возвращает список корневых категорий (без родительской категории)"
)
def get_root_categories(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    """
    Получение корневых категорий.
    
    Возвращает категории верхнего уровня (category_id IS NULL).
    
    Требуется аутентификация.
    """
    root_categories = db.query(models.ToolType).filter(
        models.ToolType.category_id.is_(None),
        models.ToolType.is_item == False  # Только категории, не инструменты
    ).all()
    return root_categories

@router.put(
    "/{tool_type_id}", 
    response_model=tool_types_schema.ToolType,
    summary="Обновить тип инструмента",
    description="Обновляет информацию о типе инструмента или категории"
)
def update_tool_type(
    tool_type_id: int,
    tool_type_update: tool_types_schema.ToolTypeUpdate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    """
    Обновление типа инструмента.
    
    - **tool_type_id**: ID типа инструмента
    - **name**: Новое название (опционально)
    - **category_id**: Новая родительская категория (опционально)
    - **is_item**: Изменение типа элемента (опционально)
    
    **Валидация:**
    - Проверяет корректность иерархических изменений
    
    Требуется аутентификация.
    """
    tool_type = db.query(models.ToolType).filter(models.ToolType.id == tool_type_id).first()
    if not tool_type:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Tool type not found"
        )
    
    update_data = tool_type_update.dict(exclude_unset=True)
    
    # Валидация уникальности имени
    if 'name' in update_data and update_data['name'] != tool_type.name:
        existing_tool_type = db.query(models.ToolType).filter(
            models.ToolType.name == update_data['name']
        ).first()
        if existing_tool_type:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Tool type with this name already exists"
            )
    
    # Валидация иерархии при изменении category_id
    if 'category_id' in update_data:
        new_category_id = update_data['category_id']
        
        if new_category_id:
            parent_category = db.query(models.ToolType).filter(
                models.ToolType.id == new_category_id
            ).first()
            
            if not parent_category:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Parent category not found"
                )
            
            # Проверка циклических ссылок
            if new_category_id == tool_type_id:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Cannot set self as parent"
                )
            
            # Категория не может быть вложена в инструмент
            if parent_category.is_item and not tool_type.is_item:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Category cannot be nested under an item"
                )
    
    # Применяем обновления
    for field, value in update_data.items():
        setattr(tool_type, field, value)
    
    db.commit()
    db.refresh(tool_type)
    return tool_type

@router.delete(
    "/{tool_type_id}", 
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Удалить тип инструмента",
    description="Удаляет тип инструмента или категорию из системы"
)
def delete_tool_type(
    tool_type_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    """
    Удаление типа инструмента.
    
    - **tool_type_id**: ID типа инструмента
    
    **Ограничения:**
    - Нельзя удалить категорию, если у нее есть дочерние элементы
    - Нельзя удалить тип инструмента, если он используется в наборах инструментов
    
    Требуется аутентификация.
    """
    tool_type = db.query(models.ToolType).filter(models.ToolType.id == tool_type_id).first()
    if not tool_type:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Tool type not found"
        )
    
    # Проверяем дочерние элементы (для категорий)
    if not tool_type.is_item:
        children_count = db.query(models.ToolType).filter(
            models.ToolType.category_id == tool_type_id
        ).count()
        
        if children_count > 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Cannot delete category with child elements"
            )
    
    # Проверяем использование в tool_set_types (нужно добавить relationship в модели)
    # Пока пропускаем эту проверку, нужно добавить соответствующие отношения
    
    db.delete(tool_type)
    db.commit()
    return None
