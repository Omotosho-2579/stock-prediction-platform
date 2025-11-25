# tests/test_trading_signals.py

import pytest
import pandas as pd
import sys
from pathlib import Path

project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.trading_signals.signal_generator import SignalGenerator
from src.trading_signals.risk_analyzer import RiskAnalyzer
from src.data.data_loader import DataLoader
from src.data.technical_indicators import TechnicalIndicators

@pytest.fixture
def sample_data_with_indicators():
    data_loader = DataLoader()
    tech_indicators = TechnicalIndicators()
    
    df = data_loader.load_stock_data('AAPL', period='6mo', use_cache=False)
    df_with_indicators = tech_indicators.add_all_indicators(df)
    
    return df_with_indicators

@pytest.fixture
def signal_generator():
    return SignalGenerator()

@pytest.fixture
def risk_analyzer():
    return RiskAnalyzer()

class TestSignalGenerator:
    
    def test_signal_generator_initialization(self, signal_generator):
        assert signal_generator is not None
    
    def test_generate_signal_rsi_strategy(self, signal_generator, sample_data_with_indicators):
        signal_data = signal_generator.generate_signal(
            sample_data_with_indicators,
            strategy='RSI Strategy',
            sensitivity='Moderate'
        )
        
        assert signal_data is not None
        assert 'signal' in signal_data
        assert signal_data['signal'] in ['BUY', 'SELL', 'HOLD']
        assert 'confidence' in signal_data
        assert 0 <= signal_data['confidence'] <= 100
    
    def test_generate_signal_macd_strategy(self, signal_generator, sample_data_with_indicators):
        signal_data = signal_generator.generate_signal(
            sample_data_with_indicators,
            strategy='MACD Strategy',
            sensitivity='Moderate'
        )
        
        assert signal_data is not None
        assert 'signal' in signal_data
        assert signal_data['signal'] in ['BUY', 'SELL', 'HOLD']
    
    def test_generate_signal_different_sensitivities(self, signal_generator, sample_data_with_indicators):
        conservative = signal_generator.generate_signal(
            sample_data_with_indicators,
            strategy='RSI Strategy',
            sensitivity='Conservative'
        )
        
        aggressive = signal_generator.generate_signal(
            sample_data_with_indicators,
            strategy='RSI Strategy',
            sensitivity='Aggressive'
        )
        
        assert conservative is not None
        assert aggressive is not None

class TestRiskAnalyzer:
    
    def test_risk_analyzer_initialization(self, risk_analyzer):
        assert risk_analyzer is not None
    
    def test_analyze_risk(self, risk_analyzer, sample_data_with_indicators):
        current_price = sample_data_with_indicators['Close'].iloc[-1]
        
        risk_metrics = risk_analyzer.analyze_risk(
            sample_data_with_indicators,
            current_price,
            'Medium'
        )
        
        assert risk_metrics is not None
        assert 'risk_score' in risk_metrics
        assert 'volatility' in risk_metrics
        assert 'sharpe_ratio' in risk_metrics
        assert risk_metrics['risk_score'] >= 0
        assert risk_metrics['risk_score'] <= 10
    
    def test_calculate_position_size(self, risk_analyzer):
        portfolio_size = 10000
        current_price = 150
        stop_loss = 145
        
        position_size = risk_analyzer.calculate_position_size(
            portfolio_size,
            current_price,
            stop_loss,
            'Medium'
        )
        
        assert position_size > 0
        assert position_size <= portfolio_size
        