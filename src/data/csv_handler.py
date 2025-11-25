# src/data/csv_handler.py

import pandas as pd
import io
from pathlib import Path
import sys

project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from src.data.data_validator import DataValidator
from src.utils.logger import Logger

class CSVHandler:
    def __init__(self):
        self.validator = DataValidator()
        self.logger = Logger(__name__)
    
    def read_csv(self, file_path_or_buffer, parse_dates=True):
        try:
            if isinstance(file_path_or_buffer, str):
                df = pd.read_csv(file_path_or_buffer)
            else:
                df = pd.read_csv(file_path_or_buffer)
            
            df.columns = df.columns.str.strip()
            
            if parse_dates and 'Date' in df.columns:
                df['Date'] = pd.to_datetime(df['Date'])
                df.set_index('Date', inplace=True)
            elif parse_dates and df.index.name == 'Date':
                df.index = pd.to_datetime(df.index)
            
            self.logger.info(f"Successfully loaded CSV with {len(df)} rows")
            return df
        
        except Exception as e:
            self.logger.error(f"Error reading CSV: {str(e)}")
            return None
    
    def read_uploaded_file(self, uploaded_file):
        try:
            if uploaded_file is None:
                return None
            
            file_extension = uploaded_file.name.split('.')[-1].lower()
            
            if file_extension == 'csv':
                df = pd.read_csv(uploaded_file)
            elif file_extension in ['xls', 'xlsx']:
                df = pd.read_excel(uploaded_file)
            else:
                self.logger.error(f"Unsupported file format: {file_extension}")
                return None
            
            df.columns = df.columns.str.strip()
            
            if 'Date' in df.columns:
                df['Date'] = pd.to_datetime(df['Date'])
                df.set_index('Date', inplace=True)
            
            df = self.validator.validate_and_clean(df)
            
            self.logger.info(f"Successfully loaded uploaded file: {uploaded_file.name}")
            return df
        
        except Exception as e:
            self.logger.error(f"Error reading uploaded file: {str(e)}")
            return None
    
    def validate_csv_format(self, df):
        required_columns = ['Open', 'High', 'Low', 'Close', 'Volume']
        
        missing_columns = [col for col in required_columns if col not in df.columns]
        
        if missing_columns:
            self.logger.error(f"Missing required columns: {missing_columns}")
            return False, f"Missing columns: {', '.join(missing_columns)}"
        
        for col in required_columns:
            if not pd.api.types.is_numeric_dtype(df[col]):
                return False, f"Column '{col}' must contain numeric data"
        
        if df.empty:
            return False, "CSV file is empty"
        
        if len(df) < 10:
            return False, "CSV file must contain at least 10 rows of data"
        
        return True, "CSV format is valid"
    
    def save_to_csv(self, df, file_path, include_index=True):
        try:
            df.to_csv(file_path, index=include_index)
            self.logger.info(f"Data saved to {file_path}")
            return True
        
        except Exception as e:
            self.logger.error(f"Error saving to CSV: {str(e)}")
            return False
    
    def parse_portfolio_csv(self, uploaded_file):
        try:
            df = pd.read_csv(uploaded_file)
            df.columns = df.columns.str.strip()
            
            required_columns = ['Symbol', 'Shares', 'Purchase Price']
            missing = [col for col in required_columns if col not in df.columns]
            
            if missing:
                return None, f"Missing required columns: {', '.join(missing)}"
            
            if 'Purchase Date' in df.columns:
                df['Purchase Date'] = pd.to_datetime(df['Purchase Date'])
            
            df['Symbol'] = df['Symbol'].str.upper().str.strip()
            
            df['Shares'] = pd.to_numeric(df['Shares'], errors='coerce')
            df['Purchase Price'] = pd.to_numeric(df['Purchase Price'], errors='coerce')
            
            df = df.dropna(subset=['Symbol', 'Shares', 'Purchase Price'])
            
            portfolio_list = df.to_dict('records')
            
            self.logger.info(f"Parsed portfolio with {len(portfolio_list)} positions")
            return portfolio_list, None
        
        except Exception as e:
            self.logger.error(f"Error parsing portfolio CSV: {str(e)}")
            return None, str(e)
    
    def export_portfolio_csv(self, portfolio_data):
        try:
            df = pd.DataFrame(portfolio_data)
            
            csv_buffer = io.StringIO()
            df.to_csv(csv_buffer, index=False)
            
            return csv_buffer.getvalue()
        
        except Exception as e:
            self.logger.error(f"Error exporting portfolio CSV: {str(e)}")
            return None
    
    def parse_watchlist_csv(self, uploaded_file):
        try:
            df = pd.read_csv(uploaded_file)
            df.columns = df.columns.str.strip()
            
            if 'Symbol' not in df.columns:
                return None, "CSV must contain 'Symbol' column"
            
            symbols = df['Symbol'].str.upper().str.strip().tolist()
            symbols = [s for s in symbols if s]
            
            self.logger.info(f"Parsed watchlist with {len(symbols)} symbols")
            return symbols, None
        
        except Exception as e:
            self.logger.error(f"Error parsing watchlist CSV: {str(e)}")
            return None, str(e)