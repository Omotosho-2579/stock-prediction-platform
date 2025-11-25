# src/data/data_loader.py

import yfinance as yf
import pandas as pd
import requests
from datetime import datetime, timedelta
from pathlib import Path
import sys

project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from app.config import (
    ALPHAVANTAGE_KEY,
    DEFAULT_PERIOD,
    DEFAULT_INTERVAL,
    ENABLE_BACKUP_DATA_SOURCE
)
from src.data.data_cache import DataCache
from src.data.data_validator import DataValidator
from src.utils.logger import Logger

class DataLoader:
    def __init__(self):
        self.cache = DataCache()
        self.validator = DataValidator()
        self.logger = Logger(__name__)
    
    def load_stock_data(self, symbol, period=DEFAULT_PERIOD, interval=DEFAULT_INTERVAL, use_cache=True):
        try:
            if use_cache:
                cached_data = self.cache.get_cached_data(symbol, period)
                if cached_data is not None:
                    self.logger.info(f"Loaded {symbol} from cache")
                    return cached_data
            
            self.logger.info(f"Fetching {symbol} from yfinance")
            ticker = yf.Ticker(symbol)
            df = ticker.history(period=period, interval=interval)
            
            if df.empty:
                self.logger.warning(f"No data from yfinance for {symbol}, trying backup")
                if ENABLE_BACKUP_DATA_SOURCE:
                    df = self._fetch_from_alphavantage(symbol, period)
                else:
                    self.logger.error(f"Failed to load data for {symbol}")
                    return None
            
            df = self.validator.validate_and_clean(df)
            
            if df is not None and not df.empty:
                self.cache.save_to_cache(symbol, df, period)
            
            return df
        
        except Exception as e:
            self.logger.error(f"Error loading {symbol}: {str(e)}")
            if ENABLE_BACKUP_DATA_SOURCE:
                return self._fetch_from_alphavantage(symbol, period)
            return None
    
    def _fetch_from_alphavantage(self, symbol, period):
        if not ALPHAVANTAGE_KEY:
            self.logger.error("Alpha Vantage API key not configured")
            return None
        
        try:
            outputsize = 'full' if period in ['5y', '10y'] else 'compact'
            
            url = f"https://www.alphavantage.co/query"
            params = {
                'function': 'TIME_SERIES_DAILY',
                'symbol': symbol,
                'apikey': ALPHAVANTAGE_KEY,
                'outputsize': outputsize,
                'datatype': 'json'
            }
            
            response = requests.get(url, params=params, timeout=10)
            data = response.json()
            
            if 'Time Series (Daily)' not in data:
                self.logger.error(f"Alpha Vantage error: {data.get('Note', 'Unknown error')}")
                return None
            
            time_series = data['Time Series (Daily)']
            
            df = pd.DataFrame.from_dict(time_series, orient='index')
            df.index = pd.to_datetime(df.index)
            df = df.sort_index()
            
            df.columns = ['Open', 'High', 'Low', 'Close', 'Volume']
            df = df.astype(float)
            
            period_days = self._period_to_days(period)
            if period_days:
                cutoff_date = datetime.now() - timedelta(days=period_days)
                df = df[df.index >= cutoff_date]
            
            self.logger.info(f"Successfully fetched {symbol} from Alpha Vantage")
            return df
        
        except Exception as e:
            self.logger.error(f"Alpha Vantage fetch error: {str(e)}")
            return None
    
    def _period_to_days(self, period):
        period_map = {
            '1d': 1,
            '5d': 5,
            '1mo': 30,
            '3mo': 90,
            '6mo': 180,
            '1y': 365,
            '2y': 730,
            '5y': 1825,
            '10y': 3650
        }
        return period_map.get(period, None)
    
    def get_stock_info(self, symbol):
        try:
            ticker = yf.Ticker(symbol)
            info = ticker.info
            
            return {
                'name': info.get('longName', symbol),
                'sector': info.get('sector', 'N/A'),
                'industry': info.get('industry', 'N/A'),
                'market_cap': info.get('marketCap', 0),
                'pe_ratio': info.get('trailingPE', 0),
                'dividend_yield': info.get('dividendYield', 0),
                'beta': info.get('beta', 1.0),
                'fifty_two_week_high': info.get('fiftyTwoWeekHigh', 0),
                'fifty_two_week_low': info.get('fiftyTwoWeekLow', 0),
                'avg_volume': info.get('averageVolume', 0)
            }
        
        except Exception as e:
            self.logger.error(f"Error getting info for {symbol}: {str(e)}")
            return {}
    
    def get_multiple_stocks(self, symbols, period=DEFAULT_PERIOD):
        results = {}
        
        for symbol in symbols:
            df = self.load_stock_data(symbol, period=period)
            if df is not None and not df.empty:
                results[symbol] = df
        
        return results
    
    def get_realtime_quote(self, symbol):
        try:
            ticker = yf.Ticker(symbol)
            data = ticker.history(period='1d', interval='1m')
            
            if data.empty:
                return None
            
            latest = data.iloc[-1]
            
            return {
                'symbol': symbol,
                'price': latest['Close'],
                'open': latest['Open'],
                'high': latest['High'],
                'low': latest['Low'],
                'volume': latest['Volume'],
                'timestamp': data.index[-1]
            }
        
        except Exception as e:
            self.logger.error(f"Error getting realtime quote for {symbol}: {str(e)}")
            return None