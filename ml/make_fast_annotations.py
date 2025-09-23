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

# --- Core Processing ---
def process_image_center_crop(
        img_path, class_id, out_img_path, out_label_path,
        out_oriented_label_path, dbg_path, use_crop = True):
    img = imread_unicode(img_path)
    if img is None:
        print("WARNING: Failed to load", img_path)
        return
    
    orig_h, orig_w = img.shape[:2]
    debug_img = img.copy()
    global_mask = np.zeros((orig_h, orig_w), dtype=np.uint8)

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
    cv2.imwrite('gray.png', gray)
    _, mask = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)
    # # Fill holes / smooth mask
    # mask_clean = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, np.ones((5,5), np.uint8))
    # mask_clean = cv2.morphologyEx(mask_clean, cv2.MORPH_OPEN, np.ones((3,3), np.uint8))
    mask_clean = mask
    contours, _ = cv2.findContours(mask_clean, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    # ---- Annotations storage ----
    yolo_lines = []
    oriented_labels = []

    for cnt in contours:
        # axis aligned box (relative to crop)
        x, y, bw, bh = cv2.boundingRect(cnt)
        bbox_area = bw * bh

        # skip weird boxes
        if bbox_area < crop_area / 20:
            continue
        if bbox_area > crop_area * 0.9:
            continue

        global_cnt = cnt.astype(np.int32) + np.array([[x0, y0]], dtype=np.int32)

        # ---- Translate coordinates back to full image ----
        gx, gy = x + x0, y + y0

        # Oriented box in global coordinates
        rot_rect = cv2.minAreaRect(global_cnt)
        box = cv2.boxPoints(rot_rect).astype(int)

        # YOLO normalized coords
        cx = (gx + bw/2) / orig_w
        cy = (gy + bh/2) / orig_h
        nw = bw / orig_w
        nh = bh / orig_h

        yolo_lines.append(f"{class_id} {cx:.6f} {cy:.6f} {nw:.6f} {nh:.6f}")
        oriented_labels.append(
            f"{class_id} " + " ".join([f"{px/orig_w:.6f} {py/orig_h:.6f}" for px,py in box])
        )

        # Draw for debug
        cv2.rectangle(debug_img, (gx, gy), (gx+bw, gy+bh), (0,0,255), 2)
        cv2.drawContours(debug_img, [box], 0, (0,255,0), 2)
        cv2.drawContours(global_mask, [global_cnt], -1, 255, -1)

    # ---- Save outputs ----
    with open(out_label_path, "w", encoding="utf-8") as f:
        f.write("\n".join(yolo_lines))
    with open(out_oriented_label_path, "w", encoding="utf-8") as f:
        f.write("\n".join(oriented_labels))

    cv2.imwrite(out_img_path, global_mask)
    cv2.imwrite(dbg_path, debug_img)

# --- Driver ---
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

    # Main loop
    for cls in class_names:
        class_id = class_to_id[cls]
        img_paths = glob.glob(os.path.join(dataset_root, cls, "*.*"))
        for img_path in img_paths:
            fname, ext = os.path.splitext(os.path.basename(img_path))
            out_img_path   = os.path.join(output_root, "mask", fname+ext)
            out_label_path = os.path.join(output_root, "labels", fname+".txt")
            out_oriented_label_path = os.path.join(output_root, "oriented_labels", fname+".txt")
            dbg_path       = os.path.join(output_root, "debug", fname+ext)
            process_image_center_crop(img_path, class_id, out_img_path, out_label_path, out_oriented_label_path, dbg_path)

    # Save classes
    with open(os.path.join(output_root, "classes.txt"), "w", encoding="utf-8") as f:
        f.write("\n".join(class_names))
    with open(os.path.join(output_root, "class_mapping.txt"), "w", encoding="utf-8") as f:
        for cls, idx in class_to_id.items():
            f.write(f"{idx} {cls}\n")

    print(f"✅ Done. Cropped annotations, masks, and debug visuals saved in {output_root}")