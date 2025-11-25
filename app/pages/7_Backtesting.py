# app/pages/7_🎲_Backtesting.py

import streamlit as st
import pandas as pd
import sys
from pathlib import Path
from datetime import datetime, timedelta

sys.path.append(str(Path(__file__).parent.parent.parent))

from app.config import ENABLE_BACKTESTING, POPULAR_STOCKS, TRADING_STRATEGIES
from src.portfolio.backtesting_engine import BacktestingEngine
from src.trading_signals.strategy_engine import StrategyEngine
from src.data.data_loader import DataLoader
from src.visualization.plotly_charts import PlotlyCharts
from src.utils.formatters import Formatters

st.set_page_config(page_title="Backtesting", page_icon="🎲", layout="wide")

st.title("🎲 Strategy Backtesting")
st.markdown("Test your trading strategies on historical data")

if not ENABLE_BACKTESTING:
    st.warning("⚠️ Backtesting feature is currently disabled. Check configuration settings.")
    st.stop()

backtesting_engine = BacktestingEngine()
strategy_engine = StrategyEngine()
data_loader = DataLoader()
plotly_charts = PlotlyCharts()
formatters = Formatters()

col1, col2 = st.columns(2)

with col1:
    symbol = st.text_input("Stock Symbol", value=POPULAR_STOCKS[0] if POPULAR_STOCKS else "AAPL").upper()

with col2:
    period = st.selectbox(
        "Backtest Period",
        options=["1y", "2y", "3y", "5y"],
        index=1
    )

st.subheader("Strategy Configuration")

strategy_options = [
    "Moving Average Crossover",
    "RSI Strategy",
    "MACD Strategy",
    "Bollinger Bands",
    "Combined Strategy"
]

strategy_type = st.selectbox(
    "Select Strategy",
    options=strategy_options
)

col_params1, col_params2, col_params3 = st.columns(3)

with col_params1:
    initial_capital = st.number_input(
        "Initial Capital ($)",
        min_value=1000,
        max_value=1000000,
        value=10000,
        step=1000
    )

with col_params2:
    position_size = st.slider(
        "Position Size (%)",
        min_value=10,
        max_value=100,
        value=100,
        step=10
    )

with col_params3:
    commission = st.number_input(
        "Commission per Trade ($)",
        min_value=0.0,
        max_value=100.0,
        value=1.0,
        step=0.5
    )

if strategy_type == "Moving Average Crossover":
    col_ma1, col_ma2 = st.columns(2)
    with col_ma1:
        short_window = st.number_input("Short MA Period", min_value=5, max_value=50, value=20)
    with col_ma2:
        long_window = st.number_input("Long MA Period", min_value=20, max_value=200, value=50)
    
    strategy_params = {
        "type": "ma_crossover",
        "short_window": short_window,
        "long_window": long_window
    }

elif strategy_type == "RSI Strategy":
    col_rsi1, col_rsi2, col_rsi3 = st.columns(3)
    with col_rsi1:
        rsi_period = st.number_input("RSI Period", min_value=5, max_value=30, value=14)
    with col_rsi2:
        rsi_oversold = st.number_input("Oversold Level", min_value=10, max_value=40, value=30)
    with col_rsi3:
        rsi_overbought = st.number_input("Overbought Level", min_value=60, max_value=90, value=70)
    
    strategy_params = {
        "type": "rsi",
        "period": rsi_period,
        "oversold": rsi_oversold,
        "overbought": rsi_overbought
    }

elif strategy_type == "MACD Strategy":
    col_macd1, col_macd2, col_macd3 = st.columns(3)
    with col_macd1:
        fast_period = st.number_input("Fast Period", min_value=5, max_value=20, value=12)
    with col_macd2:
        slow_period = st.number_input("Slow Period", min_value=15, max_value=40, value=26)
    with col_macd3:
        signal_period = st.number_input("Signal Period", min_value=5, max_value=15, value=9)
    
    strategy_params = {
        "type": "macd",
        "fast_period": fast_period,
        "slow_period": slow_period,
        "signal_period": signal_period
    }

elif strategy_type == "Bollinger Bands":
    col_bb1, col_bb2 = st.columns(2)
    with col_bb1:
        bb_period = st.number_input("Period", min_value=10, max_value=50, value=20)
    with col_bb2:
        bb_std = st.number_input("Standard Deviations", min_value=1.0, max_value=3.0, value=2.0, step=0.1)
    
    strategy_params = {
        "type": "bollinger",
        "period": bb_period,
        "std_dev": bb_std
    }

else:
    strategy_params = {
        "type": "combined"
    }

if st.button("Run Backtest", type="primary"):
    with st.spinner("Running backtest..."):
        try:
            df = data_loader.load_stock_data(symbol, period=period)
            
            if df is None or df.empty:
                st.error(f"Failed to load data for {symbol}")
                st.stop()
            
            backtest_config = {
                "initial_capital": initial_capital,
                "position_size": position_size / 100,
                "commission": commission
            }
            
            results = backtesting_engine.run_backtest(
                df,
                strategy_params,
                backtest_config
            )
            
            st.success("Backtest completed successfully!")
            
            col_metric1, col_metric2, col_metric3, col_metric4 = st.columns(4)
            
            with col_metric1:
                st.metric(
                    "Final Portfolio Value",
                    formatters.format_currency(results['final_value'])
                )
            
            with col_metric2:
                total_return = ((results['final_value'] - initial_capital) / initial_capital) * 100
                st.metric(
                    "Total Return",
                    f"{total_return:.2f}%"
                )
            
            with col_metric3:
                st.metric(
                    "Total Trades",
                    results['total_trades']
                )
            
            with col_metric4:
                win_rate = (results['winning_trades'] / results['total_trades'] * 100) if results['total_trades'] > 0 else 0
                st.metric(
                    "Win Rate",
                    f"{win_rate:.2f}%"
                )
            
            tab1, tab2, tab3 = st.tabs(["Portfolio Value", "Trade History", "Statistics"])
            
            with tab1:
                st.subheader("Portfolio Value Over Time")
                fig_portfolio = plotly_charts.plot_line_chart(
                    results['portfolio_history'],
                    x_col='Date',
                    y_col='Portfolio Value',
                    title=f"{symbol} Backtest Results"
                )
                st.plotly_chart(fig_portfolio, use_container_width=True)
                
                fig_comparison = backtesting_engine.plot_strategy_vs_buy_hold(
                    results['portfolio_history'],
                    df
                )
                st.plotly_chart(fig_comparison, use_container_width=True)
            
            with tab2:
                st.subheader("Trade History")
                trades_df = pd.DataFrame(results['trades'])
                if not trades_df.empty:
                    st.dataframe(trades_df, use_container_width=True)
                else:
                    st.info("No trades executed during backtest period")
            
            with tab3:
                st.subheader("Performance Statistics")
                
                col_stat1, col_stat2 = st.columns(2)
                
                with col_stat1:
                    st.metric("Winning Trades", results['winning_trades'])
                    st.metric("Losing Trades", results['losing_trades'])
                    st.metric("Average Win", formatters.format_currency(results['avg_win']))
                
                with col_stat2:
                    st.metric("Average Loss", formatters.format_currency(results['avg_loss']))
                    st.metric("Largest Win", formatters.format_currency(results['largest_win']))
                    st.metric("Largest Loss", formatters.format_currency(results['largest_loss']))
                
                st.subheader("Risk Metrics")
                col_risk1, col_risk2, col_risk3 = st.columns(3)
                
                with col_risk1:
                    st.metric("Sharpe Ratio", f"{results['sharpe_ratio']:.2f}")
                with col_risk2:
                    st.metric("Max Drawdown", f"{results['max_drawdown']:.2f}%")
                with col_risk3:
                    st.metric("Volatility", f"{results['volatility']:.2f}%")
        
        except Exception as e:
            st.error(f"Error running backtest: {str(e)}")