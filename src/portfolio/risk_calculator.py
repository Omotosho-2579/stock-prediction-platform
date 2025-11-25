# src/portfolio/risk_calculator.py

import numpy as np
import pandas as pd
from pathlib import Path
import sys

project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from src.data.data_loader import DataLoader
from src.utils.logger import Logger

class RiskCalculator:
    def __init__(self):
        self.logger = Logger(__name__)
        self.data_loader = DataLoader()
    
    def calculate_portfolio_risk(self, holdings):
        if not holdings:
            return {
                'volatility': 0,
                'beta': 1.0,
                'sharpe_ratio': 0,
                'var_95': 0,
                'cvar_95': 0
            }
        
        returns_data = {}
        
        for holding in holdings:
            try:
                df = self.data_loader.load_stock_data(holding['symbol'], period='1y')
                
                if df is not None and not df.empty:
                    returns = df['Close'].pct_change().dropna()
                    returns_data[holding['symbol']] = returns
            
            except Exception as e:
                self.logger.error(f"Error loading data for {holding['symbol']}: {str(e)}")
        
        if not returns_data:
            return {
                'volatility': 0,
                'beta': 1.0,
                'sharpe_ratio': 0,
                'var_95': 0,
                'cvar_95': 0
            }
        
        volatility = self._calculate_portfolio_volatility(returns_data, holdings)
        beta = self._calculate_portfolio_beta(returns_data, holdings)
        sharpe = self._calculate_sharpe_ratio(returns_data, holdings)
        var_95 = self._calculate_var(returns_data, holdings)
        cvar_95 = self._calculate_cvar(returns_data, holdings)
        
        return {
            'volatility': volatility,
            'beta': beta,
            'sharpe_ratio': sharpe,
            'var_95': var_95,
            'cvar_95': cvar_95
        }
    
    def _calculate_portfolio_volatility(self, returns_data, holdings):
        if not returns_data:
            return 0
        
        returns_df = pd.DataFrame(returns_data)
        
        total_value = sum(h['shares'] * h['purchase_price'] for h in holdings)
        
        weights = []
        for holding in holdings:
            if holding['symbol'] in returns_df.columns:
                weight = (holding['shares'] * holding['purchase_price']) / total_value
                weights.append(weight)
        
        weights = np.array(weights)
        
        if len(weights) != len(returns_df.columns):
            return 0
        
        cov_matrix = returns_df.cov()
        
        portfolio_variance = np.dot(weights.T, np.dot(cov_matrix, weights))
        portfolio_volatility = np.sqrt(portfolio_variance) * np.sqrt(252) * 100
        
        return portfolio_volatility
    
    def _calculate_portfolio_beta(self, returns_data, holdings):
        return 1.0
    
    def _calculate_sharpe_ratio(self, returns_data, holdings, risk_free_rate=0.02):
        if not returns_data:
            return 0
        
        returns_df = pd.DataFrame(returns_data)
        
        total_value = sum(h['shares'] * h['purchase_price'] for h in holdings)
        
        weights = []
        for holding in holdings:
            if holding['symbol'] in returns_df.columns:
                weight = (holding['shares'] * holding['purchase_price']) / total_value
                weights.append(weight)
        
        weights = np.array(weights)
        
        portfolio_returns = returns_df.dot(weights)
        
        mean_return = portfolio_returns.mean() * 252
        std_return = portfolio_returns.std() * np.sqrt(252)
        
        if std_return == 0:
            return 0
        
        sharpe_ratio = (mean_return - risk_free_rate) / std_return
        
        return sharpe_ratio
    
    def _calculate_var(self, returns_data, holdings, confidence=0.95):
        if not returns_data:
            return 0
        
        returns_df = pd.DataFrame(returns_data)
        
        total_value = sum(h['shares'] * h['purchase_price'] for h in holdings)
        
        weights = []
        for holding in holdings:
            if holding['symbol'] in returns_df.columns:
                weight = (holding['shares'] * holding['purchase_price']) / total_value
                weights.append(weight)
        
        weights = np.array(weights)
        
        portfolio_returns = returns_df.dot(weights)
        
        var = np.percentile(portfolio_returns, (1 - confidence) * 100)
        
        var_dollar = var * total_value
        
        return abs(var_dollar)
    
    def _calculate_cvar(self, returns_data, holdings, confidence=0.95):
        if not returns_data:
            return 0
        
        returns_df = pd.DataFrame(returns_data)
        
        total_value = sum(h['shares'] * h['purchase_price'] for h in holdings)
        
        weights = []
        for holding in holdings:
            if holding['symbol'] in returns_df.columns:
                weight = (holding['shares'] * holding['purchase_price']) / total_value
                weights.append(weight)
        
        weights = np.array(weights)
        
        portfolio_returns = returns_df.dot(weights)
        
        var_threshold = np.percentile(portfolio_returns, (1 - confidence) * 100)
        
        cvar = portfolio_returns[portfolio_returns <= var_threshold].mean()
        
        cvar_dollar = cvar * total_value
        
        return abs(cvar_dollar)
    
    def calculate_correlation_matrix(self, holdings):
        returns_data = {}
        
        for holding in holdings:
            try:
                df = self.data_loader.load_stock_data(holding['symbol'], period='1y')
                
                if df is not None and not df.empty:
                    returns = df['Close'].pct_change().dropna()
                    returns_data[holding['symbol']] = returns
            
            except Exception as e:
                self.logger.error(f"Error loading data for {holding['symbol']}: {str(e)}")
        
        if not returns_data:
            return None
        
        returns_df = pd.DataFrame(returns_data)
        correlation_matrix = returns_df.corr()
        
        return correlation_matrix