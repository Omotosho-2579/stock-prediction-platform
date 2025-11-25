# src/portfolio/tax_calculator.py

from datetime import datetime
from pathlib import Path
import sys

project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from src.data.data_loader import DataLoader
from src.utils.logger import Logger

class TaxCalculator:
    def __init__(self):
        self.logger = Logger(__name__)
        self.data_loader = DataLoader()
    
    def calculate_capital_gains(self, holdings, tax_year=None):
        if tax_year is None:
            tax_year = datetime.now().year
        
        short_term_gains = 0
        long_term_gains = 0
        
        realized_gains = []
        unrealized_gains = []
        
        for holding in holdings:
            try:
                df = self.data_loader.load_stock_data(holding['symbol'], period='1d')
                
                if df is None or df.empty:
                    continue
                
                current_price = df['Close'].iloc[-1]
                current_value = current_price * holding['shares']
                cost_basis = holding['cost_basis']
                
                gain_loss = current_value - cost_basis
                
                purchase_date = datetime.strptime(holding['purchase_date'], '%Y-%m-%d')
                days_held = (datetime.now() - purchase_date).days
                
                if holding.get('sold', False):
                    if days_held <= 365:
                        short_term_gains += gain_loss
                    else:
                        long_term_gains += gain_loss
                    
                    realized_gains.append({
                        'symbol': holding['symbol'],
                        'gain_loss': gain_loss,
                        'holding_period': 'short-term' if days_held <= 365 else 'long-term',
                        'days_held': days_held
                    })
                else:
                    unrealized_gains.append({
                        'symbol': holding['symbol'],
                        'gain_loss': gain_loss,
                        'holding_period': 'short-term' if days_held <= 365 else 'long-term',
                        'days_held': days_held
                    })
            
            except Exception as e:
                self.logger.error(f"Error calculating gains for {holding['symbol']}: {str(e)}")
        
        return {
            'tax_year': tax_year,
            'short_term_gains': short_term_gains,
            'long_term_gains': long_term_gains,
            'total_realized_gains': short_term_gains + long_term_gains,
            'realized_gains_detail': realized_gains,
            'unrealized_gains_detail': unrealized_gains
        }
    
    def estimate_tax_liability(self, capital_gains, income_bracket='24%'):
        short_term = capital_gains['short_term_gains']
        long_term = capital_gains['long_term_gains']
        
        income_tax_rates = {
            '10%': 0.10,
            '12%': 0.12,
            '22%': 0.22,
            '24%': 0.24,
            '32%': 0.32,
            '35%': 0.35,
            '37%': 0.37
        }
        
        long_term_rates = {
            '10%': 0.0,
            '12%': 0.0,
            '22%': 0.15,
            '24%': 0.15,
            '32%': 0.15,
            '35%': 0.20,
            '37%': 0.20
        }
        
        ordinary_rate = income_tax_rates.get(income_bracket, 0.24)
        long_term_rate = long_term_rates.get(income_bracket, 0.15)
        
        short_term_tax = max(0, short_term * ordinary_rate)
        long_term_tax = max(0, long_term * long_term_rate)
        
        total_tax = short_term_tax + long_term_tax
        
        return {
            'short_term_tax': short_term_tax,
            'long_term_tax': long_term_tax,
            'total_tax_liability': total_tax,
            'effective_tax_rate': (total_tax / (short_term + long_term) * 100) if (short_term + long_term) > 0 else 0
        }
    
    def identify_tax_loss_harvesting_opportunities(self, holdings):
        opportunities = []
        
        for holding in holdings:
            try:
                df = self.data_loader.load_stock_data(holding['symbol'], period='1d')
                
                if df is None or df.empty:
                    continue
                
                current_price = df['Close'].iloc[-1]
                current_value = current_price * holding['shares']
                cost_basis = holding['cost_basis']
                
                unrealized_loss = current_value - cost_basis
                
                if unrealized_loss < 0:
                    purchase_date = datetime.strptime(holding['purchase_date'], '%Y-%m-%d')
                    days_held = (datetime.now() - purchase_date).days
                    
                    opportunities.append({
                        'symbol': holding['symbol'],
                        'unrealized_loss': abs(unrealized_loss),
                        'loss_percentage': (unrealized_loss / cost_basis) * 100,
                        'days_held': days_held,
                        'shares': holding['shares'],
                        'current_price': current_price,
                        'cost_basis': holding['purchase_price']
                    })
            
            except Exception as e:
                self.logger.error(f"Error analyzing {holding['symbol']}: {str(e)}")
        
        opportunities.sort(key=lambda x: x['unrealized_loss'], reverse=True)
        
        return opportunities
    
    def calculate_wash_sale_impact(self, symbol, sale_date, repurchase_date):
        sale_dt = datetime.strptime(sale_date, '%Y-%m-%d')
        repurchase_dt = datetime.strptime(repurchase_date, '%Y-%m-%d')
        
        days_between = (repurchase_dt - sale_dt).days
        
        is_wash_sale = days_between <= 30
        
        return {
            'is_wash_sale': is_wash_sale,
            'days_between': days_between,
            'wash_sale_period': 30,
            'warning': 'Loss deduction disallowed due to wash sale rule' if is_wash_sale else None
        }
    
    def generate_tax_report(self, holdings, tax_year=None):
        capital_gains = self.calculate_capital_gains(holdings, tax_year)
        
        tax_liability = self.estimate_tax_liability(capital_gains)
        
        tax_loss_opportunities = self.identify_tax_loss_harvesting_opportunities(holdings)
        
        report = {
            'tax_year': capital_gains['tax_year'],
            'summary': {
                'total_realized_gains': capital_gains['total_realized_gains'],
                'short_term_gains': capital_gains['short_term_gains'],
                'long_term_gains': capital_gains['long_term_gains'],
                'estimated_tax_liability': tax_liability['total_tax_liability']
            },
            'realized_gains': capital_gains['realized_gains_detail'],
            'unrealized_gains': capital_gains['unrealized_gains_detail'],
            'tax_loss_harvesting': tax_loss_opportunities,
            'tax_liability_breakdown': tax_liability
        }
        
        return report