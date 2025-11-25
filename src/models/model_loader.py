# src/models/model_loader.py

import pandas as pd
from pathlib import Path
import sys

project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from app.config import get_model_path, POPULAR_STOCKS
from src.models.model_registry import ModelRegistry
from src.models.linear_regression import LinearRegressionModel
from src.models.random_forest import RandomForestModel
from src.models.xgboost_model import XGBoostModel
from src.models.lstm_model import LSTMModel
from src.models.ensemble import EnsembleModel
from src.models.model_trainer import ModelTrainer
from src.utils.logger import Logger

class ModelLoader:
    def __init__(self):
        self.logger = Logger(__name__)
        self.registry = ModelRegistry()
        self.trainer = ModelTrainer()
    
    def load_or_train(self, symbol, model_type, df=None, force_retrain=False):
        is_popular = symbol in POPULAR_STOCKS
        
        if not force_retrain and self.registry.is_model_available(symbol, model_type):
            if not self.registry.is_model_stale(symbol, model_type):
                self.logger.info(f"Loading existing model: {symbol}_{model_type}")
                return self._load_model(symbol, model_type, is_popular)
        
        if df is None:
            self.logger.error("Cannot train model without data")
            return None
        
        self.logger.info(f"Training new model: {symbol}_{model_type}")
        return self._train_and_save_model(symbol, model_type, df, is_popular)
    
    def _load_model(self, symbol, model_type, is_popular):
        try:
            model_path = get_model_path(symbol, model_type, is_popular)
            
            if model_type == 'linear_regression':
                model = LinearRegressionModel()
            elif model_type == 'random_forest':
                model = RandomForestModel()
            elif model_type == 'xgboost':
                model = XGBoostModel()
            elif model_type == 'lstm':
                model = LSTMModel()
            elif model_type == 'ensemble':
                model = EnsembleModel()
            else:
                self.logger.error(f"Unknown model type: {model_type}")
                return None
            
            if model.load_model(model_path):
                return model
            
            return None
        
        except Exception as e:
            self.logger.error(f"Error loading model: {str(e)}")
            return None
    
    def _train_and_save_model(self, symbol, model_type, df, is_popular):
        try:
            if model_type == 'linear_regression':
                model = LinearRegressionModel()
            elif model_type == 'random_forest':
                model = RandomForestModel()
            elif model_type == 'xgboost':
                model = XGBoostModel()
            elif model_type == 'lstm':
                model = LSTMModel()
            elif model_type == 'ensemble':
                model = EnsembleModel()
            else:
                self.logger.error(f"Unknown model type: {model_type}")
                return None
            
            X_train, X_test, y_train, y_test = model.split_data(df)
            
            model.train(X_train, y_train, X_test, y_test)
            
            metrics = model.evaluate(X_test, y_test)
            
            model_path = get_model_path(symbol, model_type, is_popular)
            model.save_model(model_path)
            
            self.registry.register_model(symbol, model_type, metrics, is_popular)
            
            return model
        
        except Exception as e:
            self.logger.error(f"Error training and saving model: {str(e)}")
            return None
    
    def predict(self, df, symbol, model_type, forecast_days=30):
        model = self.load_or_train(symbol, model_type, df)
        
        if model is None:
            self.logger.error(f"Failed to load or train model: {symbol}_{model_type}")
            return None
        
        try:
            predictions = model.predict_future(df, days=forecast_days)
            return predictions
        
        except Exception as e:
            self.logger.error(f"Error making predictions: {str(e)}")
            return None
    
    def load_all_models_for_symbol(self, symbol, df=None):
        models = {}
        model_types = ['linear_regression', 'random_forest', 'xgboost']
        
        for model_type in model_types:
            model = self.load_or_train(symbol, model_type, df)
            if model is not None:
                models[model_type] = model
        
        return models
    
    def get_best_model(self, symbol, df=None):
        best_model_info = self.registry.get_best_model_for_symbol(symbol)
        
        if best_model_info:
            model_type = best_model_info['model_type']
            return self.load_or_train(symbol, model_type, df)
        
        if df is not None:
            return self._train_and_save_model(symbol, 'ensemble', df, symbol in POPULAR_STOCKS)
        
        return None