from typing import Dict, Union
from pathlib import Path
import numpy as np
import cv2
from PIL import Image, ImageEnhance
from craft_text_detector import (
    read_image,
    load_craftnet_model,
    load_refinenet_model,
    get_prediction,
    export_detected_regions,
    export_extra_results,
    empty_cuda_cache
)




def preprocess_image_for_engraving(image, save_intermediate=False) -> np.ndarray:
    img = image
    
    # Convert to grayscale
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    
    # Optional: Denoise (if image is noisy)
    denoised = cv2.fastNlMeansDenoising(gray, h=10)
    
    # CLAHE for local contrast enhancement (CRUCIAL for engravings)
    clahe = cv2.createCLAHE(clipLimit=3.0, tileGridSize=(8,8))
    enhanced = clahe.apply(denoised)
    
    # Sharpening kernel
    kernel = np.array([[0, -1, 0],
                       [-1, 5,-1],
                       [0, -1, 0]])
    sharpened = cv2.filter2D(enhanced, -1, kernel)
    
    # Optional: Gamma correction to brighten/darken
    gamma = 1.2
    inv_gamma = 1.0 / gamma
    table = np.array([((i / 255.0) ** inv_gamma) * 255 for i in np.arange(0, 256)]).astype("uint8")
    gamma_corrected = cv2.LUT(sharpened, table)
    
    # Optional: Morphological closing to connect broken strokes
    kernel_morph = cv2.getStructuringElement(cv2.MORPH_RECT, (1,1))  # tiny kernel
    morphed = cv2.morphologyEx(gamma_corrected, cv2.MORPH_CLOSE, kernel_morph)
    
    if save_intermediate:
        cv2.imwrite("preprocessed_debug.jpg", morphed)
    
    return morphed


class CraftDetector:
    def __init__(
            self, 
            use_cuda: bool = False,
            text_threshold: float = 0.7,
            link_threshold: float = 0.4,
            low_text: float = 0.4,
            long_size: int = 1280,
            poly: bool = False,
            bboxes_dir: str = './results_craft'):
        self.craft_net = load_craftnet_model(cuda=use_cuda)
        self.refine_net = load_refinenet_model(cuda=use_cuda)
        self.text_threshold = text_threshold
        self.link_threshold = link_threshold
        self.low_text = low_text
        self.long_size = long_size
        self.poly = poly
        self.bboxes_dir = bboxes_dir

    def predict(self, img_path: Union[str, Path], save_path: Union[str, Path]
                )->Dict:
        img_path = str(img_path)
        save_path = str(save_path)
        image = read_image(str(img_path))
        image = preprocess_image_for_engraving(image)
        prediction_result = get_prediction(
            image=image,
            craft_net=self.craft_net,
            refine_net=self.refine_net,
            text_threshold=self.text_threshold,
            link_threshold=self.link_threshold,
            low_text=self.low_text,
            long_size=self.long_size,
            poly=self.poly
        )
        # prediction_result = filter_predictions_by_boxes(prediction_result)
        
        export_detected_regions(
            image=image,
            regions=prediction_result["boxes"],
            output_dir=f'{self.bboxes_dir}/{save_path}',
            rectify=True
        )

        export_extra_results(
            image=image,
            regions=prediction_result["boxes"],
            heatmaps=prediction_result["heatmaps"],
            output_dir=self.bboxes_dir,
            file_name=save_path
        )
        # unload models from gpu
        empty_cuda_cache()  
        return prediction_result

def filter_predictions_by_boxes(prediction_result_orig: Dict) -> Dict:
    # Определяем плохой бокс как numpy array
    bad_box = np.array([[[0, 0], [0, 0], [0, 0], [0, 0]]], dtype=np.float32)

    # Получаем маску для фильтрации
    mask = ~np.all(prediction_result_orig['boxes'] == bad_box, axis=(1, 2))

    # Создаем новый отфильтрованный словарь
    filtered_result = {
        key: val[mask] if isinstance(val, np.ndarray) and val.shape[0] == len(mask)
            else val.copy() 
            for key, val in prediction_result_orig.items()
    }

    # Для вложенных numpy массивов в других ключах (например, 'polys'):
    if 'polys' in filtered_result:
        filtered_result['polys'] = np.array([p for p, m in zip(filtered_result['polys'], mask) if m])

    return filtered_result