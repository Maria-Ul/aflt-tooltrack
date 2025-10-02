# train_overlap_cls.py
import os
import random
import shutil
from pathlib import Path
from glob import glob
import cv2
import numpy as np
import albumentations as A
from ultralytics import YOLO
from tqdm import tqdm

random.seed(42)
np.random.seed(42)

# 1) Путь к исходным данным
SRC_OVERLAP = Path('datasets/group_overlapping_classifier_dataset/group_overlapping')  # 70
SRC_CLEAN   = Path('datasets/group_overlapping_classifier_dataset/group_not_overlapping')    # 400
OUT_ROOT    = Path('datasets/yolo_classsify_overlaps') # будет создано

SPLITS = {'train': 0.8, 'val': 0.1, 'test': 0.1}
IMG_EXTS = ('*.jpg', '*.JPG' ,'*.jpeg','*.png','*.bmp','*.tif','*.tiff','*.webp')

# 2) Сбор путей к картинкам
def collect_images(d: Path):
    files = []
    for ext in IMG_EXTS:
        files += list(d.glob(ext))
    return sorted(files)

def make_dirs(root: Path):
    for split in ['train','val','test']:
        for cls in ['overlap','clean']:
            (root / split / cls).mkdir(parents=True, exist_ok=True)

def stratified_split(overlap_paths, clean_paths, splits=SPLITS):
    def split(lst, r_train, r_val):
        n = len(lst)
        n_train = int(n * r_train)
        n_val   = int(n * r_val)
        random.shuffle(lst)
        return lst[:n_train], lst[n_train:n_train+n_val], lst[n_train+n_val:]
    r_train = splits['train']
    r_val   = splits['val']
    over_train, over_val, over_test = split(list(overlap_paths), r_train, r_val)
    clean_train, clean_val, clean_test = split(list(clean_paths), r_train, r_val)
    return {
        'train': {'overlap': over_train, 'clean': clean_train},
        'val':   {'overlap': over_val,   'clean': clean_val},
        'test':  {'overlap': over_test,  'clean': clean_test},
    }

def copy_list(paths, dst_dir: Path):
    for p in paths:
        shutil.copy2(p, dst_dir / p.name)

# Лёгкие, “безопасные” для сцены аугментации (не меняют семантику перекрытия)
AUG = A.Compose([
    A.Rotate(limit=8, border_mode=cv2.BORDER_REFLECT_101, p=0.6),
    A.Affine(scale=(0.95, 1.05), shear=(-4,4), translate_percent=(0.0, 0.02), p=0.6),
    A.RandomBrightnessContrast(0.1, 0.1, p=0.5),
    A.HueSaturationValue(5, 10, 5, p=0.3),
    A.GaussNoise(var_limit=(3.0, 15.0), p=0.2),
    A.MotionBlur(blur_limit=3, p=0.15),
], p=1.0)

def read_img(path):
    img = cv2.imread(str(path), cv2.IMREAD_COLOR)
    if img is None:
        raise RuntimeError(f'Failed to read {path}')
    return img

def save_img(path, img):
    cv2.imwrite(str(path), img, [cv2.IMWRITE_JPEG_QUALITY, 95])

def oversample_with_aug(src_dir: Path, target_count: int):
    imgs = list(src_dir.glob('*'))
    imgs = [p for p in imgs if p.suffix.lower() in ('.jpg','.jpeg','.png','.bmp','.tif','.tiff','.webp')]
    if not imgs:
        return
    cur = len(imgs)
    idx = 0
    pbar = tqdm(total=max(0, target_count - cur), desc=f'Oversample {src_dir.name}')
    while cur < target_count:
        src = imgs[idx % len(imgs)]
        img = read_img(src)
        aug = AUG(image=img)['image']
        out_name = f'{src.stem}_aug{cur- len(imgs) + 1}.jpg'
        save_img(src_dir / out_name, aug)
        cur += 1
        idx += 1
        pbar.update(1)
    pbar.close()

def main():
    # Сбор данных
    over_paths = collect_images(SRC_OVERLAP)
    clean_paths = collect_images(SRC_CLEAN)
    assert len(over_paths) > 0 and len(clean_paths) > 0, "Нет изображений в исходных папках"

    # Стратифицированный сплит
    split = stratified_split(over_paths, clean_paths, SPLITS)
    make_dirs(OUT_ROOT)

    # Копирование
    for sp in ['train','val','test']:
        for cls in ['overlap','clean']:
            copy_list(split[sp][cls], OUT_ROOT / sp / cls)

    # Балансировка train через oversampling позитива
    train_over_dir = OUT_ROOT / 'train' / 'overlap'
    train_clean_dir = OUT_ROOT / 'train' / 'clean'
    n_pos = len(list(train_over_dir.glob('*')))
    n_neg = len(list(train_clean_dir.glob('*')))
    if n_pos < n_neg:
        oversample_with_aug(train_over_dir, target_count=n_neg)
    elif n_neg < n_pos:
        # На всякий: обычно это не ваш случай
        oversample_with_aug(train_clean_dir, target_count=n_pos)

    # Обучение
    model_name = 'yolo11m-cls.pt'
    try:
        model = YOLO(model_name)
    except Exception:
        print("Не удалось загрузить yolo11n-cls.pt, пробуем yolov8n-cls.pt")
        model = YOLO('yolov8n-cls.pt')

    results = model.train(
        data=str(OUT_ROOT),   # структура с train/val/test
        imgsz=640,
        epochs=60,
        batch=-1,
        patience=12,
        optimizer='AdamW',
        lr0=1e-3,
        weight_decay=5e-4,
        project='runs/cls',
        name='overlap_y11n',
        verbose=True,
        seed=42,
        cache=True
    )

    # Валидация на test (опционально)
    # Ultralytics для классификации выводит top-1/top-5; для порогов лучше сделать свой отчёт
    # print("\nГотово. Лучшие веса:", results.best)
    # Для быстрой проверки:
    # model.val(data=str(OUT_ROOT), split='test', imgsz=640)  # может не работать во всех версиях

if __name__ == '__main__':
    main()