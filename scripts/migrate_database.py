# scripts/migrate_database.py

import sys
from pathlib import Path
import sqlite3
from datetime import datetime

project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from app.config import DATABASE_PATH, MODELS_DIR
from src.utils.logger import Logger

logger = Logger(__name__)

MIGRATIONS = [
    {
        'version': 1,
        'name': '001_initial_schema',
        'sql': """
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                email TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
            
            CREATE TABLE IF NOT EXISTS portfolios (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                symbol TEXT NOT NULL,
                shares REAL NOT NULL,
                purchase_price REAL NOT NULL,
                purchase_date DATE NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
            );
            
            CREATE TABLE IF NOT EXISTS watchlists (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                symbol TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
                UNIQUE(user_id, symbol)
            );
            
            CREATE INDEX IF NOT EXISTS idx_portfolios_user_id ON portfolios(user_id);
            CREATE INDEX IF NOT EXISTS idx_watchlists_user_id ON watchlists(user_id);
        """
    },
    {
        'version': 2,
        'name': '002_add_alerts_table',
        'sql': """
            CREATE TABLE IF NOT EXISTS alerts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                symbol TEXT NOT NULL,
                alert_type TEXT NOT NULL,
                condition TEXT NOT NULL,
                target_price REAL,
                percentage_change REAL,
                is_active BOOLEAN DEFAULT 1,
                triggered_at TIMESTAMP,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
            );
            
            CREATE INDEX IF NOT EXISTS idx_alerts_user_id ON alerts(user_id);
            CREATE INDEX IF NOT EXISTS idx_alerts_symbol ON alerts(symbol);
            CREATE INDEX IF NOT EXISTS idx_alerts_active ON alerts(is_active);
        """
    },
    {
        'version': 3,
        'name': '003_add_predictions_table',
        'sql': """
            CREATE TABLE IF NOT EXISTS predictions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                symbol TEXT NOT NULL,
                model_type TEXT NOT NULL,
                prediction_date DATE NOT NULL,
                predicted_price REAL NOT NULL,
                actual_price REAL,
                confidence_score REAL,
                forecast_days INTEGER NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
            
            CREATE INDEX IF NOT EXISTS idx_predictions_symbol ON predictions(symbol);
            CREATE INDEX IF NOT EXISTS idx_predictions_date ON predictions(prediction_date);
            CREATE INDEX IF NOT EXISTS idx_predictions_model ON predictions(model_type);
        """
    },
    {
        'version': 4,
        'name': '004_add_trading_signals_table',
        'sql': """
            CREATE TABLE IF NOT EXISTS trading_signals (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                symbol TEXT NOT NULL,
                signal_type TEXT NOT NULL,
                signal_strength REAL NOT NULL,
                confidence REAL NOT NULL,
                entry_price REAL,
                stop_loss REAL,
                take_profit REAL,
                strategy_name TEXT,
                is_active BOOLEAN DEFAULT 1,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                closed_at TIMESTAMP,
                profit_loss REAL
            );
            
            CREATE INDEX IF NOT EXISTS idx_signals_symbol ON trading_signals(symbol);
            CREATE INDEX IF NOT EXISTS idx_signals_active ON trading_signals(is_active);
            CREATE INDEX IF NOT EXISTS idx_signals_date ON trading_signals(created_at);
        """
    },
    {
        'version': 5,
        'name': '005_add_user_preferences',
        'sql': """
            CREATE TABLE IF NOT EXISTS user_preferences (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER UNIQUE NOT NULL,
                theme TEXT DEFAULT 'light',
                default_period TEXT DEFAULT '1y',
                currency TEXT DEFAULT 'USD',
                notifications_enabled BOOLEAN DEFAULT 1,
                email_digest_frequency TEXT DEFAULT 'daily',
                telegram_chat_id TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
            );
        """
    },
    {
        'version': 6,
        'name': '006_add_model_performance_tracking',
        'sql': """
            CREATE TABLE IF NOT EXISTS model_performance (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                symbol TEXT NOT NULL,
                model_type TEXT NOT NULL,
                r2_score REAL,
                rmse REAL,
                mae REAL,
                mape REAL,
                training_samples INTEGER,
                test_samples INTEGER,
                trained_at TIMESTAMP NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
            
            CREATE INDEX IF NOT EXISTS idx_model_perf_symbol ON model_performance(symbol);
            CREATE INDEX IF NOT EXISTS idx_model_perf_model ON model_performance(model_type);
        """
    }
]

def get_connection():
    conn = sqlite3.connect(DATABASE_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def create_migrations_table():
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS schema_migrations (
            version INTEGER PRIMARY KEY,
            name TEXT NOT NULL,
            applied_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    conn.commit()
    conn.close()
    logger.info("Migrations table created")

def get_applied_migrations():
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute("SELECT version FROM schema_migrations ORDER BY version")
    applied = [row[0] for row in cursor.fetchall()]
    
    conn.close()
    return applied

def apply_migration(migration):
    conn = get_connection()
    cursor = conn.cursor()
    
    try:
        logger.info(f"Applying migration {migration['version']}: {migration['name']}")
        
        cursor.executescript(migration['sql'])
        
        cursor.execute(
            "INSERT INTO schema_migrations (version, name) VALUES (?, ?)",
            (migration['version'], migration['name'])
        )
        
        conn.commit()
        logger.info(f"Migration {migration['version']} applied successfully")
        return True
    
    except Exception as e:
        conn.rollback()
        logger.error(f"Error applying migration {migration['version']}: {str(e)}")
        return False
    
    finally:
        conn.close()

def rollback_migration(version):
    conn = get_connection()
    cursor = conn.cursor()
    
    try:
        logger.info(f"Rolling back migration {version}")
        
        cursor.execute("DELETE FROM schema_migrations WHERE version = ?", (version,))
        
        conn.commit()
        logger.info(f"Migration {version} rolled back")
        return True
    
    except Exception as e:
        conn.rollback()
        logger.error(f"Error rolling back migration {version}: {str(e)}")
        return False
    
    finally:
        conn.close()

def migrate_up():
    create_migrations_table()
    applied = get_applied_migrations()
    
    pending_migrations = [m for m in MIGRATIONS if m['version'] not in applied]
    
    if not pending_migrations:
        logger.info("No pending migrations")
        print("✓ Database is up to date")
        return True
    
    logger.info(f"Found {len(pending_migrations)} pending migrations")
    print(f"\nApplying {len(pending_migrations)} migrations:")
    
    for migration in pending_migrations:
        print(f"  → {migration['version']}: {migration['name']}")
        
        if not apply_migration(migration):
            print(f"  ✗ Failed to apply migration {migration['version']}")
            return False
        
        print(f"  ✓ Applied successfully")
    
    print("\n✓ All migrations applied successfully")
    return True

def migrate_down(steps=1):
    applied = get_applied_migrations()
    
    if not applied:
        logger.info("No migrations to rollback")
        print("✓ No migrations to rollback")
        return True
    
    migrations_to_rollback = sorted(applied, reverse=True)[:steps]
    
    print(f"\nRolling back {len(migrations_to_rollback)} migrations:")
    
    for version in migrations_to_rollback:
        migration = next((m for m in MIGRATIONS if m['version'] == version), None)
        
        if migration:
            print(f"  → {version}: {migration['name']}")
        else:
            print(f"  → {version}")
        
        if not rollback_migration(version):
            print(f"  ✗ Failed to rollback migration {version}")
            return False
        
        print(f"  ✓ Rolled back successfully")
    
    print("\n✓ Migrations rolled back successfully")
    print("⚠️  Note: You may need to manually drop tables created by these migrations")
    return True

def get_migration_status():
    create_migrations_table()
    applied = get_applied_migrations()
    
    print("\n" + "="*60)
    print("DATABASE MIGRATION STATUS")
    print("="*60)
    
    print(f"\nDatabase: {DATABASE_PATH}")
    print(f"Total migrations: {len(MIGRATIONS)}")
    print(f"Applied migrations: {len(applied)}")
    print(f"Pending migrations: {len(MIGRATIONS) - len(applied)}")
    
    print("\n" + "-"*60)
    print("Migration History:")
    print("-"*60)
    
    for migration in MIGRATIONS:
        status = "✓ Applied" if migration['version'] in applied else "⧗ Pending"
        print(f"{migration['version']:2d}. {migration['name']:30s} {status}")
    
    print("="*60 + "\n")

def reset_database():
    print("\n⚠️  WARNING: This will delete ALL data in the database!")
    confirm = input("Type 'RESET' to confirm: ")
    
    if confirm != 'RESET':
        print("✓ Operation cancelled")
        return
    
    try:
        if DATABASE_PATH.exists():
            DATABASE_PATH.unlink()
            logger.info("Database deleted")
        
        print("\n✓ Database reset successfully")
        print("Run 'migrate up' to recreate the database schema")
    
    except Exception as e:
        logger.error(f"Error resetting database: {str(e)}")
        print(f"\n✗ Error: {str(e)}")

def main():
    import argparse
    
    parser = argparse.ArgumentParser(description='Database migration tool')
    parser.add_argument('command', choices=['up', 'down', 'status', 'reset'],
                       help='Migration command')
    parser.add_argument('--steps', type=int, default=1,
                       help='Number of migrations to rollback (for down command)')
    
    args = parser.parse_args()
    
    print(f"\n{'='*60}")
    print(f"Stock Prediction Platform - Database Migration")
    print(f"{'='*60}\n")
    
    if args.command == 'up':
        migrate_up()
    elif args.command == 'down':
        migrate_down(args.steps)
    elif args.command == 'status':
        get_migration_status()
    elif args.command == 'reset':
        reset_database()

if __name__ == "__main__":
    main()