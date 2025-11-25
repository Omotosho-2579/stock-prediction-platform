# src/database/crud_operations.py

from pathlib import Path
import sys

project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from src.database.db_manager import DBManager
from src.database.models import User, Portfolio, Alert, Prediction, Watchlist
from src.utils.logger import Logger

class CRUDOperations:
    def __init__(self):
        self.logger = Logger(__name__)
        self.db = DBManager()
        self.db.connect()
    
    def create_user(self, username, email, preferences=None):
        query = """
        INSERT INTO users (username, email, preferences, created_at)
        VALUES (?, ?, ?, datetime('now'))
        """
        
        import json
        preferences_json = json.dumps(preferences) if preferences else '{}'
        
        cursor = self.db.execute_query(query, (username, email, preferences_json))
        
        if cursor:
            return cursor.lastrowid
        return None
    
    def get_user(self, user_id):
        query = "SELECT * FROM users WHERE user_id = ?"
        result = self.db.fetch_one(query, (user_id,))
        
        if result:
            return User.from_dict(result)
        return None
    
    def update_user(self, user_id, username=None, email=None, preferences=None):
        updates = []
        params = []
        
        if username:
            updates.append("username = ?")
            params.append(username)
        
        if email:
            updates.append("email = ?")
            params.append(email)
        
        if preferences:
            import json
            updates.append("preferences = ?")
            params.append(json.dumps(preferences))
        
        if not updates:
            return False
        
        params.append(user_id)
        query = f"UPDATE users SET {', '.join(updates)} WHERE user_id = ?"
        
        cursor = self.db.execute_query(query, tuple(params))
        return cursor is not None
    
    def delete_user(self, user_id):
        query = "DELETE FROM users WHERE user_id = ?"
        cursor = self.db.execute_query(query, (user_id,))
        return cursor is not None
    
    def create_portfolio_position(self, user_id, symbol, shares, purchase_price, purchase_date):
        query = """
        INSERT INTO portfolios (user_id, symbol, shares, purchase_price, purchase_date, created_at)
        VALUES (?, ?, ?, ?, ?, datetime('now'))
        """
        
        cursor = self.db.execute_query(query, (user_id, symbol, shares, purchase_price, purchase_date))
        
        if cursor:
            return cursor.lastrowid
        return None
    
    def get_portfolio_positions(self, user_id):
        query = "SELECT * FROM portfolios WHERE user_id = ?"
        results = self.db.fetch_all(query, (user_id,))
        
        return [Portfolio.from_dict(result) for result in results]
    
    def get_portfolio_position(self, portfolio_id):
        query = "SELECT * FROM portfolios WHERE portfolio_id = ?"
        result = self.db.fetch_one(query, (portfolio_id,))
        
        if result:
            return Portfolio.from_dict(result)
        return None
    
    def update_portfolio_position(self, portfolio_id, shares=None, purchase_price=None):
        updates = []
        params = []
        
        if shares is not None:
            updates.append("shares = ?")
            params.append(shares)
        
        if purchase_price is not None:
            updates.append("purchase_price = ?")
            params.append(purchase_price)
        
        if not updates:
            return False
        
        params.append(portfolio_id)
        query = f"UPDATE portfolios SET {', '.join(updates)} WHERE portfolio_id = ?"
        
        cursor = self.db.execute_query(query, tuple(params))
        return cursor is not None
    
    def delete_portfolio_position(self, portfolio_id):
        query = "DELETE FROM portfolios WHERE portfolio_id = ?"
        cursor = self.db.execute_query(query, (portfolio_id,))
        return cursor is not None
    
    def create_alert(self, user_id, symbol, condition, target_price, notification_method):
        query = """
        INSERT INTO alerts (user_id, symbol, condition, target_price, notification_method, active, created_at)
        VALUES (?, ?, ?, ?, ?, 1, datetime('now'))
        """
        
        cursor = self.db.execute_query(query, (user_id, symbol, condition, target_price, notification_method))
        
        if cursor:
            return cursor.lastrowid
        return None
    
    def get_alerts(self, user_id, active_only=True):
        if active_only:
            query = "SELECT * FROM alerts WHERE user_id = ? AND active = 1"
        else:
            query = "SELECT * FROM alerts WHERE user_id = ?"
        
        results = self.db.fetch_all(query, (user_id,))
        
        return [Alert.from_dict(result) for result in results]
    
    def get_alert(self, alert_id):
        query = "SELECT * FROM alerts WHERE alert_id = ?"
        result = self.db.fetch_one(query, (alert_id,))
        
        if result:
            return Alert.from_dict(result)
        return None
    
    def update_alert(self, alert_id, active=None, triggered_at=None):
        updates = []
        params = []
        
        if active is not None:
            updates.append("active = ?")
            params.append(1 if active else 0)
        
        if triggered_at is not None:
            updates.append("triggered_at = ?")
            params.append(triggered_at)
        
        if not updates:
            return False
        
        params.append(alert_id)
        query = f"UPDATE alerts SET {', '.join(updates)} WHERE alert_id = ?"
        
        cursor = self.db.execute_query(query, tuple(params))
        return cursor is not None
    
    def delete_alert(self, alert_id):
        query = "DELETE FROM alerts WHERE alert_id = ?"
        cursor = self.db.execute_query(query, (alert_id,))
        return cursor is not None
    
    def create_prediction(self, symbol, model_type, prediction_date, predicted_price, confidence):
        query = """
        INSERT INTO predictions (symbol, model_type, prediction_date, predicted_price, confidence, created_at)
        VALUES (?, ?, ?, ?, ?, datetime('now'))
        """
        
        cursor = self.db.execute_query(query, (symbol, model_type, prediction_date, predicted_price, confidence))
        
        if cursor:
            return cursor.lastrowid
        return None
    
    def get_predictions(self, symbol=None, model_type=None):
        if symbol and model_type:
            query = "SELECT * FROM predictions WHERE symbol = ? AND model_type = ?"
            results = self.db.fetch_all(query, (symbol, model_type))
        elif symbol:
            query = "SELECT * FROM predictions WHERE symbol = ?"
            results = self.db.fetch_all(query, (symbol,))
        elif model_type:
            query = "SELECT * FROM predictions WHERE model_type = ?"
            results = self.db.fetch_all(query, (model_type,))
        else:
            query = "SELECT * FROM predictions"
            results = self.db.fetch_all(query)
        
        return [Prediction.from_dict(result) for result in results]
    
    def update_prediction_actual(self, prediction_id, actual_price):
        query = "UPDATE predictions SET actual_price = ? WHERE prediction_id = ?"
        cursor = self.db.execute_query(query, (actual_price, prediction_id))
        return cursor is not None
    
    def add_to_watchlist(self, user_id, symbol):
        query = """
        INSERT INTO watchlists (user_id, symbol, added_at)
        VALUES (?, ?, datetime('now'))
        """
        
        cursor = self.db.execute_query(query, (user_id, symbol))
        
        if cursor:
            return cursor.lastrowid
        return None
    
    def get_watchlist(self, user_id):
        query = "SELECT * FROM watchlists WHERE user_id = ?"
        results = self.db.fetch_all(query, (user_id,))
        
        return [Watchlist.from_dict(result) for result in results]
    
    def remove_from_watchlist(self, user_id, symbol):
        query = "DELETE FROM watchlists WHERE user_id = ? AND symbol = ?"
        cursor = self.db.execute_query(query, (user_id, symbol))
        return cursor is not None
    
    def close(self):
        self.db.disconnect()