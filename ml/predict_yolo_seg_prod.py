from pathlib import Path
import gc
import torch
from ultralytics import YOLO
import cv2

def free_memory():
        gc.collect()
        if torch.cuda.is_available():
            torch.cuda.empty_cache()


class SegmentModel():
    def __init__(self, 
                 model_path = 'ml/weights/yolo11s-seg-tools.onnx',
                 ):
        self.model_path = model_path


        self.imgsz = 640
        self.conf_threshold = 0.5

        self.load_model()

    def load_model(self):
        try:
            self.model = YOLO(self.model_path)
            print(f"Модель {self.model_path} успешно загружена.")
        except Exception as e:
            print(f"Ошибка загрузки модели: {e}")
            raise SystemExit
         
    def export_to_onnx(self):
        self.model.export(format="onnx")

    def predict_image(self, img_path):
        results_list = self.model.predict(
            source=str(img_path),
            imgsz=self.imgsz,
            conf=self.conf_threshold,
            device=0 if torch.cuda.is_available() else 'cpu',
            workers=0,       
            batch=1,        
            half=torch.cuda.is_available(),
            verbose=False,
            save=False       
        )
        self.r = results_list[0]

    def get_probs(self):
        return self.r.boxes.conf
    
    def get_boxes(self):
        return self.r.boxes.xyxyn
    
    def get_masks(self):
        return self.r.masks.xyn

if __name__=="__main__":
    img_path = "data/Групповые/DSCN4946.JPG"
    model = SegmentModel()
    model.predict_image(img_path)

    probs = model.get_probs() # (n predicted objects, )
    boxes = model.get_boxes() # (n predicted objects, 4)
    masks = model.get_masks() # (n predicted objects, n_dots_per_mask, 2)