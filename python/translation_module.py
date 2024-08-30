import json
import re
from typing import Dict, List
from data_structures import TextDetection
import deepl
import os

deepl_auth_key = os.environ.get('TAK', '')
translator = deepl.Translator(deepl_auth_key)
CACHE_FILE = 'translation_cache.json'

def load_translation_cache() -> Dict[str, str]:
    if os.path.exists(CACHE_FILE):
        with open(CACHE_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {}

def save_translation_cache(cache: Dict[str, str]):
    with open(CACHE_FILE, 'w', encoding='utf-8') as f:
        json.dump(cache, f, ensure_ascii=False, indent=2)

# Load the cache when the module is imported
translation_cache = load_translation_cache()

def translate_detections(detections: List[TextDetection], 
                         start_with_exclusions: List[str] = [], 
                         exact_match_exclusions: List[str] = []) -> List[TextDetection]:

    def is_excluded(text: str) -> bool:
        
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
        # return ''.join(cyrillic_to_latin.get(c.lower(), c) for c in text)
        return deepl(text)

    def deepl(text: str) -> str:
        # Check if the translation is already in the cache
        if text in translation_cache:
            return translation_cache[text]
        
        # If not in cache, translate using DeepL
        translated = translator.translate_text(text, target_lang="EN-GB").text
        
        # Store the new translation in the cache
        translation_cache[text] = translated
        save_translation_cache(translation_cache)
        
        return translated
        
    
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