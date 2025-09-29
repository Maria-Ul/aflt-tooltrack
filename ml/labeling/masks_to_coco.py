import argparse
import json
import os
import re
from pathlib import Path

import cv2
import numpy as np
from tqdm import tqdm

# ==============================================================================
# СПИСОК ВАШИХ КЛАССОВ (ВАЖНО: порядок должен соответствовать YOLO class ID 0, 1, 2...)
# ==============================================================================
CLASS_NAMES = [
    "bokorezy", "key_rozgkovy_nakidnoy_3_4", "kolovorot", "otkryvashka_oil_can",
    "otvertka_minus", "otvertka_offset_cross", "otvertka_plus", "passatigi",
    "passatigi_controvochny", "razvodnoy_key", "sharnitsa"
]

# ==============================================================================
# Вспомогательные функции из вашего скрипта (без изменений)
# ==============================================================================
EXTS = {".jpg", ".jpeg", ".png", ".bmp", ".tif", ".tiff", ".JPG", ".JPEG", ".PNG", ".BMP"}

def list_images(root: Path):
    return [p for p in root.rglob("*") if p.suffix in EXTS]

def load_bin_masks_for_image(bin_dir: Path, rel_img_path: Path):
    """
    Загружает бинарные маски для одного изображения.
    rel_img_path: путь вида <class_name>/<image_name.ext>
    Ищет соответствующие маски в папках bin_dir/train/... и bin_dir/val/...
    """
    # Из относительного пути к изображению извлекаем имя класса и основу имени файла
    # Пример: из "bokorezy/DSCN4736.jpg" получаем class_name="bokorezy", image_stem="DSCN4736"
    class_name = rel_img_path.parent.name
    image_stem = rel_img_path.stem

    # Формируем два потенциальных пути к папке с масками
    path_train = bin_dir / "train" / class_name / image_stem
    path_val = bin_dir / "val" / class_name / image_stem

    # Проверяем, какой из путей существует
    base_dir = None
    if path_train.is_dir():
        base_dir = path_train
    elif path_val.is_dir():
        base_dir = path_val
    
    # Если папка с масками не найдена ни в train, ни в val, возвращаем пустой результат
    if base_dir is None:
        return [], []
    
    # Дальнейшая логика остается той же, но теперь она работает с правильным путем
    mask_files = sorted(base_dir.glob(f"{image_stem}_inst*_cls*.png"))
    bin_masks, classes = [], []
    for p in mask_files:
        m = cv2.imread(str(p), cv2.IMREAD_GRAYSCALE)
        if m is None:
            continue
        bin_masks.append((m > 127).astype(np.uint8))
        m_cls = re.search(r"_cls(\d+)\.png$", p.name)
        if m_cls:
            classes.append(int(m_cls.group(1)))
    return bin_masks, classes

# ==============================================================================
# МОДИФИЦИРОВАННАЯ ФУНКЦИЯ КОНВЕРТАЦИИ МАСКИ В ПОЛИГОН
# ==============================================================================
def mask_to_poly(mask: np.ndarray,
                 max_pts: int = 150,
                 min_area: float = 10.0,
                 simplify_eps: float = 0.0):
    """
    Конвертирует бинарную маску в полигон с заданным числом точек.
    Возвращает точки в абсолютных пиксельных координатах.
    """
    # Находим контуры. CHAIN_APPROX_NONE извлекает ВСЕ точки контура.
    cnts, _ = cv2.findContours(mask.astype(np.uint8),
                               cv2.RETR_EXTERNAL,
                               cv2.CHAIN_APPROX_NONE)
    if not cnts:
        return None

    cnt = max(cnts, key=cv2.contourArea)
    if cv2.contourArea(cnt) < min_area:
        return None

    # Опционально: мягкое упрощение по RDP. Для высокой детализации держите eps=0.
    if simplify_eps > 0:
        eps = simplify_eps * cv2.arcLength(cnt, True)
        approx = cv2.approxPolyDP(cnt, eps, True)
        if len(approx) >= 3:
            cnt = approx

    pts = cnt.reshape(-1, 2).astype(np.float32)

    # Если точек больше лимита — равномерно прореживаем.
    # Это основной способ контроля детализации.
    if max_pts is not None and len(pts) > max_pts:
        idx = np.linspace(0, len(pts) - 1, num=max_pts, dtype=np.int32)
        pts = pts[idx]

    if len(pts) < 3:
        return None

    return pts


# ==============================================================================
# ОСНОВНАЯ ЛОГИКА
# ==============================================================================
def main():

    """
    python masks_to_coco.py --images_root datasets/yolo_group_part2/images_part2 --bin_dir datasets/yolo_group_part2/masks_bin_l
    """

    parser = argparse.ArgumentParser(description="Конвертация бинарных масок в COCO JSON формат.")
    parser.add_argument("--images_root", type=str, required=True, help="Корень с изображениями: .../images")
    parser.add_argument("--bin_dir", type=str, required=True, help="Каталог с сохраненными бинарными масками (PNG)")
    parser.add_argument("--output_json", type=str, default="aflt_tools_all.json", help="Путь для сохранения итогового COCO JSON файла")
    
    # --- Параметры для контроля детализации полигонов ---
    parser.add_argument("--max_pts", type=int, default=200, help="Макс. кол-во точек в полигоне (основной параметр)")
    parser.add_argument("--simplify_eps", type=float, default=0.0,
                        help="Коэффициент для RDP-упрощения (0 — выключить, 0.001 — слабое). Рекомендуется 0.")
    
    parser.add_argument("--min_area", type=float, default=10.0, help="Мин. площадь контура (px) для фильтрации мусора")
    parser.add_argument("--limit", type=int, default=0, help="Ограничить число изображений для быстрой проверки")
    args = parser.parse_args()

    images_root = Path(args.images_root).resolve()
    bin_dir = Path(args.bin_dir).resolve()

    assert images_root.exists(), f"Папка с изображениями не найдена: {images_root}"
    assert bin_dir.exists(), f"Папка с бинарными масками не найдена: {bin_dir}"

    imgs = list_images(images_root)
    if not imgs:
        raise SystemExit(f"В {images_root} не найдено изображений.")
    if args.limit > 0:
        imgs = imgs[:args.limit]

    # --- Инициализация COCO структуры ---
    coco_data = {
        "images": [],
        "annotations": [],
        "categories": []
    }

    # Создаем категории
    class_name_to_id = {name: i + 1 for i, name in enumerate(CLASS_NAMES)}
    for name, cat_id in class_name_to_id.items():
        coco_data["categories"].append({
            "id": cat_id,
            "name": name,
            "supercategory": "tool"
        })
    # Создаем маппинг из YOLO ID (0-10) в COCO ID (1-11)
    yolo_id_to_coco_id = {i: class_name_to_id[name] for i, name in enumerate(CLASS_NAMES)}


    image_id_counter = 1
    annotation_id_counter = 1

    pbar = tqdm(imgs, desc="Converting to COCO")
    for img_path in pbar:
        rel_path = img_path.relative_to(images_root)

        # Получаем размеры изображения
        im = cv2.imread(str(img_path))
        if im is None:
            print(f"Warning: Cannot read image {img_path}, skipping.")
            continue
        H, W = im.shape[:2]

        # Добавляем информацию об изображении в COCO
        image_entry = {
            "id": image_id_counter,
            "file_name": str(rel_path), # CVAT лучше работает с относительными путями
            "width": W,
            "height": H
        }
        coco_data["images"].append(image_entry)

        # Загружаем маски для этого изображения
        bin_masks, yolo_class_ids = load_bin_masks_for_image(bin_dir, rel_path)

        for mask, yolo_cls_id in zip(bin_masks, yolo_class_ids):
            # Конвертируем маску в полигон
            poly_pts = mask_to_poly(mask, args.max_pts, args.min_area, args.simplify_eps)
            
            if poly_pts is None or len(poly_pts) < 3:
                continue
            
            # --- Создаем аннотацию в формате COCO ---
            segmentation = [poly_pts.flatten().tolist()] # [[x1, y1, x2, y2, ...]]
            
            # Bbox [x, y, width, height]
            x, y, w, h = cv2.boundingRect(mask)
            bbox = [int(x), int(y), int(w), int(h)]
            
            # Area
            area = float(cv2.contourArea(poly_pts.astype(np.int32)))

            # Получаем COCO category_id
            coco_cat_id = yolo_id_to_coco_id.get(yolo_cls_id)
            if coco_cat_id is None:
                print(f"Warning: Unknown YOLO class id {yolo_cls_id} for image {rel_path}, skipping annotation.")
                continue

            annotation_entry = {
                "id": annotation_id_counter,
                "image_id": image_id_counter,
                "category_id": coco_cat_id,
                "segmentation": segmentation,
                "area": area,
                "bbox": bbox,
                "iscrowd": 0
            }
            coco_data["annotations"].append(annotation_entry)
            annotation_id_counter += 1
        
        image_id_counter += 1

    # Сохраняем итоговый JSON
    print(f"\nSaving COCO data to {args.output_json}...")
    with open(args.output_json, "w", encoding="utf-8") as f:
        json.dump(coco_data, f, indent=4)
    
    print("Done.")
    print(f"  Total images: {len(coco_data['images'])}")
    print(f"  Total annotations: {len(coco_data['annotations'])}")


if __name__ == "__main__":
    main()