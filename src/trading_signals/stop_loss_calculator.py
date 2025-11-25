# src/trading_signals/stop_loss_calculator.py

import numpy as np
import pandas as pd
from pathlib import Path
import sys

project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from app.config import DEFAULT_STOP_LOSS_PCT, DEFAULT_TAKE_PROFIT_PCT
from src.utils.logger import Logger

class StopLossCalculator:
    def __init__(self):
        self.logger = Logger(__name__)
    
    def calculate_stop_loss(self, entry_price, method='percentage', df=None, atr_multiplier=2.0, custom_pct=None):
        if entry_price <= 0:
            self.logger.error("Entry price must be positive")
            return 0
        
        if method == 'percentage':
            return self._percentage_stop_loss(entry_price, custom_pct)
        elif method == 'atr':
            return self._atr_stop_loss(entry_price, df, atr_multiplier)
        elif method == 'support':
            return self._support_stop_loss(entry_price, df)
        elif method == 'trailing':
            return self._trailing_stop_loss(entry_price, df)
        elif method == 'volatility':
            return self._volatility_stop_loss(entry_price, df)
        else:
            return self._percentage_stop_loss(entry_price, custom_pct)
    
    def _percentage_stop_loss(self, entry_price, stop_loss_pct=None):
        if stop_loss_pct is None:
            stop_loss_pct = DEFAULT_STOP_LOSS_PCT
        
        stop_loss = entry_price * (1 - stop_loss_pct / 100)
        
        return round(stop_loss, 2)
    
    def _atr_stop_loss(self, entry_price, df, atr_multiplier=2.0):
        if df is None or 'ATR' not in df.columns:
            self.logger.warning("ATR not available, using percentage method")
            return self._percentage_stop_loss(entry_price)
        
        atr = df['ATR'].iloc[-1]
        
        if atr <= 0:
            self.logger.warning("Invalid ATR value, using percentage method")
            return self._percentage_stop_loss(entry_price)
        
        stop_loss = entry_price - (atr * atr_multiplier)
        
        min_stop = entry_price * (1 - DEFAULT_STOP_LOSS_PCT * 2 / 100)
        stop_loss = max(stop_loss, min_stop)
        
        return round(stop_loss, 2)
    
    def _support_stop_loss(self, entry_price, df):
        if df is None or len(df) < 20:
            return self._percentage_stop_loss(entry_price)
        
        recent_low = df['Low'].tail(20).min()
        
        stop_loss = recent_low * 0.985
        
        min_stop = entry_price * (1 - DEFAULT_STOP_LOSS_PCT * 1.5 / 100)
        max_stop = entry_price * (1 - DEFAULT_STOP_LOSS_PCT * 0.5 / 100)
        
        stop_loss = max(min_stop, min(stop_loss, max_stop))
        
        return round(stop_loss, 2)
    
    def _trailing_stop_loss(self, entry_price, df, trail_pct=None):
        if trail_pct is None:
            trail_pct = DEFAULT_STOP_LOSS_PCT * 0.6
        
        if df is None or len(df) < 10:
            return self._percentage_stop_loss(entry_price)
        
        highest_price = df['High'].tail(10).max()
        
        stop_loss = highest_price * (1 - trail_pct / 100)
        
        min_stop = entry_price * (1 - DEFAULT_STOP_LOSS_PCT / 100)
        stop_loss = max(stop_loss, min_stop)
        
        return round(stop_loss, 2)
    
    def _volatility_stop_loss(self, entry_price, df):
        if df is None or len(df) < 20:
            return self._percentage_stop_loss(entry_price)
        
        returns = df['Close'].pct_change().tail(20)
        volatility = returns.std()
        
        volatility_adjusted_pct = DEFAULT_STOP_LOSS_PCT * (1 + volatility * 10)
        volatility_adjusted_pct = min(volatility_adjusted_pct, DEFAULT_STOP_LOSS_PCT * 2)
        
        stop_loss = entry_price * (1 - volatility_adjusted_pct / 100)
        
        return round(stop_loss, 2)
    
    def calculate_take_profit(self, entry_price, stop_loss, risk_reward_ratio=2.0, method='ratio'):
        if entry_price <= 0:
            self.logger.error("Entry price must be positive")
            return 0
        
        if method == 'ratio':
            risk = entry_price - stop_loss
            if risk <= 0:
                risk = entry_price * (DEFAULT_STOP_LOSS_PCT / 100)
            reward = risk * risk_reward_ratio
            take_profit = entry_price + reward
        
        elif method == 'percentage':
            take_profit = entry_price * (1 + DEFAULT_TAKE_PROFIT_PCT / 100)
        
        elif method == 'fibonacci':
            risk = entry_price - stop_loss
            if risk <= 0:
                risk = entry_price * (DEFAULT_STOP_LOSS_PCT / 100)
            take_profit = entry_price + (risk * 1.618)
        
        elif method == 'resistance':
            take_profit = entry_price * (1 + DEFAULT_TAKE_PROFIT_PCT / 100)
        
        else:
            take_profit = entry_price * (1 + DEFAULT_TAKE_PROFIT_PCT / 100)
        
        return round(take_profit, 2)
    
    def calculate_dynamic_levels(self, entry_price, df, volatility=None):
        if df is None:
            stop_loss = self._percentage_stop_loss(entry_price)
            risk = entry_price * (DEFAULT_STOP_LOSS_PCT / 100)
        else:
            atr_stop = self._atr_stop_loss(entry_price, df)
            support_stop = self._support_stop_loss(entry_price, df)
            percentage_stop = self._percentage_stop_loss(entry_price)
            
            stops = [s for s in [atr_stop, support_stop, percentage_stop] if s > 0]
            stop_loss = round(np.mean(stops), 2) if stops else percentage_stop
            
            risk = entry_price - stop_loss
        
        take_profit_conservative = round(entry_price + (risk * 1.5), 2)
        take_profit_moderate = round(entry_price + (risk * 2.0), 2)
        take_profit_aggressive = round(entry_price + (risk * 3.0), 2)
        
        return {
            'stop_loss': stop_loss,
            'take_profit_conservative': take_profit_conservative,
            'take_profit_moderate': take_profit_moderate,
            'take_profit_aggressive': take_profit_aggressive,
            'risk_amount': round(risk, 2),
            'reward_conservative': round(take_profit_conservative - entry_price, 2),
            'reward_moderate': round(take_profit_moderate - entry_price, 2),
            'reward_aggressive': round(take_profit_aggressive - entry_price, 2),
            'risk_reward_conservative': round((take_profit_conservative - entry_price) / risk, 2) if risk > 0 else 0,
            'risk_reward_moderate': round((take_profit_moderate - entry_price) / risk, 2) if risk > 0 else 0,
            'risk_reward_aggressive': round((take_profit_aggressive - entry_price) / risk, 2) if risk > 0 else 0
        }
    
    def calculate_breakeven_stop(self, entry_price, commission_per_share=0.01):
        breakeven = entry_price + (commission_per_share * 2)
        
        return round(breakeven, 2)
    
    def calculate_time_based_stop(self, entry_price, days_held, max_days=30):
        if days_held >= max_days:
            return self._percentage_stop_loss(entry_price, DEFAULT_STOP_LOSS_PCT * 1.5)
        
        time_factor = days_held / max_days
        adjusted_pct = DEFAULT_STOP_LOSS_PCT * (1 + time_factor * 0.5)
        
        stop_loss = entry_price * (1 - adjusted_pct / 100)
        
        return round(stop_loss, 2)
    
    def get_stop_loss_recommendations(self, entry_price, df=None, risk_tolerance='Medium'):
        recommendations = {}
        
        recommendations['percentage'] = self._percentage_stop_loss(entry_price)
        
        if df is not None and len(df) >= 20:
            recommendations['atr_based'] = self._atr_stop_loss(entry_price, df)
            recommendations['support_based'] = self._support_stop_loss(entry_price, df)
            recommendations['trailing'] = self._trailing_stop_loss(entry_price, df)
            recommendations['volatility_adjusted'] = self._volatility_stop_loss(entry_price, df)
        
        risk_tolerance_map = {
            'Low': DEFAULT_STOP_LOSS_PCT * 0.6,
            'Medium': DEFAULT_STOP_LOSS_PCT,
            'High': DEFAULT_STOP_LOSS_PCT * 1.4
        }
        
        recommended_pct = risk_tolerance_map.get(risk_tolerance, DEFAULT_STOP_LOSS_PCT)
        recommendations['recommended'] = self._percentage_stop_loss(entry_price, recommended_pct)
        
        if df is not None and len(df) >= 20:
            all_stops = [v for k, v in recommendations.items() if k != 'recommended' and v > 0]
            if all_stops:
                recommendations['average_technical'] = round(np.mean(all_stops), 2)
        
        return recommendations
    
    def validate_stop_loss(self, entry_price, stop_loss):
        validations = {
            'is_valid': True,
            'errors': [],
            'warnings': [],
            'suggestions': []
        }
        
        if stop_loss >= entry_price:
            validations['is_valid'] = False
            validations['errors'].append("Stop loss must be below entry price for long positions")
            return validations
        
        if stop_loss <= 0:
            validations['is_valid'] = False
            validations['errors'].append("Stop loss must be a positive value")
            return validations
        
        loss_pct = ((entry_price - stop_loss) / entry_price) * 100
        
        if loss_pct > 20:
            validations['is_valid'] = False
            validations['errors'].append(
                f"Stop loss too wide ({loss_pct:.1f}%). Risk exceeds 20% which is generally too high."
            )
        elif loss_pct > 10:
            validations['warnings'].append(
                f"Stop loss is wide ({loss_pct:.1f}%). Consider tighter stop or smaller position size."
            )
        
        if loss_pct < 0.5:
            validations['warnings'].append(
                f"Stop loss very tight ({loss_pct:.2f}%). May trigger prematurely due to normal volatility."
            )
            validations['suggestions'].append("Consider widening stop loss to at least 1-2% to account for market noise")
        
        optimal_range = (2, 8)
        if loss_pct < optimal_range[0]:
            validations['suggestions'].append(
                f"Stop loss below typical range. Consider {optimal_range[0]}-{optimal_range[1]}% for better risk management."
            )
        elif loss_pct > optimal_range[1]:
            validations['suggestions'].append(
                f"Stop loss above typical range. Consider {optimal_range[0]}-{optimal_range[1]}% for better risk/reward."
            )
        else:
            validations['suggestions'].append("Stop loss is within optimal range for most trading strategies")
        
        return validations
    
    def calculate_multiple_exit_strategy(self, entry_price, stop_loss, num_exits=3):
        risk = entry_price - stop_loss
        
        if risk <= 0:
            self.logger.error("Invalid risk calculation")
            return []
        
        exit_strategy = []
        
        for i in range(1, num_exits + 1):
            target_price = entry_price + (risk * i * 1.5)
            position_pct = 100 / num_exits
            
            if i == num_exits:
                position_pct = 100 - (position_pct * (num_exits - 1))
            
            exit_strategy.append({
                'exit_number': i,
                'target_price': round(target_price, 2),
                'position_percentage': round(position_pct, 1),
                'risk_reward_ratio': round(i * 1.5, 2),
                'description': self._get_exit_description(i, num_exits)
            })
        
        return exit_strategy
    
    def _get_exit_description(self, exit_num, total_exits):
        if exit_num == 1:
            return "First target - Take initial profits, de-risk position"
        elif exit_num == total_exits:
            return "Final target - Let winners run, maximize potential"
        else:
            return f"Intermediate target {exit_num} - Scale out position"
    
    def adjust_stop_loss_after_profit(self, entry_price, current_price, current_stop, profit_threshold=5.0):
        profit_pct = ((current_price - entry_price) / entry_price) * 100
        
        if profit_pct < profit_threshold:
            return current_stop
        
        if current_stop < entry_price:
            new_stop = entry_price * 1.001
            self.logger.info(f"Moving stop to breakeven at {new_stop:.2f}")
            return round(new_stop, 2)
        
        trailing_pct = DEFAULT_STOP_LOSS_PCT * 0.5
        new_trailing_stop = current_price * (1 - trailing_pct / 100)
        
        adjusted_stop = max(current_stop, new_trailing_stop)
        
        return round(adjusted_stop, 2)
    
    def calculate_chandelier_stop(self, df, entry_price, atr_multiplier=3.0, lookback=22):
        if df is None or 'ATR' not in df.columns or len(df) < lookback:
            self.logger.warning("Insufficient data for Chandelier stop, using ATR method")
            return self._atr_stop_loss(entry_price, df, atr_multiplier)
        
        highest_high = df['High'].tail(lookback).max()
        atr = df['ATR'].iloc[-1]
        
        chandelier_stop = highest_high - (atr * atr_multiplier)
        
        min_stop = entry_price * (1 - DEFAULT_STOP_LOSS_PCT * 2 / 100)
        chandelier_stop = max(chandelier_stop, min_stop)
        
        return round(chandelier_stop, 2)
    
    def calculate_parabolic_sar_stop(self, df, entry_price):
        if df is None or len(df) < 5:
            return self._percentage_stop_loss(entry_price)
        
        acceleration = 0.02
        max_acceleration = 0.20
        
        sar = df['Low'].iloc[-5]
        extreme_point = df['High'].iloc[-5]
        
        for i in range(-4, 0):
            sar = sar + acceleration * (extreme_point - sar)
            
            if df['High'].iloc[i] > extreme_point:
                extreme_point = df['High'].iloc[i]
                acceleration = min(acceleration + 0.02, max_acceleration)
            
            sar = min(sar, df['Low'].iloc[i], df['Low'].iloc[i-1])
        
        min_stop = entry_price * (1 - DEFAULT_STOP_LOSS_PCT * 1.5 / 100)
        sar_stop = max(sar, min_stop)
        
        return round(sar_stop, 2)
    
    def get_comprehensive_stop_analysis(self, entry_price, df=None, risk_tolerance='Medium'):
        analysis = {
            'entry_price': entry_price,
            'risk_tolerance': risk_tolerance,
            'recommendations': {},
            'optimal_stop': None,
            'confidence_score': 0
        }
        
        recommendations = self.get_stop_loss_recommendations(entry_price, df, risk_tolerance)
        analysis['recommendations'] = recommendations
        
        if df is not None and len(df) >= 20:
            technical_stops = [
                recommendations.get('atr_based', 0),
                recommendations.get('support_based', 0),
                recommendations.get('volatility_adjusted', 0)
            ]
            technical_stops = [s for s in technical_stops if s > 0]
            
            if technical_stops:
                analysis['optimal_stop'] = round(np.median(technical_stops), 2)
                
                std_dev = np.std(technical_stops)
                avg_stop = np.mean(technical_stops)
                analysis['confidence_score'] = max(0, min(100, 100 - (std_dev / avg_stop * 100)))
            else:
                analysis['optimal_stop'] = recommendations['recommended']
                analysis['confidence_score'] = 60
        else:
            analysis['optimal_stop'] = recommendations['recommended']
            analysis['confidence_score'] = 50
        
        validation = self.validate_stop_loss(entry_price, analysis['optimal_stop'])
        analysis['validation'] = validation
        
        dynamic_levels = self.calculate_dynamic_levels(entry_price, df)
        analysis['dynamic_levels'] = dynamic_levels
        
        return analysis