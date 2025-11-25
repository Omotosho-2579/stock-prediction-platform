# src/sentiment/social_sentiment.py

from datetime import datetime, timedelta
from pathlib import Path
import sys

project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from app.config import STOCK_KEYWORDS
from src.utils.logger import Logger

class SocialSentiment:
    def __init__(self):
        self.logger = Logger(__name__)
        self.twitter_bearer_token = None
        self.twitter_api_key = None
        self.twitter_api_secret = None
        self.twitter_access_token = None
        self.twitter_access_secret = None
        self.twitter_client = None
        
        self._initialize_twitter()
    
    def _initialize_twitter(self):
        try:
            import os
            
            self.twitter_bearer_token = os.getenv("TWITTER_BEARER_TOKEN")
            self.twitter_api_key = os.getenv("TWITTER_API_KEY")
            self.twitter_api_secret = os.getenv("TWITTER_API_SECRET")
            self.twitter_access_token = os.getenv("TWITTER_ACCESS_TOKEN")
            self.twitter_access_secret = os.getenv("TWITTER_ACCESS_SECRET")
            
            if not all([self.twitter_api_key, self.twitter_api_secret, 
                       self.twitter_access_token, self.twitter_access_secret]):
                self.logger.warning("Twitter API credentials not configured")
                return
            
            import tweepy
            
            auth = tweepy.OAuthHandler(self.twitter_api_key, self.twitter_api_secret)
            auth.set_access_token(self.twitter_access_token, self.twitter_access_secret)
            
            self.twitter_client = tweepy.API(auth, wait_on_rate_limit=True)
            
            self.twitter_client.verify_credentials()
            self.logger.info("Twitter API initialized successfully")
        
        except ImportError:
            self.logger.warning("tweepy not installed. Install with: pip install tweepy")
        except Exception as e:
            self.logger.error(f"Error initializing Twitter API: {str(e)}")
    
    def get_twitter_sentiment(self, symbol, limit=100):
        if not self.twitter_client:
            self.logger.warning("Twitter API not initialized")
            return []
        
        tweets = []
        
        try:
            search_query = f"${symbol} OR #{symbol} -filter:retweets"
            
            for tweet in tweepy.Cursor(
                self.twitter_client.search_tweets,
                q=search_query,
                lang="en",
                result_type="recent",
                tweet_mode="extended"
            ).items(limit):
                tweets.append({
                    'text': tweet.full_text,
                    'created_at': tweet.created_at.isoformat(),
                    'user': tweet.user.screen_name,
                    'followers_count': tweet.user.followers_count,
                    'retweet_count': tweet.retweet_count,
                    'favorite_count': tweet.favorite_count,
                    'tweet_id': tweet.id_str,
                    'verified': tweet.user.verified
                })
            
            self.logger.info(f"Fetched {len(tweets)} tweets for {symbol}")
        
        except Exception as e:
            self.logger.error(f"Error fetching tweets for {symbol}: {str(e)}")
        
        return tweets
    
    def get_trending_stocks_twitter(self, limit=100):
        if not self.twitter_client:
            return {}
        
        try:
            stock_mentions = {}
            
            search_query = "stock OR stocks OR trading OR $SPY -filter:retweets"
            
            for tweet in tweepy.Cursor(
                self.twitter_client.search_tweets,
                q=search_query,
                lang="en",
                result_type="popular",
                tweet_mode="extended"
            ).items(limit):
                text = tweet.full_text.upper()
                
                words = text.split()
                for word in words:
                    if word.startswith('$') and len(word) > 2 and len(word) <= 6:
                        ticker = word[1:].strip('.,!?')
                        if ticker.isalpha():
                            stock_mentions[ticker] = stock_mentions.get(ticker, 0) + 1
                    elif word.startswith('#') and len(word) > 2 and len(word) <= 6:
                        ticker = word[1:].strip('.,!?')
                        if ticker.isalpha():
                            stock_mentions[ticker] = stock_mentions.get(ticker, 0) + 1
            
            sorted_mentions = sorted(stock_mentions.items(), key=lambda x: x[1], reverse=True)
            
            return dict(sorted_mentions[:20])
        
        except Exception as e:
            self.logger.error(f"Error getting trending stocks: {str(e)}")
            return {}
    
    def get_twitter_replies(self, symbol, limit=50):
        if not self.twitter_client:
            return []
        
        try:
            replies = []
            
            search_query = f"${symbol} -filter:retweets"
            
            for tweet in tweepy.Cursor(
                self.twitter_client.search_tweets,
                q=search_query,
                lang="en",
                result_type="recent",
                tweet_mode="extended"
            ).items(limit):
                if tweet.in_reply_to_status_id:
                    replies.append({
                        'text': tweet.full_text,
                        'created_at': tweet.created_at.isoformat(),
                        'user': tweet.user.screen_name,
                        'followers_count': tweet.user.followers_count,
                        'favorite_count': tweet.favorite_count,
                        'reply_to_id': tweet.in_reply_to_status_id_str
                    })
            
            return replies
        
        except Exception as e:
            self.logger.error(f"Error fetching Twitter replies: {str(e)}")
            return []
    
    def calculate_twitter_sentiment_score(self, tweets):
        if not tweets:
            return 0
        
        total_score = 0
        total_weight = 0
        
        for tweet in tweets:
            retweets = tweet.get('retweet_count', 0)
            favorites = tweet.get('favorite_count', 0)
            followers = tweet.get('followers_count', 0)
            verified = tweet.get('verified', False)
            
            engagement = retweets + favorites
            weight = engagement + (followers / 100)
            
            if verified:
                weight *= 1.5
            
            sentiment_value = self._analyze_tweet_sentiment(tweet.get('text', ''))
            
            total_score += sentiment_value * weight
            total_weight += weight
        
        if total_weight > 0:
            normalized_score = (total_score / total_weight)
            return max(-100, min(100, normalized_score))
        
        return 0
    
    def _analyze_tweet_sentiment(self, text):
        positive_words = [
            'bullish', 'moon', 'buy', 'long', 'calls', 'up', 'gain', 'profit',
            'surge', 'rally', 'breakout', 'strong', 'positive', 'growth', 'rocket'
        ]
        
        negative_words = [
            'bearish', 'sell', 'short', 'puts', 'down', 'loss', 'crash', 'drop',
            'decline', 'weak', 'negative', 'dump', 'falling', 'bear', 'risk'
        ]
        
        text_lower = text.lower()
        
        positive_count = sum(1 for word in positive_words if word in text_lower)
        negative_count = sum(1 for word in negative_words if word in text_lower)
        
        if positive_count == 0 and negative_count == 0:
            return 0
        
        sentiment = ((positive_count - negative_count) / (positive_count + negative_count)) * 100
        
        return sentiment
    
    def get_twitter_user_timeline(self, username, limit=50):
        if not self.twitter_client:
            return []
        
        try:
            tweets = []
            
            for tweet in tweepy.Cursor(
                self.twitter_client.user_timeline,
                screen_name=username,
                tweet_mode="extended",
                exclude_replies=True
            ).items(limit):
                tweets.append({
                    'text': tweet.full_text,
                    'created_at': tweet.created_at.isoformat(),
                    'retweet_count': tweet.retweet_count,
                    'favorite_count': tweet.favorite_count
                })
            
            return tweets
        
        except Exception as e:
            self.logger.error(f"Error fetching user timeline: {str(e)}")
            return []
    
    def aggregate_social_sentiment(self, symbol):
        twitter_tweets = self.get_twitter_sentiment(symbol)
        
        sentiment_data = {
            'symbol': symbol,
            'twitter_tweets_count': len(twitter_tweets),
            'twitter_sentiment_score': self.calculate_twitter_sentiment_score(twitter_tweets),
            'overall_social_sentiment': 0,
            'timestamp': datetime.now().isoformat()
        }
        
        if twitter_tweets:
            sentiment_data['overall_social_sentiment'] = sentiment_data['twitter_sentiment_score']
        
        sentiment_level = 'Neutral'
        score = sentiment_data['overall_social_sentiment']
        
        if score > 30:
            sentiment_level = 'Very Bullish'
        elif score > 10:
            sentiment_level = 'Bullish'
        elif score < -30:
            sentiment_level = 'Very Bearish'
        elif score < -10:
            sentiment_level = 'Bearish'
        
        sentiment_data['sentiment_level'] = sentiment_level
        
        return sentiment_data
    
    def get_influential_tweets(self, symbol, min_followers=10000, limit=50):
        if not self.twitter_client:
            return []
        
        try:
            influential_tweets = []
            
            search_query = f"${symbol} -filter:retweets"
            
            for tweet in tweepy.Cursor(
                self.twitter_client.search_tweets,
                q=search_query,
                lang="en",
                result_type="popular",
                tweet_mode="extended"
            ).items(limit * 2):
                if tweet.user.followers_count >= min_followers:
                    influential_tweets.append({
                        'text': tweet.full_text,
                        'created_at': tweet.created_at.isoformat(),
                        'user': tweet.user.screen_name,
                        'followers_count': tweet.user.followers_count,
                        'retweet_count': tweet.retweet_count,
                        'favorite_count': tweet.favorite_count,
                        'verified': tweet.user.verified,
                        'influence_score': (tweet.user.followers_count / 1000) + 
                                         (tweet.retweet_count * 2) + 
                                         tweet.favorite_count
                    })
                    
                    if len(influential_tweets) >= limit:
                        break
            
            influential_tweets.sort(key=lambda x: x['influence_score'], reverse=True)
            
            return influential_tweets
        
        except Exception as e:
            self.logger.error(f"Error fetching influential tweets: {str(e)}")
            return []