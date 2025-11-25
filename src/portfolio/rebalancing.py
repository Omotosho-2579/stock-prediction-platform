# src/portfolio/rebalancing.py

import pandas as pd
import numpy as np
from pathlib import Path
import sys

project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from src.data.data_loader import DataLoader
from src.utils.logger import Logger

class PortfolioRebalancing:
    def __init__(self):
        self.logger = Logger(__name__)
        self.data_loader = DataLoader()
    
    def calculate_rebalancing_needs(self, current_holdings, target_weights, tolerance=5.0):
        current_portfolio = self._get_current_portfolio_state(current_holdings)
        
        if not current_portfolio:
            return None
        
        total_value = sum(p['current_value'] for p in current_portfolio)
        
        rebalancing_actions = []
        
        for holding in current_portfolio:
            symbol = holding['symbol']
            current_weight = (holding['current_value'] / total_value) * 100
            target_weight = target_weights.get(symbol, 0)
            
            weight_diff = current_weight - target_weight
            
            if abs(weight_diff) > tolerance:
                target_value = (target_weight / 100) * total_value
                current_value = holding['current_value']
                value_diff = target_value - current_value
                
                shares_diff = value_diff / holding['current_price']
                
                action = 'BUY' if shares_diff > 0 else 'SELL'
                
                rebalancing_actions.append({
                    'symbol': symbol,
                    'action': action,
                    'current_weight': current_weight,
                    'target_weight': target_weight,
                    'weight_difference': weight_diff,
                    'shares_to_trade': abs(int(shares_diff)),
                    'value_to_trade': abs(value_diff)
                })
        
        for symbol, target_weight in target_weights.items():
            if not any(h['symbol'] == symbol for h in current_holdings):
                if target_weight > 0:
                    target_value = (target_weight / 100) * total_value
                    
                    df = self.data_loader.load_stock_data(symbol, period='1d')
                    if df is not None and not df.empty:
                        current_price = df['Close'].iloc[-1]
                        shares_to_buy = int(target_value / current_price)
                        
                        if shares_to_buy > 0:
                            rebalancing_actions.append({
                                'symbol': symbol,
                                'action': 'BUY',
                                'current_weight': 0,
                                'target_weight': target_weight,
                                'weight_difference': -target_weight,
                                'shares_to_trade': shares_to_buy,
                                'value_to_trade': target_value
                            })
        
        return rebalancing_actions
    
    def _get_current_portfolio_state(self, holdings):
        portfolio_state = []
        
        for holding in holdings:
            try:
                df = self.data_loader.load_stock_data(holding['symbol'], period='1d')
                
                if df is not None and not df.empty:
                    current_price = df['Close'].iloc[-1]
                    current_value = current_price * holding['shares']
                    
                    portfolio_state.append({
                        'symbol': holding['symbol'],
                        'shares': holding['shares'],
                        'current_price': current_price,
                        'current_value': current_value
                    })
            
            except Exception as e:
                self.logger.error(f"Error getting state for {holding['symbol']}: {str(e)}")
        
        return portfolio_state
    
    def suggest_rebalancing_schedule(self, rebalancing_frequency='quarterly'):
        schedules = {
            'monthly': 30,
            'quarterly': 90,
            'semi_annual': 180,
            'annual': 365
        }
        
        days = schedules.get(rebalancing_frequency, 90)
        
        from datetime import datetime, timedelta
        
        next_rebalance = datetime.now() + timedelta(days=days)
        
        return {
            'frequency': rebalancing_frequency,
            'days_between': days,
            'next_rebalance_date': next_rebalance.strftime('%Y-%m-%d')
        }
    
    def calculate_tax_efficient_rebalancing(self, holdings, target_weights, holding_period_days=365):
        rebalancing_actions = self.calculate_rebalancing_needs(holdings, target_weights)
        
        if not rebalancing_actions:
            return []
        
        from datetime import datetime
        
        tax_efficient_actions = []
        
        for action in rebalancing_actions:
            symbol = action['symbol']
            
            holding = next((h for h in holdings if h['symbol'] == symbol), None)
            
            if holding and action['action'] == 'SELL':
                purchase_date = datetime.strptime(holding['purchase_date'], '%Y-%m-%d')
                days_held = (datetime.now() - purchase_date).days
                
                if days_held < holding_period_days:
                    action['tax_warning'] = f"Short-term capital gains (held {days_held} days)"
                    action['priority'] = 'low'
                else:
                    action['tax_warning'] = None
                    action['priority'] = 'normal'
            else:
                action['tax_warning'] = None
                action['priority'] = 'normal'
            
            tax_efficient_actions.append(action)
        
        return sorted(tax_efficient_actions, key=lambda x: x['priority'])