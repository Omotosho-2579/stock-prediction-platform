# scripts/backup_database.py

import sys
from pathlib import Path
from datetime import datetime
import shutil

project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from app.config import DATABASE_PATH, DATA_DIR
from src.database.db_manager import DBManager
from src.utils.logger import Logger

class DatabaseBackup:
    def __init__(self):
        self.logger = Logger(__name__)
        self.db = DBManager()
        self.backup_dir = DATA_DIR / 'backups'
        self.backup_dir.mkdir(parents=True, exist_ok=True)
    
    def create_backup(self):
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        backup_filename = f"database_backup_{timestamp}.db"
        backup_path = self.backup_dir / backup_filename
        
        try:
            shutil.copy2(DATABASE_PATH, backup_path)
            
            self.logger.info(f"Database backed up to {backup_path}")
            print(f"✓ Backup created: {backup_filename}")
            
            return backup_path
        
        except Exception as e:
            self.logger.error(f"Backup failed: {str(e)}")
            print(f"✗ Backup failed: {str(e)}")
            return None
    
    def list_backups(self):
        backups = sorted(self.backup_dir.glob("database_backup_*.db"), reverse=True)
        
        print("\n=== Available Backups ===")
        for i, backup in enumerate(backups, 1):
            size_mb = backup.stat().st_size / (1024 * 1024)
            print(f"{i}. {backup.name} ({size_mb:.2f} MB)")
        
        return backups
    
    def restore_backup(self, backup_path):
        try:
            shutil.copy2(backup_path, DATABASE_PATH)
            
            self.logger.info(f"Database restored from {backup_path}")
            print(f"✓ Database restored from {backup_path.name}")
            
            return True
        
        except Exception as e:
            self.logger.error(f"Restore failed: {str(e)}")
            print(f"✗ Restore failed: {str(e)}")
            return False
    
    def cleanup_old_backups(self, keep_count=10):
        backups = sorted(self.backup_dir.glob("database_backup_*.db"), reverse=True)
        
        if len(backups) <= keep_count:
            print(f"No cleanup needed. Current backups: {len(backups)}")
            return
        
        to_delete = backups[keep_count:]
        
        for backup in to_delete:
            backup.unlink()
            print(f"Deleted old backup: {backup.name}")
        
        print(f"Cleaned up {len(to_delete)} old backups")

if __name__ == "__main__":
    backup = DatabaseBackup()
    
    import argparse
    parser = argparse.ArgumentParser(description='Database backup utility')
    parser.add_argument('--create', action='store_true', help='Create new backup')
    parser.add_argument('--list', action='store_true', help='List all backups')
    parser.add_argument('--restore', type=str, help='Restore from backup file')
    parser.add_argument('--cleanup', action='store_true', help='Remove old backups')
    
    args = parser.parse_args()
    
    if args.create:
        backup.create_backup()
    elif args.list:
        backup.list_backups()
    elif args.restore:
        backup_path = backup.backup_dir / args.restore
        if backup_path.exists():
            backup.restore_backup(backup_path)
        else:
            print(f"Backup file not found: {args.restore}")
    elif args.cleanup:
        backup.cleanup_old_backups()
    else:
        print("Use --help to see available options")