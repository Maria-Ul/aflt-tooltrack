import os
import shutil
import glob

# --- Paths ---
src_images = r"D:\projects\aflt-tooltrack\data\yolo_dataset\images"
src_labels = r"D:\projects\aflt-tooltrack\data\yolo_dataset\labels"
src_classes = "./data/yolo_dataset/classes.txt"
out_dir = "archive"   # final export folder

# --- Create output dirs ---
os.makedirs(out_dir, exist_ok=True)
subset = "train"
subset_dir = os.path.join(out_dir, f"obj_{subset}_data")
os.makedirs(subset_dir, exist_ok=True)

# --- Copy images & labels with correct alignment ---
img_paths = sorted(glob.glob(os.path.join(src_images, "*.*")))
train_txt_lines = []

for img_path in img_paths:
    fname = os.path.basename(img_path)
    name, ext = os.path.splitext(fname)

    label_src = os.path.join(src_labels, f"{name}.txt")
    label_dst = os.path.join(subset_dir, f"{name}.txt")
    img_dst = os.path.join(subset_dir, fname)

    shutil.copy(img_path, img_dst)
    if os.path.exists(label_src):
        shutil.copy(label_src, label_dst)
    else:
        print("⚠️ No label for", fname)

    # Add entry to train.txt
    train_txt_lines.append(f"{os.path.basename(subset_dir)}/{fname}")

# --- Write train.txt (relative paths) ---
with open(os.path.join(out_dir, "train.txt"), "w", encoding="utf-8") as f:
    f.write("\n".join(train_txt_lines))

# --- Write obj.names ---
names_dst = os.path.join(out_dir, "obj.names")
shutil.copy(src_classes, names_dst)

# --- Write obj.data ---
with open(os.path.join(out_dir, "obj.data"), "w", encoding="utf-8") as f:
    f.write(f"classes = {len(open(src_classes).read().splitlines())}\n")
    f.write("names = obj.names\n")
    f.write("train = train.txt\n")
    f.write("backup = backup/\n")