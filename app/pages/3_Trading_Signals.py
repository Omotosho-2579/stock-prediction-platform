# app/pages/3_🎯_Trading_Signals.py

import streamlit as st
import pandas as pd
import sys
from pathlib import Path
from datetime import datetime

sys.path.append(str(Path(__file__).parent.parent.parent))

from app.config import (
    POPULAR_STOCKS, RSI_OVERSOLD, RSI_OVERBOUGHT,
    DEFAULT_STOP_LOSS_PCT, DEFAULT_TAKE_PROFIT_PCT
)
from src.data.data_loader import DataLoader
from src.data.technical_indicators import TechnicalIndicators
from src.trading_signals.signal_generator import SignalGenerator
from src.trading_signals.risk_analyzer import RiskAnalyzer
from src.trading_signals.strategy_engine import StrategyEngine
from src.trading_signals.recommendation_ai import RecommendationAI
from src.visualization.plotly_charts import PlotlyCharts
from src.utils.formatters import Formatters
from src.utils.validators import Validators

st.set_page_config(page_title="Trading Signals", page_icon="🎯", layout="wide")

st.title("🎯 AI Trading Signals")
st.markdown("Get intelligent buy/sell recommendations based on technical analysis and AI models")

if 'selected_ticker' not in st.session_state:
    st.session_state.selected_ticker = POPULAR_STOCKS[0] if POPULAR_STOCKS else 'AAPL'

data_loader = DataLoader()
tech_indicators = TechnicalIndicators()
signal_generator = SignalGenerator()
risk_analyzer = RiskAnalyzer()
strategy_engine = StrategyEngine()
recommendation_ai = RecommendationAI()
plotly_charts = PlotlyCharts()
formatters = Formatters()
validators = Validators()

col1, col2, col3 = st.columns([2, 1, 1])

with col1:
    symbol = st.text_input(
        "Stock Symbol",
        value=st.session_state.selected_ticker,
        help="Enter stock ticker for trading signals"
    ).upper()
    st.session_state.selected_ticker = symbol

with col2:
    timeframe = st.selectbox(
        "Analysis Timeframe",
        options=["1d", "1wk", "1mo"],
        format_func=lambda x: {"1d": "Daily", "1wk": "Weekly", "1mo": "Monthly"}[x],
        index=0
    )

with col3:
    signal_sensitivity = st.selectbox(
        "Signal Sensitivity",
        options=["Conservative", "Moderate", "Aggressive"],
        index=1
    )

if not validators.validate_ticker(symbol):
    st.warning("Please enter a valid stock ticker symbol")
    st.stop()

col_strategy1, col_strategy2 = st.columns(2)

with col_strategy1:
    strategy_type = st.selectbox(
        "Trading Strategy",
        options=[
            "AI Composite",
            "RSI Strategy",
            "MACD Crossover",
            "Moving Average",
            "Bollinger Bands",
            "Momentum"
        ]
    )

with col_strategy2:
    risk_tolerance = st.selectbox(
        "Risk Tolerance",
        options=["Low", "Medium", "High"],
        index=1
    )

if st.button("🔍 Generate Trading Signals", type="primary"):
    with st.spinner(f"Analyzing {symbol}..."):
        df = data_loader.load_stock_data(symbol, period="1y")
        
        if df is None or df.empty:
            st.error(f"Failed to load data for {symbol}")
            st.stop()
        
        df_with_indicators = tech_indicators.add_all_indicators(df)
        
        st.success(f"Analysis complete for {symbol}")
    
    current_price = df['Close'].iloc[-1]
    prev_price = df['Close'].iloc[-2]
    price_change = ((current_price - prev_price) / prev_price) * 100
    
    col_info1, col_info2, col_info3, col_info4 = st.columns(4)
    
    with col_info1:
        st.metric(
            "Current Price",
            formatters.format_currency(current_price),
            f"{price_change:.2f}%"
        )
    
    with col_info2:
        volume = df['Volume'].iloc[-1]
        avg_volume = df['Volume'].tail(30).mean()
        volume_change = ((volume - avg_volume) / avg_volume) * 100
        st.metric(
            "Volume",
            formatters.format_number(volume),
            f"{volume_change:.1f}% vs avg"
        )
    
    with col_info3:
        rsi = df_with_indicators['RSI'].iloc[-1]
        st.metric("RSI (14)", f"{rsi:.2f}")
    
    with col_info4:
        volatility = df['Close'].pct_change().std() * 100
        st.metric("Volatility", f"{volatility:.2f}%")
    
    st.divider()
    
    with st.spinner("Generating trading signals..."):
        signal_data = signal_generator.generate_signal(
            df_with_indicators,
            strategy=strategy_type,
            sensitivity=signal_sensitivity
        )
    
    signal = signal_data.get('signal', 'HOLD')
    signal_strength = signal_data.get('strength', 0)
    confidence = signal_data.get('confidence', 0)
    
    if signal == "BUY":
        signal_color = "🟢"
        signal_bg = "#d4edda"
    elif signal == "SELL":
        signal_color = "🔴"
        signal_bg = "#f8d7da"
    else:
        signal_color = "🟡"
        signal_bg = "#fff3cd"
    
    st.markdown(
        f"""
        <div style="background-color: {signal_bg}; padding: 20px; border-radius: 10px; text-align: center;">
            <h2>{signal_color} {signal} SIGNAL</h2>
            <p style="font-size: 18px;">Confidence: {confidence}% | Strength: {signal_strength}/10</p>
        </div>
        """,
        unsafe_allow_html=True
    )
    
    st.divider()
    
    tab1, tab2, tab3, tab4 = st.tabs(["Signal Details", "Risk Analysis", "Technical Indicators", "Strategy Insights"])
    
    with tab1:
        st.subheader("📊 Signal Analysis")
        
        col_sig1, col_sig2 = st.columns(2)
        
        with col_sig1:
            st.markdown("#### Current Signal")
            st.markdown(f"**Action:** {signal}")
            st.markdown(f"**Confidence Level:** {confidence}%")
            st.markdown(f"**Signal Strength:** {signal_strength}/10")
            st.markdown(f"**Strategy Used:** {strategy_type}")
            
            reasons = signal_data.get('reasons', [])
            if reasons:
                st.markdown("#### Key Reasons:")
                for reason in reasons:
                    st.markdown(f"• {reason}")
        
        with col_sig2:
            st.markdown("#### Price Targets")
            
            entry_price = current_price
            stop_loss = entry_price * (1 - DEFAULT_STOP_LOSS_PCT / 100)
            take_profit = entry_price * (1 + DEFAULT_TAKE_PROFIT_PCT / 100)
            
            st.metric("Entry Price", formatters.format_currency(entry_price))
            st.metric("Stop Loss", formatters.format_currency(stop_loss), f"-{DEFAULT_STOP_LOSS_PCT}%")
            st.metric("Take Profit", formatters.format_currency(take_profit), f"+{DEFAULT_TAKE_PROFIT_PCT}%")
            
            risk_reward = DEFAULT_TAKE_PROFIT_PCT / DEFAULT_STOP_LOSS_PCT
            st.metric("Risk/Reward Ratio", f"1:{risk_reward:.2f}")
        
        st.markdown("#### Signal History (Last 30 Days)")
        
        signal_history = []
        for i in range(min(30, len(df_with_indicators))):
            idx = -(i + 1)
            hist_signal = signal_generator.generate_signal(
                df_with_indicators.iloc[:idx],
                strategy=strategy_type,
                sensitivity=signal_sensitivity
            )
            
            signal_history.append({
                "Date": df_with_indicators.index[idx].strftime("%Y-%m-%d"),
                "Signal": hist_signal.get('signal', 'HOLD'),
                "Price": formatters.format_currency(df['Close'].iloc[idx]),
                "Confidence": f"{hist_signal.get('confidence', 0)}%"
            })
        
        if signal_history:
            signal_df = pd.DataFrame(signal_history[:10])
            st.dataframe(signal_df, use_container_width=True, hide_index=True)
    
    with tab2:
        st.subheader("⚠️ Risk Analysis")
        
        risk_metrics = risk_analyzer.analyze_risk(
            df_with_indicators,
            current_price,
            risk_tolerance
        )
        
        col_risk1, col_risk2, col_risk3 = st.columns(3)
        
        with col_risk1:
            st.metric("Risk Score", f"{risk_metrics.get('risk_score', 0):.1f}/10")
            st.metric("Beta", f"{risk_metrics.get('beta', 1.0):.2f}")
        
        with col_risk2:
            st.metric("Volatility", f"{risk_metrics.get('volatility', 0):.2f}%")
            st.metric("Max Drawdown", f"{risk_metrics.get('max_drawdown', 0):.2f}%")
        
        with col_risk3:
            st.metric("Sharpe Ratio", f"{risk_metrics.get('sharpe_ratio', 0):.2f}")
            st.metric("Value at Risk", formatters.format_currency(risk_metrics.get('var', 0)))
        
        st.markdown("#### Position Sizing Recommendation")
        
        portfolio_size = st.number_input(
            "Portfolio Size ($)",
            min_value=1000,
            max_value=10000000,
            value=10000,
            step=1000
        )
        
        position_size = risk_analyzer.calculate_position_size(
            portfolio_size,
            current_price,
            stop_loss,
            risk_tolerance
        )
        
        shares = int(position_size / current_price)
        position_value = shares * current_price
        position_pct = (position_value / portfolio_size) * 100
        
        col_pos1, col_pos2, col_pos3 = st.columns(3)
        
        with col_pos1:
            st.metric("Recommended Shares", shares)
        with col_pos2:
            st.metric("Position Value", formatters.format_currency(position_value))
        with col_pos3:
            st.metric("Portfolio %", f"{position_pct:.1f}%")
        
        st.info(f"💡 Risk per trade: {formatters.format_currency(position_value * DEFAULT_STOP_LOSS_PCT / 100)}")
    
    with tab3:
        st.subheader("📈 Technical Indicators")
        
        col_tech1, col_tech2 = st.columns(2)
        
        with col_tech1:
            st.markdown("#### Momentum Indicators")
            
            rsi = df_with_indicators['RSI'].iloc[-1]
            rsi_signal = "🔴 Overbought" if rsi > RSI_OVERBOUGHT else "🟢 Oversold" if rsi < RSI_OVERSOLD else "🟡 Neutral"
            st.markdown(f"**RSI (14):** {rsi:.2f} - {rsi_signal}")
            
            macd = df_with_indicators['MACD'].iloc[-1]
            macd_signal = df_with_indicators['MACD_Signal'].iloc[-1]
            macd_diff = macd - macd_signal
            macd_status = "🟢 Bullish" if macd_diff > 0 else "🔴 Bearish"
            st.markdown(f"**MACD:** {macd:.2f} - {macd_status}")
            
            st.markdown("#### Moving Averages")
            sma_20 = df_with_indicators['SMA_20'].iloc[-1]
            sma_50 = df_with_indicators['SMA_50'].iloc[-1]
            
            st.markdown(f"**SMA 20:** {formatters.format_currency(sma_20)}")
            st.markdown(f"**SMA 50:** {formatters.format_currency(sma_50)}")
            
            ma_signal = "🟢 Bullish" if sma_20 > sma_50 else "🔴 Bearish"
            st.markdown(f"**Trend:** {ma_signal}")
        
        with col_tech2:
            st.markdown("#### Volatility Indicators")
            
            bb_upper = df_with_indicators['BB_Upper'].iloc[-1]
            bb_middle = df_with_indicators['BB_Middle'].iloc[-1]
            bb_lower = df_with_indicators['BB_Lower'].iloc[-1]
            
            st.markdown(f"**BB Upper:** {formatters.format_currency(bb_upper)}")
            st.markdown(f"**BB Middle:** {formatters.format_currency(bb_middle)}")
            st.markdown(f"**BB Lower:** {formatters.format_currency(bb_lower)}")
            
            if current_price > bb_upper:
                bb_signal = "🔴 Overbought"
            elif current_price < bb_lower:
                bb_signal = "🟢 Oversold"
            else:
                bb_signal = "🟡 Normal"
            
            st.markdown(f"**Status:** {bb_signal}")
            
            st.markdown("#### Volume Analysis")
            current_volume = df['Volume'].iloc[-1]
            avg_volume_20 = df['Volume'].tail(20).mean()
            volume_ratio = current_volume / avg_volume_20
            
            st.markdown(f"**Current Volume:** {formatters.format_number(current_volume)}")
            st.markdown(f"**Avg Volume (20D):** {formatters.format_number(avg_volume_20)}")
            st.markdown(f"**Volume Ratio:** {volume_ratio:.2f}x")
        
        st.markdown("#### Technical Chart")
        fig_technical = plotly_charts.plot_technical_analysis(df_with_indicators, symbol)
        st.plotly_chart(fig_technical, use_container_width=True)
    
    with tab4:
        st.subheader("🧠 Strategy Insights")
        
        strategy_analysis = strategy_engine.analyze_strategy(
            df_with_indicators,
            strategy_type
        )
        
        st.markdown("#### Strategy Performance")
        
        col_strat1, col_strat2, col_strat3 = st.columns(3)
        
        with col_strat1:
            st.metric("Win Rate", f"{strategy_analysis.get('win_rate', 0):.1f}%")
        with col_strat2:
            st.metric("Avg Return", f"{strategy_analysis.get('avg_return', 0):.2f}%")
        with col_strat3:
            st.metric("Total Signals", strategy_analysis.get('total_signals', 0))
        
        st.markdown("#### AI Recommendation")
        
        ai_recommendation = recommendation_ai.get_recommendation(
            df_with_indicators,
            signal_data,
            risk_metrics
        )
        
        st.info(ai_recommendation.get('recommendation', 'No recommendation available'))
        
        st.markdown("#### Market Conditions")
        market_conditions = ai_recommendation.get('market_conditions', {})
        
        col_market1, col_market2 = st.columns(2)
        
        with col_market1:
            st.markdown(f"**Trend:** {market_conditions.get('trend', 'Unknown')}")
            st.markdown(f"**Volatility:** {market_conditions.get('volatility_level', 'Unknown')}")
        
        with col_market2:
            st.markdown(f"**Momentum:** {market_conditions.get('momentum', 'Unknown')}")
            st.markdown(f"**Volume:** {market_conditions.get('volume_status', 'Unknown')}")
        
        st.markdown("#### Strategy Recommendations")
        recommendations = strategy_analysis.get('recommendations', [])
        
        if recommendations:
            for rec in recommendations:
                st.markdown(f"• {rec}")
        else:
            st.info("No specific recommendations at this time")

st.divider()

col_action1, col_action2, col_action3 = st.columns(3)

with col_action1:
    if st.button("📈 View Price Forecast", use_container_width=True):
        st.switch_page("pages/2_📈_Price_Forecast.py")

with col_action2:
    if st.button("🎲 Backtest Strategy", use_container_width=True):
        st.switch_page("pages/7_🎲_Backtesting.py")

with col_action3:
    if st.button("💼 Add to Portfolio", use_container_width=True):
        st.switch_page("pages/6_💼_Portfolio_Tracker.py")

st.divider()

st.markdown("### ⚠️ Disclaimer")
st.caption("""
Trading signals are generated based on technical analysis and AI models. These signals are for informational 
purposes only and should not be considered as financial advice. Always conduct your own research and consult 
with a qualified financial advisor before making investment decisions. Past performance does not guarantee 
future results.
""")