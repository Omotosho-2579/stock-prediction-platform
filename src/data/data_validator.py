# src/data/data_validator.py

import pandas as pd
import numpy as np
from pathlib import Path
import sys

project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from src.utils.logger import Logger

class DataValidator:
    def __init__(self):
        self.logger = Logger(__name__)
    
    def validate_and_clean(self, df):
        if df is None or df.empty:
            self.logger.warning("Empty dataframe provided")
            return None
        
        required_columns = ['Open', 'High', 'Low', 'Close', 'Volume']
        missing_columns = [col for col in required_columns if col not in df.columns]
        
        if missing_columns:
            self.logger.error(f"Missing required columns: {missing_columns}")
            return None
        
        df = self._handle_missing_values(df)
        df = self._remove_outliers(df)
        df = self._fix_data_types(df)
        df = self._validate_price_relationships(df)
        
        return df
    
    def _handle_missing_values(self, df):
        original_length = len(df)
        
        df = df.replace([np.inf, -np.inf], np.nan)
        
        missing_pct = (df.isnull().sum() / len(df)) * 100
        
        for col in df.columns:
            if missing_pct[col] > 50:
                self.logger.warning(f"Column {col} has {missing_pct[col]:.1f}% missing values")
        
        if 'Volume' in df.columns:
            df['Volume'].fillna(0, inplace=True)
        
        for col in ['Open', 'High', 'Low', 'Close']:
            if col in df.columns:
                df[col].fillna(method='ffill', inplace=True)
                df[col].fillna(method='bfill', inplace=True)
        
        df.dropna(subset=['Close'], inplace=True)
        
        removed = original_length - len(df)
        if removed > 0:
            self.logger.info(f"Removed {removed} rows with missing critical data")
        
        return df
    
    def _remove_outliers(self, df, threshold=5):
        for col in ['Open', 'High', 'Low', 'Close']:
            if col in df.columns:
                z_scores = np.abs((df[col] - df[col].mean()) / df[col].std())
                df = df[z_scores < threshold]
        
        return df
    
    def _fix_data_types(self, df):
        numeric_columns = ['Open', 'High', 'Low', 'Close', 'Volume']
        
        for col in numeric_columns:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors='coerce')
        
        if not isinstance(df.index, pd.DatetimeIndex):
            if 'Date' in df.columns:
                df['Date'] = pd.to_datetime(df['Date'], errors='coerce')
                df.set_index('Date', inplace=True)
            else:
                df.index = pd.to_datetime(df.index, errors='coerce')
        
        df.sort_index(inplace=True)
        
        return df
    
    def _validate_price_relationships(self, df):
        if all(col in df.columns for col in ['Open', 'High', 'Low', 'Close']):
            invalid_high = df['High'] < df[['Open', 'Close']].max(axis=1)
            invalid_low = df['Low'] > df[['Open', 'Close']].min(axis=1)
            
            if invalid_high.any():
                self.logger.warning(f"Found {invalid_high.sum()} rows where High < max(Open, Close)")
                df.loc[invalid_high, 'High'] = df.loc[invalid_high, ['Open', 'Close']].max(axis=1)
            
            if invalid_low.any():
                self.logger.warning(f"Found {invalid_low.sum()} rows where Low > min(Open, Close)")
                df.loc[invalid_low, 'Low'] = df.loc[invalid_low, ['Open', 'Close']].min(axis=1)
        
        return df
    
    def check_data_quality(self, df):
        quality_report = {
            'total_rows': len(df),
            'date_range': None,
            'missing_values': {},
            'data_types': {},
            'outliers': {},
            'quality_score': 0
        }
        
        if isinstance(df.index, pd.DatetimeIndex):
            quality_report['date_range'] = {
                'start': df.index.min(),
                'end': df.index.max(),
                'days': (df.index.max() - df.index.min()).days
            }
        
        for col in df.columns:
            missing_count = df[col].isnull().sum()
            quality_report['missing_values'][col] = {
                'count': int(missing_count),
                'percentage': float((missing_count / len(df)) * 100)
            }
        
        for col in df.columns:
            quality_report['data_types'][col] = str(df[col].dtype)
        
        for col in ['Open', 'High', 'Low', 'Close']:
            if col in df.columns:
                z_scores = np.abs((df[col] - df[col].mean()) / df[col].std())
                outlier_count = (z_scores > 3).sum()
                quality_report['outliers'][col] = int(outlier_count)
        
        score = 100
        
        for col, info in quality_report['missing_values'].items():
            score -= info['percentage'] * 0.5
        
        total_outliers = sum(quality_report['outliers'].values())
        outlier_pct = (total_outliers / len(df)) * 100
        score -= outlier_pct * 0.3
        
        quality_report['quality_score'] = max(0, min(100, score))
        
        return quality_report
    
    def validate_ticker_symbol(self, symbol):
        if not symbol or not isinstance(symbol, str):
            return False
        
        symbol = symbol.strip().upper()
        
        if len(symbol) < 1 or len(symbol) > 5:
            return False
        
        if not symbol.isalpha() and '-' not in symbol:
            return False
        
        return True