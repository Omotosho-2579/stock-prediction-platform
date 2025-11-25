# scripts/pretrain_models.py

import sys
from pathlib import Path

project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from app.config import POPULAR_STOCKS, MODELS_DIR, POPULAR_MODELS_DIR
from src.data.data_loader import DataLoader
from src.models.model_trainer import ModelTrainer
from src.models.model_registry import ModelRegistry
from src.utils.logger import Logger
import json
from datetime import datetime

class ModelPretrainer:
    def __init__(self):
        self.logger = Logger(__name__)
        self.data_loader = DataLoader()
        self.trainer = ModelTrainer()
        self.registry = ModelRegistry()
        
        POPULAR_MODELS_DIR.mkdir(parents=True, exist_ok=True)
    
    def pretrain_popular_stocks(self, stocks=None):
        if stocks is None:
            stocks = POPULAR_STOCKS[:10]
        
        self.logger.info(f"Starting pretraining for {len(stocks)} stocks")
        
        results = []
        
        for i, symbol in enumerate(stocks, 1):
            self.logger.info(f"[{i}/{len(stocks)}] Training models for {symbol}")
            
            try:
                df = self.data_loader.load_stock_data(symbol, period='2y')
                
                if df is None or df.empty:
                    self.logger.error(f"Failed to load data for {symbol}")
                    continue
                
                ensemble_model = self.trainer.train_model('ensemble', *self.trainer.train_all_models(df).split_data(df))
                
                if ensemble_model:
                    model_path = POPULAR_MODELS_DIR / f"{symbol}_ensemble.pkl"
                    ensemble_model.save_model(model_path)
                    
                    X_train, X_test, y_train, y_test = ensemble_model.split_data(df)
                    metrics = ensemble_model.evaluate(X_test, y_test)
                    
                    self.registry.register_model(symbol, 'ensemble', metrics, is_popular=True)
                    
                    results.append({
                        'symbol': symbol,
                        'status': 'success',
                        'metrics': metrics
                    })
                    
                    self.logger.info(f"Successfully trained {symbol} - R²: {metrics['r2_score']:.4f}")
                else:
                    results.append({
                        'symbol': symbol,
                        'status': 'failed',
                        'error': 'Model training failed'
                    })
            
            except Exception as e:
                self.logger.error(f"Error training {symbol}: {str(e)}")
                results.append({
                    'symbol': symbol,
                    'status': 'error',
                    'error': str(e)
                })
        
        self._save_training_report(results)
        
        return results
    
    def _save_training_report(self, results):
        report = {
            'training_date': datetime.now().isoformat(),
            'total_stocks': len(results),
            'successful': len([r for r in results if r['status'] == 'success']),
            'failed': len([r for r in results if r['status'] != 'success']),
            'results': results
        }
        
        report_path = MODELS_DIR / 'pretraining_report.json'
        
        with open(report_path, 'w') as f:
            json.dump(report, f, indent=2)
        
        self.logger.info(f"Training report saved to {report_path}")

if __name__ == "__main__":
    pretrainer = ModelPretrainer()
    
    print("Starting model pretraining for popular stocks...")
    print("This may take 10-30 minutes depending on your system.")
    
    results = pretrainer.pretrain_popular_stocks()
    
    successful = len([r for r in results if r['status'] == 'success'])
    print(f"\nPretraining complete: {successful}/{len(results)} models trained successfully")