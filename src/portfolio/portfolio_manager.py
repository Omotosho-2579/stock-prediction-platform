# src/portfolio/portfolio_manager.py

from datetime import datetime
from pathlib import Path
import sys
import json

project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from src.data.data_loader import DataLoader
from src.utils.logger import Logger

class PortfolioManager:
    def __init__(self):
        self.logger = Logger(__name__)
        self.data_loader = DataLoader()
        self.holdings = []
    
    def add_position(self, symbol, shares, purchase_price, purchase_date=None):
        if shares <= 0:
            self.logger.error("Shares must be positive")
            return False
        
        if purchase_price <= 0:
            self.logger.error("Purchase price must be positive")
            return False
        
        if purchase_date is None:
            purchase_date = datetime.now().strftime('%Y-%m-%d')
        
        position = {
            'id': self._generate_position_id(),
            'symbol': symbol.upper(),
            'shares': shares,
            'purchase_price': purchase_price,
            'purchase_date': purchase_date,
            'cost_basis': shares * purchase_price,
            'added_at': datetime.now().isoformat()
        }
        
        self.holdings.append(position)
        self.logger.info(f"Added position: {shares} shares of {symbol} at ${purchase_price}")
        
        return True
    
    def remove_position(self, position_id):
        original_count = len(self.holdings)
        self.holdings = [h for h in self.holdings if h.get('id') != position_id]
        
        if len(self.holdings) < original_count:
            self.logger.info(f"Removed position {position_id}")
            return True
        
        self.logger.warning(f"Position {position_id} not found")
        return False
    
    def update_position(self, position_id, shares=None, purchase_price=None):
        for holding in self.holdings:
            if holding.get('id') == position_id:
                if shares is not None and shares > 0:
                    holding['shares'] = shares
                    holding['cost_basis'] = shares * holding['purchase_price']
                
                if purchase_price is not None and purchase_price > 0:
                    holding['purchase_price'] = purchase_price
                    holding['cost_basis'] = holding['shares'] * purchase_price
                
                holding['updated_at'] = datetime.now().isoformat()
                self.logger.info(f"Updated position {position_id}")
                return True
        
        self.logger.warning(f"Position {position_id} not found")
        return False
    
    def get_position(self, position_id):
        for holding in self.holdings:
            if holding.get('id') == position_id:
                return holding
        
        return None
    
    def get_all_positions(self):
        return self.holdings
    
    def get_positions_by_symbol(self, symbol):
        return [h for h in self.holdings if h['symbol'] == symbol.upper()]
    
    def get_current_value(self):
        total_value = 0
        
        for holding in self.holdings:
            try:
                df = self.data_loader.load_stock_data(holding['symbol'], period='1d')
                
                if df is not None and not df.empty:
                    current_price = df['Close'].iloc[-1]
                    position_value = current_price * holding['shares']
                    total_value += position_value
            
            except Exception as e:
                self.logger.error(f"Error getting value for {holding['symbol']}: {str(e)}")
        
        return total_value
    
    def get_total_cost_basis(self):
        return sum(h['cost_basis'] for h in self.holdings)
    
    def get_portfolio_summary(self):
        total_cost = self.get_total_cost_basis()
        current_value = self.get_current_value()
        total_gain_loss = current_value - total_cost
        total_return_pct = (total_gain_loss / total_cost * 100) if total_cost > 0 else 0
        
        positions_detail = []
        
        for holding in self.holdings:
            try:
                df = self.data_loader.load_stock_data(holding['symbol'], period='1d')
                
                if df is not None and not df.empty:
                    current_price = df['Close'].iloc[-1]
                    position_value = current_price * holding['shares']
                    gain_loss = position_value - holding['cost_basis']
                    gain_loss_pct = (gain_loss / holding['cost_basis'] * 100) if holding['cost_basis'] > 0 else 0
                    
                    positions_detail.append({
                        'symbol': holding['symbol'],
                        'shares': holding['shares'],
                        'purchase_price': holding['purchase_price'],
                        'current_price': current_price,
                        'cost_basis': holding['cost_basis'],
                        'current_value': position_value,
                        'gain_loss': gain_loss,
                        'gain_loss_pct': gain_loss_pct,
                        'weight': (position_value / current_value * 100) if current_value > 0 else 0
                    })
            
            except Exception as e:
                self.logger.error(f"Error processing {holding['symbol']}: {str(e)}")
        
        return {
            'total_positions': len(self.holdings),
            'total_cost_basis': total_cost,
            'current_value': current_value,
            'total_gain_loss': total_gain_loss,
            'total_return_pct': total_return_pct,
            'positions': positions_detail
        }
    
    def _generate_position_id(self):
        import uuid
        return str(uuid.uuid4())
    
    def save_portfolio(self, file_path):
        try:
            with open(file_path, 'w') as f:
                json.dump(self.holdings, f, indent=2)
            
            self.logger.info(f"Portfolio saved to {file_path}")
            return True
        
        except Exception as e:
            self.logger.error(f"Error saving portfolio: {str(e)}")
            return False
    
    def load_portfolio(self, file_path):
        try:
            with open(file_path, 'r') as f:
                self.holdings = json.load(f)
            
            self.logger.info(f"Portfolio loaded from {file_path}")
            return True
        
        except Exception as e:
            self.logger.error(f"Error loading portfolio: {str(e)}")
            return False