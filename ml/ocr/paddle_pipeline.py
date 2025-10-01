import os
from paddleocr import PaddleOCR
import re


# Полный эталон
FULL_PREFIX_MAIN = "AT-288293-"     # то, что мы достраиваем до цифры
OIL_CAN = "AT-389759"

# Регулярки для поиска OCR-хвостов
pattern_main = re.compile(
    r'(?:AT-)?(?:288293-\d{1,2}|88293-\d{1,2}|8293-\d{1,2}|293-\d{1,2}|93-\d{1,2})'
)
pattern_oil  = re.compile(r'(?:AT-)?(?:389759|89759|9759|759)')

def reconstruct(text):
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


def bbox_to_rect(poly):
    xs = [p[0] for p in poly]
    ys = [p[1] for p in poly]
    return min(xs), min(ys), max(xs), max(ys)

def intersect(rect1, rect2):
    x1_min, y1_min, x1_max, y1_max = rect1
    x2_min, y2_min, x2_max, y2_max = rect2
    return not (x1_max < x2_min or x2_max < x1_min or
                y1_max < y2_min or y2_max < y1_min)

def filter_duplicates(texts, boxes):
    keep = [True] * len(texts)
    rects = [bbox_to_rect(b) for b in boxes]

    for i in range(len(texts)):
        if not keep[i]:
            continue
        for j in range(i+1, len(texts)):
            if not keep[j]:
                continue
            if intersect(rects[i], rects[j]):
                # оставляем более длинный текст
                if len(texts[i]) >= len(texts[j]):
                    keep[j] = False
                else:
                    keep[i] = False
    filtered_texts = [t for t, k in zip(texts, keep) if k]
    filtered_boxes = [b for b, k in zip(boxes, keep) if k]
    return filtered_texts, filtered_boxes


if __name__=='__main__':
    img_dir = 'imgs'
    ocr = PaddleOCR(
        use_doc_orientation_classify=True, 
        use_doc_unwarping=True, 
        use_textline_orientation=True) # text detection + text recognition
    # основной цикл
    for fname in os.listdir(img_dir):
        img_path = os.path.join(img_dir, fname)
        text_list = []
        boxes_list = []
        result = ocr.predict(img_path)
        for res in result:
            rec_texts = res['rec_texts']
            boxes = res['rec_polys']
            for t, b in zip(rec_texts, boxes):
                print(t)
                reconstructed_text = reconstruct(t)
                print(reconstructed_text)
                if reconstructed_text is not None:
                    text_list.append(reconstructed_text)
                    boxes_list.append(b)

            res.save_to_img(f"output_{fname[:-4]}")
            # res.save_to_json(f"output_json_{fname[:-4]}.json")
        # чистим повторы
        unique_texts, unique_boxes = filter_duplicates(text_list, boxes_list)
        print(fname, ' == ', unique_texts )