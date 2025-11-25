# src/models/model_trainer.py

import numpy as np
import pandas as pd
from pathlib import Path
import sys
from datetime import datetime

project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from src.models.linear_regression import LinearRegressionModel
from src.models.random_forest import RandomForestModel
from src.models.xgboost_model import XGBoostModel
from src.models.lstm_model import LSTMModel
from src.models.ensemble import EnsembleModel
from src.utils.logger import Logger

class ModelTrainer:
    def __init__(self):
        self.logger = Logger(__name__)
        self.training_history = []
    
    def train_model(self, model_type, X_train, y_train, X_val=None, y_val=None, **kwargs):
        self.logger.info(f"Starting training for {model_type}")
        start_time = datetime.now()
        
        try:
            if model_type == 'linear_regression':
                model = LinearRegressionModel()
            elif model_type == 'random_forest':
                model = RandomForestModel(**kwargs)
            elif model_type == 'xgboost':
                model = XGBoostModel(**kwargs)
            elif model_type == 'lstm':
                model = LSTMModel(**kwargs)
            elif model_type == 'ensemble':
                model = EnsembleModel()
            else:
                raise ValueError(f"Unknown model type: {model_type}")
            
            model.build()
            model.train(X_train, y_train, X_val, y_val)
            
            end_time = datetime.now()
            training_time = (end_time - start_time).total_seconds()
            
            training_record = {
                'model_type': model_type,
                'timestamp': start_time,
                'training_time': training_time,
                'samples': len(X_train),
                'features': X_train.shape[1] if hasattr(X_train, 'shape') else 0,
                'success': True
            }
            
            self.training_history.append(training_record)
            self.logger.info(f"{model_type} training completed in {training_time:.2f}s")
            
            return model
        
        except Exception as e:
            self.logger.error(f"Error training {model_type}: {str(e)}")
            
            training_record = {
                'model_type': model_type,
                'timestamp': start_time,
                'training_time': 0,
                'samples': 0,
                'features': 0,
                'success': False,
                'error': str(e)
            }
            
            self.training_history.append(training_record)
            return None
    
    def train_all_models(self, df, target_col='Close', test_size=0.2):
        self.logger.info("Training all models")
        
        from src.models.base_model import BaseModel
        base_model = BaseModel("temp")
        X_train, X_test, y_train, y_test = base_model.split_data(df, target_col, test_size)
        
        models = {}
        model_types = ['linear_regression', 'random_forest', 'xgboost']
        
        for model_type in model_types:
            model = self.train_model(model_type, X_train, y_train, X_test, y_test)
            if model is not None:
                models[model_type] = model
        
        if len(models) > 1:
            ensemble = EnsembleModel(models=models)
            ensemble.feature_names = X_train.columns.tolist()
            ensemble.is_trained = True
            models['ensemble'] = ensemble
        
        return models
    
    def train_with_progress(self, model_type, X_train, y_train, progress_callback=None):
        total_steps = 5
        current_step = 0
        
        if progress_callback:
            progress_callback(current_step / total_steps, "Initializing model...")
        
        current_step += 1
        
        if model_type == 'linear_regression':
            model = LinearRegressionModel()
        elif model_type == 'random_forest':
            model = RandomForestModel()
        elif model_type == 'xgboost':
            model = XGBoostModel()
        elif model_type == 'lstm':
            model = LSTMModel()
        else:
            raise ValueError(f"Unknown model type: {model_type}")
        
        if progress_callback:
            progress_callback(current_step / total_steps, "Building model architecture...")
        
        current_step += 1
        model.build()
        
        if progress_callback:
            progress_callback(current_step / total_steps, "Preparing training data...")
        
        current_step += 1
        
        if progress_callback:
            progress_callback(current_step / total_steps, "Training model...")
        
        current_step += 1
        model.train(X_train, y_train)
        
        if progress_callback:
            progress_callback(current_step / total_steps, "Training complete!")
        
        return model
    
    def get_training_history(self):
        return pd.DataFrame(self.training_history)
    
    def get_training_summary(self):
        if not self.training_history:
            return {}
        
        df = pd.DataFrame(self.training_history)
        
        summary = {
            'total_trainings': len(df),
            'successful': df['success'].sum(),
            'failed': (~df['success']).sum(),
            'avg_training_time': df[df['success']]['training_time'].mean(),
            'models_trained': df[df['success']]['model_type'].unique().tolist()
        }
        
        return summary