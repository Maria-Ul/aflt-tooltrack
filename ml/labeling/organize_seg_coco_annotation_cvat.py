import os, json
from PIL import Image

# папки
dir_path = "data/polygons/results"
images_dir = f"data/polygons/otvertka_minus"
labels_dir = f"{dir_path}/labels"

# Если у вас всегда один и тот же класс для всего датасета
CLASS_NAME = "otvertka_minus"
categories = [{"id": 1, "name": CLASS_NAME}]

images, annotations = [], []
ann_id, img_id = 0, 0

for fname in sorted(os.listdir(images_dir)):
    if not fname.lower().endswith((".jpg", ".jpeg", ".png")):
        continue

    img_path = os.path.join(images_dir, fname)
    label_path = os.path.join(labels_dir, os.path.splitext(fname)[0] + ".txt")

    w, h = Image.open(img_path).size
    img_id += 1
    images.append({
        "id": img_id,
        "file_name": fname,
        "width": w,
        "height": h
    })

    if not os.path.exists(label_path):
        continue

    with open(label_path) as f:
        for line in f:
            parts = line.strip().split()
            if not parts:
                continue

            coords = list(map(float, parts[1:]))  # YOLO: class_id skip (всегда 0)
            # нормализованные координаты -> пиксели
            polygon = [(coords[i]*w, coords[i+1]*h) for i in range(0, len(coords), 2)]
            xs, ys = zip(*polygon)
            bbox = [min(xs), min(ys), max(xs)-min(xs), max(ys)-min(ys)]
            area = bbox[2] * bbox[3]

            ann_id += 1
            annotations.append({
                "id": ann_id,
                "image_id": img_id,
                "category_id": 1,
                "segmentation": [[c for xy in polygon for c in xy]],  # flatten polygon
                "bbox": bbox,
                "area": area,
                "iscrowd": 0
            })

coco = {
    "images": images,
    "annotations": annotations,
    "categories": categories
}


os.makedirs(f"{dir_path}/annotations", exist_ok=True)
with open(f"{dir_path}//annotations/instances_default.json", "w") as f:
    json.dump(coco, f, indent=2)