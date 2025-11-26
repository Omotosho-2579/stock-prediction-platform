"""
Application Configuration
Centralized settings, constants, and API configurations
"""

import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Try to load from Streamlit secrets (for deployment)
try:
    import streamlit as st
    if hasattr(st, 'secrets') and 'secrets' in st.secrets:
        USE_STREAMLIT_SECRETS = True
    else:
        USE_STREAMLIT_SECRETS = False
except (ImportError, FileNotFoundError, AttributeError):
    USE_STREAMLIT_SECRETS = False

def get_secret(key, default=None):
    """Get secret from Streamlit secrets or environment variables"""
    if USE_STREAMLIT_SECRETS:
        try:
            value = st.secrets["secrets"].get(key, default)
            if value is not None:
                return value
        except:
            pass
    return os.getenv(key, default)

# ============================================================================
# PROJECT PATHS
# ============================================================================
BASE_DIR = Path(__file__).parent.parent
DATA_DIR = BASE_DIR / "data"
MODELS_DIR = BASE_DIR / "models"
ASSETS_DIR = BASE_DIR / "assets"

# Data subdirectories
CACHE_DIR = DATA_DIR / "cache"
PREDICTIONS_DIR = DATA_DIR / "predictions"
SENTIMENT_DIR = DATA_DIR / "sentiment"

# Models subdirectories
POPULAR_MODELS_DIR = MODELS_DIR / "popular"
CACHED_MODELS_DIR = MODELS_DIR / "cache"

# Create directories if they don't exist
for directory in [DATA_DIR, CACHE_DIR, PREDICTIONS_DIR, SENTIMENT_DIR, 
                  MODELS_DIR, POPULAR_MODELS_DIR, CACHED_MODELS_DIR]:
    directory.mkdir(parents=True, exist_ok=True)

# ============================================================================
# API KEYS & CREDENTIALS
# ============================================================================

# News API (for sentiment analysis)
NEWSAPI_KEY = get_secret("NEWSAPI_KEY")

# Alpha Vantage (backup stock data source)
ALPHAVANTAGE_KEY = get_secret("ALPHAVANTAGE_KEY")

# Finnhub (alternative financial news)
FINNHUB_KEY = get_secret("FINNHUB_KEY")

# Telegram Bot (for alerts)
TELEGRAM_BOT_TOKEN = get_secret("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID = get_secret("TELEGRAM_CHAT_ID")

# Twitter API (for social sentiment)
TWITTER_API_KEY = get_secret("TWITTER_API_KEY")
TWITTER_API_SECRET = get_secret("TWITTER_API_SECRET")
TWITTER_ACCESS_TOKEN = get_secret("TWITTER_ACCESS_TOKEN")
TWITTER_ACCESS_SECRET = get_secret("TWITTER_ACCESS_SECRET")
TWITTER_BEARER_TOKEN = get_secret("TWITTER_BEARER_TOKEN")

# Email Configuration (for alerts)
EMAIL_SENDER = get_secret("EMAIL_SENDER")
EMAIL_PASSWORD = get_secret("EMAIL_PASSWORD")
SMTP_SERVER = get_secret("SMTP_SERVER", "smtp.gmail.com")
SMTP_PORT = int(get_secret("SMTP_PORT", "587"))

# ============================================================================
# STOCK DATA CONFIGURATION
# ============================================================================

# Popular stocks for pre-training
POPULAR_STOCKS = [
    'AAPL', 'GOOGL', 'MSFT', 'TSLA', 'AMZN',
    'META', 'NVDA', 'JPM', 'V', 'WMT',
    'JNJ', 'PG', 'MA', 'UNH', 'HD',
    'DIS', 'BAC', 'NFLX', 'ADBE', 'CSCO'
]

# Stock categories for easy filtering
STOCK_CATEGORIES = {
    'Tech Giants': ['AAPL', 'GOOGL', 'MSFT', 'AMZN', 'META', 'NVDA'],
    'Financial': ['JPM', 'V', 'MA', 'BAC', 'GS', 'AXP'],
    'Healthcare': ['JNJ', 'UNH', 'PFE', 'ABBV', 'TMO'],
    'Consumer': ['WMT', 'PG', 'KO', 'PEP', 'NKE'],
    'Entertainment': ['DIS', 'NFLX', 'CMCSA'],
    'Auto & Energy': ['TSLA', 'F', 'XOM', 'CVX'],
    'Crypto': ['BTC-USD', 'ETH-USD', 'BNB-USD']
}

# Default data parameters
DEFAULT_PERIOD = '2y'  # Historical data period
DEFAULT_INTERVAL = '1d'  # Daily data
CACHE_TTL_HOURS = 24  # Cache time-to-live

# ============================================================================
# MODEL CONFIGURATION
# ============================================================================

# Model types available
MODEL_TYPES = ['linear_regression', 'lstm', 'random_forest', 'xgboost', 'ensemble']

# Model training parameters
TRAIN_TEST_SPLIT = 0.2  # 80% train, 20% test
LSTM_LOOKBACK_DAYS = 60  # Days of historical data for LSTM
LSTM_EPOCHS = 50
LSTM_BATCH_SIZE = 32

# Model performance thresholds
MIN_R2_SCORE = 0.70  # Minimum acceptable R² score
MODEL_STALE_DAYS = 7  # Retrain if model older than 7 days

# Feature engineering
TECHNICAL_INDICATORS = [
    'SMA_5', 'SMA_10', 'SMA_20', 'SMA_50',
    'EMA_12', 'EMA_26',
    'RSI_14',
    'MACD', 'MACD_Signal',
    'BB_Upper', 'BB_Middle', 'BB_Lower',
    'ATR_14',
    'Volume_SMA_20'
]

# ============================================================================
# TRADING SIGNALS CONFIGURATION
# ============================================================================

# Signal generation parameters
RSI_OVERSOLD = 30
RSI_OVERBOUGHT = 70
MACD_SIGNAL_THRESHOLD = 0.5

# Risk management
DEFAULT_STOP_LOSS_PCT = 5.0  # 5% stop loss
DEFAULT_TAKE_PROFIT_PCT = 10.0  # 10% take profit
MAX_POSITION_SIZE_PCT = 20.0  # Max 20% of portfolio per position

# Trading strategies available
TRADING_STRATEGIES = [
    'RSI_Strategy',
    'MACD_Crossover',
    'Moving_Average_Crossover',
    'Bollinger_Bands',
    'Mean_Reversion',
    'Momentum'
]

# ============================================================================
# SENTIMENT ANALYSIS CONFIGURATION
# ============================================================================

# News sources
NEWS_SOURCES = [
    'bloomberg', 'reuters', 'financial-times',
    'the-wall-street-journal', 'cnbc', 'marketwatch'
]

# Sentiment thresholds
SENTIMENT_POSITIVE_THRESHOLD = 0.3
SENTIMENT_NEGATIVE_THRESHOLD = -0.3

# Social media keywords for filtering
STOCK_KEYWORDS = ['stock', 'shares', 'trading', 'invest', 'market', 'earnings', 'dividend']

# ============================================================================
# ALERT CONFIGURATION
# ============================================================================

# Alert types
ALERT_TYPES = [
    'price_target',      # When stock reaches specific price
    'percent_change',    # When stock moves X%
    'volume_spike',      # Unusual volume
    'signal_generated',  # When buy/sell signal triggers
    'earnings_date',     # Before earnings announcement
    'news_sentiment'     # Significant sentiment change
]

# Alert frequency limits (to avoid spam)
MAX_ALERTS_PER_DAY = 10
ALERT_COOLDOWN_MINUTES = 30

# ============================================================================
# UI CONFIGURATION
# ============================================================================

# App metadata
APP_NAME = "AI Stock Prediction Platform"
APP_VERSION = "1.0.0"
APP_AUTHOR = "Mohammed Abdulrafiu Omotosho"
APP_DESCRIPTION = "Advanced stock price prediction with AI trading signals"

# Theme colors
PRIMARY_COLOR = "#1f77b4"
SECONDARY_COLOR = "#ff7f0e"
SUCCESS_COLOR = "#2ecc71"
WARNING_COLOR = "#f39c12"
DANGER_COLOR = "#e74c3c"

# Chart configuration
CHART_HEIGHT = 500
CHART_TEMPLATE = "plotly_white"  # or "plotly_dark"

# Pagination
ITEMS_PER_PAGE = 20
MAX_STOCKS_COMPARE = 5

# ============================================================================
# DATABASE CONFIGURATION
# ============================================================================

# SQLite database path
DATABASE_PATH = DATA_DIR / "database.db"

# Table names
TABLE_USERS = "users"
TABLE_PORTFOLIOS = "portfolios"
TABLE_ALERTS = "alerts"
TABLE_PREDICTIONS = "predictions"
TABLE_WATCHLISTS = "watchlists"

# ============================================================================
# LOGGING CONFIGURATION
# ============================================================================

LOG_LEVEL = get_secret("LOG_LEVEL", "INFO")
LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
LOG_FILE = DATA_DIR / "app.log"

# ============================================================================
# RATE LIMITING
# ============================================================================

# API rate limits (requests per minute)
YFINANCE_RATE_LIMIT = 60
NEWSAPI_RATE_LIMIT = 100  # per day with free tier
ALPHAVANTAGE_RATE_LIMIT = 5  # per minute with free tier
TWITTER_RATE_LIMIT = 180  # per 15 minutes with free tier

# ============================================================================
# FEATURE FLAGS
# ============================================================================

# Enable/disable features based on API availability
ENABLE_SENTIMENT_ANALYSIS = NEWSAPI_KEY is not None
ENABLE_SOCIAL_SENTIMENT = (TWITTER_API_KEY is not None and 
                           TWITTER_API_SECRET is not None and 
                           TWITTER_ACCESS_TOKEN is not None and 
                           TWITTER_ACCESS_SECRET is not None)
ENABLE_TELEGRAM_ALERTS = TELEGRAM_BOT_TOKEN is not None
ENABLE_EMAIL_ALERTS = EMAIL_SENDER is not None and EMAIL_PASSWORD is not None
ENABLE_BACKUP_DATA_SOURCE = ALPHAVANTAGE_KEY is not None

# Advanced features
ENABLE_CRYPTO_TRADING = True
ENABLE_PORTFOLIO_OPTIMIZATION = True
ENABLE_BACKTESTING = True
ENABLE_TAX_CALCULATOR = False

# ============================================================================
# VALIDATION
# ============================================================================

def validate_config():
    """Validate configuration and warn about missing API keys"""
    warnings = []
    
    if not NEWSAPI_KEY:
        warnings.append("⚠️ NewsAPI key missing - Sentiment analysis disabled")
    
    if not ALPHAVANTAGE_KEY:
        warnings.append("⚠️ Alpha Vantage key missing - No backup data source")
    
    if not TELEGRAM_BOT_TOKEN:
        warnings.append("⚠️ Telegram bot token missing - Telegram alerts disabled")
    
    if not EMAIL_SENDER or not EMAIL_PASSWORD:
        warnings.append("⚠️ Email credentials missing - Email alerts disabled")
    
    if not all([TWITTER_API_KEY, TWITTER_API_SECRET, TWITTER_ACCESS_TOKEN, TWITTER_ACCESS_SECRET]):
        warnings.append("⚠️ Twitter API credentials missing - Social sentiment analysis disabled")
    
    return warnings

# Run validation on import
CONFIG_WARNINGS = validate_config()

# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def get_model_path(ticker: str, model_type: str, is_popular: bool = False) -> Path:
    """Get full path for a saved model file"""
    base_dir = POPULAR_MODELS_DIR if is_popular else CACHED_MODELS_DIR
    extension = '.h5' if model_type == 'lstm' else '.pkl'
    return base_dir / f"{ticker}_{model_type}{extension}"

def get_cache_path(ticker: str, data_type: str = 'historical') -> Path:
    """Get full path for cached data file"""
    if data_type == 'historical':
        return CACHE_DIR / f"{ticker}_2y_historical.csv"
    elif data_type == 'prediction':
        from datetime import datetime
        month = datetime.now().strftime("%Y-%m")
        return PREDICTIONS_DIR / f"{ticker}_predictions_{month}.csv"
    elif data_type == 'sentiment':
        from datetime import datetime
        date = datetime.now().strftime("%Y-%m-%d")
        return SENTIMENT_DIR / f"{ticker}_news_{date}.json"
    else:
        raise ValueError(f"Unknown data type: {data_type}")

def is_market_open() -> bool:
    """Check if US stock market is currently open"""
    from datetime import datetime
    import pytz
    
    # US Eastern Time
    et = pytz.timezone('US/Eastern')
    now = datetime.now(et)
    
    # Market closed on weekends
    if now.weekday() >= 5:
        return False
    
    # Market hours: 9:30 AM - 4:00 PM ET
    market_open = now.replace(hour=9, minute=30, second=0)
    market_close = now.replace(hour=16, minute=0, second=0)
    
    return market_open <= now <= market_close

# ============================================================================
# EXPORT CONFIGURATION
# ============================================================================

__all__ = [
    'BASE_DIR', 'DATA_DIR', 'MODELS_DIR', 'ASSETS_DIR',
    'POPULAR_STOCKS', 'STOCK_CATEGORIES',
    'MODEL_TYPES', 'TRADING_STRATEGIES',
    'ENABLE_SENTIMENT_ANALYSIS', 'ENABLE_SOCIAL_SENTIMENT',
    'ENABLE_TELEGRAM_ALERTS', 'ENABLE_EMAIL_ALERTS',
    'ENABLE_CRYPTO_TRADING', 'ENABLE_PORTFOLIO_OPTIMIZATION',
    'ENABLE_BACKTESTING',
    'TWITTER_API_KEY', 'TWITTER_API_SECRET',
    'TWITTER_ACCESS_TOKEN', 'TWITTER_ACCESS_SECRET',
    'get_model_path', 'get_cache_path', 'is_market_open',
    'CONFIG_WARNINGS'
]
