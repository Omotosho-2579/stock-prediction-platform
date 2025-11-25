# docs/API_DOCUMENTATION.md

# API Documentation

Complete reference for all data sources, APIs, and integrations used in the Stock Prediction Platform.

---

## Table of Contents

1. [Stock Data APIs](#stock-data-apis)
2. [News & Sentiment APIs](#news--sentiment-apis)
3. [Notification APIs](#notification-apis)
4. [Internal APIs](#internal-apis)
5. [Rate Limits](#rate-limits)
6. [Error Handling](#error-handling)

---

## Stock Data APIs

### 1. yfinance (Primary Source)

**Provider**: Yahoo Finance  
**Cost**: Free  
**Documentation**: https://github.com/ranaroussi/yfinance

#### Usage
```python
from src.data.data_loader import DataLoader

loader = DataLoader()
df = loader.load_stock_data('AAPL', period='1y')
```

#### Available Periods
- `1d`, `5d`, `1mo`, `3mo`, `6mo`, `1y`, `2y`, `5y`, `10y`, `ytd`, `max`

#### Available Intervals
- `1m`, `2m`, `5m`, `15m`, `30m`, `60m`, `90m`, `1h`, `1d`, `5d`, `1wk`, `1mo`, `3mo`

#### Data Fields
```python
{
    'Open': float,
    'High': float,
    'Low': float,
    'Close': float,
    'Volume': int,
    'Dividends': float,
    'Stock Splits': float
}
```

#### Rate Limits
- Unlimited requests
- No authentication required
- Recommended: 1 request per second

---

### 2. Alpha Vantage (Backup Source)

**Provider**: Alpha Vantage  
**Cost**: Free (500 calls/day), Paid tiers available  
**Documentation**: https://www.alphavantage.co/documentation/

#### Setup
```bash
ALPHAVANTAGE_KEY=your_api_key
```

#### Usage
```python
from src.data.data_loader import DataLoader

loader = DataLoader()
df = loader._fetch_from_alphavantage('AAPL', period='1y')
```

#### Endpoints Used
- `TIME_SERIES_DAILY` - Daily historical data
- `TIME_SERIES_INTRADAY` - Intraday data
- `GLOBAL_QUOTE` - Real-time quotes

#### Rate Limits
- **Free**: 5 calls/minute, 500 calls/day
- **Premium**: 75 calls/minute, unlimited daily

---

## News & Sentiment APIs

### 1. NewsAPI

**Provider**: NewsAPI.org  
**Cost**: Free (100 requests/day), Paid tiers available  
**Documentation**: https://newsapi.org/docs

#### Setup
```bash
NEWSAPI_KEY=your_api_key
```

#### Usage
```python
from src.sentiment.news_scraper import NewsScraper

scraper = NewsScraper()
articles = scraper.fetch_news('AAPL', days=7)
```

#### Parameters
```python
{
    'q': 'stock_symbol',           # Query
    'from': 'YYYY-MM-DD',          # Start date
    'to': 'YYYY-MM-DD',            # End date
    'language': 'en',              # Language
    'sortBy': 'publishedAt',       # Sort order
    'pageSize': 100                # Results per page
}
```

#### Response Format
```python
{
    'status': 'ok',
    'totalResults': 1234,
    'articles': [
        {
            'source': {'id': None, 'name': 'Bloomberg'},
            'author': 'John Doe',
            'title': 'Article title',
            'description': 'Article description',
            'url': 'https://...',
            'publishedAt': '2024-03-15T10:30:00Z',
            'content': 'Full content...'
        }
    ]
}
```

#### Rate Limits
- **Free**: 100 requests/day
- **Developer**: 250 requests/day
- **Business**: 100,000 requests/day

---

### 2. Finnhub

**Provider**: Finnhub.io  
**Cost**: Free (60 calls/minute), Paid tiers available  
**Documentation**: https://finnhub.io/docs/api

#### Setup
```bash
FINNHUB_KEY=your_api_key
```

#### Usage
```python
import finnhub

client = finnhub.Client(api_key="YOUR_KEY")
news = client.company_news('AAPL', _from="2024-01-01", to="2024-12-31")
```

#### Available Endpoints
- `company_news()` - Company-specific news
- `market_news()` - General market news
- `quote()` - Real-time quotes
- `financials()` - Financial statements

#### Rate Limits
- **Free**: 60 calls/minute
- **Starter**: 300 calls/minute
- **Pro**: 600 calls/minute

---

## Notification APIs

### 1. Telegram Bot API

**Provider**: Telegram  
**Cost**: Free  
**Documentation**: https://core.telegram.org/bots/api

#### Setup
```bash
TELEGRAM_BOT_TOKEN=your_bot_token
TELEGRAM_CHAT_ID=your_chat_id
```

#### Usage
```python
from src.alerts.telegram_bot import TelegramBot

bot = TelegramBot()
bot.send_message("AAPL reached $150!")
```

#### Creating a Bot
1. Message @BotFather on Telegram
2. Send `/newbot`
3. Follow instructions
4. Copy bot token

#### Get Chat ID
1. Message @userinfobot
2. Copy your chat ID

---

### 2. Email (SMTP)

**Provider**: Gmail, SendGrid, etc.  
**Cost**: Free (Gmail), Paid (SendGrid)  

#### Setup
```bash
EMAIL_SENDER=your_email@gmail.com
EMAIL_PASSWORD=your_app_password
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
```

#### Gmail App Password
1. Enable 2-Factor Authentication
2. Go to Security Settings
3. Generate App Password
4. Use generated password

#### Usage
```python
from src.alerts.email_sender import EmailSender

sender = EmailSender()
sender.send_alert("user@example.com", "Price Alert", "AAPL at $150")
```

---

## Internal APIs

### Data Loader API

#### Load Stock Data
```python
loader.load_stock_data(
    symbol='AAPL',
    period='1y',
    interval='1d',
    use_cache=True
)
```

#### Get Stock Info
```python
info = loader.get_stock_info('AAPL')
```

#### Get Multiple Stocks
```python
data = loader.get_multiple_stocks(['AAPL', 'GOOGL', 'MSFT'], period='1y')
```

---

### Model API

#### Train Model
```python
from src.models.ensemble import EnsembleModel

model = EnsembleModel()
model.train(X_train, y_train, X_val, y_val)
```

#### Make Predictions
```python
predictions = model.predict(X_test)
```

#### Future Predictions
```python
forecast = model.predict_future(df, days=30)
```

---

### Trading Signals API

#### Generate Signal
```python
from src.trading_signals.signal_generator import SignalGenerator

generator = SignalGenerator()
signal = generator.generate_signal(
    df_with_indicators,
    strategy='AI Composite',
    sensitivity='Moderate'
)
```

#### Response Format
```python
{
    'signal': 'BUY',           # BUY, SELL, or HOLD
    'confidence': 85,          # 0-100
    'strength': 8,             # 0-10
    'reasons': [               # List of reasons
        'RSI indicates oversold',
        'MACD bullish crossover'
    ]
}
```

---

## Rate Limits

### Summary Table

| Service | Free Tier | Rate Limit | Daily Limit |
|---------|-----------|------------|-------------|
| yfinance | ✅ | ~1 req/sec | Unlimited |
| Alpha Vantage | ✅ | 5 req/min | 500 |
| NewsAPI | ✅ | - | 100 |
| Finnhub | ✅ | 60 req/min | Unlimited |
| Telegram | ✅ | 30 msg/sec | Unlimited |

### Best Practices
1. **Cache responses** - Use built-in caching (24h TTL)
2. **Batch requests** - Combine multiple operations
3. **Retry logic** - Implement exponential backoff
4. **Monitor usage** - Track API call counts
5. **Use fallbacks** - Switch to backup sources

---

## Error Handling

### Common Errors

#### 1. Rate Limit Exceeded
```python
{
    'error': 'Rate limit exceeded',
    'retry_after': 60,  # seconds
    'status_code': 429
}
```

**Solution**: Wait and retry, use caching

#### 2. Invalid API Key
```python
{
    'error': 'Invalid API key',
    'status_code': 401
}
```

**Solution**: Check `.env` configuration

#### 3. Symbol Not Found
```python
{
    'error': 'Symbol not found',
    'status_code': 404
}
```

**Solution**: Validate ticker symbol

#### 4. Network Error
```python
{
    'error': 'Connection timeout',
    'status_code': 504
}
```

**Solution**: Retry with exponential backoff

---

### Error Handling Example
```python
import time

def fetch_with_retry(func, max_retries=3):
    for attempt in range(max_retries):
        try:
            return func()
        except RateLimitError:
            wait_time = 2 ** attempt
            time.sleep(wait_time)
        except NetworkError:
            if attempt == max_retries - 1:
                raise
            time.sleep(1)
    
    raise Exception("Max retries exceeded")
```

---

## API Testing

### Test Endpoints
```python
# Test yfinance
python -c "import yfinance as yf; print(yf.Ticker('AAPL').info)"

# Test NewsAPI
curl "https://newsapi.org/v2/everything?q=apple&apiKey=YOUR_KEY"

# Test Finnhub
curl "https://finnhub.io/api/v1/quote?symbol=AAPL&token=YOUR_KEY"
```

---

## Additional Resources

- [yfinance GitHub](https://github.com/ranaroussi/yfinance)
- [Alpha Vantage Docs](https://www.alphavantage.co/documentation/)
- [NewsAPI Docs](https://newsapi.org/docs)
- [Finnhub API Reference](https://finnhub.io/docs/api)
- [Telegram Bot API](https://core.telegram.org/bots/api)

---

**Last Updated**: November 2025  
**Version**: 1.0.0