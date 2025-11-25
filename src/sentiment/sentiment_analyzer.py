# src/sentiment/sentiment_analyzer.py

import re
from pathlib import Path
import sys

project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from app.config import SENTIMENT_POSITIVE_THRESHOLD, SENTIMENT_NEGATIVE_THRESHOLD
from src.utils.logger import Logger

class SentimentAnalyzer:
    def __init__(self):
        self.logger = Logger(__name__)
        self.finbert_model = None
        self.vader_analyzer = None
        
        self._initialize_vader()
    
    def _initialize_vader(self):
        try:
            from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
            self.vader_analyzer = SentimentIntensityAnalyzer()
            self.logger.info("VADER sentiment analyzer initialized")
        except ImportError:
            self.logger.warning("vaderSentiment not installed. Install with: pip install vaderSentiment")
    
    def _initialize_finbert(self):
        if self.finbert_model is not None:
            return
        
        try:
            from transformers import AutoTokenizer, AutoModelForSequenceClassification
            import torch
            
            model_name = "ProsusAI/finbert"
            self.finbert_tokenizer = AutoTokenizer.from_pretrained(model_name)
            self.finbert_model = AutoModelForSequenceClassification.from_pretrained(model_name)
            
            self.logger.info("FinBERT model initialized")
        except ImportError:
            self.logger.warning("transformers not installed. Install with: pip install transformers torch")
        except Exception as e:
            self.logger.error(f"Error initializing FinBERT: {str(e)}")
    
    def analyze_text_vader(self, text):
        if not self.vader_analyzer:
            return {'compound': 0, 'positive': 0, 'neutral': 1, 'negative': 0}
        
        if not text or not isinstance(text, str):
            return {'compound': 0, 'positive': 0, 'neutral': 1, 'negative': 0}
        
        scores = self.vader_analyzer.polarity_scores(text)
        
        return scores
    
    def analyze_text_finbert(self, text):
        if not text or not isinstance(text, str):
            return {'label': 'neutral', 'score': 0.5}
        
        if self.finbert_model is None:
            self._initialize_finbert()
        
        if self.finbert_model is None:
            return self.analyze_text_vader(text)
        
        try:
            import torch
            
            inputs = self.finbert_tokenizer(text, return_tensors="pt", truncation=True, max_length=512)
            
            with torch.no_grad():
                outputs = self.finbert_model(**inputs)
            
            predictions = torch.nn.functional.softmax(outputs.logits, dim=-1)
            
            labels = ['positive', 'negative', 'neutral']
            scores = predictions[0].tolist()
            
            max_idx = scores.index(max(scores))
            
            return {
                'label': labels[max_idx],
                'score': scores[max_idx],
                'positive': scores[0],
                'negative': scores[1],
                'neutral': scores[2]
            }
        
        except Exception as e:
            self.logger.error(f"Error with FinBERT analysis: {str(e)}")
            return self.analyze_text_vader(text)
    
    def analyze_article(self, article, method='vader'):
        title = article.get('title', '')
        description = article.get('description', '')
        content = article.get('content', '')
        
        text = f"{title}. {description}. {content}"
        text = self._clean_text(text)
        
        if method == 'finbert':
            sentiment = self.analyze_text_finbert(text)
        else:
            sentiment = self.analyze_text_vader(text)
        
        article_sentiment = {
            'title': title,
            'sentiment': sentiment,
            'classification': self._classify_sentiment(sentiment, method),
            'url': article.get('url', ''),
            'publishedAt': article.get('publishedAt', ''),
            'source': article.get('source', '')
        }
        
        return article_sentiment
    
    def analyze_articles_batch(self, articles, method='vader'):
        analyzed_articles = []
        
        for article in articles:
            try:
                sentiment = self.analyze_article(article, method)
                analyzed_articles.append(sentiment)
            except Exception as e:
                self.logger.error(f"Error analyzing article: {str(e)}")
        
        return analyzed_articles
    
    def _clean_text(self, text):
        text = re.sub(r'http\S+|www\S+|https\S+', '', text, flags=re.MULTILINE)
        
        text = re.sub(r'@\w+|#\w+', '', text)
        
        text = re.sub(r'[^\w\s.,!?-]', '', text)
        
        text = ' '.join(text.split())
        
        return text
    
    def _classify_sentiment(self, sentiment, method='vader'):
        if method == 'vader':
            compound = sentiment.get('compound', 0)
            
            if compound >= SENTIMENT_POSITIVE_THRESHOLD:
                return 'Positive'
            elif compound <= SENTIMENT_NEGATIVE_THRESHOLD:
                return 'Negative'
            else:
                return 'Neutral'
        
        else:
            label = sentiment.get('label', 'neutral')
            return label.capitalize()
    
    def calculate_aggregate_sentiment(self, analyzed_articles):
        if not analyzed_articles:
            return {
                'overall_sentiment': 'Neutral',
                'sentiment_score': 0,
                'positive_count': 0,
                'negative_count': 0,
                'neutral_count': 0,
                'total_articles': 0
            }
        
        positive_count = 0
        negative_count = 0
        neutral_count = 0
        total_score = 0
        
        for article in analyzed_articles:
            classification = article.get('classification', 'Neutral')
            
            if classification == 'Positive':
                positive_count += 1
                total_score += 1
            elif classification == 'Negative':
                negative_count += 1
                total_score -= 1
            else:
                neutral_count += 1
        
        total_articles = len(analyzed_articles)
        
        if total_articles > 0:
            sentiment_score = (total_score / total_articles) * 100
        else:
            sentiment_score = 0
        
        if positive_count > negative_count and positive_count > neutral_count:
            overall = 'Positive'
        elif negative_count > positive_count and negative_count > neutral_count:
            overall = 'Negative'
        else:
            overall = 'Neutral'
        
        return {
            'overall_sentiment': overall,
            'sentiment_score': round(sentiment_score, 2),
            'positive_count': positive_count,
            'negative_count': negative_count,
            'neutral_count': neutral_count,
            'total_articles': total_articles,
            'positive_percentage': round((positive_count / total_articles) * 100, 1) if total_articles > 0 else 0,
            'negative_percentage': round((negative_count / total_articles) * 100, 1) if total_articles > 0 else 0,
            'neutral_percentage': round((neutral_count / total_articles) * 100, 1) if total_articles > 0 else 0
        }