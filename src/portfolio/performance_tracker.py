# src/portfolio/performance_tracker.py

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from pathlib import Path
import sys

project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from src.data.data_loader import DataLoader
from src.utils.logger import Logger

class PerformanceTracker:
    def __init__(self):
        self.logger = Logger(__name__)
        self.data_loader = DataLoader()
    
    def calculate_returns(self, initial_value, current_value):
        if initial_value == 0:
            return 0
        
        return ((current_value - initial_value) / initial_value) * 100
    
    def calculate_time_weighted_return(self, portfolio_values, dates):
        if len(portfolio_values) < 2:
            return 0
        
        returns = []
        for i in range(1, len(portfolio_values)):
            period_return = (portfolio_values[i] - portfolio_values[i-1]) / portfolio_values[i-1]
            returns.append(period_return)
        
        twr = 1
        for r in returns:
            twr *= (1 + r)
        
        twr = (twr - 1) * 100
        
        return twr
    
    def calculate_money_weighted_return(self, cash_flows, dates):
        try:
            from scipy.optimize import newton
            
            def npv(rate):
                npv_sum = 0
                t0 = dates[0]
                
                for i, cf in enumerate(cash_flows):
                    days_diff = (dates[i] - t0).days
                    npv_sum += cf / ((1 + rate) ** (days_diff / 365))
                
                return npv_sum
            
            irr = newton(npv, 0.1)
            return irr * 100
        
        except:
            self.logger.warning("Could not calculate money-weighted return")
            return 0
    
    def calculate_portfolio_history(self, holdings, days=90):
        if not holdings:
            return None
        
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days)
        
        portfolio_history = {}
        
        date_range = pd.date_range(start=start_date, end=end_date, freq='D')
        
        for date in date_range:
            daily_value = 0
            
            for holding in holdings:
                try:
                    df = self.data_loader.load_stock_data(holding['symbol'], period='1y')
                    
                    if df is not None and not df.empty:
                        date_prices = df[df.index <= date]
                        
                        if not date_prices.empty:
                            price = date_prices['Close'].iloc[-1]
                            daily_value += price * holding['shares']
                
                except Exception as e:
                    self.logger.error(f"Error calculating history for {holding['symbol']}: {str(e)}")
            
            portfolio_history[date.strftime('%Y-%m-%d')] = daily_value
        
        return portfolio_history
    
    def calculate_daily_returns(self, portfolio_values):
        values = list(portfolio_values.values())
        
        if len(values) < 2:
            return []
        
        daily_returns = []
        for i in range(1, len(values)):
            if values[i-1] > 0:
                ret = (values[i] - values[i-1]) / values[i-1]
                daily_returns.append(ret)
        
        return daily_returns
    
    def calculate_cumulative_returns(self, portfolio_values):
        values = list(portfolio_values.values())
        
        if not values:
            return []
        
        initial_value = values[0]
        cumulative_returns = []
        
        for value in values:
            if initial_value > 0:
                cum_return = ((value - initial_value) / initial_value) * 100
                cumulative_returns.append(cum_return)
        
        return cumulative_returns
    
    def calculate_annualized_return(self, total_return_pct, days):
        if days == 0:
            return 0
        
        years = days / 365.25
        
        annualized = ((1 + total_return_pct / 100) ** (1 / years) - 1) * 100
        
        return annualized
    
    def calculate_profit_loss(self, holdings):
        total_profit_loss = 0
        realized_pl = 0
        unrealized_pl = 0
        
        for holding in holdings:
            try:
                df = self.data_loader.load_stock_data(holding['symbol'], period='1d')
                
                if df is not None and not df.empty:
                    current_price = df['Close'].iloc[-1]
                    current_value = current_price * holding['shares']
                    cost_basis = holding['cost_basis']
                    
                    pl = current_value - cost_basis
                    total_profit_loss += pl
                    
                    if holding.get('sold', False):
                        realized_pl += pl
                    else:
                        unrealized_pl += pl
            
            except Exception as e:
                self.logger.error(f"Error calculating P/L for {holding['symbol']}: {str(e)}")
        
        return {
            'total_profit_loss': total_profit_loss,
            'realized_pl': realized_pl,
            'unrealized_pl': unrealized_pl
        }
    
    def calculate_position_performance(self, symbol, shares, purchase_price, purchase_date):
        try:
            df = self.data_loader.load_stock_data(symbol, period='1y')
            
            if df is None or df.empty:
                return None
            
            current_price = df['Close'].iloc[-1]
            current_value = current_price * shares
            cost_basis = purchase_price * shares
            
            profit_loss = current_value - cost_basis
            return_pct = (profit_loss / cost_basis * 100) if cost_basis > 0 else 0
            
            purchase_dt = datetime.strptime(purchase_date, '%Y-%m-%d')
            days_held = (datetime.now() - purchase_dt).days
            
            if days_held > 0:
                annualized_return = self.calculate_annualized_return(return_pct, days_held)
            else:
                annualized_return = 0
            
            return {
                'symbol': symbol,
                'shares': shares,
                'purchase_price': purchase_price,
                'current_price': current_price,
                'cost_basis': cost_basis,
                'current_value': current_value,
                'profit_loss': profit_loss,
                'return_pct': return_pct,
                'days_held': days_held,
                'annualized_return': annualized_return
            }
        
        except Exception as e:
            self.logger.error(f"Error calculating position performance: {str(e)}")
            return None