import os
import shutil
from pathlib import Path
from sklearn.model_selection import train_test_split
from tqdm import tqdm

# --- НАСТРОЙКИ ---
# Путь к вашему исходному датасету
source_dir = Path("datasets/aflt_tools_yolo_seg_validated_rare")
# Директория для подготовленного датасета
output_dir = Path("datasets/yolo_seg_dataset_no_side_view_no_rep_w_group_rare")
# Соотношение для разделения данных (80% train, 20% val)
train_ratio = 0.8
# -----------------

# Пути к исходным данным
source_images_dir = source_dir / "images"
source_labels_dir = source_dir / "labels_seg_hand_validated"

# Создаем выходные директории
(output_dir / "images/train").mkdir(parents=True, exist_ok=True)
(output_dir / "images/val").mkdir(parents=True, exist_ok=True)
(output_dir / "labels/train").mkdir(parents=True, exist_ok=True)
(output_dir / "labels/val").mkdir(parents=True, exist_ok=True)

all_image_paths = []

print("Поиск изображений...")
# Рекурсивно ищем все файлы изображений
for ext in ["*.JPG", "*.jpg", "*.jpeg", "*.png"]:
    all_image_paths.extend(source_images_dir.rglob(ext))

print(f"Найдено {len(all_image_paths)} изображений. Проверка наличия меток...")

# Фильтруем изображения, для которых есть соответствующие метки
valid_image_paths = []
for img_path in tqdm(all_image_paths, desc="Проверка меток"):
    # Формируем относительный путь от папки 'images' (например, 'class_A/image01.jpg')
    relative_path = img_path.relative_to(source_images_dir)
    # Создаем ожидаемый путь к файлу метки, заменяя расширение на .txt
    expected_label_path = source_labels_dir / relative_path.with_suffix('.txt')

    if expected_label_path.exists():
        valid_image_paths.append(img_path)
    else:
        print(f"ВНИМАНИЕ: Не найдена метка для изображения {img_path}")

print(f"Найдено {len(valid_image_paths)} изображений с соответствующими метками.")

# Если не найдено ни одного валидного изображения, выходим
if not valid_image_paths:
    print("Не найдено ни одной пары изображение-метка. Завершение работы.")
    exit()

# Разделяем на train/val
train_paths, val_paths = train_test_split(
    valid_image_paths,
    train_size=train_ratio,
    random_state=42,  # для воспроизводимости
    shuffle=True
)

print(f"Разделение данных: {len(train_paths)} в train, {len(val_paths)} в val.")


def copy_files(file_paths, split_name):
    """
    Копирует изображения и соответствующие им метки в нужную директорию,
    добавляя префикс класса к имени файла.
    """
    print(f"\nКопирование {split_name} данных...")
    for img_path in tqdm(file_paths, desc=f"Копирование {split_name}"):
        # --- МОДИФИКАЦИЯ НАЧАЛАСЬ ---

        # 1. Получаем имя класса из родительской директории
        # Например, для '.../images/car/001.jpg', parent.name будет 'car'
        class_prefix = img_path.parent.name

        # 2. Создаем новое, уникальное имя файла
        new_img_name = f"{class_prefix}_{img_path.name}"
        new_label_name = f"{class_prefix}_{img_path.stem}.txt"

        # 3. Находим соответствующий файл метки (так же, как при фильтрации)
        relative_path = img_path.relative_to(source_images_dir)
        label_path = source_labels_dir / relative_path.with_suffix('.txt')

        # 4. Определяем пути назначения с новыми именами
        dest_img_path = output_dir / f"images/{split_name}" / new_img_name
        dest_label_path = output_dir / f"labels/{split_name}" / new_label_name

        # 5. Копируем файлы
        shutil.copy(img_path, dest_img_path)
        shutil.copy(label_path, dest_label_path)
        # --- МОДИФИКАЦИЯ ЗАКОНЧИЛАСЬ ---


# Копируем файлы
copy_files(train_paths, "train")
copy_files(val_paths, "val")

print("\nПодготовка данных завершена!")