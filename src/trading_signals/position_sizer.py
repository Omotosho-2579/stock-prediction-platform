# src/trading_signals/position_sizer.py

import numpy as np
from pathlib import Path
import sys

project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from app.config import MAX_POSITION_SIZE_PCT
from src.utils.logger import Logger

class PositionSizer:
    def __init__(self):
        self.logger = Logger(__name__)
    
    def calculate_position_size(self, portfolio_value, entry_price, stop_loss_price, risk_per_trade_pct=2.0):
        if portfolio_value <= 0 or entry_price <= 0:
            self.logger.error("Invalid portfolio value or entry price")
            return 0
        
        risk_amount = portfolio_value * (risk_per_trade_pct / 100)
        
        risk_per_share = abs(entry_price - stop_loss_price)
        
        if risk_per_share == 0:
            self.logger.warning("Risk per share is zero, cannot calculate position size")
            return 0
        
        shares = risk_amount / risk_per_share
        
        position_value = shares * entry_price
        
        max_position_value = portfolio_value * (MAX_POSITION_SIZE_PCT / 100)
        if position_value > max_position_value:
            shares = max_position_value / entry_price
            position_value = max_position_value
            self.logger.info(f"Position size capped at {MAX_POSITION_SIZE_PCT}% of portfolio")
        
        return int(shares)
    
    def calculate_kelly_criterion(self, win_rate, avg_win, avg_loss):
        if not (0 <= win_rate <= 1):
            self.logger.error("Win rate must be between 0 and 1")
            return 0
        
        if avg_loss == 0:
            self.logger.error("Average loss cannot be zero")
            return 0
        
        win_loss_ratio = abs(avg_win / avg_loss)
        
        kelly_fraction = (win_rate * win_loss_ratio - (1 - win_rate)) / win_loss_ratio
        
        kelly_fraction = max(0, min(kelly_fraction, 0.25))
        
        return kelly_fraction * 100
    
    def calculate_fixed_fractional(self, portfolio_value, risk_pct=2.0):
        risk_amount = portfolio_value * (risk_pct / 100)
        
        return risk_amount
    
    def calculate_volatility_based_size(self, portfolio_value, volatility, target_volatility=15.0):
        if volatility <= 0:
            self.logger.warning("Invalid volatility, using default sizing")
            return portfolio_value * 0.1
        
        volatility_ratio = target_volatility / volatility
        
        position_fraction = min(volatility_ratio * 0.1, MAX_POSITION_SIZE_PCT / 100)
        
        position_size = portfolio_value * position_fraction
        
        return position_size
    
    def calculate_equal_weight(self, portfolio_value, number_of_positions):
        if number_of_positions <= 0:
            return 0
        
        position_size = portfolio_value / number_of_positions
        
        max_size = portfolio_value * (MAX_POSITION_SIZE_PCT / 100)
        
        return min(position_size, max_size)
    
    def calculate_risk_parity(self, portfolio_value, asset_volatilities):
        if not asset_volatilities or sum(asset_volatilities) == 0:
            return []
        
        inverse_vols = [1/vol if vol > 0 else 0 for vol in asset_volatilities]
        total_inverse = sum(inverse_vols)
        
        weights = [inv_vol / total_inverse for inv_vol in inverse_vols]
        
        position_sizes = [portfolio_value * weight for weight in weights]
        
        max_size = portfolio_value * (MAX_POSITION_SIZE_PCT / 100)
        position_sizes = [min(size, max_size) for size in position_sizes]
        
        return position_sizes
    
    def get_position_recommendations(self, portfolio_value, entry_price, stop_loss_price, 
                                     volatility=None, risk_tolerance='Medium', win_rate=None, 
                                     avg_win=None, avg_loss=None):
        risk_pct_map = {
            'Low': 1.0,
            'Medium': 2.0,
            'High': 3.0
        }
        
        risk_pct = risk_pct_map.get(risk_tolerance, 2.0)
        
        basic_shares = self.calculate_position_size(portfolio_value, entry_price, stop_loss_price, risk_pct)
        
        recommendations = {
            'conservative': {
                'shares': int(basic_shares * 0.5),
                'value': int(basic_shares * 0.5) * entry_price,
                'description': 'Half of calculated position - minimal risk'
            },
            'moderate': {
                'shares': basic_shares,
                'value': basic_shares * entry_price,
                'description': 'Standard position based on risk parameters'
            },
            'aggressive': {
                'shares': int(basic_shares * 1.5),
                'value': int(basic_shares * 1.5) * entry_price,
                'description': '150% of standard - higher risk/reward'
            }
        }
        
        if volatility:
            vol_based_value = self.calculate_volatility_based_size(portfolio_value, volatility)
            vol_shares = int(vol_based_value / entry_price)
            recommendations['volatility_adjusted'] = {
                'shares': vol_shares,
                'value': vol_shares * entry_price,
                'description': f'Adjusted for {volatility:.1f}% volatility'
            }
        
        if win_rate and avg_win and avg_loss:
            kelly_pct = self.calculate_kelly_criterion(win_rate, avg_win, avg_loss)
            kelly_value = portfolio_value * (kelly_pct / 100) * 0.5
            kelly_shares = int(kelly_value / entry_price)
            recommendations['kelly_criterion'] = {
                'shares': kelly_shares,
                'value': kelly_shares * entry_price,
                'description': f'Kelly Criterion: {kelly_pct:.1f}% allocation (half-kelly)'
            }
        
        return recommendations
    
    def validate_position_size(self, portfolio_value, position_value, number_of_positions=1):
        validations = {
            'is_valid': True,
            'warnings': [],
            'errors': []
        }
        
        position_pct = (position_value / portfolio_value) * 100
        
        if position_pct > MAX_POSITION_SIZE_PCT:
            validations['is_valid'] = False
            validations['errors'].append(
                f"Position size ({position_pct:.1f}%) exceeds maximum allowed ({MAX_POSITION_SIZE_PCT}%)"
            )
        
        if position_pct > 15:
            validations['warnings'].append(
                f"Large position size ({position_pct:.1f}%). Consider diversification."
            )
        
        if position_pct < 1:
            validations['warnings'].append(
                f"Very small position ({position_pct:.2f}%). May not be worth transaction costs."
            )
        
        total_exposure = position_value * number_of_positions
        exposure_pct = (total_exposure / portfolio_value) * 100
        
        if exposure_pct > 80:
            validations['warnings'].append(
                f"High total market exposure ({exposure_pct:.1f}%). Consider keeping cash reserves."
            )
        
        return validations
    
    def calculate_scaling_strategy(self, portfolio_value, entry_price, stop_loss_price, 
                                   number_of_entries=3):
        total_shares = self.calculate_position_size(portfolio_value, entry_price, stop_loss_price)
        
        if total_shares == 0:
            return []
        
        shares_per_entry = total_shares // number_of_entries
        
        scaling_plan = []
        
        for i in range(number_of_entries):
            entry_shares = shares_per_entry
            if i == number_of_entries - 1:
                entry_shares = total_shares - (shares_per_entry * (number_of_entries - 1))
            
            price_adjustment = 1 - (i * 0.02)
            
            scaling_plan.append({
                'entry_number': i + 1,
                'shares': entry_shares,
                'target_price': entry_price * price_adjustment,
                'value': entry_shares * entry_price * price_adjustment,
                'percentage_of_total': (entry_shares / total_shares) * 100
            })
        
        return scaling_plan