# src/models/hyperparameter_tuner.py

import numpy as np
import pandas as pd
from sklearn.model_selection import GridSearchCV, TimeSeriesSplit
from pathlib import Path
import sys

project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from src.models.random_forest import RandomForestModel
from src.models.xgboost_model import XGBoostModel
from src.utils.logger import Logger

class HyperparameterTuner:
    def __init__(self):
        self.logger = Logger(__name__)
    
    def tune_random_forest(self, X_train, y_train, cv=3):
        self.logger.info("Tuning Random Forest hyperparameters")
        
        param_grid = {
            'n_estimators': [50, 100, 200],
            'max_depth': [None, 10, 20, 30],
            'min_samples_split': [2, 5, 10],
            'min_samples_leaf': [1, 2, 4]
        }
        
        from sklearn.ensemble import RandomForestRegressor
        base_model = RandomForestRegressor(random_state=42)
        
        tscv = TimeSeriesSplit(n_splits=cv)
        
        grid_search = GridSearchCV(
            estimator=base_model,
            param_grid=param_grid,
            cv=tscv,
            scoring='r2',
            n_jobs=-1,
            verbose=1
        )
        
        grid_search.fit(X_train, y_train)
        
        best_params = grid_search.best_params_
        best_score = grid_search.best_score_
        
        self.logger.info(f"Best Random Forest params: {best_params}")
        self.logger.info(f"Best CV score: {best_score:.4f}")
        
        return best_params, best_score
    
    def tune_xgboost(self, X_train, y_train, cv=3):
        self.logger.info("Tuning XGBoost hyperparameters")
        
        param_grid = {
            'n_estimators': [50, 100, 200],
            'max_depth': [3, 6, 9],
            'learning_rate': [0.01, 0.1, 0.3],
            'subsample': [0.8, 1.0],
            'colsample_bytree': [0.8, 1.0]
        }
        
        try:
            import xgboost as xgb
            base_model = xgb.XGBRegressor(random_state=42, verbosity=0)
            
            tscv = TimeSeriesSplit(n_splits=cv)
            
            grid_search = GridSearchCV(
                estimator=base_model,
                param_grid=param_grid,
                cv=tscv,
                scoring='r2',
                n_jobs=-1,
                verbose=1
            )
            
            grid_search.fit(X_train, y_train)
            
            best_params = grid_search.best_params_
            best_score = grid_search.best_score_
            
            self.logger.info(f"Best XGBoost params: {best_params}")
            self.logger.info(f"Best CV score: {best_score:.4f}")
            
            return best_params, best_score
        
        except ImportError:
            self.logger.error("XGBoost not available")
            return None, None
    
    def tune_lstm(self, X_train, y_train, lookback_values=[30, 60, 90]):
        self.logger.info("Tuning LSTM hyperparameters")
        
        best_lookback = None
        best_score = -np.inf
        results = []
        
        from sklearn.metrics import r2_score
        
        for lookback in lookback_values:
            try:
                from src.models.lstm_model import LSTMModel
                
                model = LSTMModel(lookback=lookback)
                
                if isinstance(X_train, pd.DataFrame):
                    train_data = X_train['Close'].values
                else:
                    train_data = X_train
                
                X_seq, y_seq = model.prepare_sequences(train_data)
                
                split_idx = int(len(X_seq) * 0.8)
                X_train_seq = X_seq[:split_idx]
                y_train_seq = y_seq[:split_idx]
                X_val_seq = X_seq[split_idx:]
                y_val_seq = y_seq[split_idx:]
                
                model.build(input_shape=(lookback, 1))
                
                model.model.fit(
                    X_train_seq, y_train_seq,
                    validation_data=(X_val_seq, y_val_seq),
                    epochs=20,
                    batch_size=32,
                    verbose=0
                )
                
                y_pred = model.model.predict(X_val_seq, verbose=0)
                score = r2_score(y_val_seq, y_pred)
                
                results.append({
                    'lookback': lookback,
                    'r2_score': score
                })
                
                self.logger.info(f"Lookback {lookback}: R² = {score:.4f}")
                
                if score > best_score:
                    best_score = score
                    best_lookback = lookback
            
            except Exception as e:
                self.logger.error(f"Error tuning LSTM with lookback {lookback}: {str(e)}")
        
        if best_lookback:
            self.logger.info(f"Best LSTM lookback: {best_lookback} (R² = {best_score:.4f})")
            return {'lookback': best_lookback}, best_score
        
        return None, None
    
    def tune_model(self, model_type, X_train, y_train, cv=3):
        if model_type == 'random_forest':
            return self.tune_random_forest(X_train, y_train, cv)
        elif model_type == 'xgboost':
            return self.tune_xgboost(X_train, y_train, cv)
        elif model_type == 'lstm':
            return self.tune_lstm(X_train, y_train)
        else:
            self.logger.error(f"Tuning not supported for model type: {model_type}")
            return None, None
    
    def optimize_ensemble_weights(self, models, X_val, y_val):
        from scipy.optimize import differential_evolution
        
        def objective(weights):
            ensemble_pred = np.zeros(len(y_val))
            
            for i, model in enumerate(models):
                try:
                    pred = model.predict(X_val)
                    ensemble_pred += pred * weights[i]
                except:
                    pass
            
            mse = np.mean((y_val - ensemble_pred) ** 2)
            return mse
        
        bounds = [(0, 1) for _ in range(len(models))]
        
        result = differential_evolution(
            objective,
            bounds,
            maxiter=100,
            popsize=15,
            seed=42
        )
        
        optimized_weights = result.x
        optimized_weights = optimized_weights / optimized_weights.sum()
        
        self.logger.info(f"Optimized ensemble weights: {optimized_weights}")
        
        return optimized_weights
    
    def cross_validate_with_tuning(self, model_type, df, n_splits=5):
        from src.models.base_model import BaseModel
        
        base_model = BaseModel("temp")
        X = base_model.prepare_features(df)
        y = df['Close']
        
        X = X.drop(columns=['Close'])
        
        tscv = TimeSeriesSplit(n_splits=n_splits)
        
        cv_results = []
        
        for fold, (train_idx, test_idx) in enumerate(tscv.split(X)):
            self.logger.info(f"Processing fold {fold + 1}/{n_splits}")
            
            X_train_fold = X.iloc[train_idx]
            y_train_fold = y.iloc[train_idx]
            X_test_fold = X.iloc[test_idx]
            y_test_fold = y.iloc[test_idx]
            
            best_params, best_score = self.tune_model(model_type, X_train_fold, y_train_fold, cv=3)
            
            if best_params:
                if model_type == 'random_forest':
                    model = RandomForestModel(**best_params)
                elif model_type == 'xgboost':
                    model = XGBoostModel(**best_params)
                else:
                    continue
                
                model.build()
                model.train(X_train_fold, y_train_fold)
                
                metrics = model.evaluate(X_test_fold, y_test_fold)
                
                cv_results.append({
                    'fold': fold + 1,
                    'best_params': best_params,
                    'metrics': metrics
                })
        
        if cv_results:
            avg_r2 = np.mean([r['metrics']['r2_score'] for r in cv_results])
            avg_rmse = np.mean([r['metrics']['rmse'] for r in cv_results])
            
            self.logger.info(f"Cross-validation complete - Avg R²: {avg_r2:.4f}, Avg RMSE: {avg_rmse:.4f}")
            
            return {
                'fold_results': cv_results,
                'avg_r2': avg_r2,
                'avg_rmse': avg_rmse
            }
        
        return None
    
    def grid_search_ensemble(self, df, weight_combinations=None):
        from src.models.model_trainer import ModelTrainer
        
        trainer = ModelTrainer()
        models_dict = trainer.train_all_models(df)
        
        if len(models_dict) < 2:
            self.logger.error("Need at least 2 models for ensemble tuning")
            return None
        
        base_model = list(models_dict.values())[0]
        X_train, X_test, y_train, y_test = base_model.split_data(df)
        
        if weight_combinations is None:
            weight_combinations = [
                [0.33, 0.33, 0.34],
                [0.25, 0.25, 0.50],
                [0.20, 0.30, 0.50],
                [0.50, 0.25, 0.25],
                [0.40, 0.30, 0.30]
            ]
        
        best_weights = None
        best_r2 = -np.inf
        results = []
        
        for weights in weight_combinations:
            if len(weights) != len(models_dict):
                continue
            
            weights_dict = {name: w for name, w in zip(models_dict.keys(), weights)}
            
            from src.models.ensemble import EnsembleModel
            ensemble = EnsembleModel(models=models_dict, weights=weights_dict)
            ensemble.feature_names = base_model.feature_names
            ensemble.is_trained = True
            
            try:
                y_pred = ensemble.predict(X_test)
                
                from sklearn.metrics import r2_score
                r2 = r2_score(y_test, y_pred)
                
                results.append({
                    'weights': weights_dict,
                    'r2_score': r2
                })
                
                self.logger.info(f"Weights {weights}: R² = {r2:.4f}")
                
                if r2 > best_r2:
                    best_r2 = r2
                    best_weights = weights_dict
            
            except Exception as e:
                self.logger.error(f"Error evaluating weights {weights}: {str(e)}")
        
        if best_weights:
            self.logger.info(f"Best ensemble weights: {best_weights} (R² = {best_r2:.4f})")
            return best_weights, best_r2, results
        
        return None, None, results