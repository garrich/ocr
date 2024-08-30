import re
from typing import List
from data_structures import TextDetection


def translate_detections(detections: List[TextDetection], 
                         start_with_exclusions: List[str] = [], 
                         exact_match_exclusions: List[str] = []) -> List[TextDetection]:
    cyrillic_to_latin = {
        'а': 'a', 'б': 'b', 'в': 'v', 'г': 'h', 'ґ': 'g', 'д': 'd', 'е': 'e', 'є': 'ye',
        'ж': 'zh', 'з': 'z', 'и': 'y', 'і': 'i', 'ї': 'yi', 'й': 'y', 'к': 'k', 'л': 'l',
        'м': 'm', 'н': 'n', 'о': 'o', 'п': 'p', 'р': 'r', 'с': 's', 'т': 't', 'у': 'u',
        'ф': 'f', 'х': 'kh', 'ц': 'ts', 'ч': 'ch', 'ш': 'sh', 'щ': 'shch', 'ь': "'",
        'ю': 'yu', 'я': 'ya'
    }

    def is_excluded(text: str) -> bool:
        # Check for exact match exclusions
        if text.strip().lower() in exact_match_exclusions:
            return True

        # Check for start with exclusions
        for prefix in start_with_exclusions:
            if text.strip().lower().__contains__(prefix.lower()):
                return True

        # Check if it's a date or number
        if is_date_or_number(text):
            return True

        return False

    def is_date_or_number(text: str) -> bool:
        # Trim leading and trailing whitespace
        text = text.strip()
        
        # Regex for specific "100 00О,00" pattern
        specific_pattern = r'^\d{1,3}(?: \d{2}[ОоOo],\d{2})$'

        # Regex for generic numbers (including those with Cyrillic characters)
        generic_number_pattern = r'^[-+]?(?:\d[\d\s]*(?:[.,]\d+)?|[ОоOo][\d\s]*(?:[.,]\d+)?)(?:[ОоOo])?$'
        
        # Regex for dates (now includes trailing spaces)
        date_pattern = r'^\d{1,2}[-/.]\d{1,2}[-/.]\d{2,4}\s*$'

        return bool(re.match(specific_pattern, text, re.IGNORECASE) or 
                    re.match(generic_number_pattern, text, re.IGNORECASE) or 
                    re.match(date_pattern, text))

    def translate_text(text: str) -> str:
        return ''.join(cyrillic_to_latin.get(c.lower(), c) for c in text)

    translated_detections = []

    for detection in detections:
        print("---")
        print(detection.text)
        if is_excluded(detection.text):
            print("excluded "+ detection.text)
            continue  # Skip this detection entirely
        
        detection.translated_text = translate_text(detection.text)
        
        # Check if translated_text exists and is not blank
        if detection.translated_text and detection.translated_text.strip():
            translated_detections.append(detection)

    return translated_detections