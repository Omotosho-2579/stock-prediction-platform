# src/trading_signals/risk_analyzer.py
# Run in: VS Code (Python environment with required packages)

import numpy as np
import pandas as pd
from pathlib import Path
import sys

project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from src.utils.logger import Logger

class RiskAnalyzer:
    def __init__(self):
        self.logger = Logger(__name__)
    
    def analyze_risk(self, df, current_price, risk_tolerance='Medium'):
        risk_metrics = {}
        
        risk_metrics['risk_score'] = self._calculate_risk_score(df, risk_tolerance)
        risk_metrics['volatility'] = self._calculate_volatility(df)
        risk_metrics['beta'] = self._calculate_beta(df)
        risk_metrics['max_drawdown'] = self._calculate_max_drawdown(df)
        risk_metrics['sharpe_ratio'] = self._calculate_sharpe_ratio(df)
        risk_metrics['var'] = self._calculate_var(df, current_price)
        
        return risk_metrics
    
    def _calculate_risk_score(self, df, risk_tolerance):
        volatility = self._calculate_volatility(df)
        max_dd = abs(self._calculate_max_drawdown(df))
        
        base_score = (volatility * 0.6) + (max_dd * 0.4)
        
        if risk_tolerance == 'Low':
            risk_score = min(10, base_score * 1.2)
        elif risk_tolerance == 'High':
            risk_score = max(1, base_score * 0.8)
        else:
            risk_score = base_score
        
        return min(10, max(1, risk_score))
    
    def _calculate_volatility(self, df, period=30):
        returns = df['Close'].pct_change().dropna()
        
        if len(returns) < period:
            period = len(returns)
        
        volatility = returns.tail(period).std() * np.sqrt(252) * 100
        
        return volatility
    
    def _calculate_beta(self, df, market_returns=None):
        stock_returns = df['Close'].pct_change().dropna()
        
        if market_returns is None:
            return 1.0
        
        if len(stock_returns) != len(market_returns):
            min_len = min(len(stock_returns), len(market_returns))
            stock_returns = stock_returns.tail(min_len)
            market_returns = market_returns.tail(min_len)
        
        covariance = np.cov(stock_returns, market_returns)[0][1]
        market_variance = np.var(market_returns)
        
        beta = covariance / market_variance if market_variance != 0 else 1.0
        
        return beta
    
    def _calculate_max_drawdown(self, df):
        cumulative = (1 + df['Close'].pct_change()).cumprod()
        running_max = cumulative.expanding().max()
        drawdown = (cumulative - running_max) / running_max * 100
        
        max_drawdown = drawdown.min()
        
        return max_drawdown
    
    def _calculate_sharpe_ratio(self, df, risk_free_rate=0.02):
        returns = df['Close'].pct_change().dropna()
        
        excess_returns = returns.mean() * 252 - risk_free_rate
        volatility = returns.std() * np.sqrt(252)
        
        sharpe = excess_returns / volatility if volatility != 0 else 0
        
        return sharpe
    
    def _calculate_var(self, df, current_price, confidence=0.95):
        returns = df['Close'].pct_change().dropna()
        
        var_percentile = np.percentile(returns, (1 - confidence) * 100)
        var = current_price * var_percentile
        
        return abs(var)
    
    def calculate_position_size(self, portfolio_size, current_price, stop_loss, risk_tolerance):
        risk_per_trade = {
            'Low': 0.01,
            'Medium': 0.02,
            'High': 0.03
        }
        
        risk_amount = portfolio_size * risk_per_trade.get(risk_tolerance, 0.02)
        
        risk_per_share = current_price - stop_loss
        
        if risk_per_share <= 0:
            return 0
        
        shares = risk_amount / risk_per_share
        position_value = shares * current_price
        
        max_position = portfolio_size * 0.2
        if position_value > max_position:
            shares = max_position / current_price
        
        return position_value
    
    def assess_risk_reward(self, entry_price, stop_loss, take_profit):
        risk = entry_price - stop_loss
        reward = take_profit - entry_price
        
        if risk <= 0:
            return {
                'risk_reward_ratio': 0,
                'risk_amount': 0,
                'reward_amount': 0,
                'assessment': 'Invalid'
            }
        
        ratio = reward / risk
        
        if ratio >= 3:
            assessment = 'Excellent'
        elif ratio >= 2:
            assessment = 'Good'
        elif ratio >= 1:
            assessment = 'Acceptable'
        else:
            assessment = 'Poor'
        
        return {
            'risk_reward_ratio': ratio,
            'risk_amount': risk,
            'reward_amount': reward,
            'assessment': assessment
        }
    
    def calculate_portfolio_risk(self, portfolio):
        if not portfolio:
            return {
                'beta': 1.0,
                'sharpe_ratio': 0,
                'volatility': 0
            }
        
        total_value = sum(p['shares'] * p['purchase_price'] for p in portfolio)
        
        weights = [p['shares'] * p['purchase_price'] / total_value for p in portfolio]
        
        portfolio_beta = sum(w * 1.0 for w in weights)
        
        return {
            'beta': portfolio_beta,
            'sharpe_ratio': 0.5,
            'volatility': 15.0
        }