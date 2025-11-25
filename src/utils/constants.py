# src/utils/constants.py

from pathlib import Path
import sys

project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

class Constants:
    STOCK_EXCHANGES = {
        'NYSE': 'New York Stock Exchange',
        'NASDAQ': 'NASDAQ Stock Market',
        'AMEX': 'American Stock Exchange',
        'LSE': 'London Stock Exchange',
        'TSE': 'Tokyo Stock Exchange'
    }
    
    MAJOR_INDICES = {
        '^GSPC': 'S&P 500',
        '^DJI': 'Dow Jones Industrial Average',
        '^IXIC': 'NASDAQ Composite',
        '^RUT': 'Russell 2000',
        '^VIX': 'CBOE Volatility Index'
    }
    
    SECTORS = [
        'Technology',
        'Healthcare',
        'Financial Services',
        'Consumer Cyclical',
        'Industrials',
        'Communication Services',
        'Consumer Defensive',
        'Energy',
        'Real Estate',
        'Basic Materials',
        'Utilities'
    ]
    
    TECHNICAL_INDICATORS = [
        'SMA', 'EMA', 'RSI', 'MACD', 'Bollinger Bands',
        'ATR', 'Stochastic', 'CCI', 'ADX', 'Williams %R'
    ]
    
    TIMEFRAMES = {
        '1d': 'Daily',
        '1wk': 'Weekly',
        '1mo': 'Monthly',
        '3mo': 'Quarterly',
        '1y': 'Yearly'
    }
    
    PERIODS = {
        '1d': 1,
        '5d': 5,
        '1mo': 30,
        '3mo': 90,
        '6mo': 180,
        '1y': 365,
        '2y': 730,
        '5y': 1825,
        '10y': 3650,
        'max': 7300
    }
    
    RISK_LEVELS = {
        'Very Low': 0,
        'Low': 1,
        'Medium': 2,
        'High': 3,
        'Very High': 4
    }
    
    TRADING_SIGNALS = ['BUY', 'SELL', 'HOLD', 'STRONG BUY', 'STRONG SELL']
    
    MODEL_TYPES = [
        'Linear Regression',
        'Random Forest',
        'XGBoost',
        'LSTM',
        'Ensemble'
    ]
    
    ALERT_CONDITIONS = ['Above', 'Below', 'Equals', 'Change %']
    
    NOTIFICATION_METHODS = ['Email', 'Telegram', 'Discord', 'SMS', 'Push']
    
    SUPPORTED_CURRENCIES = ['USD', 'EUR', 'GBP', 'JPY', 'CAD', 'AUD', 'CHF']
    
    DATE_FORMATS = {
        'US': '%m/%d/%Y',
        'EU': '%d/%m/%Y',
        'ISO': '%Y-%m-%d',
        'LONG': '%B %d, %Y',
        'SHORT': '%m/%d/%y'
    }
    
    NUMBER_FORMATS = {
        'decimal': '{:,.2f}',
        'integer': '{:,}',
        'percentage': '{:.2f}%',
        'currency': '${:,.2f}',
        'scientific': '{:.2e}'
    }
    
    HTTP_STATUS_CODES = {
        200: 'OK',
        201: 'Created',
        400: 'Bad Request',
        401: 'Unauthorized',
        403: 'Forbidden',
        404: 'Not Found',
        500: 'Internal Server Error',
        503: 'Service Unavailable'
    }
    
    FILE_EXTENSIONS = {
        'csv': ['.csv'],
        'excel': ['.xlsx', '.xls'],
        'json': ['.json'],
        'pickle': ['.pkl', '.pickle'],
        'image': ['.png', '.jpg', '.jpeg', '.gif'],
        'document': ['.pdf', '.doc', '.docx']
    }
    
    MAX_FILE_SIZE_MB = 100
    
    DEFAULT_PAGINATION_SIZE = 20
    
    CACHE_TTL_SECONDS = {
        'realtime': 60,
        'intraday': 300,
        'daily': 3600,
        'weekly': 86400
    }
    
    API_RATE_LIMITS = {
        'yfinance': 2000,
        'alpha_vantage': 5,
        'news_api': 1000,
        'finnhub': 60
    }