# src/models/random_forest.py

import numpy as np
import pandas as pd
import pickle
from sklearn.ensemble import RandomForestRegressor
from sklearn.preprocessing import StandardScaler
from pathlib import Path
import sys

project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from src.models.base_model import BaseModel

class RandomForestModel(BaseModel):
    def __init__(self, n_estimators=100, max_depth=None, random_state=42):
        super().__init__("Random Forest")
        self.n_estimators = n_estimators
        self.max_depth = max_depth
        self.random_state = random_state
        self.scaler = StandardScaler()
    
    def build(self, input_shape=None):
        self.model = RandomForestRegressor(
            n_estimators=self.n_estimators,
            max_depth=self.max_depth,
            random_state=self.random_state,
            n_jobs=-1
        )
        self.logger.info(f"{self.name} model built with {self.n_estimators} estimators")
    
    def train(self, X_train, y_train, X_val=None, y_val=None):
        if self.model is None:
            self.build()
        
        X_train_scaled = self.scaler.fit_transform(X_train)
        
        self.model.fit(X_train_scaled, y_train)
        
        self.is_trained = True
        self.logger.info(f"{self.name} training completed")
        
        train_score = self.model.score(X_train_scaled, y_train)
        self.logger.info(f"Training R² Score: {train_score:.4f}")
        
        if X_val is not None and y_val is not None:
            X_val_scaled = self.scaler.transform(X_val)
            val_score = self.model.score(X_val_scaled, y_val)
            self.logger.info(f"Validation R² Score: {val_score:.4f}")
        
        return self
    
    def predict(self, X):
        if not self.is_trained:
            raise ValueError("Model must be trained before prediction")
        
        X_scaled = self.scaler.transform(X)
        predictions = self.model.predict(X_scaled)
        
        return predictions
    
    def predict_future(self, last_data, days=30):
        predictions = []
        current_data = last_data.copy()
        
        for _ in range(days):
            if len(current_data) < len(self.feature_names):
                features = self.prepare_features(current_data)
            else:
                features = current_data
            
            X = features[self.feature_names].iloc[-1:].values
            X_scaled = self.scaler.transform(X)
            
            pred = self.model.predict(X_scaled)[0]
            predictions.append(pred)
            
            new_row = features.iloc[-1:].copy()
            new_row['Close'] = pred
            current_data = pd.concat([current_data, new_row])
        
        return np.array(predictions)
    
    def save_model(self, file_path):
        try:
            model_data = {
                'model': self.model,
                'scaler': self.scaler,
                'feature_names': self.feature_names,
                'is_trained': self.is_trained,
                'n_estimators': self.n_estimators,
                'max_depth': self.max_depth
            }
            
            with open(file_path, 'wb') as f:
                pickle.dump(model_data, f)
            
            self.logger.info(f"{self.name} saved to {file_path}")
            return True
        
        except Exception as e:
            self.logger.error(f"Error saving model: {str(e)}")
            return False
    
    def load_model(self, file_path):
        try:
            with open(file_path, 'rb') as f:
                model_data = pickle.load(f)
            
            self.model = model_data['model']
            self.scaler = model_data['scaler']
            self.feature_names = model_data['feature_names']
            self.is_trained = model_data['is_trained']
            self.n_estimators = model_data.get('n_estimators', 100)
            self.max_depth = model_data.get('max_depth', None)
            
            self.logger.info(f"{self.name} loaded from {file_path}")
            return True
        
        except Exception as e:
            self.logger.error(f"Error loading model: {str(e)}")
            return False
    
    def get_feature_importance(self):
        if self.model is None or not self.is_trained:
            return None
        
        importances = self.model.feature_importances_
        
        importance_df = pd.DataFrame({
            'feature': self.feature_names,
            'importance': importances
        })
        
        importance_df = importance_df.sort_values('importance', ascending=False)
        
        return importance_df