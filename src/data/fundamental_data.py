# src/data/fundamental_data.py

import yfinance as yf
import pandas as pd
from pathlib import Path
import sys

project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from src.utils.logger import Logger

class FundamentalData:
    def __init__(self):
        self.logger = Logger(__name__)
    
    def get_fundamental_data(self, symbol):
        try:
            ticker = yf.Ticker(symbol)
            info = ticker.info
            
            fundamental_data = {
                'company_name': info.get('longName', 'N/A'),
                'sector': info.get('sector', 'N/A'),
                'industry': info.get('industry', 'N/A'),
                'market_cap': info.get('marketCap', 0),
                'enterprise_value': info.get('enterpriseValue', 0),
                'pe_ratio': info.get('trailingPE', 0),
                'forward_pe': info.get('forwardPE', 0),
                'peg_ratio': info.get('pegRatio', 0),
                'price_to_book': info.get('priceToBook', 0),
                'price_to_sales': info.get('priceToSalesTrailing12Months', 0),
                'eps': info.get('trailingEps', 0),
                'forward_eps': info.get('forwardEps', 0),
                'dividend_yield': info.get('dividendYield', 0),
                'dividend_rate': info.get('dividendRate', 0),
                'payout_ratio': info.get('payoutRatio', 0),
                'beta': info.get('beta', 1.0),
                'revenue': info.get('totalRevenue', 0),
                'revenue_per_share': info.get('revenuePerShare', 0),
                'profit_margin': info.get('profitMargins', 0),
                'operating_margin': info.get('operatingMargins', 0),
                'roe': info.get('returnOnEquity', 0),
                'roa': info.get('returnOnAssets', 0),
                'debt_to_equity': info.get('debtToEquity', 0),
                'current_ratio': info.get('currentRatio', 0),
                'quick_ratio': info.get('quickRatio', 0),
                'book_value': info.get('bookValue', 0),
                'earnings_growth': info.get('earningsGrowth', 0),
                'revenue_growth': info.get('revenueGrowth', 0),
                'target_mean_price': info.get('targetMeanPrice', 0),
                'recommendation': info.get('recommendationKey', 'none')
            }
            
            return fundamental_data
        
        except Exception as e:
            self.logger.error(f"Error getting fundamental data for {symbol}: {str(e)}")
            return {}
    
    def get_financial_statements(self, symbol):
        try:
            ticker = yf.Ticker(symbol)
            
            statements = {
                'income_statement': ticker.financials,
                'balance_sheet': ticker.balance_sheet,
                'cash_flow': ticker.cashflow
            }
            
            return statements
        
        except Exception as e:
            self.logger.error(f"Error getting financial statements for {symbol}: {str(e)}")
            return {}
    
    def get_earnings_data(self, symbol):
        try:
            ticker = yf.Ticker(symbol)
            
            earnings = {
                'quarterly_earnings': ticker.quarterly_earnings,
                'earnings_history': ticker.earnings_history,
                'earnings_dates': ticker.earnings_dates
            }
            
            return earnings
        
        except Exception as e:
            self.logger.error(f"Error getting earnings data for {symbol}: {str(e)}")
            return {}
    
    def get_dividends(self, symbol):
        try:
            ticker = yf.Ticker(symbol)
            dividends = ticker.dividends
            
            if dividends.empty:
                return None
            
            return dividends
        
        except Exception as e:
            self.logger.error(f"Error getting dividends for {symbol}: {str(e)}")
            return None
    
    def get_analyst_recommendations(self, symbol):
        try:
            ticker = yf.Ticker(symbol)
            recommendations = ticker.recommendations
            
            if recommendations is None or recommendations.empty:
                return None
            
            return recommendations
        
        except Exception as e:
            self.logger.error(f"Error getting recommendations for {symbol}: {str(e)}")
            return None
    
    def calculate_intrinsic_value_dcf(self, symbol):
        try:
            ticker = yf.Ticker(symbol)
            info = ticker.info
            cash_flow = ticker.cashflow
            
            if cash_flow.empty:
                return None
            
            fcf = cash_flow.loc['Free Cash Flow'].iloc[0] if 'Free Cash Flow' in cash_flow.index else 0
            
            growth_rate = info.get('earningsGrowth', 0.05)
            discount_rate = 0.10
            terminal_growth = 0.03
            years = 5
            
            projected_fcf = []
            for year in range(1, years + 1):
                projected_fcf.append(fcf * ((1 + growth_rate) ** year))
            
            pv_fcf = sum([fcf / ((1 + discount_rate) ** (i + 1)) for i, fcf in enumerate(projected_fcf)])
            
            terminal_value = projected_fcf[-1] * (1 + terminal_growth) / (discount_rate - terminal_growth)
            pv_terminal = terminal_value / ((1 + discount_rate) ** years)
            
            enterprise_value = pv_fcf + pv_terminal
            
            cash = info.get('totalCash', 0)
            debt = info.get('totalDebt', 0)
            shares_outstanding = info.get('sharesOutstanding', 1)
            
            equity_value = enterprise_value + cash - debt
            intrinsic_value_per_share = equity_value / shares_outstanding
            
            return {
                'intrinsic_value': intrinsic_value_per_share,
                'current_price': info.get('currentPrice', 0),
                'upside_downside': ((intrinsic_value_per_share - info.get('currentPrice', 0)) / info.get('currentPrice', 1)) * 100
            }
        
        except Exception as e:
            self.logger.error(f"Error calculating DCF for {symbol}: {str(e)}")
            return None
    
    def get_valuation_metrics(self, symbol):
        try:
            fundamental = self.get_fundamental_data(symbol)
            
            valuation = {
                'pe_ratio': fundamental.get('pe_ratio', 0),
                'forward_pe': fundamental.get('forward_pe', 0),
                'peg_ratio': fundamental.get('peg_ratio', 0),
                'price_to_book': fundamental.get('price_to_book', 0),
                'price_to_sales': fundamental.get('price_to_sales', 0),
                'ev_to_revenue': 0,
                'ev_to_ebitda': 0
            }
            
            if fundamental.get('enterprise_value', 0) > 0:
                valuation['ev_to_revenue'] = fundamental['enterprise_value'] / fundamental.get('revenue', 1)
            
            return valuation
        
        except Exception as e:
            self.logger.error(f"Error getting valuation metrics for {symbol}: {str(e)}")
            return {}
    
    def get_profitability_metrics(self, symbol):
        try:
            fundamental = self.get_fundamental_data(symbol)
            
            profitability = {
                'profit_margin': fundamental.get('profit_margin', 0),
                'operating_margin': fundamental.get('operating_margin', 0),
                'roe': fundamental.get('roe', 0),
                'roa': fundamental.get('roa', 0),
                'earnings_growth': fundamental.get('earnings_growth', 0),
                'revenue_growth': fundamental.get('revenue_growth', 0)
            }
            
            return profitability
        
        except Exception as e:
            self.logger.error(f"Error getting profitability metrics for {symbol}: {str(e)}")
            return {}
    
    def get_financial_health(self, symbol):
        try:
            fundamental = self.get_fundamental_data(symbol)
            
            health = {
                'debt_to_equity': fundamental.get('debt_to_equity', 0),
                'current_ratio': fundamental.get('current_ratio', 0),
                'quick_ratio': fundamental.get('quick_ratio', 0),
                'health_score': 0
            }
            
            score = 0
            if health['debt_to_equity'] < 1:
                score += 33
            if health['current_ratio'] > 1.5:
                score += 33
            if health['quick_ratio'] > 1:
                score += 34
            
            health['health_score'] = score
            
            return health
        
        except Exception as e:
            self.logger.error(f"Error getting financial health for {symbol}: {str(e)}")
            return {}