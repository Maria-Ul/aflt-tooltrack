import os
from pathlib import Path
from craft_detector import CraftDetector



if __name__ == '__main__':
    img_dir ='./imgs'
    bboxes_dir = './results'
    os.makedirs(bboxes_dir, exist_ok=True)

    # это плюс обработка детектирует стертый текст на ручке отвертки
    detector = CraftDetector(
        text_threshold=0.1,
        link_threshold=0.1,
        low_text=0.1,
        long_size=1280,
        poly=True,
        bboxes_dir = bboxes_dir
    )
    
    for img_name in os.listdir(img_dir):
        try:
            img_path = os.path.join(img_dir, img_name)
            detector.predict(img_path, save_path = f'{Path(img_path).stem}_2')
        except Exception as e:
            print(f'{img_name}: {e}')