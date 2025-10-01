from pathlib import Path
import gc
import warnings

import torch
from ultralytics import YOLO

import cv2
import numpy as np
import math

from paddleocr import PaddleOCR
import re

def free_memory():
    gc.collect()
    if torch.cuda.is_available():
        torch.cuda.empty_cache()


def _onnx_gpu_available():
    try:
        import onnxruntime as ort
        providers = ort.get_available_providers()
        return "CUDAExecutionProvider" in providers
    except Exception:
        return False


def _openvino_available():
    try:
        import openvino.runtime as ov  # noqa: F401
        return True
    except Exception:
        return False


class SegmentModel:
    """
    Автовыбор бэкенда:
      - onnx-gpu  -> ONNX Runtime (GPU, если есть CUDA и установлен onnxruntime-gpu)
      - openvino  -> OpenVINO (CPU)
      - torch     -> PyTorch (CUDA/CPU) фолбэк
    Автоматически экспортирует .pt в .onnx и/или OpenVINO, если нужных файлов нет.
    """

    def __init__(
        self,
        model_path="ml/weights/yolo11s-seg-tools.pt",
        conf_threshold=0.5,
        imgsz=640,
        prefer="auto",  # "auto" | "onnx-gpu" | "openvino" | "torch"
        verbose=True,
    ):
        self.model_path = Path(model_path)
        self.imgsz = imgsz
        self.conf_threshold = conf_threshold
        self.prefer = prefer
        self.verbose = verbose

        self.backend = None      # "onnx-gpu" | "openvino" | "torch"
        self.device_arg = None  
        self.model = None
        self.r = None

        self._select_and_load_model()

    # --------- Paths for exported models ---------

    @property
    def onnx_path(self) -> Path:
        if self.model_path.suffix == ".pt":
            return self.model_path.with_suffix(".onnx")
        return self.model_path  

    @property
    def openvino_dir(self) -> Path:
        stem = self.model_path.stem if self.model_path.suffix else self.model_path.name
        return self.model_path.with_name(f"{stem}_openvino_model")

    # --------- Backend selection ---------

    def _decide_backend(self):
        if self.prefer != "auto":
            if self.prefer == "onnx-gpu":
                return "onnx-gpu" if _onnx_gpu_available() else "torch"
            if self.prefer == "openvino":
                return "openvino" if _openvino_available() else "torch"
            return "torch"

        if torch.cuda.is_available() and _onnx_gpu_available():
            return "onnx-gpu"
        if _openvino_available():
            return "openvino"
        return "torch"


    def _ensure_onnx(self):
        if self.onnx_path.exists():
            return
        if self.verbose:
            print("Экспорт в ONNX…")
        base_model = YOLO(str(self.model_path))
        onnx_fp16 = torch.cuda.is_available() 
        exported = base_model.export(
            format="onnx",
            half=onnx_fp16,
            dynamic=False,
        )
        if self.verbose:
            print(f"ONNX экспортирован: {exported}")
        free_memory()

    def _ensure_openvino(self):
        if self.openvino_dir.exists():
            return
        if self.verbose:
            print("Экспорт в OpenVINO…")
        base_model = YOLO(str(self.model_path))
        exported = base_model.export(
            format="openvino",
            half=False,  
            dynamic=False,
        )
        if self.verbose:
            print(f"OpenVINO экспортирован: {exported}")
        free_memory()


    def _select_and_load_model(self):
        if not self.model_path.exists():
            raise FileNotFoundError(f"Не найден файл модели: {self.model_path}")

        backend = self._decide_backend()

        if backend == "onnx-gpu":
            try:
                self._ensure_onnx()
            except Exception as e:
                warnings.warn(f"Не удалось экспортировать в ONNX, откат к PyTorch. Причина: {e}")
                backend = "torch"
            else:
                self.model = YOLO(str(self.onnx_path))
                self.device_arg = 0 
                self.backend = "onnx-gpu"
                if self.verbose:
                    print(f"Модель загружена (ONNX Runtime GPU): {self.onnx_path}")
                return

        if backend == "openvino":
            try:
                self._ensure_openvino()
            except Exception as e:
                warnings.warn(f"Не удалось экспортировать в OpenVINO, откат к PyTorch. Причина: {e}")
                backend = "torch"
            else:
                self.model = YOLO(str(self.openvino_dir))
                self.device_arg = "CPU"
                self.backend = "openvino"
                if self.verbose:
                    print(f"Модель загружена (OpenVINO CPU): {self.openvino_dir}")
                return

        self.model = YOLO(str(self.model_path))
        self.backend = "torch"
        self.device_arg = 0 if torch.cuda.is_available() else "cpu"
        if self.verbose:
            dev_str = "CUDA" if torch.cuda.is_available() else "CPU"
            print(f"Модель загружена (PyTorch {dev_str}): {self.model_path}")

    # --------- Public API ---------

    def export_to_onnx(self):
        self._ensure_onnx()

    def export_to_openvino(self):
        self._ensure_openvino()

    def predict_image(self, img_path):
        half_flag = True if (self.backend == "torch" and torch.cuda.is_available()) else False

        results_list = self.model.predict(
            source=str(img_path),
            imgsz=self.imgsz,
            conf=self.conf_threshold,
            device=self.device_arg,
            workers=0,
            batch=1,
            half=half_flag,
            verbose=False,
            save=False
        )
        self.r = results_list[0]

    def get_probs(self):
        return getattr(self.r.boxes, "conf", None)

    def get_axis_aligned_boxes(self):
        return getattr(self.r.boxes, "xyxyn", None)

    def get_masks(self):
        return getattr(self.r.masks, "xyn", None)

    def get_oriented_bboxes(self, normalized=True):
            """
            Возвращает список строк формата:
                class_index x1 y1 x2 y2 x3 y3 x4 y4
            Координаты по умолчанию в пикселях. Если normalized=True, то в [0,1].

            Требует, чтобы self.r был заполнен (после predict_image).
            """
            if self.r is None or getattr(self.r, "masks", None) is None:
                return []

            h, w = self._get_img_hw()
            polys_xy = getattr(self.r.masks, "xy", None)
            if polys_xy is None:
                # берем нормализованные полигоны и денормализуем
                polys_xyn = getattr(self.r.masks, "xyn", None)
                if polys_xyn is None:
                    return []
                polys = [np.asarray(p, dtype=np.float32) * np.array([w, h], dtype=np.float32) for p in polys_xyn]
            else:
                polys = [np.asarray(p, dtype=np.float32) for p in polys_xy]

            cls_tensor = getattr(getattr(self.r, "boxes", None), "cls", None)
            cls_ids = [int(c.item()) for c in cls_tensor] if cls_tensor is not None else [-1] * len(polys)

            obb_rows = []

            for i, poly in enumerate(polys):
                if poly is None or len(poly) < 3:
                    continue

                rect = cv2.minAreaRect(poly)      # ((cx,cy), (w,h), angle)
                box = cv2.boxPoints(rect)         # 4x2 float
                box = self._order_box_points(box) # tl, tr, br, bl

                if normalized:
                    box = box / np.array([w, h], dtype=np.float32)

                coords = box.reshape(-1).tolist()
                if not normalized:
                    coords = [int(round(v)) for v in coords]

                row = [cls_ids[i]] + coords
                obb_rows.append(row)

            return obb_rows

    def visualize_oriented_bboxes(
        self,
        save_path="obb_vis.png",
        show=False,
        line_thickness=2,
        mask_alpha=0.35,
        draw_mask_contours=True,
        mask_contour_thickness=1,
        text_scale=0.6,
        text_thickness=1,
        text_bg_alpha=0.55,
        mask_fill_lighter=False,     # осветлять заливку масок (тот же оттенок, выше V, ниже S)
        mask_s_mul=0.90,             
        mask_v_mul=1.35              
    ):
        if self.r is None:
            raise RuntimeError("Сначала вызовите predict_image(...)")

        base_img = getattr(self.r, "orig_img", None)
        if base_img is None:
            base_img = self.r.plot(masks=False, boxes=False)
        img = base_img.copy()
        h, w = img.shape[:2]

        names = getattr(self.r, "names", None) or getattr(self.model, "names", None) or {}
        boxes = getattr(self.r, "boxes", None)
        confs = getattr(boxes, "conf", None)
        cls_tensor = getattr(boxes, "cls", None)

        masks_obj = getattr(self.r, "masks", None)
        if masks_obj is None or getattr(masks_obj, "data", None) is None:
            if save_path is not None:
                cv2.imwrite(str(save_path), img)
            if show:
                cv2.imshow("OBB visualization", img)
                cv2.waitKey(0)
                cv2.destroyAllWindows()
            return img

        n_inst = masks_obj.data.shape[0]
        cls_ids = [int(c.item()) for c in cls_tensor] if cls_tensor is not None else [-1] * n_inst

        for i in range(n_inst):
            cls_id = cls_ids[i] if i < len(cls_ids) else -1
            prob = float(confs[i].item()) if (confs is not None and i < len(confs)) else None
            name = names.get(cls_id, str(cls_id)) if isinstance(names, dict) else (
                names[cls_id] if isinstance(names, (list, tuple)) and 0 <= cls_id < len(names) else str(cls_id)
            )
            label = f"{name} {prob:.2f}" if prob is not None else f"{name}"
    
            base_color = self._color_for_class(cls_id)
            fill_color = self._lighten_bgr(base_color, s_mul=mask_s_mul, v_mul=mask_v_mul) if mask_fill_lighter else base_color

            # Полигон(ы) данного инстанса в пикселях оригинального изображения
            polys_px = self._get_instance_polygons_px(i, h, w)

            # 1) Маска по полигонам (идеально совпадает с полигонами/OBB)
            m_bin = np.zeros((h, w), dtype=np.uint8)
            for poly in polys_px:
                if poly.shape[0] >= 3:
                    cv2.fillPoly(m_bin, [np.round(poly).astype(np.int32)], 1)
            m_bool = m_bin.astype(bool)
            if m_bool.any():
                self._alpha_blend_mask_inplace(img, m_bool, fill_color, alpha=mask_alpha)

            # 2) Контур полигонов (опционально)
            if draw_mask_contours and mask_contour_thickness > 0:
                for poly in polys_px:
                    if poly.shape[0] >= 2:
                        cv2.polylines(img, [np.round(poly).astype(np.int32)], True, base_color, mask_contour_thickness, cv2.LINE_AA)

            # 3) OBB по всем точкам полигонов
            pts_all = np.vstack([p for p in polys_px if p.shape[0] >= 3]) if len(polys_px) else None
            if pts_all is None or pts_all.shape[0] < 3:
                continue
            rect = cv2.minAreaRect(pts_all.astype(np.float32))
            box = cv2.boxPoints(rect)
            box = self._order_box_points(box)
            cv2.polylines(img, [box.astype(np.int32)], True, base_color, line_thickness, cv2.LINE_AA)

            tl, tr, br, bl = box  # порядок из _order_box_points
            anchor = (int(bl[0]), int(bl[1]))  # нижний левый угол
            self._draw_label_box(
                img_bgr=img,
                text=label,
                anchor=anchor,
                bg_color=base_color,           # тот же цвет, что и у рамки
                text_color=(255, 255, 255),    # белый шрифт
                font_scale=text_scale,         # можно сделать крупнее, напр. 0.9–1.1
                thickness=text_thickness,      # толщина шрифта, напр. 2
                pad=4,                         # внутренние отступы плашки
                bg_alpha=text_bg_alpha         # 1.0 = непрозрачно, можно оставить как есть
            )            

        if save_path is not None:
            cv2.imwrite(str(save_path), img)
        if show:
            cv2.imshow("OBB visualization", img)
            cv2.waitKey(0)
            cv2.destroyAllWindows()
        return img
    
    ### helpers#####

    def _draw_label_box(
        self,
        img_bgr,
        text,
        anchor,                 # (x, y) — нижний левый угол текста (baseline), привязан к нижнему левому углу OBB
        bg_color=(0, 0, 0),
        text_color=(255, 255, 255),
        font_scale=0.95,
        thickness=2,
        pad=4,
        bg_alpha=1.0
    ):
        """
        Рисует горизонтальный ярлык (плашка + текст) из нижнего левого угла anchor.
        Плашка — цвет рамки (bg_color), текст — белый.
        """
        x, y = int(anchor[0]), int(anchor[1])
        H, W = img_bgr.shape[:2]
        font = cv2.FONT_HERSHEY_SIMPLEX

        (tw, th), baseline = cv2.getTextSize(text, font, font_scale, thickness)
        # прямоугольник под текст: отступы pad
        rx0 = x - pad
        ry1 = y + pad
        rx1 = x + tw + pad
        ry0 = y - th - baseline - pad

        # Клип прямоугольника в границы изображения
        cx0 = max(rx0, 0)
        cy0 = max(ry0, 0)
        cx1 = min(rx1, W)
        cy1 = min(ry1, H)

        if cx1 > cx0 and cy1 > cy0:
            if bg_alpha >= 1.0:
                cv2.rectangle(img_bgr, (rx0, ry0), (rx1, ry1), bg_color, thickness=-1, lineType=cv2.LINE_AA)
            else:
                # полупрозрачная плашка
                roi = img_bgr[cy0:cy1, cx0:cx1].astype(np.float32)
                overlay = np.full_like(roi, bg_color, dtype=np.uint8).astype(np.float32)
                a = float(np.clip(bg_alpha, 0.0, 1.0))
                blended = (1.0 - a) * roi + a * overlay
                img_bgr[cy0:cy1, cx0:cx1] = blended.astype(np.uint8)

        # Текст поверх плашки (белый), ровно от нижнего левого угла anchor
        cv2.putText(img_bgr, text, (x, y), font, font_scale, text_color, thickness, cv2.LINE_AA)

    def _get_instance_polygons_px(self, idx, H, W):
        """
        Возвращает список полигонов (каждый: np.ndarray [N,2] float32 в пикселях оригинального изображения).
        Источник: r.masks.xy (если есть) или r.masks.xyn * [W,H]. Если ни того ни другого нет — пустой список.
        """
        masks = getattr(self.r, "masks", None)
        if masks is None:
            return []

        def to_np(a):
            if a is None:
                return None
            if isinstance(a, np.ndarray):
                return a.astype(np.float32)
            if hasattr(a, "cpu"):
                return a.cpu().numpy().astype(np.float32)
            return np.asarray(a, dtype=np.float32)

        # 1) Предпочитаем xy (уже в пикселях)
        xy = getattr(masks, "xy", None)
        if xy is not None and len(xy) > idx:
            seg = xy[idx]
            # seg может быть массивом Nx2 или списком таких массивов
            if isinstance(seg, (list, tuple)):
                polys = [to_np(s) for s in seg if s is not None]
            else:
                polys = [to_np(seg)]
            return [p for p in polys if p is not None and p.ndim == 2 and p.shape[0] >= 3]

        # 2) Иначе xyn (нормированные), домножаем на (W, H)
        xyn = getattr(masks, "xyn", None)
        if xyn is not None and len(xyn) > idx:
            seg = xyn[idx]
            scale = np.array([W, H], dtype=np.float32)
            if isinstance(seg, (list, tuple)):
                polys = [to_np(s) for s in seg if s is not None]
            else:
                polys = [to_np(seg)]
            polys = [p * scale for p in polys if p is not None and p.ndim == 2 and p.shape[0] >= 3]
            return polys

        return []

    def _alpha_blend_mask_inplace(self, img_bgr, mask_bool, color, alpha=0.35):
        """
        Альфа-композитинг цвета поверх img_bgr только в пикселях маски.
        color — BGR tuple, alpha — [0..1]
        """
        if alpha <= 0.0:
            return
        if mask_bool is None or not mask_bool.any():
            return
        c = np.array(color, dtype=np.float32)
        region = img_bgr[mask_bool].astype(np.float32)
        blended = region * (1.0 - alpha) + c * alpha
        img_bgr[mask_bool] = blended.astype(np.uint8)

    # --------- Helpers ---------
    def _get_img_hw(self):
        if hasattr(self.r, "orig_shape") and self.r.orig_shape is not None:
            h, w = self.r.orig_shape[:2]
        elif hasattr(self.r, "orig_img") and self.r.orig_img is not None:
            h, w = self.r.orig_img.shape[:2]
        else:
            tmp = self.r.plot(masks=False, boxes=False)
            h, w = tmp.shape[:2]
        return h, w

    @staticmethod
    def _order_box_points(pts):
        """
        Упорядочивает 4 точки в порядке: top-left, top-right, bottom-right, bottom-left.
        pts: (4,2)
        """
        pts = np.asarray(pts, dtype=np.float32)
        s = pts.sum(axis=1)           # x+y
        diff = pts[:, 0] - pts[:, 1]  # x - y
        tl = pts[np.argmin(s)]
        br = pts[np.argmax(s)]
        tr = pts[np.argmax(diff)]
        bl = pts[np.argmin(diff)]
        return np.array([tl, tr, br, bl], dtype=np.float32)


    def _color_for_class(self, cls_id: int, s=0.90, v=0.95, h_offset=0.0):
        """
        Яркий детерминированный BGR-цвет для класса из HSV круга.
        Используем золотое сечение для равномерного разнесения оттенков.
        s, v ∈ [0..1] — насыщенность и яркость.
        """
        i = int(cls_id) if cls_id is not None else 0
        if i < 0:
            i = -i
        phi = 0.61803398875
        h = (i * phi + float(h_offset)) % 1.0  # [0..1)
        hsv = np.array([[[int(h * 179), int(s * 255), int(v * 255)]]], dtype=np.uint8)
        bgr = cv2.cvtColor(hsv, cv2.COLOR_HSV2BGR)[0, 0]
        return int(bgr[0]), int(bgr[1]), int(bgr[2])


    def _lighten_bgr(self, bgr, s_mul=0.90, v_mul=1.35):
        """
        Немного осветлить цвет в HSV: понизить насыщенность (S), поднять яркость (V).
        """
        c = np.uint8([[list(bgr)]])
        hsv = cv2.cvtColor(c, cv2.COLOR_BGR2HSV).astype(np.float32)
        h, s, v = hsv[0, 0]
        s = max(0, min(255, s * float(s_mul)))
        v = max(0, min(255, v * float(v_mul)))
        hsv[0, 0] = (h, s, v)
        out = cv2.cvtColor(hsv.astype(np.uint8), cv2.COLOR_HSV2BGR)[0, 0]
        return (int(out[0]), int(out[1]), int(out[2]))


def order_points(pts):
    # pts: numpy array shape (4,2)
    rect = np.zeros((4, 2), dtype="float32")
    
    s = pts.sum(axis=1)
    rect[0] = pts[np.argmin(s)]   # top-left
    rect[2] = pts[np.argmax(s)]   # bottom-right
    
    diff = np.diff(pts, axis=1)
    rect[1] = pts[np.argmin(diff)]  # top-right
    rect[3] = pts[np.argmax(diff)]  # bottom-left
    return rect

def crop_obb(obb, img):
    """
    obb: [class_index, x1, y1, x2, y2, x3, y3, x4, y4]
    img: исходное изображение (numpy BGR, как из cv2.imread)
    
    return: выровненный кроп (numpy array)
    """
    # достаём только точки
    pts = np.array(obb[1:], dtype="float32").reshape(4, 2)
    rect = order_points(pts)
    (tl, tr, br, bl) = rect

    # размеры "расправленного" прямоугольника
    widthA = np.linalg.norm(br - bl)
    widthB = np.linalg.norm(tr - tl)
    maxWidth = int(max(widthA, widthB))

    heightA = np.linalg.norm(tr - br)
    heightB = np.linalg.norm(tl - bl)
    maxHeight = int(max(heightA, heightB))

    dst = np.array([
        [0, 0],
        [maxWidth - 1, 0],
        [maxWidth - 1, maxHeight - 1],
        [0, maxHeight - 1]], dtype="float32")

    # считаем матрицу преобразования и трансформируем
    M = cv2.getPerspectiveTransform(rect, dst)
    warp = cv2.warpPerspective(img, M, (maxWidth, maxHeight))

    return warp


def reconstruct(text):
    # Полный эталон
    FULL_PREFIX_MAIN = "AT-288293-"     # то, что мы достраиваем до цифры
    OIL_CAN = "AT-389759"

    # Регулярки для поиска OCR-хвостов
    pattern_main = re.compile(
        r'(?:AT-)?(?:288293-\d{1,2}|88293-\d{1,2}|8293-\d{1,2}|293-\d{1,2}|93-\d{1,2})'
    )
    pattern_oil  = re.compile(r'(?:AT-)?(?:389759|89759|9759|759)')

    # сначала проверяем основной номер
    m1 = pattern_main.search(text)
    if m1:
        tail = m1.group(0)
        if tail.startswith("AT-"):
            return tail
        return FULL_PREFIX_MAIN[:-len(tail)] + tail
    
    # проверяем OIL_CAN
    m2 = pattern_oil.search(text)
    if m2:
        tail = m2.group(0)
        if tail.startswith("AT-"):
            return OIL_CAN   # уже готовый номер
        # достраиваем
        return "AT-" + "389759"[-len(tail):].replace("389759", "389759") if False else OIL_CAN    
    return None


def get_prediction_results(model, img_path):
    model.predict_image(img_path)
    # OBB в формате [class_index, x1, y1, x2, y2, x3, y3, x4, y4]
    obb_rows = model.get_oriented_bboxes(normalized=False)
    classes = [obb[0] for obb in obb_rows]
    masks = model.get_masks()
    img = cv2.imread(img_path)
    obb_texts = []
    for i, obb in enumerate(obb_rows):
        obb_img = img.copy()
        obb_img = crop_obb(obb, obb_img)
        text_list = []
        # result = ocr_model.predict(obb_img)
        # for res in result:
        #     rec_texts = res['rec_texts']
        #     for t in rec_texts:
        #         reconstructed_text = reconstruct(t)
        #         if reconstructed_text is not None:
        #             text_list.append(reconstructed_text)
        unique_texts = set(text_list)
        if len(list(unique_texts))>0:
            obb_texts.append(list(unique_texts)[0])
        else: obb_texts.append(None)

    probs  = model.get_probs()

    return classes, obb_rows, masks, probs

def run(img_path):
    script_dir = Path(__file__).parent.absolute()
    # img_path = script_dir / "img/DSCN4950.JPG"
    model_path = script_dir / "weights/yolo11s-seg-tools.pt"

    model = SegmentModel(
        model_path=model_path,
        conf_threshold=0.5,
        imgsz=640,
        prefer="auto",   #  "onnx-gpu" | "openvino" | "torch"
        verbose=True
    )
    # ocr_model = PaddleOCR(
    #     use_doc_orientation_classify=True, 
    #     use_doc_unwarping=True, 
    #     use_textline_orientation=True)
    classes, obb_rows, masks, probs = get_prediction_results(model, img_path)
    
    return classes, obb_rows, masks, probs


if __name__ == "__main__":
    # Используем абсолютные пути для теста
    script_dir = Path(__file__).parent.absolute()
    img_path = script_dir / "img/DSCN4950.JPG"
    model_path = script_dir / "weights/yolo11s-seg-tools.pt"

    model = SegmentModel(
        model_path=model_path,
        conf_threshold=0.5,
        imgsz=640,
        prefer="auto",   #  "onnx-gpu" | "openvino" | "torch"
        verbose=True
    )
    # ocr_model = PaddleOCR(
    #     use_doc_orientation_classify=True, 
    #     use_doc_unwarping=True, 
    #     use_textline_orientation=True)
    classes, obb_rows, masks, obb_texts = get_prediction_results(model, img_path)
