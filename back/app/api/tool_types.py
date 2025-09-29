from fastapi import APIRouter, Depends, HTTPException, status, Query
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
    description="""
    Создает новый тип инструмента (is_item=true) или категорию (is_item=false)
    
    **Правила валидации для tool_class:**
    - Для инструментов (is_item=true) можно указать tool_class
    - Для категорий (is_item=false) tool_class должен быть null
    - Если указан tool_class, is_item автоматически устанавливается в true
    """
)
def create_tool_type(
    tool_type: tool_types_schema.ToolTypeCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    """
    Создание типа инструмента или категории.
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
    
    # Валидация tool_class
    if tool_type.tool_class and not tool_type.is_item:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Tool class can only be set for items (is_item=true)"
        )
    
    # Если указан tool_class, автоматически устанавливаем is_item=true
    if tool_type.tool_class:
        tool_type.is_item = True
    
    # Валидация иерархии (существующий код)
    if tool_type.category_id:
        parent_category = db.query(models.ToolType).filter(
            models.ToolType.id == tool_type.category_id
        ).first()
        
        if not parent_category:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Parent category not found"
            )
        
        if parent_category.is_item and not tool_type.is_item:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Category cannot be nested under an item"
            )
    
    if tool_type.is_item and not tool_type.category_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Item must have a parent category"
        )
    
    db_tool_type = models.ToolType(
        name=tool_type.name,
        category_id=tool_type.category_id,
        is_item=tool_type.is_item,
        tool_class=tool_type.tool_class
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
    tool_class: Optional[str] = Query(None, description="Фильтр по классу инструмента"),
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
    - **tool_class**: Фильтр по классу инструмента
    
    Требуется аутентификация.
    """
    query = db.query(models.ToolType)
    
    if is_item is not None:
        query = query.filter(models.ToolType.is_item == is_item)
    
    if category_id is not None:
        query = query.filter(models.ToolType.category_id == category_id)
    
    if tool_class is not None:
        query = query.filter(models.ToolType.tool_class == tool_class)
    
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
    response_model=List[dict],  # Используем dict чтобы избежать проблем с валидацией
    summary="Получить дерево категорий",
    description="Возвращает дерево категорий и инструментов, начиная с корневого уровня"
)
def get_tool_type_tree(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    """
    Получение полного дерева категорий и инструментов.
    """
    def build_tree(parent_id: Optional[int] = None):
        query = db.query(models.ToolType).filter(models.ToolType.category_id == parent_id)
        items = query.all()
        
        result = []
        for item in items:
            node = {
                "id": item.id,
                "name": item.name,
                "category_id": item.category_id,
                "is_item": item.is_item,
                "children": build_tree(item.id) if not item.is_item else []
            }
            result.append(node)
        
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
    """
    tool_type = db.query(models.ToolType).filter(models.ToolType.id == tool_type_id).first()
    if not tool_type:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Tool type not found"
        )
    
    update_data = tool_type_update.model_dump(exclude_unset=True)
    
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
    
    # Валидация tool_class
    if 'tool_class' in update_data:
        tool_class = update_data['tool_class']
        
        # Если устанавливаем tool_class, проверяем что это инструмент
        if tool_class and not (tool_type.is_item or update_data.get('is_item', True)):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Tool class can only be set for items (is_item=true)"
            )
        
        # Если устанавливаем tool_class, автоматически устанавливаем is_item=true
        if tool_class:
            update_data['is_item'] = True
    
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
            is_item = update_data.get('is_item', tool_type.is_item)
            if parent_category.is_item and not is_item:
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
    description="Удаляет тип инструмента или категорию из системы. Для категорий рекурсивно удаляет все дочерние элементы."
)
def delete_tool_type(
    tool_type_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    """
    Удаление типа инструмента.
    """
    try:
        # Начинаем транзакцию для безопасности
        tool_type = db.query(models.ToolType).filter(models.ToolType.id == tool_type_id).first()
        if not tool_type:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Tool type not found"
            )
        
        def delete_children(parent_id: int):
            """Удаляет всех дочерних элементов"""
            children = db.query(models.ToolType).filter(
                models.ToolType.category_id == parent_id
            ).all()
            
            for child in children:
                # Рекурсивно удаляем детей детей
                delete_children(child.id)
                # Удаляем самого ребенка
                db.delete(child)
        
        # Удаляем всех детей (если это категория)
        if not tool_type.is_item:
            delete_children(tool_type_id)
        
        # Удаляем сам элемент
        db.delete(tool_type)
        
        db.commit()
        
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error deleting tool type: {str(e)}"
        )
    
    return None

@router.get(
    "/tool-classes/enum",
    response_model=dict[str, str],
    summary="Получить список доступных классов инструментов",
    description="Возвращает словарь всех доступных классов инструментов"
)
def get_tool_classes():
    """
    Получение списка доступных классов инструментов.
    
    Возвращает словарь, где ключ - название класса, значение - описание.
    
    Требуется аутентификация.
    """
    tool_classes = {
        "BOKOREZY": "Бокорезы",
        "KEY_ROZGKOVY_NAKIDNOY_3_4": "Ключ рожковый накидной 3/4",
        "KOLOVOROT": "Коловорот", 
        "OTKRYVASHKA_OIL_CAN": "Открывашка oil can",
        "OTVERTKA_MINUS": "Отвертка минус",
        "OTVERTKA_OFFSET_CROSS": "Отвертка offset cross",
        "OTVERTKA_PLUS": "Отвертка плюс",
        "PASSATIGI": "Пассатижи",
        "PASSATIGI_CONTROVOCHNY": "Пассатижи контрольные",
        "RAZVODNOY_KEY": "Разводной ключ",
        "SHARNITSA": "Шарница"
    }

    return tool_classes