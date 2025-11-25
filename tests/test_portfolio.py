# tests/test_portfolio.py

import pytest
import sys
from pathlib import Path
from datetime import datetime

project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.portfolio.portfolio_manager import PortfolioManager
from src.portfolio.performance_tracker import PerformanceTracker
from src.portfolio.risk_calculator import RiskCalculator

@pytest.fixture
def portfolio_manager():
    return PortfolioManager()

@pytest.fixture
def performance_tracker():
    return PerformanceTracker()

@pytest.fixture
def risk_calculator():
    return RiskCalculator()

@pytest.fixture
def sample_portfolio():
    return [
        {
            'symbol': 'AAPL',
            'shares': 10,
            'purchase_price': 150.00,
            'purchase_date': '2024-01-01'
        },
        {
            'symbol': 'GOOGL',
            'shares': 5,
            'purchase_price': 140.00,
            'purchase_date': '2024-01-15'
        }
    ]

class TestPortfolioManager:
    
    def test_manager_initialization(self, portfolio_manager):
        assert portfolio_manager is not None
    
    def test_add_position(self, portfolio_manager):
        position = {
            'symbol': 'AAPL',
            'shares': 10,
            'purchase_price': 150.00,
            'purchase_date': '2024-01-01'
        }
        
        result = portfolio_manager.add_position(position)
        
        assert result is not None
    
    def test_calculate_portfolio_value(self, portfolio_manager, sample_portfolio):
        total_value = portfolio_manager.calculate_total_value(sample_portfolio)
        
        assert total_value > 0
    
    def test_calculate_portfolio_allocation(self, portfolio_manager, sample_portfolio):
        allocation = portfolio_manager.calculate_allocation(sample_portfolio)
        
        assert allocation is not None
        assert len(allocation) > 0

class TestPerformanceTracker:
    
    def test_tracker_initialization(self, performance_tracker):
        assert performance_tracker is not None
    
    def test_calculate_portfolio_history(self, performance_tracker, sample_portfolio):
        history = performance_tracker.calculate_portfolio_history(sample_portfolio)
        
        assert history is not None

class TestRiskCalculator:
    
    def test_calculator_initialization(self, risk_calculator):
        assert risk_calculator is not None
    
    def test_calculate_portfolio_risk(self, risk_calculator, sample_portfolio):
        risk_metrics = risk_calculator.calculate_portfolio_risk(sample_portfolio)
        
        assert risk_metrics is not None
        assert 'beta' in risk_metrics
        assert 'sharpe_ratio' in risk_metrics
        assert 'volatility' in risk_metrics