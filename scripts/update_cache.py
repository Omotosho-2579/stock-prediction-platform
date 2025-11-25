# scripts/update_cache.py

import sys
from pathlib import Path

project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from app.config import CACHE_DIR
from src.data.data_cache import DataCache
from src.utils.logger import Logger

class CacheUpdater:
    def __init__(self):
        self.logger = Logger(__name__)
        self.cache = DataCache()
    
    def clear_expired_cache(self):
        self.logger.info("Clearing expired cache files...")
        
        count = self.cache.clear_expired_cache()
        
        self.logger.info(f"Cleared {count} expired cache files")
        return count
    
    def clear_all_cache(self):
        self.logger.info("Clearing all cache files...")
        
        self.cache.clear_cache()
        
        self.logger.info("All cache cleared")
    
    def get_cache_statistics(self):
        info = self.cache.get_cache_info()
        
        print("\n=== Cache Statistics ===")
        print(f"Total Files: {info['total_files']}")
        print(f"Total Size: {info['total_size_mb']:.2f} MB")
        print(f"\nExpired Files: {len([f for f in info['files'] if f['expired']])}")
        
        return info

if __name__ == "__main__":
    updater = CacheUpdater()
    
    import argparse
    parser = argparse.ArgumentParser(description='Cache management utility')
    parser.add_argument('--clear-expired', action='store_true', help='Clear expired cache')
    parser.add_argument('--clear-all', action='store_true', help='Clear all cache')
    parser.add_argument('--stats', action='store_true', help='Show cache statistics')
    
    args = parser.parse_args()
    
    if args.clear_expired:
        updater.clear_expired_cache()
    elif args.clear_all:
        updater.clear_all_cache()
    elif args.stats:
        updater.get_cache_statistics()
    else:
        print("Use --help to see available options")