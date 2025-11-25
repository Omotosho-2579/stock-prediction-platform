# docs/USER_GUIDE.md

# User Guide

Complete guide to using the AI Stock Prediction Platform.

---

## Table of Contents

1. [Getting Started](#getting-started)
2. [Dashboard](#dashboard)
3. [Price Forecast](#price-forecast)
4. [Trading Signals](#trading-signals)
5. [Sentiment Analysis](#sentiment-analysis)
6. [Stock Comparison](#stock-comparison)
7. [Portfolio Tracker](#portfolio-tracker)
8. [Backtesting](#backtesting)
9. [Settings](#settings)
10. [Tips & Best Practices](#tips--best-practices)

---

## Getting Started

### First Launch

1. **Start the Application**
```bash
streamlit run app/main.py
```

2. **Browse to** `http://localhost:8501`

3. **Explore the Sidebar**
   - Select stock categories
   - Choose individual stocks
   - Add to watchlist

### Interface Overview

#### Sidebar
- **Market Status** - Real-time market open/closed indicator
- **Quick Search** - Select stocks by category or custom ticker
- **Watchlist** - Your saved stocks
- **Feature Status** - Enabled/disabled features

#### Main Area
- **Multi-page navigation** - Access different features
- **Interactive charts** - Zoom, pan, hover for details
- **Real-time data** - Auto-updating market information

---

## Dashboard

The dashboard provides a comprehensive market overview.

### Features

#### Market Summary
- Major indices (S&P 500, Dow Jones, NASDAQ)
- Top gainers and losers
- High volume stocks

#### Your Watchlist
- Quick view of tracked stocks
- Price changes
- Technical indicators

#### Active Alerts
- Price target notifications
- Signal generation alerts
- Status monitoring

### Quick Actions
- **Analyze Stock** - Enter ticker for instant analysis
- **Get Signals** - View trading recommendations
- **Compare Stocks** - Side-by-side comparison

---

## Price Forecast

AI-powered price predictions using multiple machine learning models.

### How to Use

1. **Select Stock** - Enter ticker symbol (e.g., AAPL)
2. **Choose Period** - Historical data period (1y, 2y, 3y, 5y)
3. **Forecast Days** - Prediction horizon (7, 14, 30, 60, 90 days)
4. **Select Models** - Choose prediction models:
   - Linear Regression
   - Random Forest
   - XGBoost
   - LSTM (Deep Learning)
   - Ensemble (Recommended)

5. **Click "Generate Forecast"**

### Understanding Results

#### Metrics
- **R² Score** - Model accuracy (0.7+ is good)
- **RMSE** - Average prediction error
- **MAE** - Mean absolute error
- **MAPE** - Percentage error

#### Visualization
- **Blue Line** - Historical prices
- **Red Line** - Predicted prices
- **Shaded Area** - Confidence interval

#### Tabs
- **Predictions** - Forecast charts and summary
- **Historical Data** - Past price movements
- **Technical Analysis** - Indicators overlay
- **Model Performance** - Accuracy metrics

---

## Trading Signals

AI-generated BUY/SELL/HOLD recommendations.

### Signal Generation

1. **Select Stock** - Enter ticker
2. **Analysis Timeframe** - Daily, Weekly, Monthly
3. **Signal Sensitivity**:
   - **Conservative** - Fewer, stronger signals
   - **Moderate** - Balanced approach
   - **Aggressive** - More frequent signals

4. **Trading Strategy**:
   - AI Composite (Recommended)
   - RSI Strategy
   - MACD Crossover
   - Moving Average
   - Bollinger Bands

5. **Click "Generate Trading Signals"**

### Interpreting Signals

#### Signal Types
- 🟢 **BUY** - Strong positive indicators
- 🔴 **SELL** - Strong negative indicators
- 🟡 **HOLD** - Mixed or neutral signals

#### Confidence Level
- **0-30%** - Weak signal
- **31-60%** - Moderate signal
- **61-85%** - Strong signal
- **86-100%** - Very strong signal

#### Signal Strength
- Scale of 0-10
- Higher = stronger conviction

### Risk Analysis Tab

#### Key Metrics
- **Risk Score** - Overall risk (0-10)
- **Volatility** - Price fluctuation measure
- **Beta** - Market correlation
- **Sharpe Ratio** - Risk-adjusted returns
- **Max Drawdown** - Largest price drop

#### Position Sizing
- Recommended number of shares
- Position value
- Portfolio percentage
- Risk per trade

---

## Sentiment Analysis

Analyze news and social media sentiment.

### Features

1. **News Sentiment**
   - Recent news articles
   - Sentiment scores (-1 to +1)
   - Source credibility

2. **Sentiment Trends**
   - Historical sentiment chart
   - Correlation with price
   - Sentiment momentum

3. **Key Insights**
   - Positive/Negative/Neutral breakdown
   - Top news sources
   - Recent headlines

### Understanding Sentiment

#### Scores
- **> 0.3** - Positive sentiment
- **-0.3 to 0.3** - Neutral
- **< -0.3** - Negative sentiment

#### Usage Tips
- Combine with technical analysis
- Watch for extreme sentiment
- Check multiple sources
- Consider sentiment momentum

---

## Stock Comparison

Compare multiple stocks side-by-side.

### How to Compare

1. **Enter Tickers** - Comma-separated (AAPL,GOOGL,MSFT)
2. **Select Period** - Time range for comparison
3. **Click "Compare Stocks"**

### Comparison Views

#### Price Performance
- Normalized price charts
- Relative performance
- Volume comparison

#### Returns Analysis
- Cumulative returns
- Period returns
- Volatility comparison

#### Metrics Table
- Current prices
- Technical indicators
- Volume statistics

#### Correlation Matrix
- Price correlations
- Returns correlations
- Heat map visualization

---

## Portfolio Tracker

Track and manage your investment portfolio.

### Adding Positions

1. **Use Sidebar Form**:
   - Stock Symbol
   - Number of Shares
   - Purchase Price
   - Purchase Date

2. **Click "Add Position"**

### Portfolio Overview

#### Summary Metrics
- Total Invested
- Current Value
- Total Gain/Loss
- Total Return %

#### Holdings Table
- All positions
- Current prices
- Unrealized gains/losses
- Position sizes

### Portfolio Analysis

#### Allocation Tab
- Pie chart of holdings
- Percentage breakdown
- Sector allocation

#### Performance Tab
- Historical portfolio value
- Growth over time
- Benchmark comparison

#### Risk Analysis Tab
- Portfolio beta
- Sharpe ratio
- Volatility
- Diversification metrics

---

## Backtesting

Test trading strategies on historical data.

### Running a Backtest

1. **Select Stock** - Choose ticker
2. **Backtest Period** - 1y, 2y, 3y, 5y
3. **Strategy Configuration**:
   - Strategy type
   - Parameters
   - Initial capital
   - Position size
   - Commission

4. **Click "Run Backtest"**

### Results Analysis

#### Performance Metrics
- Final Portfolio Value
- Total Return
- Total Trades
- Win Rate
- Sharpe Ratio
- Max Drawdown

#### Visualization
- Portfolio value over time
- vs Buy & Hold comparison
- Trade markers on chart

#### Trade History
- All executed trades
- Entry/exit prices
- Profit/Loss per trade
- Trade duration

---

## Settings

Configure platform preferences.

### General Settings
- Theme (Light/Dark)
- Default time period
- Display currency
- Data refresh interval

### Display Preferences
- Show volume in charts
- Technical indicators default
- News sentiment display

### Alerts Configuration
- Price targets
- Alert conditions
- Notification preferences

### Notifications
- Email alerts
- Telegram notifications
- Frequency settings

### API Keys
- NewsAPI
- Alpha Vantage
- Finnhub
- Telegram Bot
- Email configuration

---

## Tips & Best Practices

### For Beginners

1. **Start with Popular Stocks**
   - Use well-known tickers (AAPL, GOOGL, MSFT)
   - Understand basics before complex strategies

2. **Use Multiple Indicators**
   - Don't rely on single signal
   - Combine technical + sentiment + fundamental

3. **Paper Trade First**
   - Use backtesting
   - Test strategies without real money

### For Advanced Users

1. **Optimize Ensemble Weights**
   - Experiment with model combinations
   - Adjust based on market conditions

2. **Custom Strategies**
   - Combine multiple signals
   - Adjust sensitivity parameters

3. **Risk Management**
   - Always use stop-loss
   - Position sizing is critical
   - Diversify portfolio

### General Best Practices

1. **Regular Monitoring**
   - Check alerts daily
   - Review portfolio weekly
   - Rebalance quarterly

2. **Data Quality**
   - Verify unusual price movements
   - Cross-reference multiple sources
   - Check for data gaps

3. **Continuous Learning**
   - Read model performance metrics
   - Understand why signals are generated
   - Learn from backtest results

### Common Pitfalls to Avoid

1. **Overtrading** - Too many signals
2. **Ignoring Risk** - No stop-loss
3. **Emotional Decisions** - Stick to strategy
4. **Overfitting** - Don't optimize for past only
5. **Neglecting Fees** - Commission impacts returns

---

## Keyboard Shortcuts

- `Ctrl + R` - Refresh page
- `Ctrl + K` - Focus search
- `Ctrl + B` - Toggle sidebar
- `Ctrl + /` - Show shortcuts

---

## Troubleshooting

### Data Not Loading
- Check internet connection
- Verify API keys in Settings
- Try different time period
- Clear cache

### Predictions Fail
- Ensure sufficient historical data (> 100 days)
- Check symbol is valid
- Try different model

### Slow Performance
- Reduce number of indicators
- Use shorter time periods
- Clear browser cache

---

## FAQs

**Q: Is this financial advice?**  
A: No, this platform is for educational purposes only.

**Q: How accurate are predictions?**  
A: Accuracy varies (70-85% R²), past performance doesn't guarantee future results.

**Q: Can I trade directly from the platform?**  
A: No, this is analysis-only. Execute trades through your broker.

**Q: How often is data updated?**  
A: Real-time during market hours, with configurable refresh intervals.

**Q: Can I export data?**  
A: Yes, use CSV export features in tables.

---

## Support

**Issues**: [GitHub Issues](https://github.com/yourusername/stock-prediction-platform/issues)  
**Email**: support@stockplatform.com  
**Documentation**: Full docs at `/docs`

---

**Happy Trading! 📈**

*Last Updated: November 2025*