# src/trading_signals/recommendation_ai.py

import numpy as np
import pandas as pd
from pathlib import Path
import sys

project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from src.utils.logger import Logger

class RecommendationAI:
    def __init__(self):
        self.logger = Logger(__name__)
    
    def get_recommendation(self, df, signal_data, risk_metrics):
        signal = signal_data.get('signal', 'HOLD')
        confidence = signal_data.get('confidence', 50)
        risk_score = risk_metrics.get('risk_score', 5)
        volatility = risk_metrics.get('volatility', 0)
        
        recommendation = self._build_recommendation(df, signal, confidence, risk_score, volatility)
        
        market_conditions = self._analyze_market_conditions(df)
        
        ai_score = self._calculate_ai_score(df, signal_data, risk_metrics, market_conditions)
        
        action_plan = self._generate_action_plan(signal, confidence, risk_score, ai_score)
        
        return {
            'recommendation': recommendation,
            'market_conditions': market_conditions,
            'ai_score': ai_score,
            'action_plan': action_plan
        }
    
    def _build_recommendation(self, df, signal, confidence, risk_score, volatility):
        if signal == 'BUY':
            if confidence > 80 and risk_score < 5:
                return "🟢 STRONG BUY: High confidence signal with low risk. Excellent entry opportunity. Consider taking a full position based on your risk management rules."
            elif confidence > 70 and risk_score < 6:
                return "🟢 BUY: Good entry signal with manageable risk. Consider entering with 60-80% of planned position size. Monitor closely for confirmation."
            elif confidence > 60:
                return "🟡 MODERATE BUY: Decent signal but elevated risk. Consider a smaller 30-50% position. Wait for pullback or better risk/reward setup."
            else:
                return "⚪ WEAK BUY: Signal lacks strong confirmation. Consider paper trading or waiting for stronger conviction before committing capital."
        
        elif signal == 'SELL':
            if confidence > 80:
                return "🔴 STRONG SELL: High confidence bearish signal. Consider closing long positions or taking profits. May consider short positions if appropriate for your strategy."
            elif confidence > 70:
                return "🔴 SELL: Clear bearish signal. Reduce position size or tighten stop losses. Consider taking partial profits if in profit."
            elif confidence > 60:
                return "🟠 MODERATE SELL: Bearish pressure building. Monitor position closely. Consider raising stop loss to breakeven or taking partial profits."
            else:
                return "⚪ WEAK SELL: Minor bearish indication. Maintain defensive stance but wait for stronger confirmation before major position changes."
        
        else:
            trend = self._determine_trend(df)
            if volatility > 30:
                return f"⚪ HOLD: No clear signal. Market showing high volatility ({volatility:.1f}%). Current trend: {trend}. Wait for market stabilization before making moves."
            else:
                return f"⚪ HOLD: No actionable signal at current levels. Current trend: {trend}. Continue monitoring for better entry/exit opportunities. Consider accumulation on dips if bullish on fundamentals."
    
    def _analyze_market_conditions(self, df):
        trend = self._determine_trend(df)
        volatility = self._assess_volatility(df)
        momentum = self._assess_momentum(df)
        volume_status = self._assess_volume(df)
        strength = self._assess_trend_strength(df)
        
        return {
            'trend': trend,
            'volatility_level': volatility,
            'momentum': momentum,
            'volume_status': volume_status,
            'trend_strength': strength
        }
    
    def _determine_trend(self, df):
        if 'SMA_20' in df.columns and 'SMA_50' in df.columns:
            sma_20 = df['SMA_20'].iloc[-1]
            sma_50 = df['SMA_50'].iloc[-1]
            current_price = df['Close'].iloc[-1]
            
            if current_price > sma_20 > sma_50 and sma_20 > sma_50 * 1.03:
                return 'Strong Uptrend'
            elif current_price > sma_20 > sma_50:
                return 'Uptrend'
            elif current_price < sma_20 < sma_50 and sma_20 < sma_50 * 0.97:
                return 'Strong Downtrend'
            elif current_price < sma_20 < sma_50:
                return 'Downtrend'
            else:
                return 'Sideways/Consolidation'
        
        returns_5d = (df['Close'].iloc[-1] - df['Close'].iloc[-6]) / df['Close'].iloc[-6] * 100
        
        if returns_5d > 3:
            return 'Uptrend'
        elif returns_5d < -3:
            return 'Downtrend'
        else:
            return 'Sideways'
    
    def _assess_volatility(self, df):
        returns = df['Close'].pct_change().tail(20).std() * np.sqrt(252) * 100
        
        if returns > 40:
            return 'Very High'
        elif returns > 25:
            return 'High'
        elif returns > 15:
            return 'Moderate'
        else:
            return 'Low'
    
    def _assess_momentum(self, df):
        price_change_5d = (df['Close'].iloc[-1] - df['Close'].iloc[-6]) / df['Close'].iloc[-6] * 100
        price_change_10d = (df['Close'].iloc[-1] - df['Close'].iloc[-11]) / df['Close'].iloc[-11] * 100
        
        if 'RSI' in df.columns:
            rsi = df['RSI'].iloc[-1]
            
            if price_change_5d > 5 and rsi > 60:
                return 'Strong Bullish'
            elif price_change_5d > 2:
                return 'Bullish'
            elif price_change_5d < -5 and rsi < 40:
                return 'Strong Bearish'
            elif price_change_5d < -2:
                return 'Bearish'
        
        if price_change_5d > 3:
            return 'Positive'
        elif price_change_5d < -3:
            return 'Negative'
        else:
            return 'Neutral'
    
    def _assess_volume(self, df):
        if 'Volume_Ratio' in df.columns:
            vol_ratio = df['Volume_Ratio'].iloc[-1]
            
            if vol_ratio > 2.0:
                return 'Very High Volume'
            elif vol_ratio > 1.5:
                return 'High Volume'
            elif vol_ratio < 0.5:
                return 'Low Volume'
            elif vol_ratio < 0.7:
                return 'Below Average Volume'
            else:
                return 'Normal Volume'
        
        avg_volume = df['Volume'].tail(20).mean()
        current_volume = df['Volume'].iloc[-1]
        
        if current_volume > avg_volume * 1.5:
            return 'High Volume'
        elif current_volume < avg_volume * 0.7:
            return 'Low Volume'
        else:
            return 'Normal Volume'
    
    def _assess_trend_strength(self, df):
        if 'SMA_20' not in df.columns:
            return 'Unknown'
        
        current_price = df['Close'].iloc[-1]
        sma_20 = df['SMA_20'].iloc[-1]
        
        distance_from_sma = abs((current_price - sma_20) / sma_20) * 100
        
        if distance_from_sma > 5:
            return 'Strong'
        elif distance_from_sma > 2:
            return 'Moderate'
        else:
            return 'Weak'
    
    def _calculate_ai_score(self, df, signal_data, risk_metrics, market_conditions):
        score = 50
        
        signal = signal_data.get('signal', 'HOLD')
        confidence = signal_data.get('confidence', 50)
        
        if signal == 'BUY':
            score += (confidence - 50) * 0.5
        elif signal == 'SELL':
            score -= (confidence - 50) * 0.5
        
        risk_score = risk_metrics.get('risk_score', 5)
        score -= (risk_score - 5) * 3
        
        sharpe = risk_metrics.get('sharpe_ratio', 0)
        if sharpe > 1:
            score += 10
        elif sharpe > 0.5:
            score += 5
        elif sharpe < 0:
            score -= 10
        
        trend = market_conditions.get('trend', '')
        if 'Strong' in trend:
            if signal == 'BUY' and 'Up' in trend:
                score += 10
            elif signal == 'SELL' and 'Down' in trend:
                score += 10
        
        volatility = market_conditions.get('volatility_level', '')
        if volatility in ['Very High', 'High']:
            score -= 5
        
        volume = market_conditions.get('volume_status', '')
        if 'High Volume' in volume and signal != 'HOLD':
            score += 5
        elif 'Low Volume' in volume:
            score -= 3
        
        score = max(0, min(100, score))
        
        return round(score)
    
    def _generate_action_plan(self, signal, confidence, risk_score, ai_score):
        actions = []
        
        if signal == 'BUY':
            if ai_score > 70:
                actions.append("✓ Execute buy order with primary position size")
                actions.append("✓ Set stop loss at recommended level")
                actions.append("✓ Set take profit targets (conservative and aggressive)")
                actions.append("✓ Monitor position daily for first week")
            elif ai_score > 60:
                actions.append("✓ Consider 50-70% position entry")
                actions.append("✓ Use tighter stop loss due to moderate confidence")
                actions.append("✓ Plan to add on strength if confirmed")
            else:
                actions.append("⚠ Wait for better setup")
                actions.append("⚠ Set price alert for improved entry")
                actions.append("⚠ Monitor for confirmation signals")
        
        elif signal == 'SELL':
            if ai_score < 30:
                actions.append("✓ Close or reduce long positions")
                actions.append("✓ Take profits if position is green")
                actions.append("✓ Tighten stop losses on remaining positions")
            elif ai_score < 40:
                actions.append("✓ Consider taking partial profits")
                actions.append("✓ Raise stop loss to protect gains")
                actions.append("✓ Monitor for reversal signals")
            else:
                actions.append("⚠ Maintain defensive stance")
                actions.append("⚠ Avoid new entries")
        
        else:
            actions.append("○ No immediate action required")
            actions.append("○ Continue monitoring key levels")
            actions.append("○ Review fundamentals if holding long-term")
        
        return actions
    
    def generate_ml_recommendation(self, df):
        features = self._extract_ml_features(df)
        
        prediction_score = self._simple_ml_prediction(features)
        
        if prediction_score > 0.6:
            return 'BUY', int(prediction_score * 100)
        elif prediction_score < 0.4:
            return 'SELL', int((1 - prediction_score) * 100)
        else:
            return 'HOLD', 50
    
    def _extract_ml_features(self, df):
        features = {}
        
        if 'RSI' in df.columns:
            features['rsi'] = df['RSI'].iloc[-1] / 100
        
        if 'MACD' in df.columns and 'MACD_Signal' in df.columns:
            features['macd_diff'] = (df['MACD'].iloc[-1] - df['MACD_Signal'].iloc[-1]) / df['Close'].iloc[-1]
        
        if 'SMA_20' in df.columns and 'SMA_50' in df.columns:
            features['ma_ratio'] = df['SMA_20'].iloc[-1] / df['SMA_50'].iloc[-1]
        
        features['price_momentum'] = (df['Close'].iloc[-1] - df['Close'].iloc[-6]) / df['Close'].iloc[-6]
        
        features['volume_trend'] = df['Volume'].iloc[-5:].mean() / df['Volume'].iloc[-20:].mean()
        
        return features
    
    def _simple_ml_prediction(self, features):
        score = 0.5
        
        rsi = features.get('rsi', 0.5)
        if rsi < 0.3:
            score += 0.15
        elif rsi > 0.7:
            score -= 0.15
        
        macd_diff = features.get('macd_diff', 0)
        if macd_diff > 0:
            score += 0.1
        elif macd_diff < 0:
            score -= 0.1
        
        ma_ratio = features.get('ma_ratio', 1.0)
        if ma_ratio > 1.02:
            score += 0.15
        elif ma_ratio < 0.98:
            score -= 0.15
        
        momentum = features.get('price_momentum', 0)
        if momentum > 0.03:
            score += 0.1
        elif momentum < -0.03:
            score -= 0.1
        
        return max(0, min(1, score))