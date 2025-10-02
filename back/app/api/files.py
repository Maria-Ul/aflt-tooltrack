from fastapi import APIRouter, UploadFile, File, HTTPException
from fastapi.responses import JSONResponse
import zipfile
import tempfile
import os
from pathlib import Path
from typing import List, Dict, Any
import uuid
from app.ml.predict_yolo_seg_prod import SegmentModel, get_prediction_results_with_img
from datetime import datetime
import zipfile
import json
import tempfile
from fastapi.responses import Response
import os
from pathlib import Path

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
    classes, obb_rows, masks, probs, img, overlap_flag, overlap_score = get_prediction_results_with_img(model, image_path)
    
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
        'overlap_flag': overlap_flag,
        'overlap_score': overlap_score
    }, img

@router.post("/predict/single")
async def predict_single_image(file: UploadFile = File(...)):
    """
    API для предсказания на одном изображении
    
    - Принимает: файл изображения (jpg, png, jpeg)
    - Возвращает: ZIP архив с JSON результатами и изображением
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
        # Создаем временный файл для загруженного изображения
        with tempfile.NamedTemporaryFile(delete=False, suffix=file_extension) as temp_file:
            content = await file.read()
            temp_file.write(content)
            temp_file_path = temp_file.name
        
        # Обрабатываем изображение
        json_data, img_path = process_single_image(temp_file_path)
        
        # Создаем временный ZIP архив
        with tempfile.NamedTemporaryFile(delete=False, suffix='.zip') as zip_temp:
            zip_path = zip_temp.name
        
        # Создаем ZIP архив с результатами
        with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
            # Добавляем JSON файл с результатами
            json_str = json.dumps(json_data, ensure_ascii=False, indent=2)
            zipf.writestr('prediction_results.json', json_str)
            
            # Добавляем обработанное изображение
            if os.path.exists(img_path):
                zipf.write(img_path, 'processed_image.jpg')
            else:
                # Если изображение не было сохранено, сохраняем оригинал
                zipf.write(temp_file_path, 'original_image.jpg')
        
        # Читаем ZIP файл в память
        with open(zip_path, 'rb') as f:
            zip_data = f.read()
        
        # Очищаем временные файлы
        os.unlink(temp_file_path)
        if os.path.exists(img_path) and img_path != temp_file_path:
            os.unlink(img_path)
        os.unlink(zip_path)
        
        # Возвращаем ZIP архив как ответ
        return Response(
            content=zip_data,
            media_type='application/zip',
            headers={
                'Content-Disposition': f'attachment; filename="prediction_results_{Path(file.filename).stem}.zip"'
            }
        )
        
    except Exception as e:
        # Очищаем временные файлы в случае ошибки
        if 'temp_file_path' in locals() and os.path.exists(temp_file_path):
            try:
                os.unlink(temp_file_path)
            except:
                pass
        if 'img_path' in locals() and os.path.exists(img_path) and img_path != temp_file_path:
            try:
                os.unlink(img_path)
            except:
                pass
        if 'zip_path' in locals() and os.path.exists(zip_path):
            try:
                os.unlink(zip_path)
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
    - Возвращает: ZIP архив с результатами (images/ и json/ папки)
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
            
            # Создаем временный ZIP архив для результатов
            with tempfile.NamedTemporaryFile(delete=False, suffix='.zip') as zip_temp:
                results_zip_path = zip_temp.name
            
            # Создаем ZIP архив с результатами
            with zipfile.ZipFile(results_zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
                
                for image_file in image_files:
                    image_path = os.path.join(temp_dir, image_file)
                    filename_stem = Path(image_file).stem
                    
                    try:
                        # Обрабатываем изображение
                        json_data, img_path = process_single_image(image_path)
                        
                        # Добавляем информацию о файле в JSON
                        json_data['filename'] = image_file
                        json_data['processed_filename'] = f"{filename_stem}_processed.jpg"
                        
                        # Добавляем обработанное изображение в папку images/
                        if os.path.exists(img_path):
                            zipf.write(img_path, f"images/{filename_stem}_processed.jpg")
                            # Очищаем временный файл изображения
                            os.unlink(img_path)
                        else:
                            # Если изображение не было сохранено, используем оригинал
                            zipf.write(image_path, f"images/{filename_stem}_original.jpg")
                        
                        # Добавляем JSON файл в папку json/
                        json_str = json.dumps(json_data, ensure_ascii=False, indent=2)
                        zipf.writestr(f"json/{filename_stem}_results.json", json_str)
                        
                    except Exception as e:
                        # Создаем JSON с ошибкой
                        error_data = {
                            'filename': image_file,
                            'error': f"Ошибка обработки: {str(e)}",
                            'classes': [],
                            'probs': [],
                            'masks': [],
                            'obb_rows': []
                        }
                        json_str = json.dumps(error_data, ensure_ascii=False, indent=2)
                        zipf.writestr(f"json/{filename_stem}_error.json", json_str)
                        
                        # Добавляем оригинальное изображение
                        zipf.write(image_path, f"images/{filename_stem}_original.jpg")
                        
            
            # Читаем ZIP файл в память
            with open(results_zip_path, 'rb') as f:
                zip_data = f.read()
            
            # Очищаем временный ZIP файл
            os.unlink(results_zip_path)
            
            # Возвращаем ZIP архив как ответ
            return Response(
                content=zip_data,
                media_type='application/zip',
                headers={
                    'Content-Disposition': f'attachment; filename="batch_prediction_results_{Path(zip_file.filename).stem}.zip"'
                }
            )
            
    except zipfile.BadZipFile:
        raise HTTPException(
            status_code=400, 
            detail="Некорректный ZIP архив"
        )
    except Exception as e:
        # Очищаем временные файлы в случае ошибки
        if 'results_zip_path' in locals() and os.path.exists(results_zip_path):
            try:
                os.unlink(results_zip_path)
            except:
                pass
                
        raise HTTPException(
            status_code=500, 
            detail=f"Ошибка обработки архива: {str(e)}"
        )