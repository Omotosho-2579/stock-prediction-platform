# src/utils/helpers.py

import hashlib
import uuid
from datetime import datetime, timedelta
import re
from pathlib import Path
import sys

project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from src.utils.logger import Logger

class Helpers:
    def __init__(self):
        self.logger = Logger(__name__)
    
    @staticmethod
    def generate_unique_id():
        return str(uuid.uuid4())
    
    @staticmethod
    def generate_hash(text):
        return hashlib.sha256(text.encode()).hexdigest()
    
    @staticmethod
    def calculate_percentage_change(old_value, new_value):
        if old_value == 0:
            return 0
        return ((new_value - old_value) / old_value) * 100
    
    @staticmethod
    def clamp(value, min_value, max_value):
        return max(min_value, min(value, max_value))
    
    @staticmethod
    def safe_divide(numerator, denominator, default=0):
        try:
            if denominator == 0:
                return default
            return numerator / denominator
        except:
            return default
    
    @staticmethod
    def get_business_days(start_date, end_date):
        from pandas.tseries.offsets import BDay
        import pandas as pd
        
        date_range = pd.date_range(start=start_date, end=end_date, freq=BDay())
        return len(date_range)
    
    @staticmethod
    def is_market_hours():
        now = datetime.now()
        
        if now.weekday() >= 5:
            return False
        
        market_open = now.replace(hour=9, minute=30, second=0, microsecond=0)
        market_close = now.replace(hour=16, minute=0, second=0, microsecond=0)
        
        return market_open <= now <= market_close
    
    @staticmethod
    def chunk_list(lst, chunk_size):
        for i in range(0, len(lst), chunk_size):
            yield lst[i:i + chunk_size]
    
    @staticmethod
    def flatten_dict(d, parent_key='', sep='_'):
        items = []
        for k, v in d.items():
            new_key = f"{parent_key}{sep}{k}" if parent_key else k
            if isinstance(v, dict):
                items.extend(Helpers.flatten_dict(v, new_key, sep=sep).items())
            else:
                items.append((new_key, v))
        return dict(items)
    
    @staticmethod
    def sanitize_filename(filename):
        filename = re.sub(r'[^\w\s\-\.]', '', filename)
        filename = re.sub(r'[\s]+', '_', filename)
        return filename
    
    @staticmethod
    def get_file_size_mb(file_path):
        try:
            size_bytes = Path(file_path).stat().st_size
            return size_bytes / (1024 * 1024)
        except:
            return 0
    
    @staticmethod
    def truncate_string(text, max_length, suffix='...'):
        if len(text) <= max_length:
            return text
        return text[:max_length - len(suffix)] + suffix
    
    @staticmethod
    def deep_merge_dicts(dict1, dict2):
        result = dict1.copy()
        
        for key, value in dict2.items():
            if key in result and isinstance(result[key], dict) and isinstance(value, dict):
                result[key] = Helpers.deep_merge_dicts(result[key], value)
            else:
                result[key] = value
        
        return result
    
    @staticmethod
    def retry_operation(func, max_attempts=3, delay=1):
        import time
        
        for attempt in range(max_attempts):
            try:
                return func()
            except Exception as e:
                if attempt == max_attempts - 1:
                    raise e
                time.sleep(delay)
        
        return None
    
    @staticmethod
    def get_age_in_days(date_string):
        try:
            date = datetime.strptime(date_string, '%Y-%m-%d')
            return (datetime.now() - date).days
        except:
            return 0
    
    @staticmethod
    def batch_process(items, batch_size, processor_func):
        results = []
        
        for batch in Helpers.chunk_list(items, batch_size):
            batch_results = processor_func(batch)
            results.extend(batch_results)
        
        return results