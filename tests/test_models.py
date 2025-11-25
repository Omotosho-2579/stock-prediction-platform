# tests/test_models.py

import pytest
import pandas as pd
import numpy as np
import sys
from pathlib import Path

project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.models.linear_regression import LinearRegressionModel
from src.models.random_forest import RandomForestModel
from src.models.xgboost_model import XGBoostModel
from src.models.ensemble import EnsembleModel
from src.data.data_loader import DataLoader

@pytest.fixture
def sample_data():
    data_loader = DataLoader()
    df = data_loader.load_stock_data('AAPL', period='1y', use_cache=False)
    return df

@pytest.fixture
def lr_model():
    return LinearRegressionModel()

@pytest.fixture
def rf_model():
    return RandomForestModel(n_estimators=10)

@pytest.fixture
def xgb_model():
    return XGBoostModel(n_estimators=10)

class TestLinearRegressionModel:
    
    def test_model_initialization(self, lr_model):
        assert lr_model is not None
        assert lr_model.name == "Linear Regression"
        assert not lr_model.is_trained
    
    def test_model_build(self, lr_model):
        lr_model.build()
        assert lr_model.model is not None
    
    def test_model_training(self, lr_model, sample_data):
        X_train, X_test, y_train, y_test = lr_model.split_data(sample_data)
        
        lr_model.build()
        lr_model.train(X_train, y_train)
        
        assert lr_model.is_trained
        assert lr_model.model is not None
    
    def test_model_prediction(self, lr_model, sample_data):
        X_train, X_test, y_train, y_test = lr_model.split_data(sample_data)
        
        lr_model.build()
        lr_model.train(X_train, y_train)
        
        predictions = lr_model.predict(X_test)
        
        assert predictions is not None
        assert len(predictions) == len(X_test)
        assert isinstance(predictions, np.ndarray)
    
    def test_model_evaluation(self, lr_model, sample_data):
        X_train, X_test, y_train, y_test = lr_model.split_data(sample_data)
        
        lr_model.build()
        lr_model.train(X_train, y_train)
        
        metrics = lr_model.evaluate(X_test, y_test)
        
        assert 'rmse' in metrics
        assert 'mae' in metrics
        assert 'r2_score' in metrics
        assert 'mape' in metrics
        assert metrics['r2_score'] <= 1.0

class TestRandomForestModel:
    
    def test_model_initialization(self, rf_model):
        assert rf_model is not None
        assert rf_model.name == "Random Forest"
        assert rf_model.n_estimators == 10
    
    def test_model_training(self, rf_model, sample_data):
        X_train, X_test, y_train, y_test = rf_model.split_data(sample_data)
        
        rf_model.build()
        rf_model.train(X_train, y_train)
        
        assert rf_model.is_trained
    
    def test_feature_importance(self, rf_model, sample_data):
        X_train, X_test, y_train, y_test = rf_model.split_data(sample_data)
        
        rf_model.build()
        rf_model.train(X_train, y_train)
        
        importance = rf_model.get_feature_importance()
        
        assert importance is not None
        assert isinstance(importance, pd.DataFrame)
        assert 'feature' in importance.columns
        assert 'importance' in importance.columns

class TestXGBoostModel:
    
    def test_model_initialization(self, xgb_model):
        assert xgb_model is not None
        assert xgb_model.name == "XGBoost"
    
    def test_model_training(self, xgb_model, sample_data):
        X_train, X_test, y_train, y_test = xgb_model.split_data(sample_data)
        
        xgb_model.build()
        xgb_model.train(X_train, y_train)
        
        assert xgb_model.is_trained

class TestEnsembleModel:
    
    def test_ensemble_initialization(self):
        ensemble = EnsembleModel()
        
        assert ensemble is not None
        assert len(ensemble.models) > 0
        assert ensemble.weights is not None
    
    def test_ensemble_training(self, sample_data):
        ensemble = EnsembleModel()
        X_train, X_test, y_train, y_test = ensemble.models['linear_regression'].split_data(sample_data)
        
        ensemble.train(X_train, y_train)
        
        assert ensemble.is_trained
    
    def test_ensemble_prediction(self, sample_data):
        ensemble = EnsembleModel()
        X_train, X_test, y_train, y_test = ensemble.models['linear_regression'].split_data(sample_data)
        
        ensemble.train(X_train, y_train)
        predictions = ensemble.predict(X_test)
        
        assert predictions is not None
        assert len(predictions) == len(X_test)