# src/database/models.py

from datetime import datetime
from pathlib import Path
import sys

project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from src.utils.logger import Logger

class BaseModel:
    def __init__(self):
        self.logger = Logger(__name__)
    
    def to_dict(self):
        return {key: value for key, value in self.__dict__.items() if not key.startswith('_')}

class User(BaseModel):
    def __init__(self, user_id=None, username=None, email=None, created_at=None, preferences=None):
        super().__init__()
        self.user_id = user_id
        self.username = username
        self.email = email
        self.created_at = created_at or datetime.now().isoformat()
        self.preferences = preferences or {}
    
    @staticmethod
    def from_dict(data):
        return User(
            user_id=data.get('user_id'),
            username=data.get('username'),
            email=data.get('email'),
            created_at=data.get('created_at'),
            preferences=data.get('preferences')
        )

class Portfolio(BaseModel):
    def __init__(self, portfolio_id=None, user_id=None, symbol=None, shares=None, 
                 purchase_price=None, purchase_date=None, created_at=None):
        super().__init__()
        self.portfolio_id = portfolio_id
        self.user_id = user_id
        self.symbol = symbol
        self.shares = shares
        self.purchase_price = purchase_price
        self.purchase_date = purchase_date
        self.created_at = created_at or datetime.now().isoformat()
    
    @staticmethod
    def from_dict(data):
        return Portfolio(
            portfolio_id=data.get('portfolio_id'),
            user_id=data.get('user_id'),
            symbol=data.get('symbol'),
            shares=data.get('shares'),
            purchase_price=data.get('purchase_price'),
            purchase_date=data.get('purchase_date'),
            created_at=data.get('created_at')
        )

class Alert(BaseModel):
    def __init__(self, alert_id=None, user_id=None, symbol=None, condition=None, 
                 target_price=None, notification_method=None, active=True, 
                 created_at=None, triggered_at=None):
        super().__init__()
        self.alert_id = alert_id
        self.user_id = user_id
        self.symbol = symbol
        self.condition = condition
        self.target_price = target_price
        self.notification_method = notification_method
        self.active = active
        self.created_at = created_at or datetime.now().isoformat()
        self.triggered_at = triggered_at
    
    @staticmethod
    def from_dict(data):
        return Alert(
            alert_id=data.get('alert_id'),
            user_id=data.get('user_id'),
            symbol=data.get('symbol'),
            condition=data.get('condition'),
            target_price=data.get('target_price'),
            notification_method=data.get('notification_method'),
            active=data.get('active', True),
            created_at=data.get('created_at'),
            triggered_at=data.get('triggered_at')
        )

class Prediction(BaseModel):
    def __init__(self, prediction_id=None, symbol=None, model_type=None, 
                 prediction_date=None, predicted_price=None, actual_price=None, 
                 confidence=None, created_at=None):
        super().__init__()
        self.prediction_id = prediction_id
        self.symbol = symbol
        self.model_type = model_type
        self.prediction_date = prediction_date
        self.predicted_price = predicted_price
        self.actual_price = actual_price
        self.confidence = confidence
        self.created_at = created_at or datetime.now().isoformat()
    
    @staticmethod
    def from_dict(data):
        return Prediction(
            prediction_id=data.get('prediction_id'),
            symbol=data.get('symbol'),
            model_type=data.get('model_type'),
            prediction_date=data.get('prediction_date'),
            predicted_price=data.get('predicted_price'),
            actual_price=data.get('actual_price'),
            confidence=data.get('confidence'),
            created_at=data.get('created_at')
        )

class Watchlist(BaseModel):
    def __init__(self, watchlist_id=None, user_id=None, symbol=None, added_at=None):
        super().__init__()
        self.watchlist_id = watchlist_id
        self.user_id = user_id
        self.symbol = symbol
        self.added_at = added_at or datetime.now().isoformat()
    
    @staticmethod
    def from_dict(data):
        return Watchlist(
            watchlist_id=data.get('watchlist_id'),
            user_id=data.get('user_id'),
            symbol=data.get('symbol'),
            added_at=data.get('added_at')
        )