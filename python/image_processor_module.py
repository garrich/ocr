import json
import math
from PIL import Image, ImageDraw, ImageFont
from typing import List, OrderedDict, Tuple
import os
from data_structures import TextDetection, FontSizeCache
import numpy as np

font_size_cache = FontSizeCache()

def adaptive_font_size(bbox, translated_text, max_iterations=15, tolerance=0.05, reduction_factor=0.9):
    original_width = bbox[1][0] - bbox[0][0]
    original_height = bbox[2][1] - bbox[0][1]
    text_length = len(translated_text)

    # Check cache first
    cached_size = font_size_cache.get(original_width, original_height, text_length)
    if cached_size:
        return int(cached_size * reduction_factor)

    def get_text_size(font_size):
        font = ImageFont.truetype("arial.ttf", font_size)
        text_width = font.getlength(translated_text)
        # Approximate height using font size and a factor
        text_height = font_size * 1.2  # Adjust this factor if needed
        return text_width, text_height
    
    # Initial guess
    font_size = cached_size or min(original_height, original_width // text_length)
    
    for _ in range(max_iterations):
        text_width, text_height = get_text_size(font_size)
        
        width_ratio = text_width / original_width
        height_ratio = text_height / original_height
        
        if abs(1 - width_ratio) <= tolerance and abs(1 - height_ratio) <= tolerance:
            # Cache the result before returning
            font_size_cache.set(original_width, original_height, text_length, font_size)
            return int(font_size * reduction_factor)
        
        if width_ratio > 1 + tolerance or height_ratio > 1 + tolerance:
            font_size = int(font_size * 0.9)  # Decrease font size
        else:
            font_size = int(font_size * 1.1)  # Increase font size
    
    # Cache the best effort result
    font_size_cache.set(original_width, original_height, text_length, font_size)
    return int(font_size * reduction_factor)

def get_text_color(img, bbox):
    x1, y1 = map(int, bbox[0])
    x2, y2 = map(int, bbox[2])
    region = np.array(img.crop((x1, y1, x2, y2)))
    
    # Flatten the region and get unique colors
    pixels = region.reshape(-1, 3)
    unique_colors, counts = np.unique(pixels, axis=0, return_counts=True)
    
    # Sort colors by count (descending) and exclude white
    sorted_colors = sorted(zip(unique_colors, counts), key=lambda x: x[1], reverse=True)
    non_white_colors = [color for color, count in sorted_colors if not np.all(color > 240)]
    
    if non_white_colors:
        dominant_color = non_white_colors[0]
        # Check if the color is dark enough to be visible on white
        if np.mean(dominant_color) < 200:
            return tuple(dominant_color)
    
    # Default to black if no suitable color is found
    return (0, 0, 0)
    
def draw_rotated_text_with_background(img, text, bbox, angle, font, text_color):
    # Create a new transparent image for the text box
    box_width = int(math.sqrt((bbox[1][0] - bbox[0][0])**2 + (bbox[1][1] - bbox[0][1])**2))
    box_height = int(math.sqrt((bbox[2][0] - bbox[1][0])**2 + (bbox[2][1] - bbox[1][1])**2))
    txt_img = Image.new('RGBA', (box_width, box_height), (0, 0, 0, 0))
    d = ImageDraw.Draw(txt_img)
    
    # Draw white background
    d.rectangle([(0, 0), (box_width, box_height)], fill=(255, 255, 255, 255))
    
    # Calculate text position
    left, top, right, bottom = font.getbbox(text)
    text_width = right - left
    text_height = bottom - top
    text_position = ((box_width - text_width) // 2, (box_height - text_height) // 2)
    
    # Draw the text
    d.text(text_position, text, font=font, fill=text_color)
    
    # Rotate the text image
    rotated = txt_img.rotate(angle, expand=1, resample=Image.BICUBIC)
    
    # Calculate paste position
    paste_x = int(bbox[0][0] - (rotated.width - box_width) / 2)
    paste_y = int(bbox[0][1] - (rotated.height - box_height) / 2)
    
    # Paste the rotated text onto the main image
    img.paste(rotated, (paste_x, paste_y), rotated)

def process_image(image_path, detections: List[TextDetection], output_dir):
    print(f"Processing image: {image_path}")
    img = Image.open(image_path).convert('RGB')

    for i, detection in enumerate(detections):
        if not detection.translated_text:
            print("skipped " + detection.text)
            continue
        font_size = adaptive_font_size(detection.bbox, detection.translated_text)
        font = ImageFont.truetype("arial.ttf", font_size)
        
        text_color = get_text_color(img, detection.bbox)
        
        # Draw rotated text with white background
        draw_rotated_text_with_background(img, detection.translated_text, detection.bbox, detection.rotation_angle, font, text_color)

    base_name = os.path.basename(image_path)
    name, ext = os.path.splitext(base_name)
    output_path = os.path.join(output_dir, f"en_{name}{ext}")
    img.save(output_path)
    print(f"Saved processed image: {output_path}")

    # Save a debug image with bounding boxes
    debug_img = Image.open(image_path)
    debug_draw = ImageDraw.Draw(debug_img)
    for detection in detections:
        top_left = tuple(map(int, detection.bbox[0]))
        bottom_right = tuple(map(int, detection.bbox[2]))
        debug_draw.rectangle([top_left, bottom_right], outline=(255, 0, 0), width=2)
    debug_output_path = os.path.join(output_dir, f"debug_en_{name}{ext}")
    debug_img.save(debug_output_path)
    print(f"Saved debug image: {debug_output_path}")