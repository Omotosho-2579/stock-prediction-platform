# docs/TRADING_STRATEGIES.md

# Trading Strategies

Comprehensive guide to trading signals, strategies, and signal generation methodology.

---

## Table of Contents

1. [Overview](#overview)
2. [Signal Types](#signal-types)
3. [Trading Strategies](#trading-strategies)
4. [Risk Management](#risk-management)
5. [Signal Interpretation](#signal-interpretation)
6. [Strategy Backtesting](#strategy-backtesting)

---

## Overview

The platform generates trading signals using a combination of:
- **Technical Analysis** - Price and volume patterns
- **Machine Learning** - AI-powered predictions
- **Sentiment Analysis** - News and social media
- **Risk Assessment** - Position sizing and stop-loss

### Signal Generation Pipeline
```
Market Data → Technical Indicators → Strategy Engine → Signal Generator → BUY/SELL/HOLD
     ↓              ↓                      ↓                  ↓              ↓
  yfinance    RSI, MACD           Multiple Rules      Confidence      Risk
  Real-time   Bollinger           Combined Logic      0-100%          Analysis
```

---

## Signal Types

### 1. BUY Signal 🟢

**Interpretation**: Favorable conditions for entering a long position

**Typical Conditions**:
- Price below key support
- RSI oversold (< 30)
- MACD bullish crossover
- Positive sentiment trend
- ML models predict upward movement

**Confidence Levels**:
- **80-100%**: Very strong signal
- **60-80%**: Strong signal
- **40-60%**: Moderate signal

### 2. SELL Signal 🔴

**Interpretation**: Favorable conditions for exiting long or entering short

**Typical Conditions**:
- Price above key resistance
- RSI overbought (> 70)
- MACD bearish crossover
- Negative sentiment trend
- ML models predict downward movement

**Confidence Levels**:
- **80-100%**: Very strong signal
- **60-80%**: Strong signal
- **40-60%**: Moderate signal

### 3. HOLD Signal 🟡

**Interpretation**: No clear direction, maintain current position

**Typical Conditions**:
- Mixed indicators
- Consolidation phase
- Low confidence predictions
- Neutral sentiment

---

## Trading Strategies

### 1. RSI Strategy

**Based On**: Relative Strength Index (14-period)

#### Logic
```python
if RSI < 30:
    signal = "BUY"  # Oversold
elif RSI > 70:
    signal = "SELL"  # Overbought
else:
    signal = "HOLD"  # Neutral zone
```

#### Parameters
- **RSI Period**: 14 days (default)
- **Oversold Threshold**: 30
- **Overbought Threshold**: 70

#### Best For
- Range-bound markets
- Mean reversion trading
- Short to medium-term trades

#### Limitations
- False signals in strong trends
- Needs confirmation from other indicators

---

### 2. MACD Crossover Strategy

**Based On**: Moving Average Convergence Divergence

#### Logic
```python
MACD = EMA(12) - EMA(26)
Signal_Line = EMA(MACD, 9)

if MACD crosses above Signal_Line:
    signal = "BUY"  # Bullish crossover
elif MACD crosses below Signal_Line:
    signal = "SELL"  # Bearish crossover
else:
    signal = "HOLD"
```

#### Parameters
- **Fast Period**: 12
- **Slow Period**: 26
- **Signal Period**: 9

#### Best For
- Trend following
- Medium to long-term trades
- Identifying momentum shifts

#### Limitations
- Lagging indicator
- Whipsaws in choppy markets

---

### 3. Moving Average Crossover

**Based On**: Simple Moving Averages

#### Logic
```python
SMA_Short = SMA(20)
SMA_Long = SMA(50)

if SMA_Short crosses above SMA_Long:
    signal = "BUY"  # Golden Cross
elif SMA_Short crosses below SMA_Long:
    signal = "SELL"  # Death Cross
else:
    signal = "HOLD"
```

#### Parameters
- **Short MA**: 20 days
- **Long MA**: 50 days
- **Alternative**: 50/200 for longer term

#### Best For
- Trend identification
- Long-term investors
- Clear market trends

#### Limitations
- Very lagging
- Poor in sideways markets

---

### 4. Bollinger Bands Strategy

**Based On**: Price volatility bands

#### Logic
```python
BB_Upper = SMA(20) + (2 × StdDev)
BB_Lower = SMA(20) - (2 × StdDev)

if Price < BB_Lower:
    signal = "BUY"  # Price at lower band
elif Price > BB_Upper:
    signal = "SELL"  # Price at upper band
else:
    signal = "HOLD"
```

#### Parameters
- **Period**: 20 days
- **Standard Deviations**: 2
- **Middle Band**: SMA(20)

#### Best For
- Volatility trading
- Mean reversion
- Identifying overbought/oversold

#### Limitations
- Assumes mean reversion
- Less effective in strong trends

---

### 5. AI Composite Strategy (Recommended)

**Based On**: Multiple indicators + ML predictions

#### Logic
```python
score = 0

# Technical Indicators (40% weight)
if RSI < 30: score += 2
if RSI > 70: score -= 2
if MACD > Signal: score += 1
if SMA_20 > SMA_50: score += 1

# ML Predictions (40% weight)
if ML_prediction > current_price * 1.02:
    score += 2
elif ML_prediction < current_price * 0.98:
    score -= 2

# Sentiment (20% weight)
if sentiment > 0.3: score += 1
if sentiment < -0.3: score -= 1

# Volume Confirmation
if volume > avg_volume * 1.5:
    score *= 1.2  # Amplify signal

# Generate Signal
if score >= 3:
    signal = "BUY"
elif score <= -3:
    signal = "SELL"
else:
    signal = "HOLD"

confidence = min(abs(score) / 5 * 100, 100)
```

#### Components Weighted
- **40%** - Technical indicators
- **40%** - ML predictions
- **20%** - Sentiment analysis
- **Multiplier** - Volume confirmation

#### Best For
- All market conditions
- Balanced approach
- Risk-adjusted decisions

#### Advantages
- Combines multiple signals
- Reduces false positives
- Adapts to market conditions

---

## Risk Management

### Position Sizing

#### Kelly Criterion
```python
win_rate = 0.60  # 60% win rate
avg_win = 1.5    # Average win size
avg_loss = 1.0   # Average loss size

kelly_pct = (win_rate / avg_loss) - ((1 - win_rate) / avg_win)
position_size = portfolio_value * kelly_pct * 0.5  # Half Kelly for safety
```

#### Fixed Percentage
```python
risk_per_trade = 0.02  # Risk 2% per trade
stop_loss_distance = entry_price - stop_loss_price
position_size = (portfolio_value * risk_per_trade) / stop_loss_distance
```

#### Maximum Position Size
```python
max_position = portfolio_value * 0.20  # Maximum 20% per stock
position_size = min(calculated_size, max_position)
```

### Stop Loss Calculation

#### ATR-Based Stop Loss
```python
ATR = Average_True_Range(14)
stop_loss = entry_price - (2 * ATR)  # For long positions
take_profit = entry_price + (3 * ATR)  # 1.5:1 reward/risk
```

#### Percentage-Based
```python
stop_loss_pct = 0.05  # 5% stop loss
stop_loss = entry_price * (1 - stop_loss_pct)

take_profit_pct = 0.10  # 10% take profit
take_profit = entry_price * (1 + take_profit_pct)
```

### Risk Metrics

#### Value at Risk (VaR)
```python
confidence_level = 0.95
returns = calculate_returns(prices)
var = percentile(returns, (1 - confidence_level) * 100)
```

#### Maximum Drawdown
```python
cumulative_returns = (1 + returns).cumprod()
running_max = cumulative_returns.cummax()
drawdown = (cumulative_returns - running_max) / running_max
max_drawdown = drawdown.min()
```

---

## Signal Interpretation

### Confidence Levels

#### Very High (85-100%)
- **Action**: Strong conviction trade
- **Position Size**: Full position (within limits)
- **Hold Time**: Until signal reverses
- **Risk**: Tight stop loss

#### High (70-85%)
- **Action**: Good trade setup
- **Position Size**: 75% of maximum
- **Hold Time**: Medium term
- **Risk**: Standard stop loss

#### Moderate (55-70%)
- **Action**: Cautious entry
- **Position Size**: 50% of maximum
- **Hold Time**: Short to medium
- **Risk**: Wider stop loss

#### Low (40-55%)
- **Action**: Wait for confirmation
- **Position Size**: 25% or skip
- **Hold Time**: Very short term
- **Risk**: Very tight stop

### Signal Strength (0-10 Scale)

**9-10**: Exceptional setup, multiple confluences  
**7-8**: Strong setup, good risk/reward  
**5-6**: Decent setup, requires monitoring  
**3-4**: Weak setup, high risk  
**0-2**: Poor setup, avoid trading

### Combining Multiple Signals

#### Confluence Trading
```python
signals = []

# Technical
if rsi_signal == "BUY": signals.append(1)
if macd_signal == "BUY": signals.append(1)
if ma_signal == "BUY": signals.append(1)

# ML
if ml_prediction > price * 1.03: signals.append(2)

# Sentiment
if sentiment > 0.4: signals.append(1)

total_score = sum(signals)

if total_score >= 4:
    final_signal = "STRONG BUY"
elif total_score >= 2:
    final_signal = "BUY"
else:
    final_signal = "HOLD"
```

---

## Strategy Backtesting

### Backtesting Process

1. **Historical Data** - Load 2-5 years of data
2. **Generate Signals** - Apply strategy rules
3. **Simulate Trades** - Execute based on signals
4. **Track Performance** - Record all metrics
5. **Analyze Results** - Evaluate strategy

### Performance Metrics

#### Return Metrics
- **Total Return**: (Final Value - Initial) / Initial
- **Annualized Return**: ((1 + Total Return) ^ (1/years)) - 1
- **CAGR**: Compound Annual Growth Rate

#### Risk Metrics
- **Sharpe Ratio**: (Return - Risk Free) / Volatility
- **Sortino Ratio**: (Return - Risk Free) / Downside Deviation
- **Max Drawdown**: Largest peak-to-trough decline

#### Trade Metrics
- **Win Rate**: Winning Trades / Total Trades
- **Profit Factor**: Gross Profit / Gross Loss
- **Average Win/Loss**: Mean profit per winning/losing trade

### Example Results
```
Strategy: MA Crossover (20/50)
Period: 2020-2024
Initial Capital: $10,000

Final Value: $15,234
Total Return: 52.34%
Annualized Return: 11.06%
Sharpe Ratio: 1.42
Max Drawdown: -18.5%

Total Trades: 24
Winning Trades: 15
Win Rate: 62.5%
Avg Win: $523
Avg Loss: $287
```

---

## Best Practices

### Do's
✅ Use stop losses always  
✅ Combine multiple indicators  
✅ Consider market context  
✅ Start with paper trading  
✅ Keep a trading journal  
✅ Review and adjust strategies  
✅ Manage position sizes  
✅ Stay disciplined

### Don'ts
❌ Trade based on single indicator  
❌ Ignore risk management  
❌ Over-leverage positions  
❌ Chase losses  
❌ Trade emotionally  
❌ Ignore market sentiment  
❌ Over-optimize on past data  
❌ Trade without a plan

---

## Strategy Selection Guide

| Market Condition | Recommended Strategy | Confidence Needed |
|------------------|---------------------|-------------------|
| Strong Uptrend | MA Crossover | 60%+ |
| Strong Downtrend | Short MACD Signals | 70%+ |
| Range-Bound | RSI + Bollinger | 65%+ |
| High Volatility | Bollinger Bands | 70%+ |
| Mixed/Uncertain | AI Composite | 75%+ |

---

## Disclaimer

⚠️ **Important**: 
- Backtest results don't guarantee future performance
- All strategies involve risk of loss
- This is educational content, not financial advice
- Always do your own research
- Never invest more than you can afford to lose

---

**Last Updated**: November 2025  
**Version**: 1.0.0