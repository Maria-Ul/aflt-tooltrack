import cv2
import numpy as np
import os
import glob
import unicodedata



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

def process_image(img_path, class_id, out_img_path, out_label_path, out_oriented_label_path, dbg_path):
    img = imread_unicode(img_path)

    if img is None:
        print("WARNING: Failed to load", img_path)
        return
    h, w = img.shape[:2]
    img_area = w * h

    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    _, mask = cv2.threshold(
        gray, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)
    _, mask = cv2.threshold(gray, threshold_val, 255, cv2.THRESH_BINARY_INV)\

    # Fill holes / smooth mask
    mask_clean = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, np.ones((5,5), np.uint8))
    mask_clean = cv2.morphologyEx(mask_clean, cv2.MORPH_OPEN, np.ones((3,3), np.uint8))

    contours, _ = cv2.findContours(mask_clean, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    mask_clean = np.zeros_like(mask_clean)

    yolo_lines = []
    oriented_labels = []
    debug_img = img.copy()
    for cnt in contours:
        # --- Axis-aligned bbox
        x, y, bw, bh = cv2.boundingRect(cnt)
        bbox_area = bw * bh

        # --- Oriented bbox
        rot_rect = cv2.minAreaRect(cnt)   # (center (x,y), (w,h), angle)
        box = cv2.boxPoints(rot_rect)     # 4 corner points
        box = box.astype(int)                # convert to integer

        # filter: skip very small boxes
        if bbox_area < img_area / 20:
            continue

        # filter: skip very small boxes
        if bbox_area > img_area*0.9:
            continue

        # YOLO format
        cx = (x + bw/2) / w
        cy = (y + bh/2) / h
        nw = bw / w
        nh = bh / h

        yolo_lines.append(f"{class_id} {cx:.6f} {cy:.6f} {nw:.6f} {nh:.6f}")
        oriented_labels.append(f"{class_id} {box[0][0]/w:.6f} {box[0][1]/h:.6f} {box[1][0]/w:.6f} {box[1][1]/h:.6f} {box[2][0]/w:.6f} {box[2][1]/h:.6f} {box[3][0]/w:.6f} {box[3][1]/h:.6f}")
        # Draw on debug image
        cv2.rectangle(debug_img, (x, y), (x + bw, y + bh), (0, 0, 255), 2)
        cv2.drawContours(debug_img, [box], 0, (0, 255, 0), 2)
        cv2.drawContours(mask_clean, [cnt], -1, 255, -1) 

    # Save label file
    with open(out_label_path, "w", encoding="utf-8") as f:
        f.write("\n".join(yolo_lines))

    with open(out_oriented_label_path, "w", encoding="utf-8") as f:
        f.write("\n".join(oriented_labels))

    if not cv2.imwrite(out_img_path, mask_clean):
        print("❌ Failed to save", out_img_path)
    if not cv2.imwrite(dbg_path, debug_img):
        print("❌ Failed to save", dbg_path)

if __name__=="__main__":

    # --- CONFIG ---
    dataset_root = "data/aflt_data"
    output_root = "ml/yolo_dataset"
    threshold_val = 100

    # Collect class names
    class_names = sorted([d for d in os.listdir(dataset_root) if os.path.isdir(os.path.join(dataset_root, d))])
    class_to_id = {cls: idx for idx, cls in enumerate(class_names)}
    print("Class mapping:", class_to_id)

    # Ensure output structure
    for sub in ["mask", "labels", "debug", "oriented_labels"]:
        os.makedirs(os.path.join(output_root, sub), exist_ok=True)

    # --- Main loop ---
    for cls in class_names:
        class_id = class_to_id[cls]
        img_paths = glob.glob(os.path.join(dataset_root, cls, "*.*"))

        for i, img_path in enumerate(img_paths):
            fname, ext = os.path.splitext(os.path.basename(img_path))
            out_img_path   = os.path.join(output_root, "mask", fname + ext)
            out_label_path = os.path.join(output_root, "labels", fname + ".txt")
            out_oriented_label_path = os.path.join(output_root, "oriented_labels", fname + ".txt")
            dbg_path       = os.path.join(output_root, "debug",  fname + ext) #remove after manual annotation
            process_image(img_path, class_id, out_img_path, out_label_path, out_oriented_label_path, dbg_path)

    # Save classes.txt for YOLO training / CVAT import
    with open(os.path.join(output_root, "classes.txt"), "w", encoding="utf-8") as f:
        f.write("\n".join(class_names))

    with open(os.path.join(output_root, "class_mapping.txt"), "w", encoding="utf-8") as f:
        for cls, idx in class_to_id.items():
            f.write(f"{idx} {cls}\n")

    print("✅ Done. Images, labels, and debug visuals are in", output_root)
