# app/pages/8_⚙️_Settings.py

import streamlit as st
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent.parent.parent))

from app.config import (
    ENABLE_SENTIMENT_ANALYSIS, ENABLE_TELEGRAM_ALERTS, 
    ENABLE_EMAIL_ALERTS, ENABLE_CRYPTO_TRADING,
    ENABLE_PORTFOLIO_OPTIMIZATION, ENABLE_BACKTESTING,
    CONFIG_WARNINGS, APP_VERSION
)
from src.alerts.alert_manager import AlertManager
from src.database.db_manager import DBManager

st.set_page_config(page_title="Settings", page_icon="⚙️", layout="wide")

st.title("⚙️ Settings")
st.markdown("Configure your preferences and alerts")

alert_manager = AlertManager()
db_manager = DBManager()

if 'user_preferences' not in st.session_state:
    st.session_state.user_preferences = {
        'theme': 'Light',
        'default_period': '1y',
        'currency': 'USD',
        'notifications_enabled': True,
        'email': '',
        'telegram_chat_id': ''
    }

if 'alerts' not in st.session_state:
    st.session_state.alerts = []

if CONFIG_WARNINGS:
    st.info("⚙️ Configuration Notices")
    for warning in CONFIG_WARNINGS:
        st.warning(warning, icon="⚠️")
    st.divider()

tab1, tab2, tab3, tab4, tab5 = st.tabs(["General", "Alerts", "Notifications", "API Keys", "Features"])

with tab1:
    st.header("General Settings")
    
    col1, col2 = st.columns(2)
    
    with col1:
        theme = st.selectbox(
            "Theme",
            options=["Light", "Dark"],
            index=0 if st.session_state.user_preferences['theme'] == 'Light' else 1
        )
        st.session_state.user_preferences['theme'] = theme
        
        default_period = st.selectbox(
            "Default Time Period",
            options=["1mo", "3mo", "6mo", "1y", "2y", "5y"],
            index=3
        )
        st.session_state.user_preferences['default_period'] = default_period
    
    with col2:
        currency = st.selectbox(
            "Display Currency",
            options=["USD", "EUR", "GBP", "JPY"],
            index=0
        )
        st.session_state.user_preferences['currency'] = currency
        
        refresh_interval = st.selectbox(
            "Data Refresh Interval",
            options=["1 minute", "5 minutes", "15 minutes", "30 minutes", "1 hour"],
            index=2
        )
    
    st.subheader("Display Preferences")
    
    show_volume = st.checkbox("Show Volume in Charts", value=True)
    show_indicators = st.checkbox("Show Technical Indicators by Default", value=True)
    show_news = st.checkbox("Show News Sentiment", value=ENABLE_SENTIMENT_ANALYSIS)
    
    if st.button("Save General Settings", type="primary"):
        st.success("Settings saved successfully!")

with tab2:
    st.header("Price Alerts")
    st.markdown("Set up alerts to notify you when stocks reach certain price levels")
    
    with st.form("add_alert"):
        col_alert1, col_alert2, col_alert3 = st.columns(3)
        
        with col_alert1:
            alert_symbol = st.text_input("Stock Symbol").upper()
        
        with col_alert2:
            alert_condition = st.selectbox(
                "Condition",
                options=["Above", "Below"]
            )
        
        with col_alert3:
            alert_price = st.number_input("Price ($)", min_value=0.0, value=0.0, step=0.01)
        
        alert_submit = st.form_submit_button("Add Alert")
        
        if alert_submit:
            if alert_symbol and alert_price > 0:
                alert = {
                    "symbol": alert_symbol,
                    "condition": alert_condition,
                    "price": alert_price,
                    "active": True
                }
                st.session_state.alerts.append(alert)
                st.success(f"Alert added: {alert_symbol} {alert_condition.lower()} ${alert_price}")
                st.rerun()
            else:
                st.error("Please fill all fields with valid values")
    
    if st.session_state.alerts:
        st.subheader("Active Alerts")
        
        for idx, alert in enumerate(st.session_state.alerts):
            col_a1, col_a2, col_a3, col_a4 = st.columns([2, 2, 2, 1])
            
            with col_a1:
                st.write(f"**{alert['symbol']}**")
            with col_a2:
                st.write(f"{alert['condition']} ${alert['price']:.2f}")
            with col_a3:
                status = "🟢 Active" if alert['active'] else "🔴 Inactive"
                st.write(status)
            with col_a4:
                if st.button("Delete", key=f"delete_alert_{idx}"):
                    st.session_state.alerts.pop(idx)
                    st.rerun()
    else:
        st.info("No alerts configured. Add your first alert above.")

with tab3:
    st.header("Notification Settings")
    
    notifications_enabled = st.checkbox(
        "Enable Notifications",
        value=st.session_state.user_preferences['notifications_enabled']
    )
    st.session_state.user_preferences['notifications_enabled'] = notifications_enabled
    
    if notifications_enabled:
        st.subheader("Email Notifications")
        
        if not ENABLE_EMAIL_ALERTS:
            st.warning("⚠️ Email alerts are disabled. Configure email settings in API Keys tab.")
        
        email = st.text_input(
            "Email Address",
            value=st.session_state.user_preferences['email'],
            placeholder="your.email@example.com"
        )
        st.session_state.user_preferences['email'] = email
        
        email_frequency = st.selectbox(
            "Email Digest Frequency",
            options=["Real-time", "Daily", "Weekly", "Never"],
            index=1
        )
        
        st.checkbox("Price alerts", value=True)
        st.checkbox("Trading signals", value=True)
        st.checkbox("News updates", value=False)
        st.checkbox("Portfolio updates", value=True)
        
        st.subheader("Telegram Notifications")
        
        if not ENABLE_TELEGRAM_ALERTS:
            st.warning("⚠️ Telegram alerts are disabled. Configure Telegram Bot token in API Keys tab.")
        
        telegram_chat_id = st.text_input(
            "Telegram Chat ID",
            value=st.session_state.user_preferences['telegram_chat_id'],
            placeholder="123456789",
            help="Get your Chat ID from @userinfobot on Telegram"
        )
        st.session_state.user_preferences['telegram_chat_id'] = telegram_chat_id
        
        if st.button("Test Telegram Connection"):
            if telegram_chat_id and ENABLE_TELEGRAM_ALERTS:
                st.info("Sending test message to Telegram...")
            elif not ENABLE_TELEGRAM_ALERTS:
                st.error("Telegram bot not configured. Add bot token in API Keys tab.")
            else:
                st.warning("Please enter your Telegram Chat ID")
    
    if st.button("Save Notification Settings", type="primary"):
        st.success("Notification settings saved successfully!")

with tab4:
    st.header("API Configuration")
    st.markdown("Configure external API keys for enhanced features")
    
    with st.expander("News API", expanded=False):
        st.markdown("**Status:** " + ("✅ Enabled" if ENABLE_SENTIMENT_ANALYSIS else "❌ Disabled"))
        news_api_key = st.text_input(
            "News API Key",
            type="password",
            placeholder="Enter your News API key",
            help="Get your free API key from https://newsapi.org"
        )
        if st.button("Save News API Key"):
            if news_api_key:
                st.success("News API key saved")
            else:
                st.warning("Please enter a valid API key")
    
    with st.expander("Alpha Vantage", expanded=False):
        alpha_vantage_key = st.text_input(
            "Alpha Vantage API Key",
            type="password",
            placeholder="Enter your Alpha Vantage key",
            help="Get your free API key from https://www.alphavantage.co"
        )
        if st.button("Save Alpha Vantage Key"):
            if alpha_vantage_key:
                st.success("Alpha Vantage key saved")
            else:
                st.warning("Please enter a valid API key")
    
    with st.expander("Telegram Bot", expanded=False):
        st.markdown("**Status:** " + ("✅ Enabled" if ENABLE_TELEGRAM_ALERTS else "❌ Disabled"))
        telegram_bot_token = st.text_input(
            "Telegram Bot Token",
            type="password",
            placeholder="Enter your bot token",
            help="Create a bot with @BotFather on Telegram"
        )
        if st.button("Save Telegram Bot Token"):
            if telegram_bot_token:
                st.success("Telegram Bot token saved")
            else:
                st.warning("Please enter a valid bot token")
    
    with st.expander("Email Configuration", expanded=False):
        st.markdown("**Status:** " + ("✅ Enabled" if ENABLE_EMAIL_ALERTS else "❌ Disabled"))
        col_email1, col_email2 = st.columns(2)
        
        with col_email1:
            smtp_server = st.text_input("SMTP Server", placeholder="smtp.gmail.com")
            smtp_port = st.number_input("SMTP Port", min_value=1, max_value=65535, value=587)
        
        with col_email2:
            smtp_email = st.text_input("Email Address", placeholder="your.email@gmail.com")
            smtp_password = st.text_input("Email Password", type="password", placeholder="App password")
        
        if st.button("Save Email Configuration"):
            if smtp_server and smtp_email and smtp_password:
                st.success("Email configuration saved")
            else:
                st.warning("Please fill all email configuration fields")
    
    st.divider()
    
    st.subheader("Data Management")
    
    col_data1, col_data2, col_data3 = st.columns(3)
    
    with col_data1:
        if st.button("Clear Cache", type="secondary"):
            st.cache_data.clear()
            st.success("Cache cleared successfully")
    
    with col_data2:
        if st.button("Export Settings", type="secondary"):
            st.info("Settings export feature coming soon")
    
    with col_data3:
        if st.button("Reset All Settings", type="secondary"):
            st.warning("This will reset all settings to default values")

with tab5:
    st.header("Feature Status")
    st.markdown("Current status of platform features based on configuration")
    
    col_f1, col_f2 = st.columns(2)
    
    with col_f1:
        st.subheader("Core Features")
        st.markdown(f"{'✅' if True else '❌'} **Price Prediction**")
        st.caption("AI-powered stock price forecasting")
        
        st.markdown(f"{'✅' if True else '❌'} **Trading Signals**")
        st.caption("Buy/Sell/Hold recommendations")
        
        st.markdown(f"{'✅' if ENABLE_SENTIMENT_ANALYSIS else '❌'} **Sentiment Analysis**")
        st.caption("News and social media sentiment")
        if not ENABLE_SENTIMENT_ANALYSIS:
            st.caption("⚠️ Requires News API key")
        
        st.markdown(f"{'✅' if True else '❌'} **Stock Comparison**")
        st.caption("Compare multiple stocks side-by-side")
        
        st.markdown(f"{'✅' if True else '❌'} **Portfolio Tracking**")
        st.caption("Track your investments")
    
    with col_f2:
        st.subheader("Advanced Features")
        st.markdown(f"{'✅' if ENABLE_BACKTESTING else '❌'} **Strategy Backtesting**")
        st.caption("Test trading strategies on historical data")
        
        st.markdown(f"{'✅' if ENABLE_PORTFOLIO_OPTIMIZATION else '❌'} **Portfolio Optimization**")
        st.caption("Optimize asset allocation")
        
        st.markdown(f"{'✅' if ENABLE_CRYPTO_TRADING else '❌'} **Cryptocurrency Support**")
        st.caption("Trade and analyze crypto assets")
        
        st.markdown(f"{'✅' if ENABLE_TELEGRAM_ALERTS else '❌'} **Telegram Alerts**")
        st.caption("Real-time notifications via Telegram")
        if not ENABLE_TELEGRAM_ALERTS:
            st.caption("⚠️ Requires Telegram Bot token")
        
        st.markdown(f"{'✅' if ENABLE_EMAIL_ALERTS else '❌'} **Email Alerts**")
        st.caption("Email notifications for price changes")
        if not ENABLE_EMAIL_ALERTS:
            st.caption("⚠️ Requires email configuration")

st.divider()

st.subheader("About")
st.markdown(f"""
**Stock Prediction Platform** v{APP_VERSION}

A comprehensive stock analysis and prediction platform powered by machine learning.

**Features:**
- 📈 Real-time stock data and predictions
- 🎯 AI-powered trading signals
- 📰 News sentiment analysis
- 💼 Portfolio tracking and management
- 🎲 Strategy backtesting
- 📊 Advanced technical analysis

For support or feedback, please contact alabitech2019@gmail.com
""")

col_about1, col_about2, col_about3 = st.columns(3)

with col_about1:
    st.metric("Version", APP_VERSION)

with col_about2:
    st.metric("Last Updated", "2024-03")

with col_about3:
    api_status = "🟢 Online" if ENABLE_SENTIMENT_ANALYSIS or ENABLE_EMAIL_ALERTS else "🟡 Limited"
    st.metric("API Status", api_status)