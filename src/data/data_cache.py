# src/data/data_cache.py

import pandas as pd
import pickle
from pathlib import Path
from datetime import datetime, timedelta
import sys

project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from app.config import CACHE_DIR, CACHE_TTL_HOURS
from src.utils.logger import Logger

class DataCache:
    def __init__(self):
        self.cache_dir = CACHE_DIR
        self.ttl_hours = CACHE_TTL_HOURS
        self.logger = Logger(__name__)
        
        self.cache_dir.mkdir(parents=True, exist_ok=True)
    
    def get_cache_path(self, symbol, period, data_type='stock'):
        filename = f"{symbol}_{period}_{data_type}.pkl"
        return self.cache_dir / filename
    
    def get_cached_data(self, symbol, period, data_type='stock'):
        cache_path = self.get_cache_path(symbol, period, data_type)
        
        if not cache_path.exists():
            return None
        
        try:
            file_age = datetime.now() - datetime.fromtimestamp(cache_path.stat().st_mtime)
            
            if file_age > timedelta(hours=self.ttl_hours):
                self.logger.info(f"Cache expired for {symbol} (age: {file_age})")
                cache_path.unlink()
                return None
            
            with open(cache_path, 'rb') as f:
                cached_data = pickle.load(f)
            
            self.logger.info(f"Loaded {symbol} from cache (age: {file_age})")
            return cached_data
        
        except Exception as e:
            self.logger.error(f"Error loading cache for {symbol}: {str(e)}")
            return None
    
    def save_to_cache(self, symbol, data, period, data_type='stock'):
        cache_path = self.get_cache_path(symbol, period, data_type)
        
        try:
            with open(cache_path, 'wb') as f:
                pickle.dump(data, f)
            
            self.logger.info(f"Saved {symbol} to cache")
            return True
        
        except Exception as e:
            self.logger.error(f"Error saving cache for {symbol}: {str(e)}")
            return False
    
    def clear_cache(self, symbol=None, data_type=None):
        try:
            if symbol:
                pattern = f"{symbol}_*"
                if data_type:
                    pattern = f"{symbol}_*_{data_type}.pkl"
                else:
                    pattern = f"{symbol}_*.pkl"
                
                for cache_file in self.cache_dir.glob(pattern):
                    cache_file.unlink()
                    self.logger.info(f"Deleted cache: {cache_file.name}")
            else:
                for cache_file in self.cache_dir.glob("*.pkl"):
                    cache_file.unlink()
                
                self.logger.info("Cleared all cache")
            
            return True
        
        except Exception as e:
            self.logger.error(f"Error clearing cache: {str(e)}")
            return False
    
    def clear_expired_cache(self):
        try:
            count = 0
            for cache_file in self.cache_dir.glob("*.pkl"):
                file_age = datetime.now() - datetime.fromtimestamp(cache_file.stat().st_mtime)
                
                if file_age > timedelta(hours=self.ttl_hours):
                    cache_file.unlink()
                    count += 1
            
            self.logger.info(f"Cleared {count} expired cache files")
            return count
        
        except Exception as e:
            self.logger.error(f"Error clearing expired cache: {str(e)}")
            return 0
    
    def get_cache_size(self):
        try:
            total_size = sum(f.stat().st_size for f in self.cache_dir.glob("*.pkl"))
            return total_size
        
        except Exception as e:
            self.logger.error(f"Error calculating cache size: {str(e)}")
            return 0
    
    def get_cache_info(self):
        try:
            cache_files = list(self.cache_dir.glob("*.pkl"))
            
            info = {
                'total_files': len(cache_files),
                'total_size_bytes': self.get_cache_size(),
                'total_size_mb': self.get_cache_size() / (1024 * 1024),
                'files': []
            }
            
            for cache_file in cache_files:
                file_age = datetime.now() - datetime.fromtimestamp(cache_file.stat().st_mtime)
                
                info['files'].append({
                    'name': cache_file.name,
                    'size_bytes': cache_file.stat().st_size,
                    'age_hours': file_age.total_seconds() / 3600,
                    'expired': file_age > timedelta(hours=self.ttl_hours)
                })
            
            return info
        
        except Exception as e:
            self.logger.error(f"Error getting cache info: {str(e)}")
            return {}