import cv2
import numpy as np
import os
import glob
import unicodedata

# --- Helpers ---

def safe_filename(text):
    # Normalize and strip accents/unsafe chars
    text = unicodedata.normalize('NFKD', text)
    text = text.encode('ascii', 'ignore').decode('ascii')
    return text if text else "class"

def imread_unicode(path):
    data = np.fromfile(path, dtype=np.uint8)
    return cv2.imdecode(data, cv2.IMREAD_COLOR)

def process_image_center_crop_poly(
        img_path, class_id, out_img_path, out_label_path,
        dbg_path, use_crop=True, max_points = 300):
    img = imread_unicode(img_path)
    if img is None:
        print("WARNING: Failed to load", img_path)
        return
    
    orig_h, orig_w = img.shape[:2]
    debug_img = img.copy()

    # ---- Center crop region with 1/8 margin removal ----
    if use_crop:
        x0 = orig_w // 8
        y0 = orig_h // 8
        x1 = orig_w - x0
        y1 = orig_h - y0
        region = img[y0:y1, x0:x1]
    else:
        x0, y0 = 0, 0
        region = img

    crop_h, crop_w = region.shape[:2]
    crop_area = crop_h * crop_w

    # ---- Mask + Threshold ----
    gray = cv2.cvtColor(region, cv2.COLOR_BGR2GRAY)
    _, mask = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)
    mask_clean = mask

    # Ищем контуры с высокой точностью, чтобы было >500 точек
    contours, _ = cv2.findContours(mask_clean, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)

    yolo_seg_lines = []

    for cnt in contours:
        bbox_area = cv2.contourArea(cnt)

        # фильтры по площади
        if bbox_area < crop_area / 20:
            continue
        if bbox_area > crop_area * 0.9:
            continue

        # фильтр по количеству точек
        if len(cnt) < 500:
            continue

        # ----- нормализация (уменьшаем кол-во точек)
        step = max(1, len(cnt) // max_points)
        cnt_reduced = cnt[::step]  # возьмём каждую N-ную точку

        # переводим координаты: нормализуем
        coords = []
        for pt in cnt_reduced:
            gx = (pt[0][0] + x0) / orig_w
            gy = (pt[0][1] + y0) / orig_h
            coords.extend([gx, gy])

        # YOLO‑Seg строка: class_id + polygon points
        yolo_seg_lines.append(f"{class_id} " + " ".join([f"{c:.6f}" for c in coords]))

        # рисуем контур для отладки
        cv2.drawContours(debug_img, [cnt_reduced + (x0, y0)], -1, (0, 255, 0), 2)

    # ---- Save outputs ----
    with open(out_label_path, "w", encoding="utf-8") as f:
        f.write("\n".join(yolo_seg_lines))

    # cv2.imwrite(out_img_path, img)
    cv2.imwrite(dbg_path, debug_img)


# --- Driver ---
if __name__=="__main__":\
    # --- CONFIG ---
    dataset_root = "data/polygons"
    output_root = "data/polygons/results"

    # Collect class names
    class_names = sorted([d for d in os.listdir(dataset_root) if os.path.isdir(os.path.join(dataset_root, d))])
    class_to_id = {cls: idx for idx, cls in enumerate(class_names)}
    print("Class mapping:", class_to_id)

    # Ensure output structure
    for sub in ["images", "labels", "debug"]:
        os.makedirs(os.path.join(output_root, sub), exist_ok=True)

    # Main loop
    for cls in class_names:
        class_id = class_to_id[cls]
        img_paths = glob.glob(os.path.join(dataset_root, cls, "*.*"))
        for img_path in img_paths:
            fname, ext = os.path.splitext(os.path.basename(img_path))
            out_img_path   = os.path.join(output_root, "images", fname+ext)
            out_label_path = os.path.join(output_root, "labels", fname+".txt")
            dbg_path       = os.path.join(output_root, "debug", fname+ext)
            process_image_center_crop_poly(img_path, class_id, out_img_path, out_label_path, dbg_path)

    # Save classes
    with open(os.path.join(output_root, "classes.txt"), "w", encoding="utf-8") as f:
        f.write("\n".join(class_names))
    with open(os.path.join(output_root, "class_mapping.txt"), "w", encoding="utf-8") as f:
        for cls, idx in class_to_id.items():
            f.write(f"{idx} {cls}\n")

    print(f"✅ Done. Cropped annotations, masks, and debug visuals saved in {output_root}")