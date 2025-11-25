# tests/test_integration.py

import pytest
import sys
from pathlib import Path

project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.data.data_loader import DataLoader
from src.data.technical_indicators import TechnicalIndicators
from src.models.ensemble import EnsembleModel
from src.trading_signals.signal_generator import SignalGenerator
from src.portfolio.portfolio_manager import PortfolioManager

@pytest.mark.integration
class TestEndToEndWorkflow:
    
    def test_complete_prediction_workflow(self):
        data_loader = DataLoader()
        tech_indicators = TechnicalIndicators()
        
        df = data_loader.load_stock_data('AAPL', period='1y', use_cache=False)
        assert df is not None
        
        df_with_indicators = tech_indicators.add_all_indicators(df)
        assert 'RSI' in df_with_indicators.columns
        assert 'MACD' in df_with_indicators.columns
        
        ensemble = EnsembleModel()
        X_train, X_test, y_train, y_test = ensemble.models['linear_regression'].split_data(df)
        
        ensemble.train(X_train, y_train)
        assert ensemble.is_trained
        
        predictions = ensemble.predict(X_test)
        assert predictions is not None
        assert len(predictions) > 0
    
    def test_complete_trading_signals_workflow(self):
        data_loader = DataLoader()
        tech_indicators = TechnicalIndicators()
        signal_generator = SignalGenerator()
        
        df = data_loader.load_stock_data('AAPL', period='6mo', use_cache=False)
        assert df is not None
        
        df_with_indicators = tech_indicators.add_all_indicators(df)
        
        signal_data = signal_generator.generate_signal(
            df_with_indicators,
            strategy='AI Composite',
            sensitivity='Moderate'
        )
        
        assert signal_data is not None
        assert 'signal' in signal_data
        assert signal_data['signal'] in ['BUY', 'SELL', 'HOLD']
    
    def test_complete_portfolio_workflow(self):
        portfolio_manager = PortfolioManager()
        
        position1 = {
            'symbol': 'AAPL',
            'shares': 10,
            'purchase_price': 150.00,
            'purchase_date': '2024-01-01'
        }
        
        position2 = {
            'symbol': 'GOOGL',
            'shares': 5,
            'purchase_price': 140.00,
            'purchase_date': '2024-01-15'
        }
        
        portfolio_manager.add_position(position1)
        portfolio_manager.add_position(position2)
        
        portfolio = [position1, position2]
        
        total_value = portfolio_manager.calculate_total_value(portfolio)
        assert total_value > 0
        
        allocation = portfolio_manager.calculate_allocation(portfolio)
        assert allocation is not None
        assert len(allocation) == 2
    
    @pytest.mark.slow
    def test_multiple_stocks_analysis(self):
        data_loader = DataLoader()
        symbols = ['AAPL', 'GOOGL', 'MSFT']
        
        results = data_loader.get_multiple_stocks(symbols, period='1mo')
        
        assert len(results) > 0
        assert all(symbol in results for symbol in symbols)
        
        for symbol, df in results.items():
            assert not df.empty
            assert 'Close' in df.columns