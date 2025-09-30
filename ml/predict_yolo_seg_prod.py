from pathlib import Path
import gc
import warnings

import torch
from ultralytics import YOLO

import cv2


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
        return self.r

    def get_probs(self):
        return getattr(self.r.boxes, "conf", None)

    def get_boxes(self):
        return getattr(self.r.boxes, "xyxyn", None)

    def get_masks(self):
        # Для задач без масок (другие модели) это будет None
        return getattr(self.r.masks, "xyn", None)


if __name__ == "__main__":
    img_path = "data/Групповые/DSCN4946.JPG"
    model = SegmentModel(
        model_path="ml/weights/yolo11s-seg-tools.pt",
        conf_threshold=0.5,
        imgsz=640,
        prefer="auto",   #  "onnx-gpu" | "openvino" | "torch"
        verbose=True
    )

    r = model.predict_image(img_path)
    probs = model.get_probs()
    boxes = model.get_boxes()
    masks = model.get_masks()

    print("backend:", model.backend)
    print("n dets:", 0 if probs is None else len(probs))