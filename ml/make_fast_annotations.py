import cv2
import numpy as np
import os
import glob
import unicodedata

# --- CONFIG ---
dataset_root = "data/aflt_data"
output_root = "data/yolo_dataset"
threshold_val = 100

# Collect class names (Cyrillic included)
class_names = sorted([d for d in os.listdir(dataset_root) if os.path.isdir(os.path.join(dataset_root, d))])
class_to_id = {cls: idx for idx, cls in enumerate(class_names)}
print("Class mapping:", class_to_id)

# Ensure output structure
for sub in ["images", "labels", "debug"]:
    os.makedirs(os.path.join(output_root, sub), exist_ok=True)

# Simple ASCII-safe filename generator
def safe_filename(text):
    # Normalize and strip accents/unsafe chars
    text = unicodedata.normalize('NFKD', text)
    text = text.encode('ascii', 'ignore').decode('ascii')
    return text if text else "class"

# Reliable image loader for Unicode paths
def imread_unicode(path):
    data = np.fromfile(path, dtype=np.uint8)
    return cv2.imdecode(data, cv2.IMREAD_COLOR)

def process_image(img_path, class_id, out_img_path, out_label_path, dbg_path):
    img = imread_unicode(img_path)
    if img is None:
        print("WARNING: Failed to load", img_path)
        return
    h, w = img.shape[:2]
    img_area = w * h

    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    _, mask = cv2.threshold(gray, threshold_val, 255, cv2.THRESH_BINARY_INV)
    contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    yolo_lines = []
    debug_img = img.copy()
    for cnt in contours:
        x, y, bw, bh = cv2.boundingRect(cnt)
        bbox_area = bw * bh

        # filter: skip very small boxes
        if bbox_area < img_area / 02:
            continue

        # YOLO format
        cx = (x + bw/2) / w
        cy = (y + bh/2) / h
        nw = bw / w
        nh = bh / h
        yolo_lines.append(f"{class_id} {cx:.6f} {cy:.6f} {nw:.6f} {nh:.6f}")

        # Draw on debug image
        cv2.rectangle(debug_img, (x, y), (x + bw, y + bh), (0, 0, 255), 2)

    # Save label file
    with open(out_label_path, "w", encoding="utf-8") as f:
        f.write("\n".join(yolo_lines))

    # Save originals + debug
    cv2.imwrite(out_img_path, img)
    cv2.imwrite(dbg_path, debug_img)

# --- Main loop ---
for cls in class_names:
    class_id = class_to_id[cls]
    img_paths = glob.glob(os.path.join(dataset_root, cls, "*.*"))
    safe_cls = safe_filename(cls)
    for i, img_path in enumerate(img_paths):
        fname = f"{safe_cls}_{i:05d}"
        out_img_path   = os.path.join(output_root, "images", fname + ".jpg")
        out_label_path = os.path.join(output_root, "labels", fname + ".txt")
        dbg_path       = os.path.join(output_root, "debug",  fname + ".jpg") #remove after manual annotation
        process_image(img_path, class_id, out_img_path, out_label_path, dbg_path)

# Save classes.txt for YOLO training / CVAT import
with open(os.path.join(output_root, "classes.txt"), "w", encoding="utf-8") as f:
    f.write("\n".join(class_names))

print("✅ Done. Images, labels, and debug visuals are in", output_root)
