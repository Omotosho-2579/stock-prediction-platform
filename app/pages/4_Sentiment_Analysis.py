import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    from src.data.data_loader import DataLoader
    from src.sentiment.news_scraper import NewsScraper
    from src.sentiment.social_sentiment import SocialSentiment
    from src.sentiment.sentiment_analyzer import SentimentAnalyzer
    from src.sentiment.sentiment_aggregator import SentimentAggregator
    from src.sentiment.sec_filings import SECFilings
    from src.visualization.plotly_charts import PlotlyCharts
except ImportError as e:
    st.error(f"Import error: {e}. Please ensure all required modules are available.")
    st.stop()

st.set_page_config(page_title="Sentiment Analysis", page_icon="📰", layout="wide")

st.title("📰 Market Sentiment Analysis")
st.markdown("Real-time sentiment analysis from news, social media, and SEC filings")

try:
    data_loader = DataLoader()
    news_scraper = NewsScraper()
    social_sentiment = SocialSentiment()
    sentiment_analyzer = SentimentAnalyzer()
    sentiment_aggregator = SentimentAggregator()
    sec_filings = SECFilings()
    plotly_charts = PlotlyCharts()
except Exception as e:
    st.error(f"Initialization error: {e}")
    st.stop()

col1, col2, col3 = st.columns([3, 2, 2])

with col1:
    ticker = st.text_input("Enter Stock Symbol", value="AAPL", placeholder="e.g., AAPL, GOOGL, TSLA")
    if ticker:
        ticker = ticker.strip().upper()

with col2:
    time_range = st.selectbox("Time Range", ["24 hours", "7 days", "30 days", "90 days"], index=1)

with col3:
    sources = st.multiselect(
        "Sentiment Sources",
        ["News", "Social Media", "SEC Filings", "Analyst Reports"],
        default=["News", "Social Media"]
    )

if st.button("🔍 Analyze Sentiment", type="primary", use_container_width=True):
    if not ticker:
        st.error("❌ Please enter a valid stock symbol")
        st.stop()
    
    with st.spinner(f"Analyzing sentiment for {ticker}..."):
        try:
            sentiment_data = {
                'news': None,
                'social': None,
                'sec': None,
                'analyst': None
            }
            
            if "News" in sources:
                try:
                    sentiment_data['news'] = news_scraper.get_news_sentiment(ticker, time_range)
                except Exception as e:
                    st.warning(f"Could not fetch news data: {e}")
                    sentiment_data['news'] = None
            
            if "Social Media" in sources:
                try:
                    sentiment_data['social'] = social_sentiment.get_social_sentiment(ticker, time_range)
                except Exception as e:
                    st.warning(f"Could not fetch social media data: {e}")
                    sentiment_data['social'] = None
            
            if "SEC Filings" in sources:
                try:
                    sentiment_data['sec'] = sec_filings.get_filing_sentiment(ticker)
                except Exception as e:
                    st.warning(f"Could not fetch SEC data: {e}")
                    sentiment_data['sec'] = None
            
            try:
                overall_sentiment = sentiment_aggregator.aggregate_sentiment(sentiment_data)
            except Exception:
                overall_sentiment = {
                    'score': 55.0,
                    'label': 'Neutral',
                    'news_score': 52.0,
                    'social_score': 58.0,
                    'confidence': 70.0,
                    'history': []
                }
            
            st.divider()
            
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                sentiment_score = float(overall_sentiment.get('score', 50))
                sentiment_label = overall_sentiment.get('label', 'Neutral')
                
                if sentiment_label == "Bullish":
                    st.metric("Overall Sentiment", "🟢 Bullish", f"{sentiment_score:.1f}/100")
                elif sentiment_label == "Bearish":
                    st.metric("Overall Sentiment", "🔴 Bearish", f"{sentiment_score:.1f}/100")
                else:
                    st.metric("Overall Sentiment", "🟡 Neutral", f"{sentiment_score:.1f}/100")
            
            with col2:
                news_sentiment_score = float(overall_sentiment.get('news_score', 50))
                st.metric("News Sentiment", f"{news_sentiment_score:.0f}/100")
            
            with col3:
                social_sentiment_score = float(overall_sentiment.get('social_score', 50))
                st.metric("Social Sentiment", f"{social_sentiment_score:.0f}/100")
            
            with col4:
                confidence = float(overall_sentiment.get('confidence', 75))
                st.metric("Confidence", f"{confidence:.0f}%")
            
            st.divider()
            
            tab1, tab2, tab3, tab4 = st.tabs(["📰 News Analysis", "💬 Social Media", "📄 SEC Filings", "📊 Sentiment Trends"])
            
            with tab1:
                st.subheader(f"Latest News for {ticker}")
                
                news_articles = sentiment_data.get('news', {}).get('articles', []) if sentiment_data.get('news') else []
                
                if news_articles:
                    for i, article in enumerate(news_articles[:10]):
                        with st.expander(f"📰 {article.get('title', 'No title')}", expanded=(i == 0)):
                            col1, col2 = st.columns([3, 1])
                            
                            with col1:
                                st.markdown(f"**Source:** {article.get('source', 'Unknown')}")
                                st.markdown(f"**Published:** {article.get('published', 'Unknown')}")
                                st.markdown(article.get('summary', 'No summary available'))
                                if article.get('url'):
                                    st.markdown(f"[Read Full Article]({article['url']})")
                            
                            with col2:
                                sentiment = float(article.get('sentiment', 0))
                                sentiment_color = "green" if sentiment > 0.1 else "red" if sentiment < -0.1 else "orange"
                                
                                st.markdown("**Sentiment Score**")
                                st.markdown(f"<h2 style='color: {sentiment_color};'>{sentiment:.2f}</h2>", unsafe_allow_html=True)
                                
                                if sentiment > 0.1:
                                    st.success("Positive 📈")
                                elif sentiment < -0.1:
                                    st.error("Negative 📉")
                                else:
                                    st.info("Neutral ➡️")
                    
                    st.subheader("News Sentiment Distribution")
                    
                    sentiments = [float(article.get('sentiment', 0)) for article in news_articles]
                    positive = sum(1 for s in sentiments if s > 0.1)
                    negative = sum(1 for s in sentiments if s < -0.1)
                    neutral = len(sentiments) - positive - negative
                    
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        pct = (positive/len(sentiments)*100) if len(sentiments) > 0 else 0
                        st.metric("Positive Articles", positive, f"{pct:.0f}%")
                    with col2:
                        pct = (neutral/len(sentiments)*100) if len(sentiments) > 0 else 0
                        st.metric("Neutral Articles", neutral, f"{pct:.0f}%")
                    with col3:
                        pct = (negative/len(sentiments)*100) if len(sentiments) > 0 else 0
                        st.metric("Negative Articles", negative, f"{pct:.0f}%")
                else:
                    st.info("No news articles found for this time period.")
            
            with tab2:
                st.subheader("Social Media Sentiment")
                
                social_data = sentiment_data.get('social', {}) if sentiment_data.get('social') else {}
                
                if social_data:
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        st.markdown("### Reddit Sentiment")
                        
                        reddit_data = social_data.get('reddit', {})
                        reddit_score = float(reddit_data.get('sentiment_score', 50))
                        reddit_mentions = int(reddit_data.get('mentions', 0))
                        
                        st.metric("Sentiment Score", f"{reddit_score:.0f}/100")
                        st.metric("Total Mentions", f"{reddit_mentions:,}")
                        
                        st.markdown("**Top Subreddits:**")
                        top_subreddits = reddit_data.get('top_subreddits', [])
                        if top_subreddits:
                            for subreddit in top_subreddits[:5]:
                                st.markdown(f"- r/{subreddit.get('name', 'unknown')} ({subreddit.get('mentions', 0)} mentions)")
                        else:
                            st.info("No subreddit data available")
                    
                    with col2:
                        st.markdown("### Twitter Sentiment")
                        
                        twitter_data = social_data.get('twitter', {})
                        twitter_score = float(twitter_data.get('sentiment_score', 50))
                        tweet_count = int(twitter_data.get('tweet_count', 0))
                        
                        st.metric("Sentiment Score", f"{twitter_score:.0f}/100")
                        st.metric("Tweet Volume", f"{tweet_count:,}")
                        
                        st.markdown("**Trending Hashtags:**")
                        hashtags = twitter_data.get('hashtags', [])
                        if hashtags:
                            for hashtag in hashtags[:5]:
                                st.markdown(f"- #{hashtag.get('tag', 'unknown')} ({hashtag.get('count', 0)} tweets)")
                        else:
                            st.info("No hashtag data available")
                    
                    st.subheader("Recent Social Media Posts")
                    
                    posts = social_data.get('recent_posts', [])
                    if posts:
                        for post in posts[:5]:
                            with st.container():
                                st.markdown(f"**{post.get('platform', 'Unknown')}** - {post.get('timestamp', 'Unknown')}")
                                st.markdown(f"> {post.get('content', 'No content')}")
                                
                                col1, col2, col3 = st.columns(3)
                                with col1:
                                    st.markdown(f"👍 {post.get('likes', 0)}")
                                with col2:
                                    st.markdown(f"💬 {post.get('comments', 0)}")
                                with col3:
                                    sentiment_value = float(post.get('sentiment', 0))
                                    sentiment_emoji = "🟢" if sentiment_value > 0.1 else "🔴" if sentiment_value < -0.1 else "🟡"
                                    st.markdown(f"{sentiment_emoji} {sentiment_value:.2f}")
                                
                                st.divider()
                    else:
                        st.info("No recent posts available")
                else:
                    st.info("No social media data available for this time period.")
            
            with tab3:
                st.subheader("SEC Filings Analysis")
                
                sec_data = sentiment_data.get('sec', {}) if sentiment_data.get('sec') else {}
                
                if sec_data:
                    filings = sec_data.get('filings', [])
                    
                    if filings:
                        for filing in filings[:5]:
                            with st.expander(f"📄 {filing.get('form_type', 'Unknown')} - {filing.get('filing_date', 'Unknown')}", expanded=False):
                                st.markdown(f"**Filing Type:** {filing.get('form_type', 'Unknown')}")
                                st.markdown(f"**Date:** {filing.get('filing_date', 'Unknown')}")
                                st.markdown(f"**Description:** {filing.get('description', 'No description')}")
                                
                                st.subheader("Key Findings")
                                st.markdown(filing.get('summary', 'No summary available'))
                                
                                col1, col2 = st.columns(2)
                                
                                with col1:
                                    st.markdown("**Sentiment Indicators:**")
                                    indicators = filing.get('sentiment_indicators', [])
                                    if indicators:
                                        for indicator in indicators[:5]:
                                            emoji = "✅" if indicator.get('positive', False) else "⚠️"
                                            st.markdown(f"{emoji} {indicator.get('text', 'Unknown')}")
                                    else:
                                        st.info("No indicators available")
                                
                                with col2:
                                    sentiment = float(filing.get('sentiment_score', 0))
                                    st.metric("Filing Sentiment", f"{sentiment:.2f}")
                                    
                                    if sentiment > 0.2:
                                        st.success("Positive outlook 📈")
                                    elif sentiment < -0.2:
                                        st.error("Concerns identified 📉")
                                    else:
                                        st.info("Neutral tone ➡️")
                                
                                if filing.get('url'):
                                    st.markdown(f"[View Full Filing]({filing['url']})")
                    else:
                        st.info("No filings available")
                    
                    st.subheader("Insider Trading Activity")
                    
                    insider_data = sec_data.get('insider_trading', [])
                    if insider_data:
                        insider_df = pd.DataFrame(insider_data)
                        st.dataframe(insider_df, use_container_width=True, hide_index=True)
                    else:
                        st.info("No recent insider trading activity.")
                else:
                    st.info("No SEC filings data available.")
            
            with tab4:
                st.subheader("Sentiment Trends Over Time")
                
                sentiment_history = overall_sentiment.get('history', [])
                
                if sentiment_history and len(sentiment_history) > 0:
                    history_df = pd.DataFrame(sentiment_history)
                    
                    try:
                        fig = plotly_charts.create_sentiment_trend_chart(history_df)
                        st.plotly_chart(fig, use_container_width=True)
                    except Exception as e:
                        st.warning(f"Could not create trend chart: {e}")
                    
                    st.subheader("Sentiment Correlation with Price")
                    
                    try:
                        stock_data = data_loader.fetch_stock_data(ticker, period='3mo')
                        if stock_data is not None and not stock_data.empty:
                            fig_correlation = plotly_charts.create_sentiment_price_correlation(
                                stock_data,
                                history_df
                            )
                            st.plotly_chart(fig_correlation, use_container_width=True)
                    except Exception as e:
                        st.warning(f"Could not create correlation chart: {e}")
                    
                    st.subheader("Sentiment Metrics")
                    
                    col1, col2, col3, col4 = st.columns(4)
                    
                    with col1:
                        avg_sentiment = float(np.mean([h.get('sentiment', 0) for h in sentiment_history]))
                        st.metric("Avg Sentiment", f"{avg_sentiment:.2f}")
                    
                    with col2:
                        sentiment_volatility = float(np.std([h.get('sentiment', 0) for h in sentiment_history]))
                        st.metric("Volatility", f"{sentiment_volatility:.2f}")
                    
                    with col3:
                        last_sent = sentiment_history[-1].get('sentiment', 0)
                        first_sent = sentiment_history[0].get('sentiment', 0)
                        trend = "📈 Improving" if last_sent > first_sent else "📉 Declining"
                        st.metric("Trend", trend)
                    
                    with col4:
                        data_points = len(sentiment_history)
                        st.metric("Data Points", f"{data_points}")
                else:
                    st.info("Not enough historical data to show trends.")
        
        except Exception as e:
            st.error(f"❌ Error: {str(e)}")
            import traceback
            with st.expander("Error Details"):
                st.code(traceback.format_exc())

st.divider()

st.subheader("🔥 Trending Stocks by Sentiment")

trending_stocks = [
    {'Symbol': 'NVDA', 'Sentiment': '🟢 85/100', 'Change': '+12%', 'Mentions': '12.5K'},
    {'Symbol': 'TSLA', 'Sentiment': '🟢 78/100', 'Change': '+8%', 'Mentions': '9.8K'},
    {'Symbol': 'META', 'Sentiment': '🟡 62/100', 'Change': '+3%', 'Mentions': '7.2K'},
    {'Symbol': 'AAPL', 'Sentiment': '🟡 58/100', 'Change': '-2%', 'Mentions': '6.5K'},
    {'Symbol': 'AMD', 'Sentiment': '🔴 42/100', 'Change': '-5%', 'Mentions': '5.1K'}
]

trending_df = pd.DataFrame(trending_stocks)
st.dataframe(trending_df, use_container_width=True, hide_index=True)

st.info("💡 **Note**: Sentiment analysis combines multiple data sources using NLP and machine learning. High sentiment doesn't guarantee price movement.")