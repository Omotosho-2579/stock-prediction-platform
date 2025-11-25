# app/pages/9_₿_Crypto_Trading.py

import streamlit as st
import pandas as pd
import sys
from pathlib import Path
from datetime import datetime

sys.path.append(str(Path(__file__).parent.parent.parent))

from app.config import ENABLE_CRYPTO_TRADING, POPULAR_STOCKS
from src.data.crypto_loader import CryptoLoader
from src.data.technical_indicators import TechnicalIndicators
from src.models.model_loader import ModelLoader
from src.trading_signals.signal_generator import SignalGenerator
from src.visualization.plotly_charts import PlotlyCharts
from src.visualization.candlestick_charts import CandlestickCharts
from src.utils.formatters import Formatters

st.set_page_config(page_title="Crypto Trading", page_icon="₿", layout="wide")

st.title("₿ Cryptocurrency Trading")
st.markdown("Trade and analyze cryptocurrencies with AI-powered insights")

if not ENABLE_CRYPTO_TRADING:
    st.error("⚠️ Cryptocurrency trading is disabled in configuration.")
    st.info("Enable crypto trading in Settings to access this feature.")
    st.stop()

crypto_loader = CryptoLoader()
tech_indicators = TechnicalIndicators()
model_loader = ModelLoader()
signal_generator = SignalGenerator()
plotly_charts = PlotlyCharts()
candlestick_charts = CandlestickCharts()
formatters = Formatters()

st.sidebar.header("Crypto Selection")

available_cryptos = crypto_loader.get_available_cryptos()

selected_crypto = st.sidebar.selectbox(
    "Select Cryptocurrency",
    options=available_cryptos,
    index=0
)

period = st.sidebar.selectbox(
    "Time Period",
    options=["1d", "5d", "1mo", "3mo", "6mo", "1y", "2y"],
    index=4
)

interval = st.sidebar.selectbox(
    "Interval",
    options=["1h", "1d", "1wk"],
    index=1,
    format_func=lambda x: {"1h": "Hourly", "1d": "Daily", "1wk": "Weekly"}[x]
)

if st.sidebar.button("🔄 Refresh Data", use_container_width=True):
    st.cache_data.clear()
    st.rerun()

st.divider()

with st.spinner(f"Loading {selected_crypto} data..."):
    df = crypto_loader.load_crypto_data(selected_crypto, period=period, interval=interval)
    crypto_info = crypto_loader.get_crypto_info(selected_crypto)

if df is None or df.empty:
    st.error(f"Failed to load data for {selected_crypto}")
    st.stop()

current_price = df['Close'].iloc[-1]
prev_price = df['Close'].iloc[-2] if len(df) > 1 else current_price
price_change = ((current_price - prev_price) / prev_price) * 100
price_change_24h = ((df['Close'].iloc[-1] - df['Close'].iloc[-24]) / df['Close'].iloc[-24]) * 100 if len(df) >= 24 else price_change

col1, col2, col3, col4, col5 = st.columns(5)

with col1:
    st.metric(
        f"{crypto_info.get('name', selected_crypto)}",
        formatters.format_currency(current_price),
        f"{price_change:.2f}%"
    )

with col2:
    market_cap = crypto_info.get('market_cap', 0)
    st.metric(
        "Market Cap",
        formatters.format_currency(market_cap) if market_cap > 0 else "N/A"
    )

with col3:
    volume_24h = df['Volume'].iloc[-1] if len(df) > 0 else 0
    st.metric(
        "24h Volume",
        formatters.format_number(volume_24h)
    )

with col4:
    ath = crypto_info.get('all_time_high', 0)
    st.metric(
        "All-Time High",
        formatters.format_currency(ath) if ath > 0 else "N/A"
    )

with col5:
    atl = crypto_info.get('all_time_low', 0)
    st.metric(
        "All-Time Low",
        formatters.format_currency(atl) if atl > 0 else "N/A"
    )

st.divider()

tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "📊 Price Chart",
    "📈 Price Prediction",
    "🎯 Trading Signals",
    "🔍 Technical Analysis",
    "🌍 Market Overview"
])

with tab1:
    st.subheader(f"{selected_crypto} Price Chart")
    
    chart_type = st.radio(
        "Chart Type",
        options=["Candlestick", "Line", "Area"],
        horizontal=True
    )
    
    if chart_type == "Candlestick":
        fig = candlestick_charts.plot_candlestick(df, selected_crypto)
        st.plotly_chart(fig, use_container_width=True)
    elif chart_type == "Line":
        fig = plotly_charts.plot_line_chart(
            df.reset_index(),
            x_col='Date',
            y_col='Close',
            title=f"{selected_crypto} Price"
        )
        st.plotly_chart(fig, use_container_width=True)
    else:
        fig = plotly_charts.plot_area_chart(
            df.reset_index(),
            x_col='Date',
            y_col='Close',
            title=f"{selected_crypto} Price"
        )
        st.plotly_chart(fig, use_container_width=True)
    
    st.subheader("Volume Analysis")
    fig_volume = plotly_charts.plot_bar_chart(
        df.reset_index().tail(60),
        x_col='Date',
        y_col='Volume',
        title=f"{selected_crypto} Trading Volume"
    )
    st.plotly_chart(fig_volume, use_container_width=True)
    
    with st.expander("📊 View Historical Data"):
        display_df = df.tail(100).reset_index()
        display_df['Date'] = display_df['Date'].dt.strftime('%Y-%m-%d %H:%M')
        st.dataframe(display_df, use_container_width=True, hide_index=True)

with tab2:
    st.subheader(f"🔮 {selected_crypto} Price Prediction")
    
    col_pred1, col_pred2 = st.columns(2)
    
    with col_pred1:
        forecast_days = st.selectbox(
            "Forecast Period",
            options=[7, 14, 30, 60, 90],
            format_func=lambda x: f"{x} days",
            index=2
        )
    
    with col_pred2:
        model_type = st.selectbox(
            "Model",
            options=["Ensemble", "XGBoost", "Random Forest", "LSTM"],
            index=0
        )
    
    if st.button("🚀 Generate Prediction", type="primary"):
        with st.spinner(f"Generating {forecast_days}-day forecast..."):
            try:
                model_type_key = model_type.lower().replace(' ', '_')
                
                predictions = model_loader.predict(
                    df=df,
                    symbol=selected_crypto,
                    model_type=model_type_key,
                    forecast_days=forecast_days
                )
                
                if predictions is not None and len(predictions) > 0:
                    final_prediction = predictions[-1]
                    prediction_change = ((final_prediction - current_price) / current_price) * 100
                    
                    col_p1, col_p2, col_p3 = st.columns(3)
                    
                    with col_p1:
                        st.metric(
                            f"{forecast_days}-Day Prediction",
                            formatters.format_currency(final_prediction),
                            f"{prediction_change:+.2f}%"
                        )
                    
                    with col_p2:
                        avg_prediction = predictions.mean()
                        st.metric("Average Forecast", formatters.format_currency(avg_prediction))
                    
                    with col_p3:
                        direction = "🟢 Bullish" if prediction_change > 0 else "🔴 Bearish"
                        st.metric("Outlook", direction)
                    
                    from src.visualization.forecast_visualizer import ForecastVisualizer
                    forecast_viz = ForecastVisualizer()
                    
                    fig_forecast = forecast_viz.plot_forecast(
                        historical_data=df,
                        predictions={model_type: predictions},
                        forecast_days=forecast_days,
                        symbol=selected_crypto,
                        confidence_level=95
                    )
                    st.plotly_chart(fig_forecast, use_container_width=True)
                else:
                    st.error("Failed to generate predictions")
            
            except Exception as e:
                st.error(f"Error generating predictions: {str(e)}")

with tab3:
    st.subheader(f"🎯 Trading Signals for {selected_crypto}")
    
    df_with_indicators = tech_indicators.add_all_indicators(df)
    
    signal_data = signal_generator.generate_signal(
        df_with_indicators,
        strategy="AI Composite",
        sensitivity="Moderate"
    )
    
    signal = signal_data.get('signal', 'HOLD')
    confidence = signal_data.get('confidence', 0)
    signal_strength = signal_data.get('strength', 0)
    
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
        <div style="background-color: {signal_bg}; padding: 20px; border-radius: 10px; text-align: center; margin-bottom: 20px;">
            <h2>{signal_color} {signal} SIGNAL</h2>
            <p style="font-size: 18px;">Confidence: {confidence}% | Strength: {signal_strength}/10</p>
        </div>
        """,
        unsafe_allow_html=True
    )
    
    col_sig1, col_sig2 = st.columns(2)
    
    with col_sig1:
        st.markdown("#### Signal Details")
        reasons = signal_data.get('reasons', [])
        if reasons:
            for reason in reasons:
                st.markdown(f"• {reason}")
        else:
            st.info("No specific reasons available")
    
    with col_sig2:
        st.markdown("#### Technical Indicators")
        
        rsi = df_with_indicators['RSI'].iloc[-1]
        macd = df_with_indicators['MACD'].iloc[-1]
        macd_signal = df_with_indicators['MACD_Signal'].iloc[-1]
        
        st.markdown(f"**RSI (14):** {rsi:.2f}")
        rsi_status = "Oversold" if rsi < 30 else "Overbought" if rsi > 70 else "Neutral"
        st.caption(f"Status: {rsi_status}")
        
        st.markdown(f"**MACD:** {macd:.2f}")
        macd_status = "Bullish" if macd > macd_signal else "Bearish"
        st.caption(f"Status: {macd_status}")

with tab4:
    st.subheader(f"🔍 Technical Analysis - {selected_crypto}")
    
    col_tech1, col_tech2, col_tech3, col_tech4 = st.columns(4)
    
    with col_tech1:
        rsi = df_with_indicators['RSI'].iloc[-1]
        st.metric("RSI (14)", f"{rsi:.2f}")
    
    with col_tech2:
        sma_20 = df_with_indicators['SMA_20'].iloc[-1]
        st.metric("SMA (20)", formatters.format_currency(sma_20))
    
    with col_tech3:
        sma_50 = df_with_indicators['SMA_50'].iloc[-1]
        st.metric("SMA (50)", formatters.format_currency(sma_50))
    
    with col_tech4:
        bb_position = df_with_indicators['BB_Position'].iloc[-1]
        st.metric("BB Position", f"{bb_position:.2f}")
    
    st.markdown("#### Moving Averages")
    fig_ma = plotly_charts.plot_moving_averages(df_with_indicators, selected_crypto)
    st.plotly_chart(fig_ma, use_container_width=True)
    
    col_ind1, col_ind2 = st.columns(2)
    
    with col_ind1:
        st.markdown("#### RSI Indicator")
        fig_rsi = plotly_charts.plot_rsi(df_with_indicators, selected_crypto)
        st.plotly_chart(fig_rsi, use_container_width=True)
    
    with col_ind2:
        st.markdown("#### MACD Indicator")
        fig_macd = plotly_charts.plot_macd(df_with_indicators, selected_crypto)
        st.plotly_chart(fig_macd, use_container_width=True)
    
    signal_summary = tech_indicators.get_signal_summary(df_with_indicators)
    
    st.markdown("#### Technical Summary")
    summary_df = pd.DataFrame([signal_summary])
    st.dataframe(summary_df, use_container_width=True, hide_index=True)

with tab5:
    st.subheader("🌍 Cryptocurrency Market Overview")
    
    with st.spinner("Loading market data..."):
        market_overview = crypto_loader.get_crypto_market_overview()
        dominance = crypto_loader.get_crypto_dominance()
    
    if dominance:
        col_dom1, col_dom2, col_dom3 = st.columns(3)
        
        with col_dom1:
            st.metric(
                "BTC Dominance",
                f"{dominance.get('btc_dominance', 0):.2f}%"
            )
        
        with col_dom2:
            st.metric(
                "ETH Dominance",
                f"{dominance.get('eth_dominance', 0):.2f}%"
            )
        
        with col_dom3:
            total_cap = dominance.get('total_market_cap', 0)
            st.metric(
                "Total Market Cap",
                formatters.format_currency(total_cap)
            )
    
    if market_overview:
        st.markdown("#### Top Cryptocurrencies")
        
        overview_data = []
        for crypto in market_overview:
            overview_data.append({
                "Symbol": crypto['symbol'],
                "Name": crypto['name'],
                "Price": formatters.format_currency(crypto['price']),
                "24h Change": f"{crypto['change_24h']:+.2f}%",
                "Market Cap": formatters.format_currency(crypto['market_cap']),
                "24h Volume": formatters.format_number(crypto['volume_24h'])
            })
        
        overview_df = pd.DataFrame(overview_data)
        st.dataframe(overview_df, use_container_width=True, hide_index=True)
    else:
        st.info("Market overview data not available")
    
    st.markdown("#### Compare Cryptocurrencies")
    
    compare_cryptos = st.multiselect(
        "Select cryptocurrencies to compare",
        options=available_cryptos,
        default=available_cryptos[:3]
    )
    
    if len(compare_cryptos) >= 2:
        if st.button("Compare Selected", type="primary"):
            with st.spinner("Loading comparison data..."):
                comparison_data = crypto_loader.get_multiple_cryptos(
                    compare_cryptos,
                    period=period
                )
                
                if comparison_data:
                    from src.visualization.comparison_plots import ComparisonPlots
                    comparison_plots = ComparisonPlots()
                    
                    fig_compare = comparison_plots.plot_normalized_prices(comparison_data)
                    st.plotly_chart(fig_compare, use_container_width=True)
                    
                    compare_summary = []
                    for symbol, data in comparison_data.items():
                        current = data['Close'].iloc[-1]
                        start = data['Close'].iloc[0]
                        change = ((current - start) / start) * 100
                        
                        compare_summary.append({
                            "Crypto": symbol,
                            "Current Price": formatters.format_currency(current),
                            "Period Change": f"{change:+.2f}%",
                            "High": formatters.format_currency(data['High'].max()),
                            "Low": formatters.format_currency(data['Low'].min())
                        })
                    
                    summary_df = pd.DataFrame(compare_summary)
                    st.dataframe(summary_df, use_container_width=True, hide_index=True)

st.divider()

col_action1, col_action2, col_action3 = st.columns(3)

with col_action1:
    if st.button("➕ Add to Watchlist", use_container_width=True):
        if 'watchlist' not in st.session_state:
            st.session_state.watchlist = []
        
        crypto_symbol = f"{selected_crypto}-USD" if '-' not in selected_crypto else selected_crypto
        
        if crypto_symbol not in st.session_state.watchlist:
            st.session_state.watchlist.append(crypto_symbol)
            st.success(f"Added {selected_crypto} to watchlist")
        else:
            st.info(f"{selected_crypto} already in watchlist")

with col_action2:
    if st.button("🏠 Back to Dashboard", use_container_width=True):
        st.switch_page("pages/1_🏠_Dashboard.py")

with col_action3:
    if st.button("🔍 Compare Stocks", use_container_width=True):
        st.switch_page("pages/5_🔍_Stock_Comparison.py")

st.divider()

st.markdown("### ⚠️ Disclaimer")
st.caption("""
Cryptocurrency markets are highly volatile and risky. The predictions and signals provided are for informational 
purposes only and should not be considered as financial advice. Always conduct your own research and consult 
with a qualified financial advisor before making investment decisions. Past performance does not guarantee future results.
""")