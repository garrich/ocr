import easyocr
from data_structures import TextDetection
import numpy as np
import cv2
from typing import List, Tuple, Any, Union

def preprocess_image(image: np.ndarray) -> np.ndarray:
    # Convert to grayscale
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    
    # Apply light Gaussian blur
    blurred = cv2.GaussianBlur(gray, (3, 3), 0)
    
    # Apply adaptive thresholding
    thresh = cv2.adaptiveThreshold(blurred, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 11, 2)
    
    # Deskew if needed
    coords = np.column_stack(np.where(thresh > 0))
    angle = cv2.minAreaRect(coords)[-1]
    if angle < -45:
        angle = -(90 + angle)
    else:
        angle = -angle
    (h, w) = thresh.shape[:2]
    center = (w // 2, h // 2)
    M = cv2.getRotationMatrix2D(center, angle, 1.0)
    rotated = cv2.warpAffine(thresh, M, (w, h), flags=cv2.INTER_CUBIC, borderMode=cv2.BORDER_REPLICATE)
    
    return rotated

def perform_ocr(image_paths: List[str]) -> List[List[TextDetection]]:
    reader = easyocr.Reader(['uk', 'ru'], gpu=True, quantize=True)
    detections_per_image = []

    for image_path in image_paths:
        image = cv2.imread(image_path)
        # preprocessed = preprocess_image(image)
        preprocessed = image
        
        # Perform OCR with different segmentation modes
        block_detections = reader.readtext(preprocessed, 
                                           paragraph=False,
                                           decoder='greedy',
                                           beamWidth=5,
                                           batch_size=8,
                                           contrast_ths=0.1,
                                           adjust_contrast=0.5,
                                           text_threshold=0.7,
                                           low_text=0.4,
                                           link_threshold=0.4,
                                           mag_ratio=1.5)
        
        line_detections = reader.readtext(preprocessed,
                                          paragraph=True,
                                          decoder='greedy',
                                          beamWidth=5,
                                          batch_size=8,
                                          contrast_ths=0.1,
                                          adjust_contrast=0.5,
                                          text_threshold=0.5,
                                          low_text=0.3,
                                          link_threshold=0.3,
                                          mag_ratio=1.5)
        
        # Combine and post-process detections
        all_detections = block_detections + line_detections
        processed_detections = post_process_detections(all_detections)
        
        detections_per_image.append(processed_detections)

    return detections_per_image

def post_process_detections(detections: List[Union[Tuple, List]]) -> List[TextDetection]:
    processed = []
    for detection in detections:
        if len(detection) >= 2:
            bbox = detection[0] if len(detection) > 0 else []
            text = detection[1] if len(detection) > 1 else ""
            confidence = detection[2] if len(detection) > 2 else 0.0
            
            # Apply post-processing rules
            processed_text = apply_post_processing_rules(text)
            
            processed.append(TextDetection(
                bbox=bbox,
                text=processed_text,
                confidence=confidence
            ))
        else:
            print(f"Skipping invalid detection: {detection}")
    return processed

def apply_post_processing_rules(text: str) -> str:
    # Implement rules for common fields (dates, account numbers, etc.)
    # This is a placeholder - expand with actual rules
    return text