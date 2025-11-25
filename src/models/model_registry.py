# src/models/model_registry.py

import json
import pandas as pd
from pathlib import Path
from datetime import datetime
import sys

project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from app.config import MODELS_DIR, POPULAR_MODELS_DIR, CACHED_MODELS_DIR
from src.utils.logger import Logger

class ModelRegistry:
    def __init__(self):
        self.logger = Logger(__name__)
        self.registry_file = MODELS_DIR / "model_metadata.json"
        self.registry = self._load_registry()
    
    def _load_registry(self):
        if self.registry_file.exists():
            try:
                with open(self.registry_file, 'r') as f:
                    return json.load(f)
            except Exception as e:
                self.logger.error(f"Error loading registry: {str(e)}")
                return {}
        return {}
    
    def _save_registry(self):
        try:
            with open(self.registry_file, 'w') as f:
                json.dump(self.registry, f, indent=2, default=str)
            return True
        except Exception as e:
            self.logger.error(f"Error saving registry: {str(e)}")
            return False
    
    def register_model(self, symbol, model_type, metrics, is_popular=False):
        key = f"{symbol}_{model_type}"
        
        model_info = {
            'symbol': symbol,
            'model_type': model_type,
            'is_popular': is_popular,
            'trained_date': datetime.now().isoformat(),
            'metrics': metrics,
            'file_path': str(self._get_model_path(symbol, model_type, is_popular))
        }
        
        self.registry[key] = model_info
        self._save_registry()
        
        self.logger.info(f"Registered model: {key}")
    
    def _get_model_path(self, symbol, model_type, is_popular):
        base_dir = POPULAR_MODELS_DIR if is_popular else CACHED_MODELS_DIR
        extension = '.h5' if model_type == 'lstm' else '.pkl'
        return base_dir / f"{symbol}_{model_type}{extension}"
    
    def get_model_info(self, symbol, model_type):
        key = f"{symbol}_{model_type}"
        return self.registry.get(key, None)
    
    def is_model_available(self, symbol, model_type):
        key = f"{symbol}_{model_type}"
        
        if key not in self.registry:
            return False
        
        model_path = Path(self.registry[key]['file_path'])
        return model_path.exists()
    
    def get_models_for_symbol(self, symbol):
        models = []
        
        for key, info in self.registry.items():
            if info['symbol'] == symbol:
                models.append(info)
        
        return models
    
    def get_all_models(self):
        return list(self.registry.values())
    
    def get_popular_models(self):
        return [info for info in self.registry.values() if info.get('is_popular', False)]
    
    def is_model_stale(self, symbol, model_type, max_age_days=7):
        model_info = self.get_model_info(symbol, model_type)
        
        if not model_info:
            return True
        
        trained_date = datetime.fromisoformat(model_info['trained_date'])
        age = (datetime.now() - trained_date).days
        
        return age > max_age_days
    
    def delete_model(self, symbol, model_type):
        key = f"{symbol}_{model_type}"
        
        if key in self.registry:
            model_path = Path(self.registry[key]['file_path'])
            
            if model_path.exists():
                try:
                    model_path.unlink()
                    self.logger.info(f"Deleted model file: {model_path}")
                except Exception as e:
                    self.logger.error(f"Error deleting model file: {str(e)}")
            
            del self.registry[key]
            self._save_registry()
            
            self.logger.info(f"Removed model from registry: {key}")
            return True
        
        return False
    
    def get_best_model_for_symbol(self, symbol):
        models = self.get_models_for_symbol(symbol)
        
        if not models:
            return None
        
        valid_models = [m for m in models if m.get('metrics', {}).get('r2_score')]
        
        if not valid_models:
            return models[0]
        
        best_model = max(valid_models, key=lambda m: m['metrics']['r2_score'])
        
        return best_model
    
    def get_registry_summary(self):
        total_models = len(self.registry)
        popular_models = len(self.get_popular_models())
        
        symbols = set(info['symbol'] for info in self.registry.values())
        model_types = set(info['model_type'] for info in self.registry.values())
        
        summary = {
            'total_models': total_models,
            'popular_models': popular_models,
            'cached_models': total_models - popular_models,
            'unique_symbols': len(symbols),
            'model_types': list(model_types)
        }
        
        return summary