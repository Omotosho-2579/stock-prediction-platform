import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    from src.data.data_loader import DataLoader
    from src.data.technical_indicators import TechnicalIndicators
    from src.data.fundamental_data import FundamentalData
    from src.visualization.comparison_plots import ComparisonPlots
    from src.visualization.heatmaps import Heatmaps
    from src.visualization.plotly_charts import PlotlyCharts
except ImportError as e:
    st.error(f"Import error: {e}. Please ensure all required modules are available.")
    st.stop()

st.set_page_config(page_title="Stock Comparison", page_icon="🔍", layout="wide")

st.title("🔍 Stock Comparison Tool")
st.markdown("Compare multiple stocks side-by-side with technical and fundamental analysis")

try:
    data_loader = DataLoader()
    tech_indicators = TechnicalIndicators()
    fundamental_data = FundamentalData()
    comparison_plots = ComparisonPlots()
    heatmaps = Heatmaps()
    plotly_charts = PlotlyCharts()
except Exception as e:
    st.error(f"Initialization error: {e}")
    st.stop()

st.subheader("Select Stocks to Compare")

col1, col2, col3 = st.columns([4, 2, 1])

with col1:
    stocks = st.multiselect(
        "Enter stock symbols (2-5 stocks)",
        ['AAPL', 'GOOGL', 'MSFT', 'TSLA', 'AMZN', 'META', 'NVDA', 'AMD', 'NFLX', 'DIS'],
        default=['AAPL', 'GOOGL', 'MSFT']
    )

with col2:
    period = st.selectbox("Time Period", ['1mo', '3mo', '6mo', '1y', '2y', '5y'], index=3)

with col3:
    st.write("")
    st.write("")
    compare_btn = st.button("🔍 Compare", type="primary", use_container_width=True)

if compare_btn and len(stocks) >= 2:
    with st.spinner("Loading and analyzing stocks..."):
        try:
            stock_data_dict = {}
            fundamental_dict = {}
            
            for ticker in stocks:
                try:
                    data = data_loader.fetch_stock_data(ticker, period=period)
                    if data is not None and not data.empty:
                        stock_data_dict[ticker] = tech_indicators.add_all_indicators(data)
                        try:
                            fundamental_dict[ticker] = fundamental_data.get_fundamentals(ticker)
                        except Exception:
                            fundamental_dict[ticker] = {}
                except Exception as e:
                    st.warning(f"Could not load data for {ticker}: {e}")
            
            if len(stock_data_dict) < 2:
                st.error("❌ Could not load enough stock data for comparison. Please try different symbols.")
                st.stop()
            
            st.success(f"✅ Loaded data for {len(stock_data_dict)} stocks")
            
            st.divider()
            
            tab1, tab2, tab3, tab4, tab5 = st.tabs([
                "📈 Price Comparison",
                "📊 Performance Metrics",
                "💰 Fundamental Analysis",
                "🔬 Technical Indicators",
                "📉 Risk Analysis"
            ])
            
            with tab1:
                st.subheader("Price Comparison")
                
                comparison_type = st.radio(
                    "Comparison Type",
                    ["Absolute Price", "Normalized (% Change)", "Volume"],
                    horizontal=True
                )
                
                try:
                    if comparison_type == "Absolute Price":
                        fig = comparison_plots.create_price_comparison(stock_data_dict)
                    elif comparison_type == "Normalized (% Change)":
                        fig = comparison_plots.create_normalized_comparison(stock_data_dict)
                    else:
                        fig = comparison_plots.create_volume_comparison(stock_data_dict)
                    
                    st.plotly_chart(fig, use_container_width=True)
                except Exception as e:
                    st.warning(f"Could not create comparison chart: {e}")
                
                st.subheader("Current Prices")
                
                price_data = []
                for ticker, data in stock_data_dict.items():
                    try:
                        current_price = float(data['Close'].iloc[-1])
                        prev_price = float(data['Close'].iloc[0])
                        change = ((current_price - prev_price) / prev_price) * 100
                        
                        price_data.append({
                            'Symbol': ticker,
                            'Current Price': f"${current_price:.2f}",
                            'Period Change': f"{change:+.2f}%",
                            'High': f"${float(data['High'].max()):.2f}",
                            'Low': f"${float(data['Low'].min()):.2f}",
                            'Avg Volume': f"{float(data['Volume'].mean()):,.0f}"
                        })
                    except Exception:
                        continue
                
                if price_data:
                    price_df = pd.DataFrame(price_data)
                    st.dataframe(price_df, use_container_width=True, hide_index=True)
            
            with tab2:
                st.subheader("Performance Metrics")
                
                metrics_data = []
                
                for ticker, data in stock_data_dict.items():
                    try:
                        returns = data['Close'].pct_change()
                        
                        total_return = ((float(data['Close'].iloc[-1]) - float(data['Close'].iloc[0])) / float(data['Close'].iloc[0])) * 100
                        volatility = float(returns.std() * np.sqrt(252) * 100)
                        sharpe = float((returns.mean() / returns.std()) * np.sqrt(252)) if returns.std() > 0 else 0
                        max_dd = float(((data['Close'] / data['Close'].cummax()) - 1).min() * 100)
                        
                        metrics_data.append({
                            'Symbol': ticker,
                            'Total Return': f"{total_return:.2f}%",
                            'Volatility': f"{volatility:.2f}%",
                            'Sharpe Ratio': f"{sharpe:.2f}",
                            'Max Drawdown': f"{max_dd:.2f}%"
                        })
                    except Exception:
                        continue
                
                if metrics_data:
                    metrics_df = pd.DataFrame(metrics_data)
                    st.dataframe(metrics_df, use_container_width=True, hide_index=True)
                
                st.subheader("Performance Comparison Charts")
                
                col1, col2 = st.columns(2)
                
                with col1:
                    try:
                        fig_returns = comparison_plots.create_returns_comparison(stock_data_dict)
                        st.plotly_chart(fig_returns, use_container_width=True)
                    except Exception as e:
                        st.warning(f"Could not create returns chart: {e}")
                
                with col2:
                    try:
                        fig_volatility = comparison_plots.create_volatility_comparison(metrics_df)
                        st.plotly_chart(fig_volatility, use_container_width=True)
                    except Exception as e:
                        st.warning(f"Could not create volatility chart: {e}")
                
                st.subheader("Monthly Returns Heatmap")
                
                selected_stock = st.selectbox("Select stock for monthly returns", list(stock_data_dict.keys()))
                if selected_stock in stock_data_dict:
                    try:
                        fig_monthly = heatmaps.create_monthly_returns_heatmap(
                            stock_data_dict[selected_stock],
                            selected_stock
                        )
                        st.plotly_chart(fig_monthly, use_container_width=True)
                    except Exception as e:
                        st.warning(f"Could not create heatmap: {e}")
            
            with tab3:
                st.subheader("Fundamental Comparison")
                
                fundamental_metrics = []
                
                for ticker, fundamentals in fundamental_dict.items():
                    fundamental_metrics.append({
                        'Symbol': ticker,
                        'Market Cap': fundamentals.get('market_cap', 'N/A'),
                        'P/E Ratio': fundamentals.get('pe_ratio', 'N/A'),
                        'EPS': fundamentals.get('eps', 'N/A'),
                        'Dividend Yield': fundamentals.get('dividend_yield', 'N/A'),
                        'Beta': fundamentals.get('beta', 'N/A'),
                        '52W High': fundamentals.get('52w_high', 'N/A'),
                        '52W Low': fundamentals.get('52w_low', 'N/A')
                    })
                
                fundamental_df = pd.DataFrame(fundamental_metrics)
                st.dataframe(fundamental_df, use_container_width=True, hide_index=True)
                
                st.subheader("Valuation Comparison")
                
                col1, col2 = st.columns(2)
                
                with col1:
                    st.markdown("**Price-to-Earnings (P/E) Ratio**")
                    pe_data = {}
                    for ticker, fundamentals in fundamental_dict.items():
                        pe_value = fundamentals.get('pe_ratio', 0)
                        try:
                            pe_data[ticker] = float(pe_value) if pe_value != 'N/A' else 0
                        except:
                            pe_data[ticker] = 0
                    
                    try:
                        fig_pe = plotly_charts.create_bar_chart(pe_data, "P/E Ratio")
                        st.plotly_chart(fig_pe, use_container_width=True)
                    except Exception as e:
                        st.warning(f"Could not create P/E chart: {e}")
                
                with col2:
                    st.markdown("**Dividend Yield**")
                    div_data = {}
                    for ticker, fundamentals in fundamental_dict.items():
                        div_value = fundamentals.get('dividend_yield', 0)
                        try:
                            div_data[ticker] = float(div_value) if div_value != 'N/A' else 0
                        except:
                            div_data[ticker] = 0
                    
                    try:
                        fig_div = plotly_charts.create_bar_chart(div_data, "Dividend Yield (%)")
                        st.plotly_chart(fig_div, use_container_width=True)
                    except Exception as e:
                        st.warning(f"Could not create dividend chart: {e}")
                
                st.subheader("Company Overview")
                
                for ticker, fundamentals in fundamental_dict.items():
                    with st.expander(f"{ticker} - {fundamentals.get('company_name', ticker)}"):
                        col1, col2 = st.columns(2)
                        
                        with col1:
                            st.markdown(f"**Sector:** {fundamentals.get('sector', 'N/A')}")
                            st.markdown(f"**Industry:** {fundamentals.get('industry', 'N/A')}")
                            st.markdown(f"**Country:** {fundamentals.get('country', 'N/A')}")
                        
                        with col2:
                            st.markdown(f"**Employees:** {fundamentals.get('employees', 'N/A')}")
                            st.markdown(f"**Website:** {fundamentals.get('website', 'N/A')}")
                        
                        st.markdown(f"**Description:** {fundamentals.get('description', 'N/A')}")
            
            with tab4:
                st.subheader("Technical Indicators Comparison")
                
                indicator = st.selectbox(
                    "Select Indicator",
                    ["RSI", "MACD", "Moving Averages", "Bollinger Bands"]
                )
                
                if indicator == "RSI":
                    st.markdown("**Relative Strength Index (RSI)**")
                    
                    rsi_data = []
                    for ticker, data in stock_data_dict.items():
                        try:
                            if 'RSI' in data.columns and not data['RSI'].isna().all():
                                current_rsi = float(data['RSI'].iloc[-1])
                                signal = "Oversold" if current_rsi < 30 else "Overbought" if current_rsi > 70 else "Neutral"
                                
                                rsi_data.append({
                                    'Symbol': ticker,
                                    'RSI': f"{current_rsi:.2f}",
                                    'Signal': signal
                                })
                        except Exception:
                            continue
                    
                    if rsi_data:
                        rsi_df = pd.DataFrame(rsi_data)
                        st.dataframe(rsi_df, use_container_width=True, hide_index=True)
                    
                    try:
                        fig_rsi = comparison_plots.create_indicator_comparison(stock_data_dict, 'RSI')
                        st.plotly_chart(fig_rsi, use_container_width=True)
                    except Exception as e:
                        st.warning(f"Could not create RSI chart: {e}")
                
                elif indicator == "MACD":
                    st.markdown("**Moving Average Convergence Divergence (MACD)**")
                    
                    try:
                        fig_macd = comparison_plots.create_macd_comparison(stock_data_dict)
                        st.plotly_chart(fig_macd, use_container_width=True)
                    except Exception as e:
                        st.warning(f"Could not create MACD chart: {e}")
                
                elif indicator == "Moving Averages":
                    st.markdown("**Simple Moving Averages**")
                    
                    ma_period = st.select_slider("MA Period", [20, 50, 100, 200], value=50)
                    
                    try:
                        fig_ma = comparison_plots.create_ma_comparison(stock_data_dict, ma_period)
                        st.plotly_chart(fig_ma, use_container_width=True)
                    except Exception as e:
                        st.warning(f"Could not create MA chart: {e}")
                
                else:
                    st.markdown("**Bollinger Bands**")
                    
                    selected_stock_bb = st.selectbox("Select stock", list(stock_data_dict.keys()), key="bb_stock")
                    if selected_stock_bb in stock_data_dict:
                        try:
                            fig_bb = comparison_plots.create_bollinger_comparison(
                                stock_data_dict[selected_stock_bb],
                                selected_stock_bb
                            )
                            st.plotly_chart(fig_bb, use_container_width=True)
                        except Exception as e:
                            st.warning(f"Could not create Bollinger Bands chart: {e}")
            
            with tab5:
                st.subheader("Risk Analysis")
                
                risk_metrics = []
                
                for ticker, data in stock_data_dict.items():
                    try:
                        returns = data['Close'].pct_change()
                        
                        daily_vol = float(returns.std())
                        annual_vol = daily_vol * np.sqrt(252) * 100
                        var_95 = float(returns.quantile(0.05) * 100)
                        max_dd = float(((data['Close'] / data['Close'].cummax()) - 1).min() * 100)
                        
                        beta_value = fundamental_dict.get(ticker, {}).get('beta', 1.0)
                        try:
                            beta = float(beta_value) if beta_value != 'N/A' else 1.0
                        except:
                            beta = 1.0
                        
                        risk_metrics.append({
                            'Symbol': ticker,
                            'Annual Volatility': f"{annual_vol:.2f}%",
                            'Beta': f"{beta:.2f}",
                            'VaR (95%)': f"{var_95:.2f}%",
                            'Max Drawdown': f"{max_dd:.2f}%"
                        })
                    except Exception:
                        continue
                
                if risk_metrics:
                    risk_df = pd.DataFrame(risk_metrics)
                    st.dataframe(risk_df, use_container_width=True, hide_index=True)
                
                st.subheader("Risk-Return Scatter")
                
                try:
                    fig_risk_return = comparison_plots.create_risk_return_scatter(stock_data_dict)
                    st.plotly_chart(fig_risk_return, use_container_width=True)
                except Exception as e:
                    st.warning(f"Could not create risk-return scatter: {e}")
                
                st.subheader("Correlation Matrix")
                
                try:
                    correlation_data = pd.DataFrame({
                        ticker: data['Close'] for ticker, data in stock_data_dict.items()
                    })
                    correlation_matrix = correlation_data.pct_change().corr()
                    
                    fig_corr = heatmaps.create_correlation_heatmap(correlation_matrix)
                    st.plotly_chart(fig_corr, use_container_width=True)
                    
                    st.markdown("**Interpretation:**")
                    st.markdown("- Values close to 1: Stocks move together (high positive correlation)")
                    st.markdown("- Values close to -1: Stocks move in opposite directions (negative correlation)")
                    st.markdown("- Values close to 0: Little to no correlation")
                except Exception as e:
                    st.warning(f"Could not create correlation matrix: {e}")
        
        except Exception as e:
            st.error(f"❌ Error: {str(e)}")
            import traceback
            with st.expander("Error Details"):
                st.code(traceback.format_exc())

elif compare_btn and len(stocks) < 2:
    st.warning("⚠️ Please select at least 2 stocks to compare")

st.divider()

st.subheader("📊 Popular Comparisons")

popular_comparisons = [
    "Tech Giants: AAPL, GOOGL, MSFT, AMZN",
    "EV Makers: TSLA, RIVN, LCID, NIO",
    "Social Media: META, SNAP, PINS, TWTR",
    "Semiconductors: NVDA, AMD, INTC, TSM",
    "Streaming: NFLX, DIS, PARA, WBD"
]

selected_preset = st.selectbox("Quick Compare", ["Select a preset..."] + popular_comparisons)

if selected_preset != "Select a preset...":
    st.info(f"💡 Selected: {selected_preset}")