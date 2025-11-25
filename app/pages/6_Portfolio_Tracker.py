# app/pages/6_💼_Portfolio_Tracker.py

import streamlit as st
import pandas as pd
import sys
from pathlib import Path
from datetime import datetime

sys.path.append(str(Path(__file__).parent.parent.parent))

from app.config import ENABLE_PORTFOLIO_OPTIMIZATION
from src.portfolio.portfolio_manager import PortfolioManager
from src.portfolio.performance_tracker import PerformanceTracker
from src.portfolio.risk_calculator import RiskCalculator
from src.data.data_loader import DataLoader
from src.visualization.portfolio_visualizer import PortfolioVisualizer
from src.utils.formatters import Formatters

st.set_page_config(page_title="Portfolio Tracker", page_icon="💼", layout="wide")

st.title("💼 Portfolio Tracker")
st.markdown("Track your portfolio performance and analyze risk metrics")

if 'portfolio' not in st.session_state:
    st.session_state.portfolio = []

portfolio_manager = PortfolioManager()
performance_tracker = PerformanceTracker()
risk_calculator = RiskCalculator()
data_loader = DataLoader()
portfolio_visualizer = PortfolioVisualizer()
formatters = Formatters()

st.sidebar.header("Add Position")

with st.sidebar.form("add_position"):
    symbol = st.text_input("Stock Symbol", value="").upper()
    shares = st.number_input("Number of Shares", min_value=0.0, value=0.0, step=1.0)
    purchase_price = st.number_input("Purchase Price ($)", min_value=0.0, value=0.0, step=0.01)
    purchase_date = st.date_input("Purchase Date", value=datetime.now())
    
    submitted = st.form_submit_button("Add Position")
    
    if submitted:
        if symbol and shares > 0 and purchase_price > 0:
            position = {
                "symbol": symbol,
                "shares": shares,
                "purchase_price": purchase_price,
                "purchase_date": purchase_date.strftime("%Y-%m-%d")
            }
            st.session_state.portfolio.append(position)
            st.success(f"Added {shares} shares of {symbol}")
            st.rerun()
        else:
            st.error("Please fill all fields with valid values")

if st.session_state.portfolio:
    st.header("Current Portfolio")
    
    portfolio_df = pd.DataFrame(st.session_state.portfolio)
    
    current_values = []
    total_invested = 0
    total_current = 0
    
    for idx, position in enumerate(st.session_state.portfolio):
        try:
            df = data_loader.load_stock_data(position['symbol'], period="1d")
            if df is not None and not df.empty:
                current_price = df['Close'].iloc[-1]
                position_value = current_price * position['shares']
                cost_basis = position['purchase_price'] * position['shares']
                gain_loss = position_value - cost_basis
                gain_loss_pct = (gain_loss / cost_basis) * 100 if cost_basis > 0 else 0
                
                current_values.append({
                    "Symbol": position['symbol'],
                    "Shares": position['shares'],
                    "Purchase Price": formatters.format_currency(position['purchase_price']),
                    "Current Price": formatters.format_currency(current_price),
                    "Cost Basis": formatters.format_currency(cost_basis),
                    "Current Value": formatters.format_currency(position_value),
                    "Gain/Loss": formatters.format_currency(gain_loss),
                    "Gain/Loss (%)": f"{gain_loss_pct:.2f}%",
                    "Index": idx
                })
                
                total_invested += cost_basis
                total_current += position_value
        except Exception as e:
            st.error(f"Error loading {position['symbol']}: {str(e)}")
    
    if current_values:
        values_df = pd.DataFrame(current_values)
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Total Invested", formatters.format_currency(total_invested))
        with col2:
            st.metric("Current Value", formatters.format_currency(total_current))
        with col3:
            total_gain_loss = total_current - total_invested
            st.metric("Total Gain/Loss", formatters.format_currency(total_gain_loss))
        with col4:
            total_return_pct = (total_gain_loss / total_invested * 100) if total_invested > 0 else 0
            st.metric("Total Return", f"{total_return_pct:.2f}%")
        
        st.dataframe(values_df.drop('Index', axis=1), use_container_width=True)
        
        col_delete1, col_delete2 = st.columns([3, 1])
        with col_delete2:
            if st.button("Clear Portfolio", type="secondary"):
                st.session_state.portfolio = []
                st.rerun()
        
        tab1, tab2, tab3 = st.tabs(["Allocation", "Performance", "Risk Analysis"])
        
        with tab1:
            st.subheader("Portfolio Allocation")
            
            allocation_data = []
            for item in current_values:
                value = float(item['Current Value'].replace('$', '').replace(',', ''))
                allocation_data.append({
                    "Symbol": item['Symbol'],
                    "Value": value,
                    "Percentage": (value / total_current * 100) if total_current > 0 else 0
                })
            
            allocation_df = pd.DataFrame(allocation_data)
            fig_pie = portfolio_visualizer.plot_allocation_pie(allocation_df)
            st.plotly_chart(fig_pie, use_container_width=True)
        
        with tab2:
            st.subheader("Portfolio Performance Over Time")
            
            portfolio_history = performance_tracker.calculate_portfolio_history(
                st.session_state.portfolio
            )
            
            if portfolio_history:
                fig_performance = portfolio_visualizer.plot_portfolio_performance(portfolio_history)
                st.plotly_chart(fig_performance, use_container_width=True)
        
        with tab3:
            st.subheader("Risk Metrics")
            
            risk_metrics = risk_calculator.calculate_portfolio_risk(st.session_state.portfolio)
            
            col_r1, col_r2, col_r3 = st.columns(3)
            
            with col_r1:
                st.metric("Portfolio Beta", f"{risk_metrics.get('beta', 0):.2f}")
            with col_r2:
                st.metric("Sharpe Ratio", f"{risk_metrics.get('sharpe_ratio', 0):.2f}")
            with col_r3:
                st.metric("Volatility", f"{risk_metrics.get('volatility', 0):.2f}%")
            
            if ENABLE_PORTFOLIO_OPTIMIZATION:
                st.info("💡 Visit Settings to enable advanced portfolio optimization features")
            
            st.info("Risk metrics are calculated based on historical data and may not predict future performance")

else:
    st.info("Your portfolio is empty. Add positions using the sidebar to get started.")
    
    st.markdown("""
    ### Getting Started
    1. Enter a stock symbol in the sidebar
    2. Specify the number of shares you own
    3. Enter your purchase price
    4. Select the purchase date
    5. Click 'Add Position' to add it to your portfolio
    """)