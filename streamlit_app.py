"""
AI Stock Prediction Platform - Main Entry Point
Streamlit multi-page application with advanced features
"""

import streamlit as st
import sys
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from app.config import (
    APP_NAME, APP_VERSION, APP_DESCRIPTION, 
    POPULAR_STOCKS, STOCK_CATEGORIES,
    CONFIG_WARNINGS, is_market_open,
    ENABLE_SENTIMENT_ANALYSIS, ENABLE_TELEGRAM_ALERTS,
    ENABLE_EMAIL_ALERTS, ENABLE_CRYPTO_TRADING
)

# ============================================================================
# PAGE CONFIGURATION
# ============================================================================

st.set_page_config(
    page_title=APP_NAME,
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={
        'Get Help': 'https://github.com/yourusername/stock-prediction-platform',
        'Report a bug': 'https://github.com/yourusername/stock-prediction-platform/issues',
        'About': f"{APP_NAME} v{APP_VERSION}\n\n{APP_DESCRIPTION}"
    }
)

# ============================================================================
# CUSTOM CSS
# ============================================================================

def load_custom_css():
    """Load custom CSS for better UI"""
    st.markdown("""
        <style>
        /* Main container styling */
        .main {
            padding-top: 2rem;
        }
        
        /* Sidebar styling */
        [data-testid="stSidebar"] {
            background-color: #f8f9fa;
        }
        
        /* Metric cards */
        [data-testid="stMetricValue"] {
            font-size: 2rem;
            font-weight: bold;
        }
        
        /* Headers */
        h1 {
            color: #1f77b4;
            font-weight: bold;
            margin-bottom: 1rem;
        }
        
        h2 {
            color: #2c3e50;
            font-weight: 600;
            margin-top: 2rem;
        }
        
        /* Info boxes */
        .stAlert {
            border-radius: 10px;
        }
        
        /* Buttons */
        .stButton>button {
            border-radius: 8px;
            font-weight: 600;
            transition: all 0.3s;
        }
        
        .stButton>button:hover {
            transform: translateY(-2px);
            box-shadow: 0 4px 8px rgba(0,0,0,0.2);
        }
        
        /* Cards */
        .custom-card {
            background-color: white;
            padding: 1.5rem;
            border-radius: 10px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            margin-bottom: 1rem;
        }
        
        /* Market status badge */
        .market-open {
            background-color: #2ecc71;
            color: white;
            padding: 0.3rem 0.8rem;
            border-radius: 20px;
            font-weight: bold;
            display: inline-block;
        }
        
        .market-closed {
            background-color: #e74c3c;
            color: white;
            padding: 0.3rem 0.8rem;
            border-radius: 20px;
            font-weight: bold;
            display: inline-block;
        }
        
        /* Footer */
        .footer {
            text-align: center;
            padding: 2rem;
            color: #7f8c8d;
            margin-top: 3rem;
            border-top: 1px solid #ecf0f1;
        }
        </style>
    """, unsafe_allow_html=True)

load_custom_css()

# ============================================================================
# SESSION STATE INITIALIZATION
# ============================================================================

def initialize_session_state():
    """Initialize session state variables"""
    if 'watchlist' not in st.session_state:
        st.session_state.watchlist = []
    
    if 'portfolio' not in st.session_state:
        st.session_state.portfolio = {}
    
    if 'alerts' not in st.session_state:
        st.session_state.alerts = []
    
    if 'theme' not in st.session_state:
        st.session_state.theme = 'light'
    
    if 'selected_ticker' not in st.session_state:
        st.session_state.selected_ticker = 'AAPL'
    
    if 'prediction_cache' not in st.session_state:
        st.session_state.prediction_cache = {}

initialize_session_state()

# ============================================================================
# SIDEBAR
# ============================================================================

def render_sidebar():
    """Render sidebar with navigation and quick actions"""
    with st.sidebar:
        # Logo with error handling
        try:
            logo_path = Path(__file__).parent.parent / "assets" / "logo.png"
            if logo_path.exists():
                st.image(str(logo_path), width=200)
        except Exception as e:
            pass  # Skip logo if not found
        
        st.title(APP_NAME)
        st.caption(f"v{APP_VERSION}")
        
        st.divider()
        
        # Market status
        st.subheader("📊 Market Status")
        try:
            if is_market_open():
                st.markdown('<span class="market-open">🟢 Market Open</span>', unsafe_allow_html=True)
            else:
                st.markdown('<span class="market-closed">🔴 Market Closed</span>', unsafe_allow_html=True)
        except:
            st.info("Market status unavailable")
        
        st.divider()
        
        # Quick stock selector
        st.subheader("🔍 Quick Search")
        
        # Category selection
        category = st.selectbox(
            "Select Category",
            options=['All'] + list(STOCK_CATEGORIES.keys()),
            key='sidebar_category'
        )
        
        # Stock selection based on category
        if category == 'All':
            available_stocks = POPULAR_STOCKS
        else:
            available_stocks = STOCK_CATEGORIES[category]
        
        selected_stock = st.selectbox(
            "Select Stock",
            options=available_stocks,
            key='sidebar_stock',
            index=0 if 'AAPL' not in available_stocks else available_stocks.index('AAPL')
        )
        
        # Custom ticker input
        st.caption("Or enter custom ticker:")
        custom_ticker = st.text_input(
            "Ticker Symbol",
            value="",
            placeholder="e.g., NFLX",
            key='custom_ticker_input'
        ).upper()
        
        # Set selected ticker
        if custom_ticker:
            st.session_state.selected_ticker = custom_ticker
        else:
            st.session_state.selected_ticker = selected_stock
        
        # Quick action buttons
        col1, col2 = st.columns(2)
        with col1:
            if st.button("📈 Predict", use_container_width=True):
                st.switch_page("pages/2_📈_Price_Forecast.py")
        with col2:
            if st.button("🎯 Signals", use_container_width=True):
                st.switch_page("pages/3_🎯_Trading_Signals.py")
        
        st.divider()
        
        # Watchlist
        st.subheader("⭐ My Watchlist")
        if st.session_state.watchlist:
            for ticker in st.session_state.watchlist[:5]:
                col1, col2 = st.columns([3, 1])
                with col1:
                    st.text(ticker)
                with col2:
                    if st.button("❌", key=f"remove_{ticker}"):
                        st.session_state.watchlist.remove(ticker)
                        st.rerun()
            
            if len(st.session_state.watchlist) > 5:
                st.caption(f"+{len(st.session_state.watchlist) - 5} more")
        else:
            st.caption("No stocks in watchlist")
        
        # Add to watchlist button
        if st.session_state.selected_ticker not in st.session_state.watchlist:
            if st.button("➕ Add to Watchlist", use_container_width=True):
                st.session_state.watchlist.append(st.session_state.selected_ticker)
                st.success(f"Added {st.session_state.selected_ticker} to watchlist!")
                st.rerun()
        
        st.divider()
        
        # Configuration warnings
        if CONFIG_WARNINGS:
            st.subheader("⚙️ Configuration")
            with st.expander("View Warnings", expanded=False):
                for warning in CONFIG_WARNINGS:
                    st.warning(warning, icon="⚠️")
        
        # Feature status
        st.subheader("✨ Features")
        st.caption(f"{'✅' if ENABLE_SENTIMENT_ANALYSIS else '❌'} Sentiment Analysis")
        st.caption(f"{'✅' if ENABLE_TELEGRAM_ALERTS else '❌'} Telegram Alerts")
        st.caption(f"{'✅' if ENABLE_EMAIL_ALERTS else '❌'} Email Alerts")
        st.caption(f"{'✅' if ENABLE_CRYPTO_TRADING else '❌'} Crypto Trading")
render_sidebar()

# ============================================================================
# MAIN CONTENT
# ============================================================================

# Hero section
st.title("🚀 Welcome to AI Stock Prediction Platform")
st.markdown(f"### {APP_DESCRIPTION}")

# Quick stats row
col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric(
        label="📊 Stocks Available",
        value=f"{len(POPULAR_STOCKS)}+",
        delta="Popular picks"
    )

with col2:
    st.metric(
        label="🤖 AI Models",
        value="5",
        delta="Ensemble powered"
    )

with col3:
    st.metric(
        label="⭐ Watchlist",
        value=len(st.session_state.watchlist),
        delta="Your stocks"
    )

with col4:
    st.metric(
        label="🔔 Active Alerts",
        value=len(st.session_state.alerts),
        delta="Monitoring"
    )

st.divider()

# Feature highlights
st.header("✨ Platform Features")

col1, col2, col3 = st.columns(3)

with col1:
    st.markdown("""
        <div class="custom-card">
            <h3>📈 Price Prediction</h3>
            <p>Advanced AI models predict future stock prices with high accuracy using LSTM, XGBoost, and ensemble methods.</p>
            <ul>
                <li>Multiple time horizons</li>
                <li>Confidence intervals</li>
                <li>Historical accuracy tracking</li>
            </ul>
        </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown("""
        <div class="custom-card">
            <h3>🎯 Trading Signals</h3>
            <p>AI-powered buy/sell recommendations based on technical analysis, sentiment, and market conditions.</p>
            <ul>
                <li>Real-time signals</li>
                <li>Risk/reward analysis</li>
                <li>Multiple strategies</li>
            </ul>
        </div>
    """, unsafe_allow_html=True)

with col3:
    st.markdown("""
        <div class="custom-card">
            <h3>📰 Sentiment Analysis</h3>
            <p>Analyze market sentiment from news articles and social media to gauge investor mood.</p>
            <ul>
                <li>Real-time news</li>
                <li>Social media tracking</li>
                <li>FinBERT AI analysis</li>
            </ul>
        </div>
    """, unsafe_allow_html=True)

st.divider()

# Quick start guide
st.header("🚀 Quick Start Guide")

tab1, tab2, tab3 = st.tabs(["📖 For Beginners", "💼 For Traders", "🔧 For Developers"])

with tab1:
    st.markdown("""
        ### Getting Started with Stock Prediction
        
        **Step 1: Choose a Stock**
        - Use the sidebar to select from popular stocks
        - Or enter any ticker symbol (e.g., AAPL, TSLA, GOOGL)
        
        **Step 2: View Predictions**
        - Go to **Price Forecast** page
        - See AI-predicted future prices
        - Review accuracy metrics
        
        **Step 3: Get Trading Signals**
        - Visit **Trading Signals** page
        - View BUY/SELL/HOLD recommendations
        - Understand risk/reward ratios
        
        **Step 4: Track Your Portfolio**
        - Add stocks to your watchlist
        - Monitor performance
        - Set up price alerts
        
        💡 **Tip:** Start with well-known stocks like AAPL or MSFT to understand the platform.
    """)

with tab2:
    st.markdown("""
        ### Advanced Trading Features
        
        **Portfolio Optimization**
        - Optimize asset allocation
        - Calculate Sharpe ratio
        - Minimize portfolio risk
        
        **Backtesting**
        - Test strategies on historical data
        - Compare different approaches
        - Validate signal accuracy
        
        **Risk Management**
        - Set stop-loss levels
        - Calculate position sizing
        - Monitor Value at Risk (VaR)
        
        **Alerts & Notifications**
        - Price target alerts
        - Volume spike notifications
        - Signal generation alerts
        
        📊 **Pro Tip:** Use the Compare feature to analyze multiple stocks simultaneously.
    """)

with tab3:
    st.markdown("""
        ### Technical Details
        
        **Models Used:**
        - Linear Regression (baseline)
        - LSTM Neural Networks (time series)
        - Random Forest (ensemble)
        - XGBoost (gradient boosting)
        - Weighted Ensemble (best accuracy)
        
        **Data Sources:**
        - yfinance (primary)
        - Alpha Vantage (backup)
        - NewsAPI (sentiment)
        - Reddit/Twitter (social sentiment)
        
        **Technical Indicators:**
        - RSI, MACD, Bollinger Bands
        - Moving Averages (SMA, EMA)
        - Volume analysis
        - ATR (volatility)
        
        **API Integration:**
        - RESTful architecture
        - Real-time data fetching
        - Caching for performance
        
        🔗 **GitHub:** [View source code](https://github.com/Omotosho-2579/stock-prediction-platform)
    """)

st.divider()

# Popular stocks quick view
st.header("📊 Popular Stocks")

# Create a row of popular stocks
cols = st.columns(5)
for idx, ticker in enumerate(POPULAR_STOCKS[:10]):
    col = cols[idx % 5]
    with col:
        if st.button(f"📈 {ticker}", use_container_width=True, key=f"popular_{ticker}"):
            st.session_state.selected_ticker = ticker
            st.switch_page("pages/2_📈_Price_Forecast.py")

if len(POPULAR_STOCKS) > 10:
    with st.expander("View More Popular Stocks"):
        cols = st.columns(5)
        for idx, ticker in enumerate(POPULAR_STOCKS[10:]):
            col = cols[idx % 5]
            with col:
                if st.button(f"📈 {ticker}", use_container_width=True, key=f"more_popular_{ticker}"):
                    st.session_state.selected_ticker = ticker
                    st.switch_page("pages/2_📈_Price_Forecast.py")

st.divider()

# Recent activity / News (placeholder)
st.header("📰 Latest Market News")
st.info("Connect your NewsAPI key in Settings to view real-time market news and sentiment analysis.", icon="ℹ️")

# Call to action
st.divider()

col1, col2, col3 = st.columns([1, 2, 1])
with col2:
    st.markdown("### Ready to start predicting?")
    if st.button("🚀 Start Predicting Now", type="primary", use_container_width=True):
        st.switch_page("pages/2_📈_Price_Forecast.py")

# Footer
st.markdown("""
    <div class="footer">
        <p>Made with ❤️ using Streamlit | © 2024 AI Stock Prediction Platform</p>
        <p>⚠️ Disclaimer: This platform is for educational purposes only. Not financial advice.</p>
    </div>
""", unsafe_allow_html=True)

# ============================================================================
# SIDEBAR FOOTER
# ============================================================================

with st.sidebar:
    st.divider()
    st.caption("📚 Need Help?")
    st.caption("[Documentation](https://github.com/Omotosho-2579/docs)")
    st.caption("[Report Bug](https://github.com/Omotosho-2579/issues)")
    st.caption(f"Version {APP_VERSION}")
