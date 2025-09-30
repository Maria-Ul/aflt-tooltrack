from __future__ import annotations
import argparse, os, cv2, numpy as np
from pathlib import Path
from ultralytics import SAM
from tqdm import tqdm
import re
import json

EXTS = {".jpg", ".jpeg", ".png", ".bmp", ".tif", ".tiff", ".JPG", ".JPEG", ".PNG", ".BMP"}

CLASS_NAMES = [
    "bokorezy", "key_rozgkovy_nakidnoy_3_4", "kolovorot", "otkryvashka_oil_can",
    "otvertka_minus", "otvertka_offset_cross", "otvertka_plus", "passatigi",
    "passatigi_controvochny", "razvodnoy_key", "sharnitsa"
]


"""

python boxes_to_sam_masks.py \
  --images_root datasets/yolo_group_part2/images_part2 \
  --labels_root datasets/yolo_group_part2/labels_boxes_part2 \
  --out_root datasets/yolo_group_part2/labels_seg_Saml \
  --sam_weights sam_l.pt \
  --device 0 \
  --mask_thresh 0.60 \
  --tta_gamma "1.0,0.85,1.2" \
  --fill_holes \
  --post_close 3 \
  --largest_cc \
  --clip_to_bbox \
  --max_pts 200 \
  --simplify_eps 0.0 \
  --save_vis \
  --vis_dir datasets/yolo_group_part2/vis_l \
  --save_bin \
  --bin_dir datasets/yolo_group_part2/masks_bin_l
"""

def parse_args():
    ap = argparse.ArgumentParser(description="Конвертация YOLO bbox -> YOLO seg через SAM + сохранение визуализаций/масок")
    ap.add_argument("--images_root", type=str, required=True, help="Корень с изображениями: .../images (внутри train/val/...)")
    ap.add_argument("--labels_root", type=str, required=True, help="Корень с bbox-лейблами: .../labels (внутри train/val/...)")
    ap.add_argument("--out_root", type=str, required=True, help="Куда писать seg-лейблы (.txt): .../labels (внутри train/val/...)")
    ap.add_argument("--sam_weights", type=str, default="sam_b.pt", help="SAM веса (sam_b.pt/sam_l.pt)")
    ap.add_argument("--device", type=str, default="0", help="GPU id или 'cpu'")
    ap.add_argument("--max_pts", type=int, default=3000, help="Макс. кол-во точек в полигоне (равномерное прореживание)")
    ap.add_argument("--min_area", type=float, default=10.0, help="Мин. площадь контура (px) для фильтрации мусора")

    # Визуализация/маски
    ap.add_argument("--save_vis", action="store_true", help="Сохранять визуализации с наложенными масками")
    ap.add_argument("--vis_dir", type=str, default=None, help="Каталог для визуализаций (если не задан, возьмем рядом с out_root)")
    ap.add_argument("--alpha", type=float, default=0.45, help="Прозрачность масок на визуализации (0..1)")
    ap.add_argument("--draw_contours", action="store_true", help="Рисовать контуры масок")
    ap.add_argument("--draw_boxes", action="store_true", help="Рисовать исходные боксы")

    ap.add_argument("--save_bin", action="store_true", help="Сохранять бинарные маски по экземплярам (PNG)")
    ap.add_argument("--bin_dir", type=str, default=None, help="Каталог для бинарных масок")

    ap.add_argument("--clip_to_bbox", action="store_true", help="Обрезать маску по исходному боксу (рекомендуется)")
    ap.add_argument("--limit", type=int, default=0, help="Ограничить число изображений (для быстрой проверки)")
    ap.add_argument("--use_saved_bin", action="store_true",
                    help="Брать маски из --bin_dir (PNG) вместо запуска SAM")
    ap.add_argument("--simplify_eps", type=float, default=0.0001,
                    help="Доля периметра для RDP-упрощения (0 — выкл). Пример: 0.001")
    
    ap.add_argument("--mask_thresh", type=float, default=0.6, help="Порог для бинаризации SAM-проб (0..1)")
    ap.add_argument("--post_close", type=int, default=0, help="Размер ядра closing (px); 0 — выкл")
    ap.add_argument("--post_open", type=int, default=0, help="Размер ядра opening (px); 0 — выкл")
    ap.add_argument("--fill_holes", action="store_true", help="Заполнять дырки в маске")
    ap.add_argument("--largest_cc", action="store_true", help="Оставлять крупнейшую компоненту связности")
    ap.add_argument("--tta_gamma", type=str, default="1.0", help="Список гамма-факторов для TTA, через запятую. Пример: 1.0,0.85,1.2")
    ap.add_argument("--refine_grabcut", action="store_true", help="Уточнять маску GrabCut’ом")
    ap.add_argument("--grabcut_iter", type=int, default=3, help="Итерации GrabCut")
    ap.add_argument("--grabcut_ring", type=int, default=3, help="Толщина кольца неопределенности для инициализации GrabCut")
    return ap.parse_args()

def apply_gamma(im_bgr: np.ndarray, gamma: float) -> np.ndarray:
    if abs(gamma - 1.0) < 1e-6:
        return im_bgr
    inv = 1.0 / max(gamma, 1e-6)
    # LUT быстрее
    table = np.array([(i / 255.0) ** inv * 255 for i in range(256)]).astype(np.uint8)
    return cv2.LUT(im_bgr, table)

def fill_holes(mask: np.ndarray) -> np.ndarray:
    # Заполнение дыр: заливаем фон с границы, оставшееся = дыры
    h, w = mask.shape
    ff = np.zeros((h + 2, w + 2), np.uint8)
    inv = (mask == 0).astype(np.uint8) * 255  # фон=255, объект=0
    cv2.floodFill(inv, ff, (0, 0), 128)       # заполняем внешний фон 255 -> 128
    holes = (inv == 255).astype(np.uint8)     # 255 остались только "дырки" внутри объекта
    return np.clip(mask + holes, 0, 1).astype(np.uint8)

def keep_largest_cc(mask: np.ndarray) -> np.ndarray:
    num, lab = cv2.connectedComponents(mask.astype(np.uint8))
    if num <= 2:
        return mask
    counts = np.bincount(lab.ravel())
    counts[0] = 0
    k = np.argmax(counts)
    return (lab == k).astype(np.uint8)

def morph(mask: np.ndarray, k_close: int = 0, k_open: int = 0) -> np.ndarray:
    m = mask.copy()
    if k_close > 0:
        k = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (k_close, k_close))
        m = cv2.morphologyEx(m, cv2.MORPH_CLOSE, k, iterations=1)
    if k_open > 0:
        k = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (k_open, k_open))
        m = cv2.morphologyEx(m, cv2.MORPH_OPEN, k, iterations=1)
    return m

def refine_with_grabcut(im_bgr: np.ndarray, init_mask: np.ndarray, ring: int = 3, iters: int = 3) -> np.ndarray:
    # Формируем маску для GrabCut: BG(0), FG(1), PR_BG(2), PR_FG(3)
    gc_mask = np.full(init_mask.shape, cv2.GC_PR_BGD, dtype=np.uint8)
    fg = cv2.erode(init_mask, cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (max(1, ring), max(1, ring))), iterations=1)
    dil = cv2.dilate(init_mask, cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (max(1, ring*2+1), max(1, ring*2+1))), iterations=1)
    border = np.clip(dil - init_mask, 0, 1)
    gc_mask[fg > 0] = cv2.GC_FGD
    gc_mask[(init_mask == 0) & (border == 0)] = cv2.GC_BGD  # далеко снаружи — фон
    # вокруг границы — PR классы оставляем как есть

    bgdModel = np.zeros((1, 65), np.float64)
    fgdModel = np.zeros((1, 65), np.float64)
    cv2.grabCut(im_bgr, gc_mask, None, bgdModel, fgdModel, iters, cv2.GC_INIT_WITH_MASK)
    out = np.where((gc_mask == cv2.GC_FGD) | (gc_mask == cv2.GC_PR_FGD), 1, 0).astype(np.uint8)
    return out

def list_images(root: Path):
    return [p for p in root.rglob("*") if p.suffix in EXTS]

def mask_to_poly_xyn(mask: np.ndarray, W: int, H: int,
                     max_pts: int | None = 3000,
                     min_area: float = 10.0,
                     simplify_eps: float | None = None):
    # Контур без упрощения — все пиксельные точки
    cnts, _ = cv2.findContours(mask.astype(np.uint8),
                               cv2.RETR_EXTERNAL,
                               cv2.CHAIN_APPROX_NONE)
    if not cnts:
        return None

    cnt = max(cnts, key=cv2.contourArea)
    if cv2.contourArea(cnt) < min_area:
        return None

    pts = cnt.reshape(-1, 2).astype(np.float32)

    # Удаляем подряд идущие дубликаты (иногда бывают)
    if len(pts) > 1:
        dif = np.diff(pts, axis=0, prepend=pts[:1])
        keep = np.any(dif != 0, axis=1)
        keep[0] = True  # сохраняем первую точку
        pts = pts[keep]

    # Опционально: мягко упростить по RDP, если очень зубчатые края
    if simplify_eps is not None and simplify_eps > 0:
        eps = simplify_eps * cv2.arcLength(cnt, True)
        approx = cv2.approxPolyDP(cnt, eps, True).reshape(-1, 2).astype(np.float32)
        if len(approx) >= 3:
            pts = approx

    # Если точек больше лимита — равномерно прореживаем, без геом. упрощения
    if max_pts is not None and len(pts) > max_pts:
        idx = np.linspace(0, len(pts) - 1, num=max_pts, dtype=np.int32)
        pts = pts[idx]

    if len(pts) < 3:
        return None

    # Нормируем
    pts[:, 0] /= float(W)
    pts[:, 1] /= float(H)
    return pts

def clip_mask_to_box(mask: np.ndarray, box_xyxy, H: int, W: int):
    x1, y1, x2, y2 = box_xyxy
    xi1 = max(0, int(np.floor(x1)))
    yi1 = max(0, int(np.floor(y1)))
    xi2 = min(W, int(np.ceil(x2)))
    yi2 = min(H, int(np.ceil(y2)))
    if xi1 >= xi2 or yi1 >= yi2:
        mask[:] = 0
        return mask
    # Обнуляем все вне бокса
    mask[:yi1, :] = 0
    mask[yi2:, :] = 0
    mask[:, :xi1] = 0
    mask[:, xi2:] = 0
    return mask

def class_color_bgr(cls_id: int):
    # детерминированный «яркий» цвет на класс
    rng = np.random.default_rng(cls_id + 12345)
    rgb = rng.integers(60, 255, size=3, dtype=np.uint8)
    bgr = (int(rgb[2]), int(rgb[1]), int(rgb[0]))
    return bgr

def overlay_masks(im_bgr: np.ndarray, masks: list[np.ndarray], classes: list[int], boxes_xyxy: list[list[float]],
                  alpha: float = 0.45, draw_contours: bool = False, draw_boxes: bool = False) -> np.ndarray:
    
    # Копируем исходное изображение для рисования контуров и боксов
    out_final = im_bgr.copy()
    
    # Создаем пустой (черный) слой для цветных масок
    color_overlay = np.zeros_like(im_bgr, dtype=np.uint8)

    # Сначала рисуем все маски на этом отдельном слое
    for m, cls_id in zip(masks, classes):
        color = class_color_bgr(cls_id)
        color_overlay[m > 0] = color

    # Создаем маску, где есть хоть какой-то объект
    # Это нужно, чтобы фон остался нетронутым при смешивании
    combined_mask = np.any(np.stack(masks, axis=-1), axis=-1)

    # Теперь смешиваем ОДИН РАЗ исходное изображение и слой с масками
    # Смешивание происходит только там, где есть маски
    roi = im_bgr[combined_mask]
    colored_roi = color_overlay[combined_mask]
    blended_roi = cv2.addWeighted(colored_roi, alpha, roi, 1.0 - alpha, 0)
    out_final[combined_mask] = blended_roi

    # Теперь поверх уже смешанного изображения рисуем контуры и боксы
    for m, cls_id, box in zip(masks, classes, boxes_xyxy):
        color = class_color_bgr(cls_id)

        if draw_contours:
            cnts, _ = cv2.findContours(m.astype(np.uint8), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            cv2.drawContours(out_final, cnts, -1, color, thickness=2)

        if draw_boxes:
            x1, y1, x2, y2 = map(int, box)
            cv2.rectangle(out_final, (x1, y1), (x2, y2), color, 1)
            label = f"{cls_id}"
            cv2.putText(out_final, label, (x1 + 3, max(12, y1 - 5)), cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 1, cv2.LINE_AA)

    return out_final

def main():
    args = parse_args()
    images_root = Path(args.images_root).resolve()
    labels_root = Path(args.labels_root).resolve()
    out_root    = Path(args.out_root).resolve()
    out_root.mkdir(parents=True, exist_ok=True)

    assert images_root.exists(), f"Нет папки {images_root}"
    assert labels_root.exists(), f"Нет папки {labels_root}"

    # Директории для визуализаций и бинарных масок
    vis_dir = Path(args.vis_dir) if args.vis_dir else (out_root.parent / "sam_vis")
    bin_dir = Path(args.bin_dir) if args.bin_dir else (out_root.parent / "sam_masks_bin")
    if args.save_vis:
        vis_dir.mkdir(parents=True, exist_ok=True)
    if args.save_bin:
        bin_dir.mkdir(parents=True, exist_ok=True)
    if args.use_saved_bin:
        assert bin_dir.exists(), f"--use_saved_bin задан, но папка с масками не найдена: {bin_dir}"

    imgs = list_images(images_root)
    if not imgs:
        raise SystemExit(f"В {images_root} не найдено изображений.")
    if args.limit > 0:
        imgs = imgs[:args.limit]

    def load_bin_masks_for_image(bin_dir: Path, split: str, rel_inside: Path):
        base_dir = bin_dir / split / rel_inside.parent / rel_inside.stem
        if not base_dir.exists():
            return [], []
        mask_files = sorted(base_dir.glob(f"{rel_inside.stem}_inst*_cls*.png"))
        bin_masks, classes = [], []
        for p in mask_files:
            m = cv2.imread(str(p), cv2.IMREAD_GRAYSCALE)
            if m is None:
                continue
            bin_masks.append((m > 127).astype(np.uint8))
            m_cls = re.search(r"_cls(\d+)\.png$", p.name)
            classes.append(int(m_cls.group(1)) if m_cls else 0)
        return bin_masks, classes

    sam = SAM(args.sam_weights) if not args.use_saved_bin else None
    pbar = tqdm(imgs, desc="Masks (saved)" if args.use_saved_bin else "SAM masks")

    ok_imgs = 0
    miss_lbl = 0
    wrote_masks = 0

    for img_path in pbar:
        # rel: <split>/<class>/.../file.jpg
        rel = img_path.relative_to(images_root)
        split = rel.parts[0] if len(rel.parts) >= 2 else "train"
        rel_inside = Path(*rel.parts[1:]) if len(rel.parts) >= 2 else Path(rel.name)

        lbl_src = labels_root / split / rel_inside.with_suffix(".txt")
        out_lbl = out_root / split / rel_inside.with_suffix(".txt")
        out_lbl.parent.mkdir(parents=True, exist_ok=True)
        

        im = cv2.imread(str(img_path))
        if im is None:
            miss_lbl += 1
            out_lbl.write_text("", encoding="utf-8")
            continue
        H, W = im.shape[:2]

        classes = []
        boxes_xyxy = []
        bin_masks = []

        gammas = [float(x) for x in args.tta_gamma.split(",") if x.strip()]
        gammas = gammas if gammas else [1.0]    

        if args.use_saved_bin:
            # Берем маски из PNG, классы из имени файла
            bin_masks, classes = load_bin_masks_for_image(bin_dir, split, rel_inside)
            if not bin_masks:
                out_lbl.write_text("", encoding="utf-8")
                continue
        else:
            # читаем bbox-лейблы
            if not lbl_src.exists():
                miss_lbl += 1
                out_lbl.write_text("", encoding="utf-8")
                continue

            lines = [l.strip() for l in lbl_src.read_text(encoding="utf-8").splitlines() if l.strip()]
            if not lines:
                out_lbl.write_text("", encoding="utf-8")
                continue

            for ln in lines:
                parts = ln.split()
                if len(parts) < 5:
                    continue
                cls_id = int(parts[0])
                x, y, w, h = map(float, parts[1:5])  # нормированные
                cx, cy = x * W, y * H
                bw, bh = w * W, h * H
                x1 = max(0.0, cx - bw / 2)
                y1 = max(0.0, cy - bh / 2)
                x2 = min(W - 1.0, cx + bw / 2)
                y2 = min(H - 1.0, cy + bh / 2)
                classes.append(cls_id)
                boxes_xyxy.append([x1, y1, x2, y2])

            if not boxes_xyxy:
                out_lbl.write_text("", encoding="utf-8")
                continue

            # TTA по гамме + усреднение вероятностей
            p_stack = []
            for g in gammas:
                im_aug = apply_gamma(im, g)
                res = sam.predict(source=im_aug, bboxes=boxes_xyxy, device=args.device, verbose=False)
                if not res or res[0].masks is None or len(res[0].masks) == 0:
                    continue
                p_stack.append(res[0].masks.data.cpu().numpy())  # [N, H, W] float

            if not p_stack:
                out_lbl.write_text("", encoding="utf-8")
                continue

            probs = np.mean(np.stack(p_stack, axis=0), axis=0)  # [N, H, W]
            bin_masks = []
            for m_prob, box in zip(probs, boxes_xyxy):
                m_bin = (m_prob > args.mask_thresh).astype(np.uint8)
                if args.clip_to_bbox:
                    m_bin = clip_mask_to_box(m_bin, box, H, W)
                if args.fill_holes:
                    m_bin = fill_holes(m_bin)
                m_bin = morph(m_bin, args.post_close, args.post_open)
                if args.largest_cc:
                    m_bin = keep_largest_cc(m_bin)
                if args.refine_grabcut and m_bin.any():
                    m_bin = refine_with_grabcut(im, m_bin, ring=args.grabcut_ring, iters=args.grabcut_iter)
                bin_masks.append(m_bin)

        if args.use_saved_bin:
            pp_masks = []
            for m_bin in bin_masks:
                mb = m_bin.copy().astype(np.uint8)
                if args.clip_to_bbox and boxes_xyxy:
                    # если нужны боксы для клипа при use_saved_bin — можно вычислить по маске
                    x, y, w, h = cv2.boundingRect(mb)
                    mb = clip_mask_to_box(mb, [x, y, x + w, y + h], H, W)
                if args.fill_holes:
                    mb = fill_holes(mb)
                mb = morph(mb, args.post_close, args.post_open)
                if args.largest_cc:
                    mb = keep_largest_cc(mb)
                if args.refine_grabcut and mb.any():
                    mb = refine_with_grabcut(im, mb, ring=args.grabcut_ring, iters=args.grabcut_iter)
                pp_masks.append(mb)
            bin_masks = pp_masks

        # Пишем YOLO-сег лейблы
        wrote_any = False
        eps = args.simplify_eps if getattr(args, "simplify_eps", 0.0) > 0 else None

        with open(out_lbl, "w", encoding="utf-8") as f:
            for cls_id, m_bin in zip(classes, bin_masks):
                poly = mask_to_poly_xyn(m_bin, W, H, args.max_pts, args.min_area, simplify_eps=eps)
                if poly is None or len(poly) < 3:
                    continue
                coords = " ".join(f"{x:.6f} {y:.6f}" for x, y in poly)
                f.write(f"{cls_id} {coords}\n")
                wrote_any = True

        # Сохранение визуализаций
        if args.save_vis and wrote_any:
            vis_path = (vis_dir / split / rel_inside)
            vis_path.parent.mkdir(parents=True, exist_ok=True)
            # Для use_saved_bin строим боксы из масок, иначе — используем исходные
            if args.use_saved_bin:
                boxes_xyxy_vis = []
                for m_bin in bin_masks:
                    x, y, w, h = cv2.boundingRect((m_bin > 0).astype(np.uint8))
                    boxes_xyxy_vis.append([x, y, x + w, y + h])
            else:
                boxes_xyxy_vis = boxes_xyxy

            vis_img = overlay_masks(im, bin_masks, classes, boxes_xyxy_vis,
                                    alpha=args.alpha, draw_contours=args.draw_contours, draw_boxes=args.draw_boxes)
            cv2.imwrite(str(vis_path), vis_img)

        # Сохранение бинарных масок по экземплярам
        if args.save_bin and wrote_any:
            # Папка с масками для конкретного изображения
            base_dir = bin_dir / split / rel_inside.parent / rel_inside.stem
            base_dir.mkdir(parents=True, exist_ok=True)
            for i, (m_bin, cls_id) in enumerate(zip(bin_masks, classes)):
                out_mask_path = base_dir / f"{rel_inside.stem}_inst{i:02d}_cls{cls_id}.png"
                cv2.imwrite(str(out_mask_path), (m_bin * 255).astype(np.uint8))

        ok_imgs += 1
        wrote_masks += int(wrote_any)

    print(f"\nГотово.")
    print(f"  Изображений обработано: {ok_imgs}")
    print(f"  Файлов без найденных bbox-лейблов: {miss_lbl}")
    print(f"  Сгенерированы маски для: {wrote_masks} изображений")
    print(f"  YOLO-сег лейблы: {out_root}")
    if args.save_vis:
        print(f"  Визуализации: {vis_dir}")
    if args.save_bin:
        print(f"  Бинарные маски: {bin_dir}")

if __name__ == "__main__":
    main()