# tests/test_database.py

import pytest
import sqlite3
import sys
from pathlib import Path
import tempfile

project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.database.db_manager import DBManager

@pytest.fixture
def temp_db():
    temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.db')
    temp_file.close()
    yield temp_file.name
    
    Path(temp_file.name).unlink(missing_ok=True)

@pytest.fixture
def db_manager(temp_db):
    return DBManager(temp_db)

class TestDatabaseManager:
    
    def test_db_initialization(self, db_manager):
        assert db_manager is not None
    
    def test_create_connection(self, db_manager):
        conn = db_manager.get_connection()
        
        assert conn is not None
        assert isinstance(conn, sqlite3.Connection)
        conn.close()
    
    def test_create_tables(self, db_manager):
        db_manager.create_tables()
        
        conn = db_manager.get_connection()
        cursor = conn.cursor()
        
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = cursor.fetchall()
        
        assert len(tables) > 0
        conn.close()
    
    def test_insert_and_retrieve_data(self, db_manager):
        db_manager.create_tables()
        
        test_data = {
            'symbol': 'AAPL',
            'shares': 10,
            'purchase_price': 150.00
        }
        
        result = db_manager.insert_portfolio(test_data)
        assert result is not None
        
        retrieved = db_manager.get_portfolio_by_symbol('AAPL')
        assert retrieved is not None
    
    def test_update_data(self, db_manager):
        db_manager.create_tables()
        
        test_data = {
            'symbol': 'AAPL',
            'shares': 10,
            'purchase_price': 150.00
        }
        
        db_manager.insert_portfolio(test_data)
        
        updated_data = {
            'shares': 15,
            'purchase_price': 155.00
        }
        
        result = db_manager.update_portfolio('AAPL', updated_data)
        assert result is True
    
    def test_delete_data(self, db_manager):
        db_manager.create_tables()
        
        test_data = {
            'symbol': 'AAPL',
            'shares': 10,
            'purchase_price': 150.00
        }
        
        db_manager.insert_portfolio(test_data)
        result = db_manager.delete_portfolio('AAPL')
        
        assert result is True