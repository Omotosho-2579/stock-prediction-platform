# src/utils/validators.py

import re
from datetime import datetime
from pathlib import Path
import sys

project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from src.utils.logger import Logger

class Validators:
    def __init__(self):
        self.logger = Logger(__name__)
    
    @staticmethod
    def validate_ticker(ticker):
        if not ticker or not isinstance(ticker, str):
            return False
        
        ticker = ticker.strip().upper()
        
        if len(ticker) < 1 or len(ticker) > 10:
            return False
        
        if not re.match(r'^[A-Z\-\.]+$', ticker):
            return False
        
        return True
    
    @staticmethod
    def validate_email(email):
        if not email or not isinstance(email, str):
            return False
        
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return re.match(pattern, email) is not None
    
    @staticmethod
    def validate_date(date_string, date_format='%Y-%m-%d'):
        try:
            datetime.strptime(date_string, date_format)
            return True
        except:
            return False
    
    @staticmethod
    def validate_date_range(start_date, end_date, date_format='%Y-%m-%d'):
        try:
            start = datetime.strptime(start_date, date_format)
            end = datetime.strptime(end_date, date_format)
            return start <= end
        except:
            return False
    
    @staticmethod
    def validate_price(price):
        try:
            price_float = float(price)
            return price_float > 0
        except:
            return False
    
    @staticmethod
    def validate_shares(shares):
        try:
            shares_float = float(shares)
            return shares_float > 0
        except:
            return False
    
    @staticmethod
    def validate_percentage(value, min_val=0, max_val=100):
        try:
            value_float = float(value)
            return min_val <= value_float <= max_val
        except:
            return False
    
    @staticmethod
    def validate_positive_number(value):
        try:
            num = float(value)
            return num > 0
        except:
            return False
    
    @staticmethod
    def validate_integer(value, min_val=None, max_val=None):
        try:
            int_val = int(value)
            
            if min_val is not None and int_val < min_val:
                return False
            
            if max_val is not None and int_val > max_val:
                return False
            
            return True
        except:
            return False
    
    @staticmethod
    def validate_phone_number(phone):
        if not phone or not isinstance(phone, str):
            return False
        
        phone = re.sub(r'[\s\-\(\)]', '', phone)
        
        return re.match(r'^\+?1?\d{10,15}$', phone) is not None
    
    @staticmethod
    def validate_url(url):
        if not url or not isinstance(url, str):
            return False
        
        pattern = r'^https?:\/\/(www\.)?[-a-zA-Z0-9@:%._\+~#=]{1,256}\.[a-zA-Z0-9()]{1,6}\b([-a-zA-Z0-9()@:%_\+.~#?&//=]*)$'
        return re.match(pattern, url) is not None
    
    @staticmethod
    def validate_portfolio_allocation(allocations):
        try:
            total = sum(allocations.values())
            return 99 <= total <= 101
        except:
            return False
    
    @staticmethod
    def validate_risk_level(risk_level):
        valid_levels = ['Low', 'Medium', 'High', 'Very High']
        return risk_level in valid_levels
    
    @staticmethod
    def validate_file_extension(filename, allowed_extensions):
        if not filename:
            return False
        
        extension = Path(filename).suffix.lower()
        return extension in [ext.lower() if ext.startswith('.') else f'.{ext.lower()}' for ext in allowed_extensions]
    
    @staticmethod
    def validate_json_structure(data, required_keys):
        if not isinstance(data, dict):
            return False
        
        return all(key in data for key in required_keys)