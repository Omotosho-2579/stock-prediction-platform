# scripts/initialize_data_structure.py

import sys
from pathlib import Path
import json
from datetime import datetime

project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from app.config import DATA_DIR, CACHE_DIR, PREDICTIONS_DIR, SENTIMENT_DIR, DATABASE_PATH
from src.utils.logger import Logger

class DataStructureInitializer:
    def __init__(self):
        self.logger = Logger(__name__)
    
    def create_directories(self):
        directories = [
            DATA_DIR,
            CACHE_DIR,
            PREDICTIONS_DIR,
            SENTIMENT_DIR,
            DATA_DIR / 'backups'
        ]
        
        for directory in directories:
            directory.mkdir(parents=True, exist_ok=True)
            self.logger.info(f"Created directory: {directory}")
        
        print("✓ All data directories created")
    
    def create_readme_files(self):
        cache_readme = CACHE_DIR / 'README.md'
        cache_readme.write_text("""# Cache Directory

This directory stores cached API responses to reduce API calls and improve performance.

## Contents
- Stock historical data (CSV files)
- Format: `{SYMBOL}_{PERIOD}_historical.csv`
- TTL: 24 hours

## Auto-cleanup
Files older than 24 hours are automatically removed.

**Note**: This directory is excluded from version control.
""")
        
        predictions_readme = PREDICTIONS_DIR / 'README.md'
        predictions_readme.write_text("""# Predictions Directory

Stores historical predictions for accuracy tracking and model evaluation.

## Contents
- Prediction results (CSV files)
- Format: `{SYMBOL}_predictions_{YYYY-MM}.csv`

## Structure
Each file contains:
- Date
- Predicted Price
- Actual Price (when available)
- Model Type
- Confidence Score

**Note**: This directory is excluded from version control.
""")
        
        sentiment_readme = SENTIMENT_DIR / 'README.md'
        sentiment_readme.write_text("""# Sentiment Directory

Caches sentiment analysis results from news and social media.

## Contents
- News sentiment data (JSON files)
- Format: `{SYMBOL}_news_{YYYY-MM-DD}.json`
- TTL: 24 hours

## Structure
```json
{
  "symbol": "AAPL",
  "date": "2024-03-15",
  "articles": [...],
  "overall_sentiment": "Positive",
  "sentiment_score": 0.65
}
```

**Note**: This directory is excluded from version control.
""")
        
        print("✓ README files created")
    
    def create_gitignore(self):
        gitignore_content = """# Data files
*.csv
*.db
*.json
*.pkl
*.h5

# Cache
cache/

# Backup files
backups/

# Logs
*.log

# Keep directory structure
!.gitkeep
!README.md
"""
        
        gitignore_path = DATA_DIR / '.gitignore'
        gitignore_path.write_text(gitignore_content)
        
        print("✓ .gitignore created")
    
    def create_gitkeep_files(self):
        directories = [CACHE_DIR, PREDICTIONS_DIR, SENTIMENT_DIR, DATA_DIR / 'backups']
        
        for directory in directories:
            gitkeep = directory / '.gitkeep'
            gitkeep.touch()
        
        print("✓ .gitkeep files created")
    
    def create_sample_data(self):
        sample_cache = {
            'symbol': 'AAPL',
            'period': '2y',
            'data_points': 500,
            'last_updated': datetime.now().isoformat(),
            'note': 'This is a sample cache file structure'
        }
        
        sample_cache_path = CACHE_DIR / 'README_SAMPLE.json'
        with open(sample_cache_path, 'w') as f:
            json.dump(sample_cache, f, indent=2)
        
        sample_prediction = {
            'symbol': 'AAPL',
            'month': '2024-03',
            'predictions': [
                {
                    'date': '2024-03-15',
                    'predicted_price': 175.50,
                    'actual_price': 176.20,
                    'model_type': 'ensemble',
                    'confidence': 0.85
                }
            ],
            'note': 'This is a sample prediction file structure'
        }
        
        sample_prediction_path = PREDICTIONS_DIR / 'README_SAMPLE.json'
        with open(sample_prediction_path, 'w') as f:
            json.dump(sample_prediction, f, indent=2)
        
        sample_sentiment = {
            'symbol': 'AAPL',
            'date': '2024-03-15',
            'articles': [
                {
                    'title': 'Apple announces new product',
                    'sentiment': 'positive',
                    'score': 0.75
                }
            ],
            'overall_sentiment': 'Positive',
            'sentiment_score': 0.65,
            'note': 'This is a sample sentiment file structure'
        }
        
        sample_sentiment_path = SENTIMENT_DIR / 'README_SAMPLE.json'
        with open(sample_sentiment_path, 'w') as f:
            json.dump(sample_sentiment, f, indent=2)
        
        print("✓ Sample data files created")
    
    def initialize_database(self):
        from src.database.db_manager import DBManager
        
        db = DBManager()
        db.initialize_database()
        
        print(f"✓ Database initialized at {DATABASE_PATH}")
    
    def run_full_initialization(self):
        print("\n" + "="*60)
        print("Data Structure Initialization")
        print("="*60 + "\n")
        
        print("Step 1: Creating directories...")
        self.create_directories()
        
        print("\nStep 2: Creating README files...")
        self.create_readme_files()
        
        print("\nStep 3: Creating .gitignore...")
        self.create_gitignore()
        
        print("\nStep 4: Creating .gitkeep files...")
        self.create_gitkeep_files()
        
        print("\nStep 5: Creating sample data files...")
        self.create_sample_data()
        
        print("\nStep 6: Initializing database...")
        self.initialize_database()
        
        print("\n" + "="*60)
        print("✅ Data structure initialization complete!")
        print("="*60)
        print(f"\nData directory: {DATA_DIR}")
        print(f"Database: {DATABASE_PATH}")
        print("\nYou can now run the Streamlit app.")

if __name__ == "__main__":
    initializer = DataStructureInitializer()
    initializer.run_full_initialization()