# src/data/crypto_loader.py

import yfinance as yf
import pandas as pd
import requests
from pathlib import Path
import sys

project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from app.config import ENABLE_CRYPTO_TRADING
from src.data.data_cache import DataCache
from src.data.data_validator import DataValidator
from src.utils.logger import Logger

class CryptoLoader:
    def __init__(self):
        self.cache = DataCache()
        self.validator = DataValidator()
        self.logger = Logger(__name__)
        
        self.crypto_symbols = {
            'BTC': 'BTC-USD',
            'ETH': 'ETH-USD',
            'BNB': 'BNB-USD',
            'XRP': 'XRP-USD',
            'ADA': 'ADA-USD',
            'DOGE': 'DOGE-USD',
            'SOL': 'SOL-USD',
            'DOT': 'DOT-USD',
            'MATIC': 'MATIC-USD',
            'LINK': 'LINK-USD'
        }
    
    def load_crypto_data(self, symbol, period='1y', interval='1d', use_cache=True):
        if not ENABLE_CRYPTO_TRADING:
            self.logger.warning("Crypto trading is disabled in configuration")
            return None
        
        try:
            crypto_symbol = self._get_crypto_symbol(symbol)
            
            if use_cache:
                cached_data = self.cache.get_cached_data(crypto_symbol, period, 'crypto')
                if cached_data is not None:
                    self.logger.info(f"Loaded {crypto_symbol} from cache")
                    return cached_data
            
            self.logger.info(f"Fetching {crypto_symbol} from yfinance")
            ticker = yf.Ticker(crypto_symbol)
            df = ticker.history(period=period, interval=interval)
            
            if df.empty:
                self.logger.error(f"No data available for {crypto_symbol}")
                return None
            
            df = self.validator.validate_and_clean(df)
            
            if df is not None and not df.empty:
                self.cache.save_to_cache(crypto_symbol, df, period, 'crypto')
            
            return df
        
        except Exception as e:
            self.logger.error(f"Error loading crypto {symbol}: {str(e)}")
            return None
    
    def _get_crypto_symbol(self, symbol):
        symbol = symbol.upper()
        
        if symbol in self.crypto_symbols:
            return self.crypto_symbols[symbol]
        
        if '-USD' in symbol:
            return symbol
        
        return f"{symbol}-USD"
    
    def get_crypto_info(self, symbol):
        try:
            crypto_symbol = self._get_crypto_symbol(symbol)
            ticker = yf.Ticker(crypto_symbol)
            info = ticker.info
            
            return {
                'name': info.get('name', symbol),
                'symbol': crypto_symbol,
                'current_price': info.get('regularMarketPrice', 0),
                'market_cap': info.get('marketCap', 0),
                'volume_24h': info.get('volume24Hr', 0),
                'circulating_supply': info.get('circulatingSupply', 0),
                'total_supply': info.get('totalSupply', 0),
                'max_supply': info.get('maxSupply', 0),
                'all_time_high': info.get('fiftyTwoWeekHigh', 0),
                'all_time_low': info.get('fiftyTwoWeekLow', 0)
            }
        
        except Exception as e:
            self.logger.error(f"Error getting crypto info for {symbol}: {str(e)}")
            return {}
    
    def get_multiple_cryptos(self, symbols, period='1y'):
        results = {}
        
        for symbol in symbols:
            df = self.load_crypto_data(symbol, period=period)
            if df is not None and not df.empty:
                results[symbol] = df
        
        return results
    
    def get_crypto_market_overview(self):
        try:
            major_cryptos = ['BTC', 'ETH', 'BNB', 'XRP', 'ADA']
            overview = []
            
            for symbol in major_cryptos:
                info = self.get_crypto_info(symbol)
                if info:
                    df = self.load_crypto_data(symbol, period='1d')
                    
                    if df is not None and len(df) >= 2:
                        current = df['Close'].iloc[-1]
                        prev = df['Close'].iloc[-2]
                        change_24h = ((current - prev) / prev) * 100
                        
                        overview.append({
                            'symbol': symbol,
                            'name': info.get('name', symbol),
                            'price': current,
                            'change_24h': change_24h,
                            'market_cap': info.get('market_cap', 0),
                            'volume_24h': info.get('volume_24h', 0)
                        })
            
            return overview
        
        except Exception as e:
            self.logger.error(f"Error getting crypto market overview: {str(e)}")
            return []
    
    def get_crypto_dominance(self):
        try:
            btc_info = self.get_crypto_info('BTC')
            eth_info = self.get_crypto_info('ETH')
            
            btc_market_cap = btc_info.get('market_cap', 0)
            eth_market_cap = eth_info.get('market_cap', 0)
            
            total_market_cap = btc_market_cap + eth_market_cap
            
            if total_market_cap == 0:
                return {}
            
            return {
                'btc_dominance': (btc_market_cap / total_market_cap) * 100,
                'eth_dominance': (eth_market_cap / total_market_cap) * 100,
                'btc_market_cap': btc_market_cap,
                'eth_market_cap': eth_market_cap,
                'total_market_cap': total_market_cap
            }
        
        except Exception as e:
            self.logger.error(f"Error calculating crypto dominance: {str(e)}")
            return {}
    
    def get_available_cryptos(self):
        return list(self.crypto_symbols.keys())
    
    def add_crypto_symbol(self, name, symbol):
        full_symbol = symbol if '-USD' in symbol else f"{symbol}-USD"
        self.crypto_symbols[name.upper()] = full_symbol
        self.logger.info(f"Added crypto symbol: {name} -> {full_symbol}")