from fastapi import APIRouter, UploadFile, File, HTTPException
from fastapi.responses import JSONResponse
import zipfile
import tempfile
import os
from pathlib import Path
from typing import List, Dict, Any
import uuid
from app.ml.predict_yolo_seg_prod import SegmentModel, get_prediction_results

router = APIRouter(prefix="/files", tags=["Загрузка файлов в модель"])

# Создаем словарь для маппинга
TOOL_CLASSES_MAP = {
    0: "BOKOREZY",
    1: "KEY_ROZGKOVY_NAKIDNOY_3_4", 
    2: "KOLOVOROT",
    3: "OTKRYVASHKA_OIL_CAN",
    4: "OTVERTKA_MINUS",
    5: "OTVERTKA_OFFSET_CROSS",
    6: "OTVERTKA_PLUS",
    7: "PASSATIGI",
    8: "PASSATIGI_CONTROVOCHNY",
    9: "RAZVODNOY_KEY",
    10: "SHARNITSA"
}


def map_classes_to_names(class_numbers: List[int]) -> List[str]:
    """Конвертирует числа классов в названия"""
    return [TOOL_CLASSES_MAP.get(cls, f"UNKNOWN_{cls}") for cls in class_numbers]

def process_single_image(image_path: str) -> Dict[str, Any]:
    """Обрабатывает одно изображение и возвращает результат"""
    # Инициализация модели (можно вынести в глобальную переменную для кэширования)
    model_path = "/app/app/ml/weights/yolo11s-seg-tools.pt"
    
    model = SegmentModel(
        model_path=model_path,
        conf_threshold=0.5,
        imgsz=640,
        prefer="auto",
        verbose=False
    )
    
    # Получаем предсказания
    classes, obb_rows, masks, probs = get_prediction_results(model, image_path)
    
    # Конвертируем masks в JSON-сериализуемый формат
    serializable_masks = []
    if masks is not None:
        for mask in masks:
            # Конвертируем numpy array в список
            if hasattr(mask, 'tolist'):
                serializable_masks.append(mask.tolist())
            else:
                serializable_masks.append(mask)
    serializable_probs = []
    if probs is not None:
        for prob in probs:
            # Конвертируем numpy array в список
            if hasattr(prob, 'tolist'):
                serializable_probs.append(prob.tolist())
            else:
                serializable_probs.append(prob)
    
    resultClasses = map_classes_to_names(classes)

    return {
        'classes': resultClasses,
        'probs': serializable_probs,
        'masks': serializable_masks,
        'obb_rows': obb_rows,
    }

@router.post("/predict/single")
async def predict_single_image(file: UploadFile = File(...)):
    """
    API для предсказания на одном изображении
    
    - Принимает: файл изображения (jpg, png, jpeg)
    - Возвращает: результаты детекции
    """
    # Проверяем тип файла
    allowed_extensions = {'.jpg', '.jpeg', '.png', '.bmp'}
    file_extension = Path(file.filename).suffix.lower()
    
    if file_extension not in allowed_extensions:
        raise HTTPException(
            status_code=400, 
            detail="Неподдерживаемый формат файла. Разрешены: jpg, jpeg, png, bmp"
        )
    
    try:
        # Создаем временный файл
        with tempfile.NamedTemporaryFile(delete=False, suffix=file_extension) as temp_file:
            # Читаем и сохраняем загруженный файл
            content = await file.read()
            temp_file.write(content)
            temp_file_path = temp_file.name
        
        # Обрабатываем изображение
        result = process_single_image(temp_file_path)
        
        # Очищаем временный файл
        os.unlink(temp_file_path)
        
        return JSONResponse(content=result)
        
    except Exception as e:
        # Очищаем временный файл в случае ошибки
        if 'temp_file_path' in locals():
            try:
                os.unlink(temp_file_path)
            except:
                pass
                
        raise HTTPException(
            status_code=500, 
            detail=f"Ошибка обработки изображения: {str(e)}"
        )

@router.post("/predict/batch")
async def predict_batch_images(zip_file: UploadFile = File(...)):
    """
    API для пакетной обработки изображений из архива
    
    - Принимает: ZIP архив с изображениями
    - Возвращает: массив результатов для каждого изображения
    """
    if not zip_file.filename.endswith('.zip'):
        raise HTTPException(
            status_code=400, 
            detail="Файл должен быть ZIP архивом"
        )
    
    try:
        # Создаем временную директорию для распаковки
        with tempfile.TemporaryDirectory() as temp_dir:
            # Сохраняем ZIP файл
            zip_path = os.path.join(temp_dir, "uploaded.zip")
            content = await zip_file.read()
            with open(zip_path, "wb") as f:
                f.write(content)
            
            # Распаковываем архив
            extracted_files = []
            with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                zip_ref.extractall(temp_dir)
                extracted_files = zip_ref.namelist()
            
            # Фильтруем только изображения
            image_extensions = {'.jpg', '.jpeg', '.png', '.bmp'}
            image_files = [
                f for f in extracted_files 
                if Path(f).suffix.lower() in image_extensions
            ]
            
            if not image_files:
                raise HTTPException(
                    status_code=400, 
                    detail="В архиве не найдено поддерживаемых изображений"
                )
            
            # Обрабатываем каждое изображение
            results = []
            for image_file in image_files:
                image_path = os.path.join(temp_dir, image_file)
                
                try:
                    result = process_single_image(image_path)
                    result['filename'] = image_file
                    results.append(result)
                except Exception as e:
                    # Если ошибка на одном изображении, продолжаем с остальными
                    results.append({
                        'filename': image_file,
                        'error': f"Ошибка обработки: {str(e)}",
                        'classes': [],
                        'probs': [],
                        'masks': [],
                        'obb_rows': [],
                        'texts': []
                    })
            
            return JSONResponse(content={
                'total_files': len(image_files),
                'processed_files': len([r for r in results if 'error' not in r]),
                'failed_files': len([r for r in results if 'error' in r]),
                'results': results
            })
            
    except zipfile.BadZipFile:
        raise HTTPException(
            status_code=400, 
            detail="Некорректный ZIP архив"
        )
    except Exception as e:
        raise HTTPException(
            status_code=500, 
            detail=f"Ошибка обработки архива: {str(e)}"
        )
