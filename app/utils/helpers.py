import os
import json

def save_to_cache(data: any, filename: str) -> str:
    """Save data to cache file."""
    cache_dir = "cache"
    os.makedirs(cache_dir, exist_ok=True)
    filepath = os.path.join(cache_dir, filename)
    
    if isinstance(data, str):
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(data)
    else:
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2)
    return filepath

def load_from_cache(filename: str) -> any:
    """Load data from cache file."""
    filepath = os.path.join("cache", filename)
    if not os.path.exists(filepath):
        return None
        
    if filename.endswith('.json'):
        with open(filepath, 'r', encoding='utf-8') as f:
            return json.load(f)
    else:
        with open(filepath, 'r', encoding='utf-8') as f:
            return f.read()

def ensure_directory_exists(path: str) -> None:
    """Ensure that a directory exists, create if it doesn't."""
    os.makedirs(path, exist_ok=True) 