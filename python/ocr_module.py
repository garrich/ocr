import easyocr
from data_structures import TextDetection
import numpy as np
import math

def calculate_rotation_angle(bbox):
    # Calculate angle based on the first two points of the bounding box
    x1, y1 = bbox[0]
    x2, y2 = bbox[1]
    return math.degrees(math.atan2(y2 - y1, x2 - x1))

def perform_ocr(image_paths):
    reader = easyocr.Reader(['uk'])  # Assuming Ukrainian language
    detections_per_image = []

    for image_path in image_paths:
        raw_detections = reader.readtext(image_path)
        detections = [
            TextDetection(
                bbox=detection[0],
                text=detection[1],
                confidence=detection[2],
                rotation_angle=calculate_rotation_angle(detection[0])
            )
            for detection in raw_detections
        ]
        detections_per_image.append(detections)

    return detections_per_image