# src/sentiment/news_scraper.py

import requests
from datetime import datetime, timedelta
import feedparser
from pathlib import Path
import sys
import json

project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from app.config import NEWSAPI_KEY, FINNHUB_KEY, SENTIMENT_DIR, NEWS_SOURCES
from src.utils.logger import Logger

class NewsScraper:
    def __init__(self):
        self.logger = Logger(__name__)
        self.newsapi_key = NEWSAPI_KEY
        self.finnhub_key = FINNHUB_KEY
        self.cache_dir = SENTIMENT_DIR
    
    def get_news(self, symbol, days=7, sources='all'):
        all_news = []
        
        if sources in ['all', 'newsapi'] and self.newsapi_key:
            newsapi_articles = self._get_newsapi_articles(symbol, days)
            all_news.extend(newsapi_articles)
        
        if sources in ['all', 'yahoo']:
            yahoo_articles = self._get_yahoo_rss(symbol)
            all_news.extend(yahoo_articles)
        
        if sources in ['all', 'finnhub'] and self.finnhub_key:
            finnhub_articles = self._get_finnhub_news(symbol, days)
            all_news.extend(finnhub_articles)
        
        all_news = self._deduplicate_articles(all_news)
        
        all_news.sort(key=lambda x: x.get('publishedAt', ''), reverse=True)
        
        self._cache_news(symbol, all_news)
        
        return all_news
    
    def _get_newsapi_articles(self, symbol, days=7):
        if not self.newsapi_key:
            self.logger.warning("NewsAPI key not configured")
            return []
        
        try:
            from_date = (datetime.now() - timedelta(days=days)).strftime('%Y-%m-%d')
            
            url = 'https://newsapi.org/v2/everything'
            params = {
                'q': f'{symbol} OR stock OR shares',
                'from': from_date,
                'sortBy': 'publishedAt',
                'language': 'en',
                'apiKey': self.newsapi_key,
                'pageSize': 20
            }
            
            if NEWS_SOURCES:
                params['sources'] = ','.join(NEWS_SOURCES)
            
            response = requests.get(url, params=params, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                articles = data.get('articles', [])
                
                formatted_articles = []
                for article in articles:
                    formatted_articles.append({
                        'title': article.get('title', ''),
                        'description': article.get('description', ''),
                        'url': article.get('url', ''),
                        'source': article.get('source', {}).get('name', 'NewsAPI'),
                        'publishedAt': article.get('publishedAt', ''),
                        'content': article.get('content', ''),
                        'author': article.get('author', 'Unknown')
                    })
                
                self.logger.info(f"Fetched {len(formatted_articles)} articles from NewsAPI for {symbol}")
                return formatted_articles
            else:
                self.logger.error(f"NewsAPI error: {response.status_code}")
                return []
        
        except Exception as e:
            self.logger.error(f"Error fetching NewsAPI articles: {str(e)}")
            return []
    
    def _get_yahoo_rss(self, symbol):
        try:
            rss_url = f"https://finance.yahoo.com/rss/headline?s={symbol}"
            
            feed = feedparser.parse(rss_url)
            
            articles = []
            for entry in feed.entries[:15]:
                articles.append({
                    'title': entry.get('title', ''),
                    'description': entry.get('summary', ''),
                    'url': entry.get('link', ''),
                    'source': 'Yahoo Finance',
                    'publishedAt': entry.get('published', datetime.now().isoformat()),
                    'content': entry.get('summary', ''),
                    'author': 'Yahoo Finance'
                })
            
            self.logger.info(f"Fetched {len(articles)} articles from Yahoo RSS for {symbol}")
            return articles
        
        except Exception as e:
            self.logger.error(f"Error fetching Yahoo RSS: {str(e)}")
            return []
    
    def _get_finnhub_news(self, symbol, days=7):
        if not self.finnhub_key:
            return []
        
        try:
            from_date = (datetime.now() - timedelta(days=days)).strftime('%Y-%m-%d')
            to_date = datetime.now().strftime('%Y-%m-%d')
            
            url = f"https://finnhub.io/api/v1/company-news"
            params = {
                'symbol': symbol,
                'from': from_date,
                'to': to_date,
                'token': self.finnhub_key
            }
            
            response = requests.get(url, params=params, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                
                articles = []
                for item in data[:15]:
                    articles.append({
                        'title': item.get('headline', ''),
                        'description': item.get('summary', ''),
                        'url': item.get('url', ''),
                        'source': item.get('source', 'Finnhub'),
                        'publishedAt': datetime.fromtimestamp(item.get('datetime', 0)).isoformat(),
                        'content': item.get('summary', ''),
                        'author': item.get('source', 'Unknown')
                    })
                
                self.logger.info(f"Fetched {len(articles)} articles from Finnhub for {symbol}")
                return articles
            else:
                self.logger.error(f"Finnhub error: {response.status_code}")
                return []
        
        except Exception as e:
            self.logger.error(f"Error fetching Finnhub news: {str(e)}")
            return []
    
    def _deduplicate_articles(self, articles):
        seen_titles = set()
        unique_articles = []
        
        for article in articles:
            title = article.get('title', '').lower().strip()
            if title and title not in seen_titles:
                seen_titles.add(title)
                unique_articles.append(article)
        
        return unique_articles
    
    def _cache_news(self, symbol, articles):
        try:
            date_str = datetime.now().strftime('%Y-%m-%d')
            cache_file = self.cache_dir / f"{symbol}_news_{date_str}.json"
            
            with open(cache_file, 'w') as f:
                json.dump(articles, f, indent=2)
            
            self.logger.info(f"Cached {len(articles)} articles for {symbol}")
        
        except Exception as e:
            self.logger.error(f"Error caching news: {str(e)}")
    
    def get_cached_news(self, symbol):
        try:
            date_str = datetime.now().strftime('%Y-%m-%d')
            cache_file = self.cache_dir / f"{symbol}_news_{date_str}.json"
            
            if cache_file.exists():
                with open(cache_file, 'r') as f:
                    articles = json.load(f)
                
                self.logger.info(f"Loaded {len(articles)} cached articles for {symbol}")
                return articles
            
            return None
        
        except Exception as e:
            self.logger.error(f"Error loading cached news: {str(e)}")
            return None
    
    def search_news_by_keyword(self, keyword, days=7):
        if not self.newsapi_key:
            return []
        
        try:
            from_date = (datetime.now() - timedelta(days=days)).strftime('%Y-%m-%d')
            
            url = 'https://newsapi.org/v2/everything'
            params = {
                'q': keyword,
                'from': from_date,
                'sortBy': 'publishedAt',
                'language': 'en',
                'apiKey': self.newsapi_key,
                'pageSize': 30
            }
            
            response = requests.get(url, params=params, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                return data.get('articles', [])
            
            return []
        
        except Exception as e:
            self.logger.error(f"Error searching news: {str(e)}")
            return []