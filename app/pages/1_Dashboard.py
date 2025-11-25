# app/pages/1_🏠_Dashboard.py

import streamlit as st
import pandas as pd
import sys
from pathlib import Path
from datetime import datetime, timedelta

sys.path.append(str(Path(__file__).parent.parent.parent))

from app.config import (
    POPULAR_STOCKS, STOCK_CATEGORIES, is_market_open,
    ENABLE_SENTIMENT_ANALYSIS, APP_NAME
)
from src.data.data_loader import DataLoader
from src.data.technical_indicators import TechnicalIndicators
from src.visualization.plotly_charts import PlotlyCharts
from src.utils.formatters import Formatters
from src.alerts.alert_manager import AlertManager

st.set_page_config(page_title="Dashboard", page_icon="🏠", layout="wide")

st.title("🏠 Dashboard")
st.markdown("### Market overview and portfolio summary")

if 'watchlist' not in st.session_state:
    st.session_state.watchlist = []
if 'alerts' not in st.session_state:
    st.session_state.alerts = []
if 'portfolio' not in st.session_state:
    st.session_state.portfolio = []

data_loader = DataLoader()
tech_indicators = TechnicalIndicators()
plotly_charts = PlotlyCharts()
formatters = Formatters()
alert_manager = AlertManager()

market_status = "🟢 OPEN" if is_market_open() else "🔴 CLOSED"
st.markdown(f"**Market Status:** {market_status}")

st.divider()

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric(
        label="📊 Watchlist",
        value=len(st.session_state.watchlist),
        delta="stocks"
    )

with col2:
    st.metric(
        label="💼 Portfolio",
        value=len(st.session_state.portfolio),
        delta="positions"
    )

with col3:
    st.metric(
        label="🔔 Active Alerts",
        value=len(st.session_state.alerts),
        delta="monitoring"
    )

with col4:
    st.metric(
        label="📈 Popular Stocks",
        value=len(POPULAR_STOCKS),
        delta="available"
    )

st.divider()

tab1, tab2, tab3, tab4 = st.tabs(["Market Overview", "Watchlist", "Alerts", "Quick Actions"])

with tab1:
    st.subheader("📊 Market Overview")
    
    col_market1, col_market2 = st.columns(2)
    
    with col_market1:
        st.markdown("#### Major Indices")
        
        indices = {
            "S&P 500": "^GSPC",
            "Dow Jones": "^DJI",
            "NASDAQ": "^IXIC"
        }
        
        index_data = []
        for name, symbol in indices.items():
            try:
                df = data_loader.load_stock_data(symbol, period="5d")
                if df is not None and not df.empty:
                    current = df['Close'].iloc[-1]
                    prev = df['Close'].iloc[-2]
                    change = ((current - prev) / prev) * 100
                    
                    index_data.append({
                        "Index": name,
                        "Price": formatters.format_number(current),
                        "Change (%)": f"{change:.2f}%"
                    })
            except Exception as e:
                st.error(f"Error loading {name}: {str(e)}")
        
        if index_data:
            index_df = pd.DataFrame(index_data)
            st.dataframe(index_df, use_container_width=True, hide_index=True)
    
    with col_market2:
        st.markdown("#### Sector Performance")
        
        sectors = {
            "Technology": "XLK",
            "Healthcare": "XLV",
            "Finance": "XLF",
            "Energy": "XLE",
            "Consumer": "XLP"
        }
        
        sector_data = []
        for name, symbol in sectors.items():
            try:
                df = data_loader.load_stock_data(symbol, period="5d")
                if df is not None and not df.empty:
                    current = df['Close'].iloc[-1]
                    prev = df['Close'].iloc[-2]
                    change = ((current - prev) / prev) * 100
                    
                    sector_data.append({
                        "Sector": name,
                        "ETF": symbol,
                        "Change (%)": f"{change:.2f}%"
                    })
            except Exception as e:
                pass
        
        if sector_data:
            sector_df = pd.DataFrame(sector_data)
            st.dataframe(sector_df, use_container_width=True, hide_index=True)
    
    st.markdown("#### Top Movers")
    
    col_gain, col_loss = st.columns(2)
    
    with col_gain:
        st.markdown("**🔥 Top Gainers**")
        
        gainers = []
        for symbol in POPULAR_STOCKS[:10]:
            try:
                df = data_loader.load_stock_data(symbol, period="2d")
                if df is not None and len(df) >= 2:
                    current = df['Close'].iloc[-1]
                    prev = df['Close'].iloc[-2]
                    change = ((current - prev) / prev) * 100
                    
                    if change > 0:
                        gainers.append({
                            "Symbol": symbol,
                            "Price": formatters.format_currency(current),
                            "Change": f"+{change:.2f}%"
                        })
            except:
                pass
        
        gainers.sort(key=lambda x: float(x['Change'].strip('+%')), reverse=True)
        if gainers[:5]:
            st.dataframe(pd.DataFrame(gainers[:5]), use_container_width=True, hide_index=True)
        else:
            st.info("No gainers data available")
    
    with col_loss:
        st.markdown("**📉 Top Losers**")
        
        losers = []
        for symbol in POPULAR_STOCKS[:10]:
            try:
                df = data_loader.load_stock_data(symbol, period="2d")
                if df is not None and len(df) >= 2:
                    current = df['Close'].iloc[-1]
                    prev = df['Close'].iloc[-2]
                    change = ((current - prev) / prev) * 100
                    
                    if change < 0:
                        losers.append({
                            "Symbol": symbol,
                            "Price": formatters.format_currency(current),
                            "Change": f"{change:.2f}%"
                        })
            except:
                pass
        
        losers.sort(key=lambda x: float(x['Change'].strip('%')))
        if losers[:5]:
            st.dataframe(pd.DataFrame(losers[:5]), use_container_width=True, hide_index=True)
        else:
            st.info("No losers data available")

with tab2:
    st.subheader("⭐ My Watchlist")
    
    if st.session_state.watchlist:
        watchlist_data = []
        
        for symbol in st.session_state.watchlist:
            try:
                df = data_loader.load_stock_data(symbol, period="5d")
                if df is not None and not df.empty:
                    df_indicators = tech_indicators.add_all_indicators(df)
                    
                    current = df['Close'].iloc[-1]
                    prev = df['Close'].iloc[0]
                    change = ((current - prev) / prev) * 100
                    rsi = df_indicators['RSI'].iloc[-1]
                    
                    watchlist_data.append({
                        "Symbol": symbol,
                        "Price": formatters.format_currency(current),
                        "5D Change (%)": f"{change:.2f}%",
                        "RSI": f"{rsi:.2f}",
                        "Volume": formatters.format_number(df['Volume'].iloc[-1])
                    })
            except Exception as e:
                st.warning(f"Error loading {symbol}: {str(e)}")
        
        if watchlist_data:
            watchlist_df = pd.DataFrame(watchlist_data)
            st.dataframe(watchlist_df, use_container_width=True, hide_index=True)
            
            col_w1, col_w2 = st.columns([3, 1])
            with col_w2:
                if st.button("Clear Watchlist", type="secondary"):
                    st.session_state.watchlist = []
                    st.rerun()
        
        st.markdown("#### Watchlist Performance")
        selected_watchlist = st.selectbox(
            "Select stock to view chart",
            options=st.session_state.watchlist
        )
        
        if selected_watchlist:
            with st.spinner(f"Loading {selected_watchlist} chart..."):
                df = data_loader.load_stock_data(selected_watchlist, period="1mo")
                if df is not None and not df.empty:
                    fig = plotly_charts.plot_line_chart(
                        df.reset_index(),
                        x_col='Date',
                        y_col='Close',
                        title=f"{selected_watchlist} Price Chart (1 Month)"
                    )
                    st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("Your watchlist is empty. Add stocks from the sidebar or search page.")
        
        st.markdown("#### Add Popular Stocks")
        cols = st.columns(5)
        for idx, symbol in enumerate(POPULAR_STOCKS[:10]):
            col = cols[idx % 5]
            with col:
                if st.button(f"➕ {symbol}", key=f"add_watchlist_{symbol}"):
                    if symbol not in st.session_state.watchlist:
                        st.session_state.watchlist.append(symbol)
                        st.success(f"Added {symbol} to watchlist")
                        st.rerun()

with tab3:
    st.subheader("🔔 Active Alerts")
    
    if st.session_state.alerts:
        st.markdown(f"**Total Active Alerts:** {len(st.session_state.alerts)}")
        
        alerts_data = []
        for idx, alert in enumerate(st.session_state.alerts):
            alerts_data.append({
                "Symbol": alert['symbol'],
                "Condition": alert['condition'],
                "Target Price": formatters.format_currency(alert['price']),
                "Status": "🟢 Active" if alert.get('active', True) else "🔴 Inactive",
                "Index": idx
            })
        
        alerts_df = pd.DataFrame(alerts_data)
        st.dataframe(alerts_df.drop('Index', axis=1), use_container_width=True, hide_index=True)
        
        st.markdown("#### Check Alerts Status")
        if st.button("Check All Alerts Now", type="primary"):
            with st.spinner("Checking alerts..."):
                triggered_alerts = []
                
                for alert in st.session_state.alerts:
                    try:
                        df = data_loader.load_stock_data(alert['symbol'], period="1d")
                        if df is not None and not df.empty:
                            current_price = df['Close'].iloc[-1]
                            
                            if alert['condition'] == 'Above' and current_price >= alert['price']:
                                triggered_alerts.append(f"{alert['symbol']} is above ${alert['price']:.2f} (Current: ${current_price:.2f})")
                            elif alert['condition'] == 'Below' and current_price <= alert['price']:
                                triggered_alerts.append(f"{alert['symbol']} is below ${alert['price']:.2f} (Current: ${current_price:.2f})")
                    except:
                        pass
                
                if triggered_alerts:
                    st.success("Triggered Alerts:")
                    for alert_msg in triggered_alerts:
                        st.info(alert_msg)
                else:
                    st.info("No alerts triggered at this time")
    else:
        st.info("No active alerts. Set up alerts in the Settings page.")
        
        if st.button("Go to Settings", type="primary"):
            st.switch_page("pages/8_⚙️_Settings.py")

with tab4:
    st.subheader("⚡ Quick Actions")
    
    col_qa1, col_qa2, col_qa3 = st.columns(3)
    
    with col_qa1:
        st.markdown("#### 📈 Analyze Stock")
        quick_symbol = st.text_input("Enter ticker", key="quick_analyze").upper()
        
        if st.button("Analyze", type="primary", use_container_width=True):
            if quick_symbol:
                st.session_state.selected_ticker = quick_symbol
                st.switch_page("pages/2_📈_Price_Forecast.py")
            else:
                st.warning("Please enter a ticker symbol")
    
    with col_qa2:
        st.markdown("#### 🎯 Get Signals")
        signal_symbol = st.selectbox(
            "Select stock",
            options=POPULAR_STOCKS[:10],
            key="quick_signal"
        )
        
        if st.button("View Signals", type="primary", use_container_width=True):
            st.session_state.selected_ticker = signal_symbol
            st.switch_page("pages/3_🎯_Trading_Signals.py")
    
    with col_qa3:
        st.markdown("#### 🔍 Compare")
        compare_category = st.selectbox(
            "Category",
            options=list(STOCK_CATEGORIES.keys()),
            key="quick_compare"
        )
        
        if st.button("Compare Stocks", type="primary", use_container_width=True):
            st.switch_page("pages/5_🔍_Stock_Comparison.py")
    
    st.divider()
    
    st.markdown("#### 📊 Popular Stocks Quick Access")
    cols = st.columns(5)
    
    for idx, symbol in enumerate(POPULAR_STOCKS[:15]):
        col = cols[idx % 5]
        with col:
            if st.button(symbol, key=f"quick_{symbol}", use_container_width=True):
                st.session_state.selected_ticker = symbol
                st.switch_page("pages/2_📈_Price_Forecast.py")

st.divider()

col_footer1, col_footer2 = st.columns([2, 1])

with col_footer1:
    st.markdown(f"**{APP_NAME}** - Last updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

with col_footer2:
    if st.button("🔄 Refresh Dashboard", use_container_width=True):
        st.cache_data.clear()
        st.rerun()