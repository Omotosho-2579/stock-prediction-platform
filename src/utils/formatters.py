# src/utils/formatters.py

from datetime import datetime
import locale
from pathlib import Path
import sys

project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from src.utils.logger import Logger

class Formatters:
    def __init__(self):
        self.logger = Logger(__name__)
        try:
            locale.setlocale(locale.LC_ALL, '')
        except:
            pass
    
    @staticmethod
    def format_currency(amount, currency_symbol='$', decimal_places=2):
        try:
            return f"{currency_symbol}{amount:,.{decimal_places}f}"
        except:
            return f"{currency_symbol}0.00"
    
    @staticmethod
    def format_number(number, decimal_places=0):
        try:
            return f"{number:,.{decimal_places}f}"
        except:
            return "0"
    
    @staticmethod
    def format_percentage(value, decimal_places=2, include_sign=False):
        try:
            if include_sign:
                return f"{value:+.{decimal_places}f}%"
            return f"{value:.{decimal_places}f}%"
        except:
            return "0.00%"
    
    @staticmethod
    def format_large_number(number):
        try:
            abs_num = abs(number)
            sign = '-' if number < 0 else ''
            
            if abs_num >= 1_000_000_000_000:
                return f"{sign}{abs_num/1_000_000_000_000:.2f}T"
            elif abs_num >= 1_000_000_000:
                return f"{sign}{abs_num/1_000_000_000:.2f}B"
            elif abs_num >= 1_000_000:
                return f"{sign}{abs_num/1_000_000:.2f}M"
            elif abs_num >= 1_000:
                return f"{sign}{abs_num/1_000:.2f}K"
            else:
                return f"{sign}{abs_num:.2f}"
        except:
            return "0"
    
    @staticmethod
    def format_date(date, format_type='ISO'):
        try:
            if isinstance(date, str):
                date = datetime.strptime(date, '%Y-%m-%d')
            
            formats = {
                'ISO': '%Y-%m-%d',
                'US': '%m/%d/%Y',
                'EU': '%d/%m/%Y',
                'LONG': '%B %d, %Y',
                'SHORT': '%m/%d/%y',
                'DATETIME': '%Y-%m-%d %H:%M:%S'
            }
            
            date_format = formats.get(format_type, '%Y-%m-%d')
            return date.strftime(date_format)
        except:
            return ''
    
    @staticmethod
    def format_time_ago(date):
        try:
            if isinstance(date, str):
                date = datetime.strptime(date, '%Y-%m-%d %H:%M:%S')
            
            now = datetime.now()
            diff = now - date
            
            seconds = diff.total_seconds()
            
            if seconds < 60:
                return "just now"
            elif seconds < 3600:
                minutes = int(seconds / 60)
                return f"{minutes} minute{'s' if minutes != 1 else ''} ago"
            elif seconds < 86400:
                hours = int(seconds / 3600)
                return f"{hours} hour{'s' if hours != 1 else ''} ago"
            elif seconds < 2592000:
                days = int(seconds / 86400)
                return f"{days} day{'s' if days != 1 else ''} ago"
            elif seconds < 31536000:
                months = int(seconds / 2592000)
                return f"{months} month{'s' if months != 1 else ''} ago"
            else:
                years = int(seconds / 31536000)
                return f"{years} year{'s' if years != 1 else ''} ago"
        except:
            return ''
    
    @staticmethod
    def format_duration(seconds):
        try:
            if seconds < 60:
                return f"{int(seconds)}s"
            elif seconds < 3600:
                minutes = int(seconds / 60)
                secs = int(seconds % 60)
                return f"{minutes}m {secs}s"
            else:
                hours = int(seconds / 3600)
                minutes = int((seconds % 3600) / 60)
                return f"{hours}h {minutes}m"
        except:
            return "0s"
    
    @staticmethod
    def format_file_size(bytes_size):
        try:
            for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
                if bytes_size < 1024.0:
                    return f"{bytes_size:.2f} {unit}"
                bytes_size /= 1024.0
            return f"{bytes_size:.2f} PB"
        except:
            return "0 B"
    
    @staticmethod
    def parse_date(date_string, input_format='%Y-%m-%d'):
        try:
            return datetime.strptime(date_string, input_format)
        except:
            return None
    
    @staticmethod
    def parse_number(number_string):
        try:
            cleaned = number_string.replace(',', '').replace('$', '').strip()
            return float(cleaned)
        except:
            return 0.0
    
    @staticmethod
    def format_ticker(ticker):
        if not ticker:
            return ''
        return ticker.upper().strip()
    
    @staticmethod
    def format_phone_number(phone, country_code='US'):
        try:
            digits = ''.join(filter(str.isdigit, phone))
            
            if country_code == 'US' and len(digits) == 10:
                return f"({digits[:3]}) {digits[3:6]}-{digits[6:]}"
            
            return phone
        except:
            return phone
    
    @staticmethod
    def truncate_text(text, max_length, suffix='...'):
        if len(text) <= max_length:
            return text
        return text[:max_length - len(suffix)] + suffix