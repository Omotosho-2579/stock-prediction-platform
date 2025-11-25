# app/pages/2_📈_Price_Forecast.py

import streamlit as st
import pandas as pd
import numpy as np
import sys
from pathlib import Path
from datetime import datetime, timedelta

sys.path.append(str(Path(__file__).parent.parent.parent))

from app.config import POPULAR_STOCKS, MODEL_TYPES, DEFAULT_PERIOD
from src.data.data_loader import DataLoader
from src.data.technical_indicators import TechnicalIndicators
from src.models.model_loader import ModelLoader
from src.models.model_evaluator import ModelEvaluator
from src.visualization.plotly_charts import PlotlyCharts
from src.visualization.candlestick_charts import CandlestickCharts
from src.visualization.forecast_visualizer import ForecastVisualizer
from src.utils.formatters import Formatters
from src.utils.validators import Validators

st.set_page_config(page_title="Price Forecast", page_icon="📈", layout="wide")

st.title("📈 Stock Price Forecast")
st.markdown("AI-powered price predictions with advanced machine learning models")

if 'selected_ticker' not in st.session_state:
    st.session_state.selected_ticker = POPULAR_STOCKS[0] if POPULAR_STOCKS else 'AAPL'

data_loader = DataLoader()
tech_indicators = TechnicalIndicators()
model_loader = ModelLoader()
model_evaluator = ModelEvaluator()
plotly_charts = PlotlyCharts()
candlestick_charts = CandlestickCharts()
forecast_visualizer = ForecastVisualizer()
formatters = Formatters()
validators = Validators()

col1, col2, col3 = st.columns([2, 1, 1])

with col1:
    symbol = st.text_input(
        "Stock Symbol",
        value=st.session_state.selected_ticker,
        help="Enter any valid stock ticker (e.g., AAPL, TSLA, GOOGL)"
    ).upper()
    st.session_state.selected_ticker = symbol

with col2:
    period = st.selectbox(
        "Historical Period",
        options=["1y", "2y", "3y", "5y"],
        index=1
    )

with col3:
    forecast_days = st.selectbox(
        "Forecast Period",
        options=[7, 14, 30, 60, 90],
        format_func=lambda x: f"{x} days",
        index=2
    )

if not validators.validate_ticker(symbol):
    st.warning("Please enter a valid stock ticker symbol")
    st.stop()

col_model1, col_model2 = st.columns([2, 1])

with col_model1:
    selected_models = st.multiselect(
        "Select Models",
        options=['LSTM', 'XGBoost', 'Random Forest', 'Linear Regression', 'Ensemble'],
        default=['Ensemble'],
        help="Choose one or more models for prediction"
    )

with col_model2:
    confidence_level = st.slider(
        "Confidence Level",
        min_value=80,
        max_value=99,
        value=95,
        help="Confidence interval for predictions"
    )

if st.button("🚀 Generate Forecast", type="primary"):
    if not selected_models:
        st.error("Please select at least one model")
        st.stop()
    
    with st.spinner(f"Loading data for {symbol}..."):
        df = data_loader.load_stock_data(symbol, period=period)
        
        if df is None or df.empty:
            st.error(f"Failed to load data for {symbol}. Please check the ticker symbol.")
            st.stop()
        
        st.success(f"Successfully loaded {len(df)} days of historical data")
    
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
        high_52w = df['High'].tail(252).max()
        st.metric("52W High", formatters.format_currency(high_52w))
    
    with col_info3:
        low_52w = df['Low'].tail(252).min()
        st.metric("52W Low", formatters.format_currency(low_52w))
    
    with col_info4:
        avg_volume = df['Volume'].tail(30).mean()
        st.metric("Avg Volume (30D)", formatters.format_number(avg_volume))
    
    st.divider()
    
    tab1, tab2, tab3, tab4 = st.tabs(["Predictions", "Historical Data", "Technical Analysis", "Model Performance"])
    
    with tab1:
        st.subheader("📊 Price Predictions")
        
        predictions_data = {}
        
        for model_name in selected_models:
            with st.spinner(f"Training {model_name} model..."):
                try:
                    model_type = model_name.lower().replace(' ', '_')
                    
                    predictions = model_loader.predict(
                        df=df,
                        symbol=symbol,
                        model_type=model_type,
                        forecast_days=forecast_days
                    )
                    
                    if predictions is not None and len(predictions) > 0:
                        predictions_data[model_name] = predictions
                        
                        last_prediction = predictions[-1]
                        prediction_change = ((last_prediction - current_price) / current_price) * 100
                        
                        st.success(f"**{model_name}** - {forecast_days}D Forecast: {formatters.format_currency(last_prediction)} ({prediction_change:+.2f}%)")
                    else:
                        st.warning(f"Could not generate predictions for {model_name}")
                
                except Exception as e:
                    st.error(f"Error with {model_name}: {str(e)}")
        
        if predictions_data:
            st.markdown("#### Forecast Visualization")
            
            fig_forecast = forecast_visualizer.plot_forecast(
                historical_data=df,
                predictions=predictions_data,
                forecast_days=forecast_days,
                symbol=symbol,
                confidence_level=confidence_level
            )
            st.plotly_chart(fig_forecast, use_container_width=True)
            
            st.markdown("#### Prediction Summary")
            
            summary_data = []
            for model_name, preds in predictions_data.items():
                min_pred = np.min(preds)
                max_pred = np.max(preds)
                avg_pred = np.mean(preds)
                final_pred = preds[-1]
                
                summary_data.append({
                    "Model": model_name,
                    "Final Prediction": formatters.format_currency(final_pred),
                    "Average": formatters.format_currency(avg_pred),
                    "Min": formatters.format_currency(min_pred),
                    "Max": formatters.format_currency(max_pred),
                    "Change (%)": f"{((final_pred - current_price) / current_price * 100):+.2f}%"
                })
            
            summary_df = pd.DataFrame(summary_data)
            st.dataframe(summary_df, use_container_width=True, hide_index=True)
            
            if len(predictions_data) > 1:
                st.markdown("#### Ensemble Forecast")
                all_predictions = np.array(list(predictions_data.values()))
                ensemble_pred = np.mean(all_predictions, axis=0)
                
                ensemble_final = ensemble_pred[-1]
                ensemble_change = ((ensemble_final - current_price) / current_price) * 100
                
                col_ens1, col_ens2, col_ens3 = st.columns(3)
                
                with col_ens1:
                    st.metric("Ensemble Prediction", formatters.format_currency(ensemble_final))
                with col_ens2:
                    st.metric("Expected Change", f"{ensemble_change:+.2f}%")
                with col_ens3:
                    direction = "🟢 Bullish" if ensemble_change > 0 else "🔴 Bearish"
                    st.metric("Signal", direction)
        else:
            st.error("Failed to generate predictions. Please try again.")
    
    with tab2:
        st.subheader("📉 Historical Price Data")
        
        chart_type = st.radio(
            "Chart Type",
            options=["Candlestick", "Line", "Area"],
            horizontal=True
        )
        
        if chart_type == "Candlestick":
            fig_candle = candlestick_charts.plot_candlestick(df, symbol)
            st.plotly_chart(fig_candle, use_container_width=True)
        elif chart_type == "Line":
            fig_line = plotly_charts.plot_line_chart(
                df.reset_index(),
                x_col='Date',
                y_col='Close',
                title=f"{symbol} Price History"
            )
            st.plotly_chart(fig_line, use_container_width=True)
        else:
            fig_area = plotly_charts.plot_area_chart(
                df.reset_index(),
                x_col='Date',
                y_col='Close',
                title=f"{symbol} Price History"
            )
            st.plotly_chart(fig_area, use_container_width=True)
        
        st.markdown("#### Volume Analysis")
        fig_volume = plotly_charts.plot_bar_chart(
            df.reset_index().tail(60),
            x_col='Date',
            y_col='Volume',
            title=f"{symbol} Trading Volume (Last 60 Days)"
        )
        st.plotly_chart(fig_volume, use_container_width=True)
        
        st.markdown("#### Raw Data")
        with st.expander("View Historical Data"):
            st.dataframe(
                df.tail(100).reset_index(),
                use_container_width=True,
                hide_index=True
            )
    
    with tab3:
        st.subheader("🔍 Technical Analysis")
        
        df_with_indicators = tech_indicators.add_all_indicators(df)
        
        col_tech1, col_tech2, col_tech3, col_tech4 = st.columns(4)
        
        with col_tech1:
            rsi = df_with_indicators['RSI'].iloc[-1]
            rsi_signal = "Oversold" if rsi < 30 else "Overbought" if rsi > 70 else "Neutral"
            st.metric("RSI (14)", f"{rsi:.2f}", rsi_signal)
        
        with col_tech2:
            macd = df_with_indicators['MACD'].iloc[-1]
            st.metric("MACD", f"{macd:.2f}")
        
        with col_tech3:
            sma_20 = df_with_indicators['SMA_20'].iloc[-1]
            st.metric("SMA (20)", formatters.format_currency(sma_20))
        
        with col_tech4:
            sma_50 = df_with_indicators['SMA_50'].iloc[-1]
            st.metric("SMA (50)", formatters.format_currency(sma_50))
        
        st.markdown("#### Moving Averages")
        fig_ma = plotly_charts.plot_moving_averages(df_with_indicators, symbol)
        st.plotly_chart(fig_ma, use_container_width=True)
        
        st.markdown("#### RSI Indicator")
        fig_rsi = plotly_charts.plot_rsi(df_with_indicators, symbol)
        st.plotly_chart(fig_rsi, use_container_width=True)
        
        st.markdown("#### MACD Indicator")
        fig_macd = plotly_charts.plot_macd(df_with_indicators, symbol)
        st.plotly_chart(fig_macd, use_container_width=True)
    
    with tab4:
        st.subheader("📊 Model Performance Metrics")
        
        if predictions_data:
            for model_name in predictions_data.keys():
                with st.expander(f"{model_name} Performance", expanded=True):
                    try:
                        model_type = model_name.lower().replace(' ', '_')
                        
                        metrics = model_evaluator.evaluate_model(
                            df=df,
                            model_type=model_type,
                            symbol=symbol
                        )
                        
                        if metrics:
                            col_m1, col_m2, col_m3, col_m4 = st.columns(4)
                            
                            with col_m1:
                                st.metric("R² Score", f"{metrics.get('r2_score', 0):.4f}")
                            with col_m2:
                                st.metric("RMSE", f"{metrics.get('rmse', 0):.4f}")
                            with col_m3:
                                st.metric("MAE", f"{metrics.get('mae', 0):.4f}")
                            with col_m4:
                                st.metric("MAPE", f"{metrics.get('mape', 0):.2f}%")
                            
                            accuracy_pct = metrics.get('r2_score', 0) * 100
                            if accuracy_pct >= 70:
                                st.success(f"✅ High accuracy model ({accuracy_pct:.1f}%)")
                            elif accuracy_pct >= 50:
                                st.info(f"ℹ️ Moderate accuracy model ({accuracy_pct:.1f}%)")
                            else:
                                st.warning(f"⚠️ Low accuracy model ({accuracy_pct:.1f}%)")
                        else:
                            st.info("Model metrics not available")
                    
                    except Exception as e:
                        st.error(f"Could not load metrics: {str(e)}")
        else:
            st.info("Generate predictions first to view model performance")

st.divider()

col_action1, col_action2, col_action3 = st.columns(3)

with col_action1:
    if st.button("➕ Add to Watchlist", use_container_width=True):
        if 'watchlist' not in st.session_state:
            st.session_state.watchlist = []
        
        if symbol not in st.session_state.watchlist:
            st.session_state.watchlist.append(symbol)
            st.success(f"Added {symbol} to watchlist")
        else:
            st.info(f"{symbol} already in watchlist")

with col_action2:
    if st.button("🎯 View Trading Signals", use_container_width=True):
        st.switch_page("pages/3_🎯_Trading_Signals.py")

with col_action3:
    if st.button("🔍 Compare Stocks", use_container_width=True):
        st.switch_page("pages/5_🔍_Stock_Comparison.py")