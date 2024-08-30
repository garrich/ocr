from dataclasses import dataclass
import json
import os
from typing import List, OrderedDict, Tuple, Union

@dataclass
class TextDetection:
    bbox: List[Tuple[int, int]]
    text: str
    confidence: float
    translated_text: str = ""
    rotation_angle: float = 0.0

class FontSizeCache:
    def __init__(self, max_size=10000, cache_file='resources/size-dict.txt'):
        self.max_size = max_size
        self.cache_file = cache_file
        self.cache: OrderedDict[Tuple[int, int, int], Union[int, float]] = OrderedDict()
        self.load_cache()
        
        # Initial guesses for common scenarios
        self.initial_guesses = {
            (100, 20, 5): 14,  # Small box, short text
            (200, 40, 10): 20, # Medium box, medium text
            (300, 60, 15): 28, # Large box, long text
            # Add more initial guesses as needed
        }
        
    def get(self, bbox_width: int, bbox_height: int, text_length: int) -> Union[int, float]:
        key = (bbox_width, bbox_height, text_length)
        if key in self.cache:
            # Move accessed item to the end to mark it as recently used
            self.cache.move_to_end(key)
            return self.cache[key]
        return self.initial_guesses.get(key)
    
    def set(self, bbox_width: int, bbox_height: int, text_length: int, font_size: Union[int, float]):
        key = (bbox_width, bbox_height, text_length)
        if key in self.cache:
            self.cache.move_to_end(key)
        elif len(self.cache) >= self.max_size:
            self.cache.popitem(last=False)  # Remove the least recently used item
        self.cache[key] = font_size
        self.save_cache()
    
    def load_cache(self):
        if os.path.exists(self.cache_file):
            try:
                with open(self.cache_file, 'r') as f:
                    data = json.load(f)
                    self.cache = OrderedDict(
                        (tuple(map(int, k.strip('()').split(','))),
                         float(v) if '.' in str(v) else int(v))
                        for k, v in data.items()
                    )
            except (json.JSONDecodeError, ValueError) as e:
                print(f"Error reading cache file: {self.cache_file}. Creating a new cache. Error: {e}")
                self.cache = OrderedDict()
        else:
            print(f"Cache file not found: {self.cache_file}. Creating a new cache.")
            self.cache = OrderedDict()
    
    def save_cache(self):
        os.makedirs(os.path.dirname(self.cache_file), exist_ok=True)
        with open(self.cache_file, 'w') as f:
            json.dump({str(k): v for k, v in self.cache.items()}, f)