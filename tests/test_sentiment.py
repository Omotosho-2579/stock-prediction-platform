# tests/test_sentiment.py

import pytest
import sys
from pathlib import Path

project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.sentiment.sentiment_analyzer import SentimentAnalyzer
from src.sentiment.sentiment_aggregator import SentimentAggregator

@pytest.fixture
def sentiment_analyzer():
    return SentimentAnalyzer()

@pytest.fixture
def sentiment_aggregator():
    return SentimentAggregator()

class TestSentimentAnalyzer:
    
    def test_analyzer_initialization(self, sentiment_analyzer):
        assert sentiment_analyzer is not None
    
    def test_analyze_positive_text(self, sentiment_analyzer):
        text = "Apple stock is performing exceptionally well with record profits"
        score = sentiment_analyzer.analyze_text(text)
        
        assert score is not None
        assert isinstance(score, (int, float))
        assert score > 0
    
    def test_analyze_negative_text(self, sentiment_analyzer):
        text = "Company faces massive losses and declining market share"
        score = sentiment_analyzer.analyze_text(text)
        
        assert score is not None
        assert isinstance(score, (int, float))
        assert score < 0
    
    def test_analyze_neutral_text(self, sentiment_analyzer):
        text = "The company released quarterly earnings report today"
        score = sentiment_analyzer.analyze_text(text)
        
        assert score is not None
        assert isinstance(score, (int, float))
    
    def test_analyze_empty_text(self, sentiment_analyzer):
        score = sentiment_analyzer.analyze_text("")
        
        assert score is not None
        assert score == 0

class TestSentimentAggregator:
    
    def test_aggregator_initialization(self, sentiment_aggregator):
        assert sentiment_aggregator is not None
    
    def test_aggregate_multiple_sentiments(self, sentiment_aggregator):
        sentiments = [
            {'source': 'news', 'score': 0.5, 'weight': 1.0},
            {'source': 'social', 'score': 0.3, 'weight': 0.8},
            {'source': 'analyst', 'score': 0.7, 'weight': 1.2}
        ]
        
        aggregated = sentiment_aggregator.aggregate(sentiments)
        
        assert aggregated is not None
        assert 'overall_score' in aggregated
        assert 'confidence' in aggregated