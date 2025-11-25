# src/models/lstm_model.py

import numpy as np
import pandas as pd
import pickle
from pathlib import Path
import sys

project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from src.models.base_model import BaseModel

try:
    from tensorflow import keras
    from tensorflow.keras.models import Sequential
    from tensorflow.keras.layers import LSTM, Dense, Dropout
    from tensorflow.keras.callbacks import EarlyStopping
    from sklearn.preprocessing import MinMaxScaler
    KERAS_AVAILABLE = True
except ImportError:
    KERAS_AVAILABLE = False

class LSTMModel(BaseModel):
    def __init__(self, lookback=60):
        super().__init__("LSTM")
        self.lookback = lookback
        self.scaler = MinMaxScaler(feature_range=(0, 1))
        
        if not KERAS_AVAILABLE:
            self.logger.warning("TensorFlow/Keras not available. LSTM model disabled.")
    
    def build(self, input_shape=None):
        if not KERAS_AVAILABLE:
            raise ImportError("TensorFlow/Keras required for LSTM model")
        
        if input_shape is None:
            input_shape = (self.lookback, 1)
        
        self.model = Sequential([
            LSTM(units=50, return_sequences=True, input_shape=input_shape),
            Dropout(0.2),
            LSTM(units=50, return_sequences=True),
            Dropout(0.2),
            LSTM(units=50),
            Dropout(0.2),
            Dense(units=1)
        ])
        
        self.model.compile(optimizer='adam', loss='mean_squared_error')
        self.logger.info(f"{self.name} model built with input shape {input_shape}")
    
    def prepare_sequences(self, data):
        data_scaled = self.scaler.fit_transform(data.reshape(-1, 1))
        
        X, y = [], []
        for i in range(self.lookback, len(data_scaled)):
            X.append(data_scaled[i-self.lookback:i, 0])
            y.append(data_scaled[i, 0])
        
        X, y = np.array(X), np.array(y)
        X = np.reshape(X, (X.shape[0], X.shape[1], 1))
        
        return X, y
    
    def train(self, X_train, y_train, X_val=None, y_val=None, epochs=50, batch_size=32):
        if not KERAS_AVAILABLE:
            raise ImportError("TensorFlow/Keras required for LSTM model")
        
        if isinstance(X_train, pd.DataFrame):
            X_train = X_train['Close'].values
        if isinstance(y_train, pd.Series):
            y_train = y_train.values
        
        X_seq, y_seq = self.prepare_sequences(X_train)
        
        if self.model is None:
            self.build(input_shape=(X_seq.shape[1], 1))
        
        early_stop = EarlyStopping(monitor='loss', patience=5, restore_best_weights=True)
        
        history = self.model.fit(
            X_seq, y_seq,
            epochs=epochs,
            batch_size=batch_size,
            callbacks=[early_stop],
            verbose=0
        )
        
        self.is_trained = True
        self.logger.info(f"{self.name} training completed")
        
        return self
    
    def predict(self, X):
        if not self.is_trained:
            raise ValueError("Model must be trained before prediction")
        
        if isinstance(X, pd.DataFrame):
            X = X['Close'].values if 'Close' in X.columns else X.iloc[:, 0].values
        
        X_scaled = self.scaler.transform(X.reshape(-1, 1))
        
        if len(X_scaled) < self.lookback:
            raise ValueError(f"Input data must have at least {self.lookback} samples")
        
        X_seq = []
        for i in range(self.lookback, len(X_scaled) + 1):
            X_seq.append(X_scaled[i-self.lookback:i, 0])
        
        X_seq = np.array(X_seq)
        X_seq = np.reshape(X_seq, (X_seq.shape[0], X_seq.shape[1], 1))
        
        predictions_scaled = self.model.predict(X_seq, verbose=0)
        predictions = self.scaler.inverse_transform(predictions_scaled)
        
        return predictions.flatten()
    
    def predict_future(self, last_data, days=30):
        if isinstance(last_data, pd.DataFrame):
            last_data = last_data['Close'].values
        
        last_sequence = last_data[-self.lookback:]
        last_sequence_scaled = self.scaler.transform(last_sequence.reshape(-1, 1))
        
        predictions = []
        current_sequence = last_sequence_scaled.copy()
        
        for _ in range(days):
            X_input = current_sequence[-self.lookback:].reshape(1, self.lookback, 1)
            pred_scaled = self.model.predict(X_input, verbose=0)
            pred = self.scaler.inverse_transform(pred_scaled)[0, 0]
            
            predictions.append(pred)
            
            current_sequence = np.append(current_sequence, pred_scaled)
            current_sequence = current_sequence.reshape(-1, 1)
        
        return np.array(predictions)
    
    def save_model(self, file_path):
        if not KERAS_AVAILABLE:
            return False
        
        try:
            model_path = str(file_path).replace('.pkl', '.h5')
            self.model.save(model_path)
            
            scaler_path = str(file_path).replace('.h5', '_scaler.pkl')
            with open(scaler_path, 'wb') as f:
                pickle.dump({
                    'scaler': self.scaler,
                    'lookback': self.lookback,
                    'feature_names': self.feature_names
                }, f)
            
            self.logger.info(f"{self.name} saved to {model_path}")
            return True
        
        except Exception as e:
            self.logger.error(f"Error saving model: {str(e)}")
            return False
    
    def load_model(self, file_path):
        if not KERAS_AVAILABLE:
            return False
        
        try:
            model_path = str(file_path).replace('.pkl', '.h5')
            self.model = keras.models.load_model(model_path)
            
            scaler_path = str(file_path).replace('.h5', '_scaler.pkl')
            with open(scaler_path, 'rb') as f:
                data = pickle.load(f)
                self.scaler = data['scaler']
                self.lookback = data['lookback']
                self.feature_names = data.get('feature_names', [])
            
            self.is_trained = True
            self.logger.info(f"{self.name} loaded from {model_path}")
            return True
        
        except Exception as e:
            self.logger.error(f"Error loading model: {str(e)}")
            return False