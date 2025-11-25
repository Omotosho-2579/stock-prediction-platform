# src/models/ensemble.py

import numpy as np
import pandas as pd
import pickle
from pathlib import Path
import sys

project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from src.models.base_model import BaseModel
from src.models.linear_regression import LinearRegressionModel
from src.models.random_forest import RandomForestModel
from src.models.xgboost_model import XGBoostModel
from src.models.lstm_model import LSTMModel

class EnsembleModel(BaseModel):
    def __init__(self, models=None, weights=None):
        super().__init__("Ensemble")
        
        if models is None:
            self.models = {
                'linear_regression': LinearRegressionModel(),
                'random_forest': RandomForestModel(),
                'xgboost': XGBoostModel()
            }
        else:
            self.models = models
        
        if weights is None:
            self.weights = {name: 1.0 / len(self.models) for name in self.models.keys()}
        else:
            self.weights = weights
        
        self._normalize_weights()
    
    def _normalize_weights(self):
        total_weight = sum(self.weights.values())
        if total_weight > 0:
            self.weights = {k: v / total_weight for k, v in self.weights.items()}
    
    def build(self, input_shape=None):
        for model in self.models.values():
            model.build(input_shape)
        
        self.logger.info(f"{self.name} built with {len(self.models)} models")
    
    def train(self, X_train, y_train, X_val=None, y_val=None):
        self.logger.info(f"Training {len(self.models)} models in ensemble")
        
        for name, model in self.models.items():
            try:
                self.logger.info(f"Training {name}...")
                model.train(X_train, y_train, X_val, y_val)
            except Exception as e:
                self.logger.error(f"Error training {name}: {str(e)}")
                self.weights[name] = 0
        
        self._normalize_weights()
        self.is_trained = True
        self.logger.info(f"{self.name} training completed")
        
        return self
    
    def predict(self, X):
        if not self.is_trained:
            raise ValueError("Model must be trained before prediction")
        
        predictions = {}
        
        for name, model in self.models.items():
            if self.weights[name] > 0:
                try:
                    predictions[name] = model.predict(X)
                except Exception as e:
                    self.logger.error(f"Error predicting with {name}: {str(e)}")
                    self.weights[name] = 0
        
        if not predictions:
            raise ValueError("No models available for prediction")
        
        ensemble_pred = np.zeros(len(predictions[list(predictions.keys())[0]]))
        
        for name, pred in predictions.items():
            ensemble_pred += pred * self.weights[name]
        
        return ensemble_pred
    
    def predict_future(self, last_data, days=30):
        predictions = {}
        
        for name, model in self.models.items():
            if self.weights[name] > 0:
                try:
                    predictions[name] = model.predict_future(last_data, days)
                except Exception as e:
                    self.logger.error(f"Error predicting future with {name}: {str(e)}")
                    continue
        
        if not predictions:
            raise ValueError("No models available for future prediction")
        
        ensemble_pred = np.zeros(days)
        
        for name, pred in predictions.items():
            ensemble_pred += pred * self.weights[name]
        
        return ensemble_pred
    
    def optimize_weights(self, X_val, y_val):
        from scipy.optimize import minimize
        
        def objective(weights):
            weighted_pred = np.zeros(len(y_val))
            
            for i, (name, model) in enumerate(self.models.items()):
                try:
                    pred = model.predict(X_val)
                    weighted_pred += pred * weights[i]
                except:
                    pass
            
            mse = np.mean((y_val - weighted_pred) ** 2)
            return mse
        
        initial_weights = list(self.weights.values())
        bounds = [(0, 1) for _ in range(len(self.models))]
        constraints = {'type': 'eq', 'fun': lambda w: np.sum(w) - 1}
        
        result = minimize(objective, initial_weights, bounds=bounds, constraints=constraints)
        
        if result.success:
            optimized_weights = result.x
            for i, name in enumerate(self.models.keys()):
                self.weights[name] = optimized_weights[i]
            
            self.logger.info(f"Optimized weights: {self.weights}")
        
        return self.weights
    
    def save_model(self, file_path):
        try:
            model_data = {
                'weights': self.weights,
                'feature_names': self.feature_names,
                'is_trained': self.is_trained,
                'model_names': list(self.models.keys())
            }
            
            with open(file_path, 'wb') as f:
                pickle.dump(model_data, f)
            
            base_path = Path(file_path).parent
            for name, model in self.models.items():
                model_path = base_path / f"{Path(file_path).stem}_{name}.pkl"
                model.save_model(model_path)
            
            self.logger.info(f"{self.name} saved to {file_path}")
            return True
        
        except Exception as e:
            self.logger.error(f"Error saving ensemble model: {str(e)}")
            return False
    
    def load_model(self, file_path):
        try:
            with open(file_path, 'rb') as f:
                model_data = pickle.load(f)
            
            self.weights = model_data['weights']
            self.feature_names = model_data['feature_names']
            self.is_trained = model_data['is_trained']
            
            base_path = Path(file_path).parent
            for name in model_data['model_names']:
                model_path = base_path / f"{Path(file_path).stem}_{name}.pkl"
                if model_path.exists() and name in self.models:
                    self.models[name].load_model(model_path)
            
            self.logger.info(f"{self.name} loaded from {file_path}")
            return True
        
        except Exception as e:
            self.logger.error(f"Error loading ensemble model: {str(e)}")
            return False
    
    def get_model_contributions(self):
        return pd.DataFrame({
            'model': list(self.weights.keys()),
            'weight': list(self.weights.values())
        }).sort_values('weight', ascending=False)