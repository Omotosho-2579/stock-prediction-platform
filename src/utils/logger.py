# src/utils/logger.py

import logging
from pathlib import Path
import sys

project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from app.config import LOG_LEVEL, LOG_FORMAT, LOG_FILE

class Logger:
    _loggers = {}
    
    def __init__(self, name):
        if name in Logger._loggers:
            self.logger = Logger._loggers[name]
        else:
            self.logger = self._setup_logger(name)
            Logger._loggers[name] = self.logger
    
    def _setup_logger(self, name):
        logger = logging.getLogger(name)
        
        log_level = getattr(logging, LOG_LEVEL.upper(), logging.INFO)
        logger.setLevel(log_level)
        
        if logger.handlers:
            return logger
        
        formatter = logging.Formatter(LOG_FORMAT)
        
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(log_level)
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)
        
        try:
            log_dir = Path(LOG_FILE).parent
            log_dir.mkdir(parents=True, exist_ok=True)
            
            file_handler = logging.FileHandler(LOG_FILE)
            file_handler.setLevel(log_level)
            file_handler.setFormatter(formatter)
            logger.addHandler(file_handler)
        except Exception as e:
            logger.warning(f"Could not create file handler: {str(e)}")
        
        return logger
    
    def debug(self, message):
        self.logger.debug(message)
    
    def info(self, message):
        self.logger.info(message)
    
    def warning(self, message):
        self.logger.warning(message)
    
    def error(self, message):
        self.logger.error(message)
    
    def critical(self, message):
        self.logger.critical(message)
    
    def exception(self, message):
        self.logger.exception(message)