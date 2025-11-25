# src/trading_signals/signal_generator.py
# Run in: VS Code (Python environment with required packages)

import numpy as np
import pandas as pd
from pathlib import Path
import sys

project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from app.config import RSI_OVERSOLD, RSI_OVERBOUGHT, MACD_SIGNAL_THRESHOLD
from src.utils.logger import Logger

class SignalGenerator:
    def __init__(self):
        self.logger = Logger(__name__)
    
    def generate_signal(self, df, strategy='AI Composite', sensitivity='Moderate'):
        if strategy == 'AI Composite':
            return self._generate_composite_signal(df, sensitivity)
        elif strategy == 'RSI Strategy':
            return self._generate_rsi_signal(df, sensitivity)
        elif strategy == 'MACD Crossover':
            return self._generate_macd_signal(df, sensitivity)
        elif strategy == 'Moving Average':
            return self._generate_ma_signal(df, sensitivity)
        elif strategy == 'Bollinger Bands':
            return self._generate_bb_signal(df, sensitivity)
        elif strategy == 'Momentum':
            return self._generate_momentum_signal(df, sensitivity)
        else:
            return self._generate_composite_signal(df, sensitivity)
    
    def _generate_composite_signal(self, df, sensitivity):
        signals = []
        weights = []
        
        rsi_signal = self._generate_rsi_signal(df, sensitivity)
        if rsi_signal['signal'] != 'HOLD':
            signals.append(rsi_signal)
            weights.append(0.25)
        
        macd_signal = self._generate_macd_signal(df, sensitivity)
        if macd_signal['signal'] != 'HOLD':
            signals.append(macd_signal)
            weights.append(0.25)
        
        ma_signal = self._generate_ma_signal(df, sensitivity)
        if ma_signal['signal'] != 'HOLD':
            signals.append(ma_signal)
            weights.append(0.25)
        
        bb_signal = self._generate_bb_signal(df, sensitivity)
        if bb_signal['signal'] != 'HOLD':
            signals.append(bb_signal)
            weights.append(0.25)
        
        if not signals:
            return {
                'signal': 'HOLD',
                'strength': 5,
                'confidence': 50,
                'reasons': ['No clear signal from technical indicators']
            }
        
        buy_score = sum(w for s, w in zip(signals, weights) if s['signal'] == 'BUY')
        sell_score = sum(w for s, w in zip(signals, weights) if s['signal'] == 'SELL')
        
        if buy_score > sell_score and buy_score > 0.4:
            signal = 'BUY'
            confidence = min(95, int(buy_score * 100))
            strength = min(10, int(buy_score * 15))
        elif sell_score > buy_score and sell_score > 0.4:
            signal = 'SELL'
            confidence = min(95, int(sell_score * 100))
            strength = min(10, int(sell_score * 15))
        else:
            signal = 'HOLD'
            confidence = 50
            strength = 5
        
        reasons = []
        for s in signals:
            if s['signal'] == signal:
                reasons.extend(s.get('reasons', []))
        
        return {
            'signal': signal,
            'strength': strength,
            'confidence': confidence,
            'reasons': reasons[:3] if reasons else ['Mixed signals from indicators']
        }
    
    def _generate_rsi_signal(self, df, sensitivity):
        if 'RSI' not in df.columns:
            return {'signal': 'HOLD', 'strength': 5, 'confidence': 50, 'reasons': []}
        
        rsi = df['RSI'].iloc[-1]
        
        if sensitivity == 'Conservative':
            oversold, overbought = 25, 75
        elif sensitivity == 'Aggressive':
            oversold, overbought = 35, 65
        else:
            oversold, overbought = RSI_OVERSOLD, RSI_OVERBOUGHT
        
        if rsi < oversold:
            strength = min(10, int((oversold - rsi) / 3))
            confidence = min(95, int(70 + (oversold - rsi)))
            return {
                'signal': 'BUY',
                'strength': strength,
                'confidence': confidence,
                'reasons': [f'RSI at {rsi:.1f} indicates oversold conditions']
            }
        elif rsi > overbought:
            strength = min(10, int((rsi - overbought) / 3))
            confidence = min(95, int(70 + (rsi - overbought)))
            return {
                'signal': 'SELL',
                'strength': strength,
                'confidence': confidence,
                'reasons': [f'RSI at {rsi:.1f} indicates overbought conditions']
            }
        else:
            return {
                'signal': 'HOLD',
                'strength': 5,
                'confidence': 50,
                'reasons': [f'RSI at {rsi:.1f} in neutral zone']
            }
    
    def _generate_macd_signal(self, df, sensitivity):
        if 'MACD' not in df.columns or 'MACD_Signal' not in df.columns:
            return {'signal': 'HOLD', 'strength': 5, 'confidence': 50, 'reasons': []}
        
        macd = df['MACD'].iloc[-1]
        macd_signal = df['MACD_Signal'].iloc[-1]
        macd_prev = df['MACD'].iloc[-2]
        signal_prev = df['MACD_Signal'].iloc[-2]
        
        diff = macd - macd_signal
        prev_diff = macd_prev - signal_prev
        
        if prev_diff < 0 and diff > 0:
            strength = min(10, int(abs(diff) * 10))
            confidence = min(90, int(65 + abs(diff) * 20))
            return {
                'signal': 'BUY',
                'strength': strength,
                'confidence': confidence,
                'reasons': ['MACD bullish crossover detected']
            }
        elif prev_diff > 0 and diff < 0:
            strength = min(10, int(abs(diff) * 10))
            confidence = min(90, int(65 + abs(diff) * 20))
            return {
                'signal': 'SELL',
                'strength': strength,
                'confidence': confidence,
                'reasons': ['MACD bearish crossover detected']
            }
        elif diff > MACD_SIGNAL_THRESHOLD:
            return {
                'signal': 'BUY',
                'strength': 6,
                'confidence': 60,
                'reasons': ['MACD above signal line']
            }
        elif diff < -MACD_SIGNAL_THRESHOLD:
            return {
                'signal': 'SELL',
                'strength': 6,
                'confidence': 60,
                'reasons': ['MACD below signal line']
            }
        else:
            return {
                'signal': 'HOLD',
                'strength': 5,
                'confidence': 50,
                'reasons': ['MACD neutral']
            }
    
    def _generate_ma_signal(self, df, sensitivity):
        if 'SMA_20' not in df.columns or 'SMA_50' not in df.columns:
            return {'signal': 'HOLD', 'strength': 5, 'confidence': 50, 'reasons': []}
        
        sma_20 = df['SMA_20'].iloc[-1]
        sma_50 = df['SMA_50'].iloc[-1]
        sma_20_prev = df['SMA_20'].iloc[-2]
        sma_50_prev = df['SMA_50'].iloc[-2]
        
        current_price = df['Close'].iloc[-1]
        
        if sma_20_prev < sma_50_prev and sma_20 > sma_50:
            return {
                'signal': 'BUY',
                'strength': 8,
                'confidence': 75,
                'reasons': ['Golden cross: SMA 20 crossed above SMA 50']
            }
        elif sma_20_prev > sma_50_prev and sma_20 < sma_50:
            return {
                'signal': 'SELL',
                'strength': 8,
                'confidence': 75,
                'reasons': ['Death cross: SMA 20 crossed below SMA 50']
            }
        elif current_price > sma_20 > sma_50:
            return {
                'signal': 'BUY',
                'strength': 6,
                'confidence': 65,
                'reasons': ['Price above both moving averages - uptrend']
            }
        elif current_price < sma_20 < sma_50:
            return {
                'signal': 'SELL',
                'strength': 6,
                'confidence': 65,
                'reasons': ['Price below both moving averages - downtrend']
            }
        else:
            return {
                'signal': 'HOLD',
                'strength': 5,
                'confidence': 50,
                'reasons': ['Moving averages show no clear trend']
            }
    
    def _generate_bb_signal(self, df, sensitivity):
        if 'BB_Upper' not in df.columns or 'BB_Lower' not in df.columns:
            return {'signal': 'HOLD', 'strength': 5, 'confidence': 50, 'reasons': []}
        
        current_price = df['Close'].iloc[-1]
        bb_upper = df['BB_Upper'].iloc[-1]
        bb_lower = df['BB_Lower'].iloc[-1]
        bb_middle = df['BB_Middle'].iloc[-1]
        
        if current_price < bb_lower:
            strength = min(10, int((bb_lower - current_price) / bb_lower * 100))
            return {
                'signal': 'BUY',
                'strength': strength,
                'confidence': 70,
                'reasons': ['Price below lower Bollinger Band']
            }
        elif current_price > bb_upper:
            strength = min(10, int((current_price - bb_upper) / bb_upper * 100))
            return {
                'signal': 'SELL',
                'strength': strength,
                'confidence': 70,
                'reasons': ['Price above upper Bollinger Band']
            }
        else:
            return {
                'signal': 'HOLD',
                'strength': 5,
                'confidence': 50,
                'reasons': ['Price within Bollinger Bands']
            }
    
    def _generate_momentum_signal(self, df, sensitivity):
        returns = df['Close'].pct_change(5).iloc[-1] * 100
        
        volume_ratio = 1.0
        if 'Volume_Ratio' in df.columns:
            volume_ratio = df['Volume_Ratio'].iloc[-1]
        
        if returns > 3 and volume_ratio > 1.2:
            return {
                'signal': 'BUY',
                'strength': 7,
                'confidence': 70,
                'reasons': [f'Strong upward momentum: {returns:.1f}% gain with high volume']
            }
        elif returns < -3 and volume_ratio > 1.2:
            return {
                'signal': 'SELL',
                'strength': 7,
                'confidence': 70,
                'reasons': [f'Strong downward momentum: {returns:.1f}% loss with high volume']
            }
        else:
            return {
                'signal': 'HOLD',
                'strength': 5,
                'confidence': 50,
                'reasons': ['Weak momentum signal']
            }