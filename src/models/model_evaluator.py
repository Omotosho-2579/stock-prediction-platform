# src/models/model_evaluator.py

import numpy as np
import pandas as pd
from sklearn.metrics import mean_squared_error, mean_absolute_error, r2_score
from pathlib import Path
import sys

project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from src.utils.logger import Logger

class ModelEvaluator:
    def __init__(self):
        self.logger = Logger(__name__)
    
    def evaluate_model(self, df, model_type, symbol):
        try:
            from src.models.model_loader import ModelLoader
            model_loader = ModelLoader()
            
            model = model_loader.load_or_train(symbol, model_type, df)
            
            if model is None:
                return None
            
            X_train, X_test, y_train, y_test = model.split_data(df)
            
            y_pred = model.predict(X_test)
            
            metrics = self.calculate_metrics(y_test, y_pred)
            metrics['model_type'] = model_type
            metrics['symbol'] = symbol
            
            return metrics
        
        except Exception as e:
            self.logger.error(f"Error evaluating model: {str(e)}")
            return None
    
    def calculate_metrics(self, y_true, y_pred):
        mse = mean_squared_error(y_true, y_pred)
        rmse = np.sqrt(mse)
        mae = mean_absolute_error(y_true, y_pred)
        r2 = r2_score(y_true, y_pred)
        
        mape = np.mean(np.abs((y_true - y_pred) / y_true)) * 100
        
        max_error = np.max(np.abs(y_true - y_pred))
        
        residuals = y_true - y_pred
        residual_std = np.std(residuals)
        
        metrics = {
            'mse': float(mse),
            'rmse': float(rmse),
            'mae': float(mae),
            'r2_score': float(r2),
            'mape': float(mape),
            'max_error': float(max_error),
            'residual_std': float(residual_std)
        }
        
        return metrics
    
    def compare_models(self, df, symbol, model_types=None):
        if model_types is None:
            model_types = ['linear_regression', 'random_forest', 'xgboost', 'ensemble']
        
        comparison_results = []
        
        for model_type in model_types:
            metrics = self.evaluate_model(df, model_type, symbol)
            if metrics:
                comparison_results.append(metrics)
        
        if not comparison_results:
            return None
        
        comparison_df = pd.DataFrame(comparison_results)
        
        comparison_df = comparison_df.sort_values('r2_score', ascending=False)
        
        return comparison_df
    
    def evaluate_prediction_accuracy(self, y_true, y_pred, confidence_level=0.95):
        errors = y_true - y_pred
        
        mean_error = np.mean(errors)
        std_error = np.std(errors)
        
        z_score = 1.96 if confidence_level == 0.95 else 2.576
        confidence_interval = z_score * std_error
        
        accuracy_metrics = {
            'mean_error': float(mean_error),
            'std_error': float(std_error),
            'confidence_interval': float(confidence_interval),
            'lower_bound': float(mean_error - confidence_interval),
            'upper_bound': float(mean_error + confidence_interval)
        }
        
        return accuracy_metrics
    
    def calculate_directional_accuracy(self, y_true, y_pred):
        y_true_series = pd.Series(y_true)
        y_pred_series = pd.Series(y_pred)
        
        true_direction = np.sign(y_true_series.diff().fillna(0))
        pred_direction = np.sign(y_pred_series.diff().fillna(0))
        
        correct_direction = (true_direction == pred_direction).sum()
        total = len(true_direction)
        
        directional_accuracy = (correct_direction / total) * 100
        
        return float(directional_accuracy)
    
    def evaluate_forecasts(self, historical_data, forecasts, actual_future=None):
        evaluation = {
            'forecast_length': len(forecasts),
            'forecast_mean': float(np.mean(forecasts)),
            'forecast_std': float(np.std(forecasts)),
            'forecast_min': float(np.min(forecasts)),
            'forecast_max': float(np.max(forecasts)),
            'trend': 'upward' if forecasts[-1] > forecasts[0] else 'downward'
        }
        
        if actual_future is not None and len(actual_future) == len(forecasts):
            metrics = self.calculate_metrics(actual_future, forecasts)
            evaluation.update(metrics)
        
        return evaluation
    
    def cross_validate_model(self, model, df, n_splits=5):
        from sklearn.model_selection import TimeSeriesSplit
        
        X = model.prepare_features(df)
        y = df['Close']
        
        X = X.drop(columns=['Close'])
        
        tscv = TimeSeriesSplit(n_splits=n_splits)
        
        cv_scores = []
        
        for fold, (train_idx, test_idx) in enumerate(tscv.split(X)):
            X_train, X_test = X.iloc[train_idx], X.iloc[test_idx]
            y_train, y_test = y.iloc[train_idx], y.iloc[test_idx]
            
            try:
                model.train(X_train, y_train)
                y_pred = model.predict(X_test)
                
                r2 = r2_score(y_test, y_pred)
                rmse = np.sqrt(mean_squared_error(y_test, y_pred))
                
                cv_scores.append({
                    'fold': fold + 1,
                    'r2_score': r2,
                    'rmse': rmse
                })
            
            except Exception as e:
                self.logger.error(f"Error in fold {fold + 1}: {str(e)}")
        
        if cv_scores:
            cv_df = pd.DataFrame(cv_scores)
            
            summary = {
                'mean_r2': cv_df['r2_score'].mean(),
                'std_r2': cv_df['r2_score'].std(),
                'mean_rmse': cv_df['rmse'].mean(),
                'std_rmse': cv_df['rmse'].std(),
                'fold_scores': cv_scores
            }
            
            return summary
        
        return None