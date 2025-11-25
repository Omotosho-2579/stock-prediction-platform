# src/data/technical_indicators.py

import pandas as pd
import numpy as np
from pathlib import Path
import sys

project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from src.utils.logger import Logger

class TechnicalIndicators:
    def __init__(self):
        self.logger = Logger(__name__)
    
    def add_all_indicators(self, df):
        df = df.copy()
        
        df = self.add_moving_averages(df)
        df = self.add_rsi(df)
        df = self.add_macd(df)
        df = self.add_bollinger_bands(df)
        df = self.add_atr(df)
        df = self.add_volume_indicators(df)
        
        return df
    
    def add_moving_averages(self, df, periods=[5, 10, 20, 50, 200]):
        df = df.copy()
        
        for period in periods:
            if len(df) >= period:
                df[f'SMA_{period}'] = df['Close'].rolling(window=period).mean()
                df[f'EMA_{period}'] = df['Close'].ewm(span=period, adjust=False).mean()
        
        return df
    
    def add_rsi(self, df, period=14):
        df = df.copy()
        
        delta = df['Close'].diff()
        
        gain = delta.where(delta > 0, 0)
        loss = -delta.where(delta < 0, 0)
        
        avg_gain = gain.rolling(window=period).mean()
        avg_loss = loss.rolling(window=period).mean()
        
        rs = avg_gain / avg_loss
        rsi = 100 - (100 / (1 + rs))
        
        df['RSI'] = rsi
        
        return df
    
    def add_macd(self, df, fast=12, slow=26, signal=9):
        df = df.copy()
        
        ema_fast = df['Close'].ewm(span=fast, adjust=False).mean()
        ema_slow = df['Close'].ewm(span=slow, adjust=False).mean()
        
        df['MACD'] = ema_fast - ema_slow
        df['MACD_Signal'] = df['MACD'].ewm(span=signal, adjust=False).mean()
        df['MACD_Histogram'] = df['MACD'] - df['MACD_Signal']
        
        return df
    
    def add_bollinger_bands(self, df, period=20, std_dev=2):
        df = df.copy()
        
        df['BB_Middle'] = df['Close'].rolling(window=period).mean()
        
        rolling_std = df['Close'].rolling(window=period).std()
        
        df['BB_Upper'] = df['BB_Middle'] + (rolling_std * std_dev)
        df['BB_Lower'] = df['BB_Middle'] - (rolling_std * std_dev)
        
        df['BB_Width'] = df['BB_Upper'] - df['BB_Lower']
        df['BB_Position'] = (df['Close'] - df['BB_Lower']) / (df['BB_Upper'] - df['BB_Lower'])
        
        return df
    
    def add_atr(self, df, period=14):
        df = df.copy()
        
        high_low = df['High'] - df['Low']
        high_close = np.abs(df['High'] - df['Close'].shift())
        low_close = np.abs(df['Low'] - df['Close'].shift())
        
        true_range = pd.concat([high_low, high_close, low_close], axis=1).max(axis=1)
        
        df['ATR'] = true_range.rolling(window=period).mean()
        
        return df
    
    def add_volume_indicators(self, df):
        df = df.copy()
        
        df['Volume_SMA_20'] = df['Volume'].rolling(window=20).mean()
        df['Volume_Ratio'] = df['Volume'] / df['Volume_SMA_20']
        
        df['OBV'] = (np.sign(df['Close'].diff()) * df['Volume']).fillna(0).cumsum()
        
        return df
    
    def add_stochastic_oscillator(self, df, period=14, smooth_k=3, smooth_d=3):
        df = df.copy()
        
        low_min = df['Low'].rolling(window=period).min()
        high_max = df['High'].rolling(window=period).max()
        
        df['Stoch_K'] = 100 * (df['Close'] - low_min) / (high_max - low_min)
        df['Stoch_K'] = df['Stoch_K'].rolling(window=smooth_k).mean()
        df['Stoch_D'] = df['Stoch_K'].rolling(window=smooth_d).mean()
        
        return df
    
    def add_cci(self, df, period=20):
        df = df.copy()
        
        tp = (df['High'] + df['Low'] + df['Close']) / 3
        
        sma = tp.rolling(window=period).mean()
        mad = tp.rolling(window=period).apply(lambda x: np.abs(x - x.mean()).mean())
        
        df['CCI'] = (tp - sma) / (0.015 * mad)
        
        return df
    
    def add_adx(self, df, period=14):
        df = df.copy()
        
        high_diff = df['High'].diff()
        low_diff = -df['Low'].diff()
        
        pos_dm = high_diff.where((high_diff > low_diff) & (high_diff > 0), 0)
        neg_dm = low_diff.where((low_diff > high_diff) & (low_diff > 0), 0)
        
        df_temp = self.add_atr(df, period)
        atr = df_temp['ATR']
        
        pos_di = 100 * (pos_dm.rolling(window=period).mean() / atr)
        neg_di = 100 * (neg_dm.rolling(window=period).mean() / atr)
        
        dx = 100 * np.abs(pos_di - neg_di) / (pos_di + neg_di)
        
        df['ADX'] = dx.rolling(window=period).mean()
        df['Plus_DI'] = pos_di
        df['Minus_DI'] = neg_di
        
        return df
    
    def add_williams_r(self, df, period=14):
        df = df.copy()
        
        highest_high = df['High'].rolling(window=period).max()
        lowest_low = df['Low'].rolling(window=period).min()
        
        df['Williams_R'] = -100 * (highest_high - df['Close']) / (highest_high - lowest_low)
        
        return df
    
    def add_momentum(self, df, period=10):
        df = df.copy()
        
        df['Momentum'] = df['Close'].diff(period)
        df['ROC'] = ((df['Close'] - df['Close'].shift(period)) / df['Close'].shift(period)) * 100
        
        return df
    
    def get_signal_summary(self, df):
        summary = {
            'RSI': 'Neutral',
            'MACD': 'Neutral',
            'BB': 'Neutral',
            'MA': 'Neutral',
            'Volume': 'Neutral',
            'Overall': 'Neutral'
        }
        
        if 'RSI' in df.columns:
            rsi = df['RSI'].iloc[-1]
            if rsi < 30:
                summary['RSI'] = 'Oversold (Buy)'
            elif rsi > 70:
                summary['RSI'] = 'Overbought (Sell)'
        
        if 'MACD' in df.columns and 'MACD_Signal' in df.columns:
            macd = df['MACD'].iloc[-1]
            signal = df['MACD_Signal'].iloc[-1]
            if macd > signal:
                summary['MACD'] = 'Bullish'
            else:
                summary['MACD'] = 'Bearish'
        
        if 'BB_Position' in df.columns:
            bb_pos = df['BB_Position'].iloc[-1]
            if bb_pos < 0.2:
                summary['BB'] = 'Oversold'
            elif bb_pos > 0.8:
                summary['BB'] = 'Overbought'
        
        if 'SMA_20' in df.columns and 'SMA_50' in df.columns:
            sma_20 = df['SMA_20'].iloc[-1]
            sma_50 = df['SMA_50'].iloc[-1]
            if sma_20 > sma_50:
                summary['MA'] = 'Bullish'
            else:
                summary['MA'] = 'Bearish'
        
        if 'Volume_Ratio' in df.columns:
            vol_ratio = df['Volume_Ratio'].iloc[-1]
            if vol_ratio > 1.5:
                summary['Volume'] = 'High'
            elif vol_ratio < 0.5:
                summary['Volume'] = 'Low'
        
        bullish_count = sum(1 for v in summary.values() if 'Bull' in v or 'Buy' in v or 'Oversold' in v)
        bearish_count = sum(1 for v in summary.values() if 'Bear' in v or 'Sell' in v or 'Overbought' in v)
        
        if bullish_count > bearish_count:
            summary['Overall'] = 'Bullish'
        elif bearish_count > bullish_count:
            summary['Overall'] = 'Bearish'
        
        return summary