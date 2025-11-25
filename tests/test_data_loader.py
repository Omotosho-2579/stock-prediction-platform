# tests/test_data_loader.py

import pytest
import pandas as pd
import sys
from pathlib import Path
from datetime import datetime

project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.data.data_loader import DataLoader
from src.data.data_validator import DataValidator

@pytest.fixture
def data_loader():
    return DataLoader()

@pytest.fixture
def validator():
    return DataValidator()

class TestDataLoader:
    
    def test_data_loader_initialization(self, data_loader):
        assert data_loader is not None
        assert hasattr(data_loader, 'cache')
        assert hasattr(data_loader, 'validator')
    
    def test_load_stock_data_valid_symbol(self, data_loader):
        df = data_loader.load_stock_data('AAPL', period='1mo', use_cache=False)
        
        assert df is not None
        assert isinstance(df, pd.DataFrame)
        assert not df.empty
        assert 'Close' in df.columns
        assert 'Open' in df.columns
        assert 'High' in df.columns
        assert 'Low' in df.columns
        assert 'Volume' in df.columns
    
    def test_load_stock_data_invalid_symbol(self, data_loader):
        df = data_loader.load_stock_data('INVALID_SYMBOL_XYZ', period='1mo', use_cache=False)
        
        assert df is None or df.empty
    
    def test_load_stock_data_different_periods(self, data_loader):
        df_1mo = data_loader.load_stock_data('AAPL', period='1mo', use_cache=False)
        df_6mo = data_loader.load_stock_data('AAPL', period='6mo', use_cache=False)
        
        assert len(df_1mo) < len(df_6mo)
    
    def test_get_stock_info(self, data_loader):
        info = data_loader.get_stock_info('AAPL')
        
        assert info is not None
        assert 'name' in info
        assert 'sector' in info
        assert 'market_cap' in info
    
    def test_get_multiple_stocks(self, data_loader):
        symbols = ['AAPL', 'GOOGL', 'MSFT']
        results = data_loader.get_multiple_stocks(symbols, period='1mo')
        
        assert len(results) > 0
        assert all(isinstance(df, pd.DataFrame) for df in results.values())
    
    def test_caching_functionality(self, data_loader):
        symbol = 'AAPL'
        
        df1 = data_loader.load_stock_data(symbol, period='1mo', use_cache=True)
        df2 = data_loader.load_stock_data(symbol, period='1mo', use_cache=True)
        
        assert df1 is not None
        assert df2 is not None
        assert len(df1) == len(df2)

class TestDataValidator:
    
    def test_validator_initialization(self, validator):
        assert validator is not None
    
    def test_validate_and_clean_valid_data(self, validator, data_loader):
        df = data_loader.load_stock_data('AAPL', period='1mo', use_cache=False)
        
        cleaned_df = validator.validate_and_clean(df)
        
        assert cleaned_df is not None
        assert not cleaned_df.empty
        assert not cleaned_df.isnull().all().any()
    
    def test_validate_and_clean_with_missing_columns(self, validator):
        df = pd.DataFrame({
            'Close': [100, 101, 102],
            'Volume': [1000, 2000, 3000]
        })
        
        result = validator.validate_and_clean(df)
        
        assert result is None
    
    def test_check_data_quality(self, validator, data_loader):
        df = data_loader.load_stock_data('AAPL', period='1mo', use_cache=False)
        
        quality_report = validator.check_data_quality(df)
        
        assert 'total_rows' in quality_report
        assert 'quality_score' in quality_report
        assert quality_report['quality_score'] >= 0
        assert quality_report['quality_score'] <= 100
    
    def test_validate_ticker_symbol(self, validator):
        assert validator.validate_ticker_symbol('AAPL') == True
        assert validator.validate_ticker_symbol('GOOGL') == True
        assert validator.validate_ticker_symbol('') == False
        assert validator.validate_ticker_symbol('123') == False
        assert validator.validate_ticker_symbol('TOOLONGSYMBOL') == False