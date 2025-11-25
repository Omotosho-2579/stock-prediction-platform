# src/models/base_model.py

from abc import ABC, abstractmethod
import pandas as pd
import numpy as np
from pathlib import Path
import sys

project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from src.utils.logger import Logger

class BaseModel(ABC):
    def __init__(self, name):
        self.name = name
        self.model = None
        self.is_trained = False
        self.logger = Logger(__name__)
        self.scaler = None
        self.feature_names = []
    
    @abstractmethod
    def build(self, input_shape=None):
        pass
    
    @abstractmethod
    def train(self, X_train, y_train, X_val=None, y_val=None):
        pass
    
    @abstractmethod
    def predict(self, X):
        pass
    
    @abstractmethod
    def save_model(self, file_path):
        pass
    
    @abstractmethod
    def load_model(self, file_path):
        pass
    
    def prepare_features(self, df):
        features = df[['Open', 'High', 'Low', 'Close', 'Volume']].copy()
        
        features['Returns'] = features['Close'].pct_change()
        features['Log_Returns'] = np.log(features['Close'] / features['Close'].shift(1))
        
        for period in [5, 10, 20]:
            features[f'SMA_{period}'] = features['Close'].rolling(window=period).mean()
            features[f'Volume_SMA_{period}'] = features['Volume'].rolling(window=period).mean()
        
        delta = features['Close'].diff()
        gain = delta.where(delta > 0, 0)
        loss = -delta.where(delta < 0, 0)
        avg_gain = gain.rolling(window=14).mean()
        avg_loss = loss.rolling(window=14).mean()
        rs = avg_gain / avg_loss
        features['RSI'] = 100 - (100 / (1 + rs))
        
        features['High_Low_Pct'] = (features['High'] - features['Low']) / features['Close'] * 100
        features['Close_Open_Pct'] = (features['Close'] - features['Open']) / features['Open'] * 100
        
        features = features.fillna(method='bfill').fillna(method='ffill')
        features = features.replace([np.inf, -np.inf], np.nan).fillna(0)
        
        return features
    
    def split_data(self, df, target_col='Close', test_size=0.2):
        features = self.prepare_features(df)
        
        split_index = int(len(features) * (1 - test_size))
        
        X = features.drop(columns=[target_col])
        y = features[target_col]
        
        X_train = X[:split_index]
        X_test = X[split_index:]
        y_train = y[:split_index]
        y_test = y[split_index:]
        
        self.feature_names = X.columns.tolist()
        
        return X_train, X_test, y_train, y_test
    
    def evaluate(self, X_test, y_test):
        from sklearn.metrics import mean_squared_error, mean_absolute_error, r2_score
        
        predictions = self.predict(X_test)
        
        mse = mean_squared_error(y_test, predictions)
        rmse = np.sqrt(mse)
        mae = mean_absolute_error(y_test, predictions)
        r2 = r2_score(y_test, predictions)
        
        mape = np.mean(np.abs((y_test - predictions) / y_test)) * 100
        
        metrics = {
            'mse': mse,
            'rmse': rmse,
            'mae': mae,
            'r2_score': r2,
            'mape': mape
        }
        
        self.logger.info(f"{self.name} - R²: {r2:.4f}, RMSE: {rmse:.4f}, MAE: {mae:.4f}")
        
        return metrics
    
    def get_feature_importance(self):
        return None