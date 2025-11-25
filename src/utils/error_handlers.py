# src/utils/error_handlers.py

import traceback
from pathlib import Path
import sys

project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from src.utils.logger import Logger

class StockPredictionError(Exception):
    def __init__(self, message, error_code=None, details=None):
        self.message = message
        self.error_code = error_code
        self.details = details
        super().__init__(self.message)
    
    def __str__(self):
        if self.error_code:
            return f"[{self.error_code}] {self.message}"
        return self.message

class DataLoadError(StockPredictionError):
    def __init__(self, message, symbol=None):
        self.symbol = symbol
        super().__init__(message, error_code='DATA_LOAD_ERROR', details={'symbol': symbol})

class ModelError(StockPredictionError):
    def __init__(self, message, model_type=None):
        self.model_type = model_type
        super().__init__(message, error_code='MODEL_ERROR', details={'model_type': model_type})

class ValidationError(StockPredictionError):
    def __init__(self, message, field=None):
        self.field = field
        super().__init__(message, error_code='VALIDATION_ERROR', details={'field': field})

class APIError(StockPredictionError):
    def __init__(self, message, api_name=None, status_code=None):
        self.api_name = api_name
        self.status_code = status_code
        super().__init__(message, error_code='API_ERROR', details={'api': api_name, 'status': status_code})

class DatabaseError(StockPredictionError):
    def __init__(self, message, operation=None):
        self.operation = operation
        super().__init__(message, error_code='DATABASE_ERROR', details={'operation': operation})

def handle_error(error, logger=None, show_traceback=False):
    if logger is None:
        logger = Logger(__name__)
    
    error_message = str(error)
    error_type = type(error).__name__
    
    if isinstance(error, StockPredictionError):
        logger.error(f"{error_type}: {error_message}")
        
        if error.details:
            logger.error(f"Details: {error.details}")
    else:
        logger.error(f"Unexpected {error_type}: {error_message}")
    
    if show_traceback:
        logger.error(f"Traceback:\n{traceback.format_exc()}")
    
    return {
        'success': False,
        'error_type': error_type,
        'error_message': error_message,
        'error_code': getattr(error, 'error_code', None),
        'details': getattr(error, 'details', None)
    }

def safe_execute(func, *args, default_return=None, logger=None, **kwargs):
    try:
        return func(*args, **kwargs)
    except Exception as e:
        if logger:
            handle_error(e, logger)
        return default_return

def validate_and_execute(validation_func, execution_func, error_message="Validation failed"):
    def wrapper(*args, **kwargs):
        if not validation_func(*args, **kwargs):
            raise ValidationError(error_message)
        
        return execution_func(*args, **kwargs)
    
    return wrapper

class ErrorContext:
    def __init__(self, operation_name, logger=None, raise_error=True):
        self.operation_name = operation_name
        self.logger = logger or Logger(__name__)
        self.raise_error = raise_error
    
    def __enter__(self):
        self.logger.info(f"Starting: {self.operation_name}")
        return self
    
    def __exit__(self, exc_type, exc_value, exc_traceback):
        if exc_type is not None:
            self.logger.error(f"Error in {self.operation_name}: {exc_value}")
            handle_error(exc_value, self.logger, show_traceback=True)
            
            if not self.raise_error:
                return True
        else:
            self.logger.info(f"Completed: {self.operation_name}")
        
        return False