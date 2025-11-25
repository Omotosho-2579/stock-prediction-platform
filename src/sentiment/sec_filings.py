# src/sentiment/sec_filings.py

import requests
from datetime import datetime, timedelta
from pathlib import Path
import sys
import re

project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from src.utils.logger import Logger

class SECFilings:
    def __init__(self):
        self.logger = Logger(__name__)
        self.base_url = "https://www.sec.gov"
        self.headers = {
            'User-Agent': 'Stock Prediction Platform contact@example.com',
            'Accept-Encoding': 'gzip, deflate',
            'Host': 'www.sec.gov'
        }
    
    def get_company_cik(self, symbol):
        try:
            url = f"{self.base_url}/cgi-bin/browse-edgar"
            params = {
                'action': 'getcompany',
                'ticker': symbol,
                'output': 'xml'
            }
            
            response = requests.get(url, params=params, headers=self.headers, timeout=10)
            
            if response.status_code == 200:
                match = re.search(r'<CIK>(\d+)</CIK>', response.text)
                if match:
                    cik = match.group(1).zfill(10)
                    return cik
            
            return None
        
        except Exception as e:
            self.logger.error(f"Error getting CIK for {symbol}: {str(e)}")
            return None
    
    def get_recent_filings(self, symbol, filing_types=None, count=10):
        if filing_types is None:
            filing_types = ['10-K', '10-Q', '8-K', '4']
        
        cik = self.get_company_cik(symbol)
        if not cik:
            self.logger.error(f"Could not find CIK for {symbol}")
            return []
        
        try:
            url = f"{self.base_url}/cgi-bin/browse-edgar"
            params = {
                'action': 'getcompany',
                'CIK': cik,
                'type': '',
                'dateb': '',
                'owner': 'exclude',
                'count': count,
                'output': 'xml'
            }
            
            response = requests.get(url, params=params, headers=self.headers, timeout=10)
            
            if response.status_code != 200:
                return []
            
            filings = []
            filing_pattern = r'<filing>.*?<type>(.*?)</type>.*?<filingDate>(.*?)</filingDate>.*?<filingHref>(.*?)</filingHref>.*?</filing>'
            
            matches = re.findall(filing_pattern, response.text, re.DOTALL)
            
            for match in matches:
                filing_type, filing_date, filing_url = match
                
                if filing_type in filing_types:
                    filings.append({
                        'type': filing_type,
                        'date': filing_date,
                        'url': filing_url,
                        'symbol': symbol
                    })
            
            self.logger.info(f"Found {len(filings)} recent filings for {symbol}")
            return filings
        
        except Exception as e:
            self.logger.error(f"Error fetching filings for {symbol}: {str(e)}")
            return []
    
    def get_insider_transactions(self, symbol, months=6):
        cik = self.get_company_cik(symbol)
        if not cik:
            return []
        
        try:
            url = f"{self.base_url}/cgi-bin/browse-edgar"
            params = {
                'action': 'getcompany',
                'CIK': cik,
                'type': '4',
                'dateb': '',
                'owner': 'include',
                'count': 40,
                'output': 'xml'
            }
            
            response = requests.get(url, params=params, headers=self.headers, timeout=10)
            
            if response.status_code != 200:
                return []
            
            transactions = []
            filing_pattern = r'<filing>.*?<filingDate>(.*?)</filingDate>.*?<filingHref>(.*?)</filingHref>.*?</filing>'
            
            matches = re.findall(filing_pattern, response.text, re.DOTALL)
            
            cutoff_date = datetime.now() - timedelta(days=months * 30)
            
            for match in matches:
                filing_date_str, filing_url = match
                
                try:
                    filing_date = datetime.strptime(filing_date_str, '%Y-%m-%d')
                    
                    if filing_date >= cutoff_date:
                        transactions.append({
                            'date': filing_date_str,
                            'url': filing_url,
                            'type': 'Form 4 - Insider Transaction',
                            'symbol': symbol
                        })
                except:
                    pass
            
            self.logger.info(f"Found {len(transactions)} insider transactions for {symbol}")
            return transactions
        
        except Exception as e:
            self.logger.error(f"Error fetching insider transactions: {str(e)}")
            return []
    
    def analyze_insider_sentiment(self, transactions):
        if not transactions:
            return {
                'sentiment': 'Neutral',
                'score': 0,
                'buy_count': 0,
                'sell_count': 0,
                'recent_activity': 'Low'
            }
        
        recent_transactions = transactions[:10]
        
        buy_keywords = ['purchase', 'acquisition', 'option exercise']
        sell_keywords = ['sale', 'disposition']
        
        buy_count = 0
        sell_count = 0
        
        for trans in recent_transactions:
            trans_text = str(trans).lower()
            
            if any(keyword in trans_text for keyword in buy_keywords):
                buy_count += 1
            elif any(keyword in trans_text for keyword in sell_keywords):
                sell_count += 1
        
        if buy_count > sell_count:
            sentiment = 'Bullish'
            score = min(100, (buy_count / max(sell_count, 1)) * 30)
        elif sell_count > buy_count:
            sentiment = 'Bearish'
            score = -min(100, (sell_count / max(buy_count, 1)) * 30)
        else:
            sentiment = 'Neutral'
            score = 0
        
        if len(transactions) > 5:
            activity = 'High'
        elif len(transactions) > 2:
            activity = 'Moderate'
        else:
            activity = 'Low'
        
        return {
            'sentiment': sentiment,
            'score': round(score, 2),
            'buy_count': buy_count,
            'sell_count': sell_count,
            'total_transactions': len(transactions),
            'recent_activity': activity
        }
    
    def get_filing_summary(self, symbol):
        filings = self.get_recent_filings(symbol, count=20)
        insider_trans = self.get_insider_transactions(symbol)
        
        filing_counts = {}
        for filing in filings:
            filing_type = filing['type']
            filing_counts[filing_type] = filing_counts.get(filing_type, 0) + 1
        
        insider_sentiment = self.analyze_insider_sentiment(insider_trans)
        
        summary = {
            'symbol': symbol,
            'recent_filings': len(filings),
            'filing_breakdown': filing_counts,
            'insider_transactions': len(insider_trans),
            'insider_sentiment': insider_sentiment,
            'latest_filings': filings[:5],
            'latest_insider_activity': insider_trans[:5]
        }
        
        return summary
    
    def check_recent_8k(self, symbol, days=30):
        filings = self.get_recent_filings(symbol, filing_types=['8-K'], count=10)
        
        cutoff_date = datetime.now() - timedelta(days=days)
        
        recent_8k = []
        for filing in filings:
            try:
                filing_date = datetime.strptime(filing['date'], '%Y-%m-%d')
                if filing_date >= cutoff_date:
                    recent_8k.append(filing)
            except:
                pass
        
        return recent_8k
    
    def check_earnings_report(self, symbol):
        filings = self.get_recent_filings(symbol, filing_types=['10-Q', '10-K'], count=5)
        
        if not filings:
            return None
        
        latest_filing = filings[0]
        
        return {
            'type': latest_filing['type'],
            'date': latest_filing['date'],
            'url': latest_filing['url'],
            'is_annual': latest_filing['type'] == '10-K'
        }
    
    def get_sec_data_summary(self, symbol):
        try:
            filing_summary = self.get_filing_summary(symbol)
            recent_8k = self.check_recent_8k(symbol)
            earnings = self.check_earnings_report(symbol)
            
            has_material_events = len(recent_8k) > 0
            
            insider_sentiment = filing_summary['insider_sentiment']['sentiment']
            
            summary = {
                'symbol': symbol,
                'total_filings': filing_summary['recent_filings'],
                'insider_sentiment': insider_sentiment,
                'insider_score': filing_summary['insider_sentiment']['score'],
                'has_recent_8k': has_material_events,
                'recent_8k_count': len(recent_8k),
                'latest_earnings_report': earnings,
                'insider_buy_count': filing_summary['insider_sentiment']['buy_count'],
                'insider_sell_count': filing_summary['insider_sentiment']['sell_count'],
                'data_freshness': 'Current'
            }
            
            return summary
        
        except Exception as e:
            self.logger.error(f"Error getting SEC summary for {symbol}: {str(e)}")
            return None