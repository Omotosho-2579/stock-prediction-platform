# src/database/db_manager.py

import sqlite3
from pathlib import Path
import sys

project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from app.config import DATABASE_PATH
from src.utils.logger import Logger

class DBManager:
    def __init__(self, db_path=None):
        self.logger = Logger(__name__)
        self.db_path = db_path or DATABASE_PATH
        self.connection = None
        self._ensure_database_exists()
    
    def _ensure_database_exists(self):
        db_dir = Path(self.db_path).parent
        db_dir.mkdir(parents=True, exist_ok=True)
        
        if not Path(self.db_path).exists():
            self.logger.info(f"Creating new database at {self.db_path}")
            self.initialize_database()
    
    def connect(self):
        try:
            self.connection = sqlite3.connect(self.db_path)
            self.connection.row_factory = sqlite3.Row
            self.logger.info("Database connection established")
            return self.connection
        
        except Exception as e:
            self.logger.error(f"Error connecting to database: {str(e)}")
            return None
    
    def disconnect(self):
        if self.connection:
            self.connection.close()
            self.connection = None
            self.logger.info("Database connection closed")
    
    def execute_query(self, query, params=None):
        try:
            if not self.connection:
                self.connect()
            
            cursor = self.connection.cursor()
            
            if params:
                cursor.execute(query, params)
            else:
                cursor.execute(query)
            
            self.connection.commit()
            
            return cursor
        
        except Exception as e:
            self.logger.error(f"Error executing query: {str(e)}")
            if self.connection:
                self.connection.rollback()
            return None
    
    def fetch_all(self, query, params=None):
        try:
            cursor = self.execute_query(query, params)
            
            if cursor:
                results = cursor.fetchall()
                return [dict(row) for row in results]
            
            return []
        
        except Exception as e:
            self.logger.error(f"Error fetching data: {str(e)}")
            return []
    
    def fetch_one(self, query, params=None):
        try:
            cursor = self.execute_query(query, params)
            
            if cursor:
                result = cursor.fetchone()
                return dict(result) if result else None
            
            return None
        
        except Exception as e:
            self.logger.error(f"Error fetching data: {str(e)}")
            return None
    
    def initialize_database(self):
        migrations_dir = Path(__file__).parent / "migrations"
        
        migration_files = sorted(migrations_dir.glob("*.sql"))
        
        for migration_file in migration_files:
            self.logger.info(f"Running migration: {migration_file.name}")
            self.run_migration(migration_file)
    
    def run_migration(self, migration_file):
        try:
            with open(migration_file, 'r') as f:
                sql_script = f.read()
            
            if not self.connection:
                self.connect()
            
            self.connection.executescript(sql_script)
            self.connection.commit()
            
            self.logger.info(f"Migration {migration_file.name} completed successfully")
            return True
        
        except Exception as e:
            self.logger.error(f"Error running migration {migration_file.name}: {str(e)}")
            return False
    
    def table_exists(self, table_name):
        query = "SELECT name FROM sqlite_master WHERE type='table' AND name=?"
        result = self.fetch_one(query, (table_name,))
        return result is not None
    
    def get_table_schema(self, table_name):
        query = f"PRAGMA table_info({table_name})"
        return self.fetch_all(query)
    
    def backup_database(self, backup_path):
        try:
            import shutil
            shutil.copy2(self.db_path, backup_path)
            self.logger.info(f"Database backed up to {backup_path}")
            return True
        
        except Exception as e:
            self.logger.error(f"Error backing up database: {str(e)}")
            return False