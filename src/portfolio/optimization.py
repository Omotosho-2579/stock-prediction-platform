# src/portfolio/optimization.py

import numpy as np
import pandas as pd
from pathlib import Path
import sys

project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from src.data.data_loader import DataLoader
from src.utils.logger import Logger

class PortfolioOptimization:
    def __init__(self):
        self.logger = Logger(__name__)
        self.data_loader = DataLoader()
    
    def optimize_portfolio(self, symbols, method='sharpe'):
        returns_data = {}
        
        for symbol in symbols:
            try:
                df = self.data_loader.load_stock_data(symbol, period='2y')
                
                if df is not None and not df.empty:
                    returns = df['Close'].pct_change().dropna()
                    returns_data[symbol] = returns
            
            except Exception as e:
                self.logger.error(f"Error loading {symbol}: {str(e)}")
        
        if len(returns_data) < 2:
            self.logger.error("Need at least 2 stocks for optimization")
            return None
        
        returns_df = pd.DataFrame(returns_data)
        
        if method == 'sharpe':
            optimal_weights = self._optimize_sharpe_ratio(returns_df)
        elif method == 'min_volatility':
            optimal_weights = self._optimize_min_volatility(returns_df)
        elif method == 'equal_weight':
            optimal_weights = self._equal_weight(returns_df)
        else:
            optimal_weights = self._optimize_sharpe_ratio(returns_df)
        
        expected_return, expected_volatility, sharpe_ratio = self._calculate_portfolio_metrics(
            returns_df, optimal_weights
        )
        
        return {
            'weights': {symbol: weight for symbol, weight in zip(returns_df.columns, optimal_weights)},
            'expected_return': expected_return,
            'expected_volatility': expected_volatility,
            'sharpe_ratio': sharpe_ratio
        }
    
    def _optimize_sharpe_ratio(self, returns_df, risk_free_rate=0.02):
        from scipy.optimize import minimize
        
        mean_returns = returns_df.mean() * 252
        cov_matrix = returns_df.cov() * 252
        
        num_assets = len(returns_df.columns)
        
        def negative_sharpe(weights):
            portfolio_return = np.dot(weights, mean_returns)
            portfolio_std = np.sqrt(np.dot(weights.T, np.dot(cov_matrix, weights)))
            
            if portfolio_std == 0:
                return 0
            
            sharpe = (portfolio_return - risk_free_rate) / portfolio_std
            return -sharpe
        
        constraints = ({'type': 'eq', 'fun': lambda x: np.sum(x) - 1})
        bounds = tuple((0, 1) for _ in range(num_assets))
        
        initial_guess = np.array([1/num_assets] * num_assets)
        
        result = minimize(negative_sharpe, initial_guess, method='SLSQP', bounds=bounds, constraints=constraints)
        
        return result.x
    
    def _optimize_min_volatility(self, returns_df):
        from scipy.optimize import minimize
        
        cov_matrix = returns_df.cov() * 252
        
        num_assets = len(returns_df.columns)
        
        def portfolio_volatility(weights):
            return np.sqrt(np.dot(weights.T, np.dot(cov_matrix, weights)))
        
        constraints = ({'type': 'eq', 'fun': lambda x: np.sum(x) - 1})
        bounds = tuple((0, 1) for _ in range(num_assets))
        
        initial_guess = np.array([1/num_assets] * num_assets)
        
        result = minimize(portfolio_volatility, initial_guess, method='SLSQP', bounds=bounds, constraints=constraints)
        
        return result.x
    
    def _equal_weight(self, returns_df):
        num_assets = len(returns_df.columns)
        return np.array([1/num_assets] * num_assets)
    
    def _calculate_portfolio_metrics(self, returns_df, weights, risk_free_rate=0.02):
        mean_returns = returns_df.mean() * 252
        cov_matrix = returns_df.cov() * 252
        
        portfolio_return = np.dot(weights, mean_returns) * 100
        portfolio_volatility = np.sqrt(np.dot(weights.T, np.dot(cov_matrix, weights))) * 100
        
        sharpe_ratio = (portfolio_return/100 - risk_free_rate) / (portfolio_volatility/100) if portfolio_volatility > 0 else 0
        
        return portfolio_return, portfolio_volatility, sharpe_ratio
    
    def calculate_efficient_frontier(self, symbols, num_portfolios=100):
        returns_data = {}
        
        for symbol in symbols:
            try:
                df = self.data_loader.load_stock_data(symbol, period='2y')
                
                if df is not None and not df.empty:
                    returns = df['Close'].pct_change().dropna()
                    returns_data[symbol] = returns
            
            except Exception as e:
                self.logger.error(f"Error loading {symbol}: {str(e)}")
        
        if len(returns_data) < 2:
            return None
        
        returns_df = pd.DataFrame(returns_data)
        
        mean_returns = returns_df.mean() * 252
        cov_matrix = returns_df.cov() * 252
        
        num_assets = len(returns_df.columns)
        
        results = []
        
        for _ in range(num_portfolios):
            weights = np.random.random(num_assets)
            weights /= np.sum(weights)
            
            portfolio_return = np.dot(weights, mean_returns) * 100
            portfolio_volatility = np.sqrt(np.dot(weights.T, np.dot(cov_matrix, weights))) * 100
            
            sharpe = portfolio_return / portfolio_volatility if portfolio_volatility > 0 else 0
            
            results.append({
                'return': portfolio_return,
                'volatility': portfolio_volatility,
                'sharpe': sharpe,
                'weights': weights.tolist()
            })
        
        return results