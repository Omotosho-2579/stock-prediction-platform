# src/sentiment/sentiment_aggregator.py

from datetime import datetime
from pathlib import Path
import sys

project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from src.sentiment.news_scraper import NewsScraper
from src.sentiment.social_sentiment import SocialSentiment
from src.sentiment.sentiment_analyzer import SentimentAnalyzer
from src.utils.logger import Logger

class SentimentAggregator:
    def __init__(self):
        self.logger = Logger(__name__)
        self.news_scraper = NewsScraper()
        self.social_sentiment = SocialSentiment()
        self.sentiment_analyzer = SentimentAnalyzer()
    
    def get_comprehensive_sentiment(self, symbol, days=7, use_finbert=False):
        sentiment_method = 'finbert' if use_finbert else 'vader'
        
        news_articles = self.news_scraper.get_news(symbol, days)
        
        analyzed_news = []
        if news_articles:
            analyzed_news = self.sentiment_analyzer.analyze_articles_batch(news_articles, sentiment_method)
        
        news_sentiment = self.sentiment_analyzer.calculate_aggregate_sentiment(analyzed_news)
        
        social_data = self.social_sentiment.aggregate_social_sentiment(symbol)
        
        combined_sentiment = self._combine_sentiments(news_sentiment, social_data)
        
        comprehensive_report = {
            'symbol': symbol,
            'timestamp': datetime.now().isoformat(),
            'period_days': days,
            'news_sentiment': news_sentiment,
            'social_sentiment': social_data,
            'combined_sentiment': combined_sentiment,
            'recent_articles': analyzed_news[:5],
            'sentiment_trend': self._calculate_sentiment_trend(analyzed_news)
        }
        
        return comprehensive_report
    
    def _combine_sentiments(self, news_sentiment, social_data):
        news_score = news_sentiment.get('sentiment_score', 0)
        social_score = social_data.get('overall_social_sentiment', 0)
        
        news_weight = 0.7
        social_weight = 0.3
        
        combined_score = (news_score * news_weight) + (social_score * social_weight)
        
        if combined_score > 20:
            overall_sentiment = 'Bullish'
            confidence = min(90, 50 + abs(combined_score) * 0.5)
        elif combined_score > 10:
            overall_sentiment = 'Moderately Bullish'
            confidence = 60
        elif combined_score < -20:
            overall_sentiment = 'Bearish'
            confidence = min(90, 50 + abs(combined_score) * 0.5)
        elif combined_score < -10:
            overall_sentiment = 'Moderately Bearish'
            confidence = 60
        else:
            overall_sentiment = 'Neutral'
            confidence = 50
        
        return {
            'overall_sentiment': overall_sentiment,
            'combined_score': round(combined_score, 2),
            'confidence': round(confidence, 1),
            'news_contribution': round(news_score * news_weight, 2),
            'social_contribution': round(social_score * social_weight, 2)
        }
    
    def _calculate_sentiment_trend(self, analyzed_articles):
        if len(analyzed_articles) < 5:
            return 'Insufficient data'
        
        recent_articles = analyzed_articles[:5]
        older_articles = analyzed_articles[-5:]
        
        recent_sentiment = self.sentiment_analyzer.calculate_aggregate_sentiment(recent_articles)
        older_sentiment = self.sentiment_analyzer.calculate_aggregate_sentiment(older_articles)
        
        recent_score = recent_sentiment.get('sentiment_score', 0)
        older_score = older_sentiment.get('sentiment_score', 0)
        
        change = recent_score - older_score
        
        if change > 15:
            return 'Improving Rapidly'
        elif change > 5:
            return 'Improving'
        elif change < -15:
            return 'Deteriorating Rapidly'
        elif change < -5:
            return 'Deteriorating'
        else:
            return 'Stable'
    
    def compare_sentiment_multiple_stocks(self, symbols, days=7):
        comparison = []
        
        for symbol in symbols:
            try:
                sentiment_data = self.get_comprehensive_sentiment(symbol, days)
                
                comparison.append({
                    'symbol': symbol,
                    'overall_sentiment': sentiment_data['combined_sentiment']['overall_sentiment'],
                    'combined_score': sentiment_data['combined_sentiment']['combined_score'],
                    'confidence': sentiment_data['combined_sentiment']['confidence'],
                    'news_articles_count': sentiment_data['news_sentiment']['total_articles'],
                    'trend': sentiment_data['sentiment_trend']
                })
            
            except Exception as e:
                self.logger.error(f"Error analyzing {symbol}: {str(e)}")
        
        comparison.sort(key=lambda x: x['combined_score'], reverse=True)
        
        return comparison
    
    def get_sentiment_summary(self, symbol, days=7):
        comprehensive = self.get_comprehensive_sentiment(symbol, days)
        
        combined = comprehensive['combined_sentiment']
        news = comprehensive['news_sentiment']
        
        summary = {
            'sentiment': combined['overall_sentiment'],
            'score': combined['combined_score'],
            'confidence': combined['confidence'],
            'articles_analyzed': news['total_articles'],
            'positive_ratio': news['positive_percentage'],
            'negative_ratio': news['negative_percentage'],
            'trend': comprehensive['sentiment_trend']
        }
        
        return summary