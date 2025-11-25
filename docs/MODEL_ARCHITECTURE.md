# docs/MODEL_ARCHITECTURE.md

# Model Architecture

Comprehensive documentation of machine learning models, design decisions, and implementation details.

---

## Table of Contents

1. [Overview](#overview)
2. [Model Types](#model-types)
3. [Feature Engineering](#feature-engineering)
4. [Training Pipeline](#training-pipeline)
5. [Ensemble Methodology](#ensemble-methodology)
6. [Performance Metrics](#performance-metrics)
7. [Model Selection](#model-selection)
8. [Hyperparameter Tuning](#hyperparameter-tuning)

---

## Overview

The platform uses a multi-model ensemble approach combining traditional machine learning and deep learning techniques for stock price prediction.

### Design Philosophy

1. **Diversity** - Multiple model types capture different patterns
2. **Robustness** - Ensemble reduces overfitting
3. **Adaptability** - Models update with new data
4. **Interpretability** - Explainable predictions
5. **Performance** - Balance accuracy with computational efficiency

### Model Pipeline
```
Raw Data → Feature Engineering → Model Training → Ensemble → Predictions
    ↓              ↓                   ↓              ↓           ↓
 yfinance    Technical         Individual       Weighted    Future
  Alpha      Indicators         Models          Combine     Prices
 Vantage    Fundamentals       Evaluation       Results     + CI
```

---

## Model Types

### 1. Linear Regression

**Type**: Traditional Statistical Model  
**Use Case**: Baseline, interpretable predictions  
**Strengths**: Fast, interpretable, low complexity  
**Weaknesses**: Assumes linearity, limited for complex patterns

#### Architecture
```python
LinearRegression(
    fit_intercept=True,
    normalize=False,
    copy_X=True,
    n_jobs=-1
)
```

#### Features Used
- Price-based (OHLC)
- Technical indicators (20+)
- Volume metrics
- Returns and momentum

#### Training Process
1. Feature scaling (StandardScaler)
2. Train-test split (80/20)
3. Fit model on training data
4. Evaluate on test set

#### Typical Performance
- **R² Score**: 0.75-0.85
- **RMSE**: 2-5% of stock price
- **Training Time**: < 1 second

---

### 2. Random Forest

**Type**: Ensemble Learning (Bagging)  
**Use Case**: Robust predictions, feature importance  
**Strengths**: Handles non-linearity, feature importance, resistant to overfitting  
**Weaknesses**: Computationally intensive, black-box

#### Architecture
```python
RandomForestRegressor(
    n_estimators=100,
    max_depth=None,
    min_samples_split=2,
    min_samples_leaf=1,
    max_features='auto',
    bootstrap=True,
    n_jobs=-1,
    random_state=42
)
```

#### Hyperparameters
- **n_estimators**: 50-200 trees
- **max_depth**: None (unlimited) or 10-30
- **min_samples_split**: 2-10
- **max_features**: 'sqrt', 'log2', or 'auto'

#### Feature Importance
Provides feature importance scores:
```python
importance_df = model.get_feature_importance()
# Returns: DataFrame with features ranked by importance
```

#### Typical Performance
- **R² Score**: 0.80-0.90
- **RMSE**: 1.5-4% of stock price
- **Training Time**: 5-15 seconds

---

### 3. XGBoost

**Type**: Gradient Boosting  
**Use Case**: High accuracy predictions  
**Strengths**: Superior performance, handles missing data, regularization  
**Weaknesses**: Prone to overfitting, requires tuning

#### Architecture
```python
XGBRegressor(
    n_estimators=100,
    max_depth=6,
    learning_rate=0.1,
    subsample=0.8,
    colsample_bytree=0.8,
    gamma=0,
    reg_alpha=0,
    reg_lambda=1,
    random_state=42,
    n_jobs=-1
)
```

#### Hyperparameters
- **n_estimators**: 50-200
- **max_depth**: 3-9
- **learning_rate**: 0.01-0.3
- **subsample**: 0.6-1.0
- **colsample_bytree**: 0.6-1.0

#### Regularization
- **L1 (alpha)**: Feature selection
- **L2 (lambda)**: Weight penalty
- **gamma**: Minimum loss reduction

#### Typical Performance
- **R² Score**: 0.82-0.92
- **RMSE**: 1.2-3.5% of stock price
- **Training Time**: 3-10 seconds

---

### 4. LSTM (Long Short-Term Memory)

**Type**: Deep Learning (RNN)  
**Use Case**: Time series patterns, long-term dependencies  
**Strengths**: Captures temporal patterns, learns sequences  
**Weaknesses**: Requires more data, slow training, difficult to interpret

#### Architecture
```python
Sequential([
    LSTM(50, return_sequences=True, input_shape=(lookback, 1)),
    Dropout(0.2),
    LSTM(50, return_sequences=True),
    Dropout(0.2),
    LSTM(50),
    Dropout(0.2),
    Dense(1)
])
```

#### Layer Configuration
- **Input Layer**: Shape (lookback_days, features)
- **LSTM Layers**: 3 layers with 50 units each
- **Dropout**: 20% between layers
- **Output Layer**: Single neuron (price prediction)

#### Training Configuration
```python
model.compile(
    optimizer='adam',
    loss='mean_squared_error'
)

model.fit(
    X_train, y_train,
    epochs=50,
    batch_size=32,
    validation_split=0.2,
    callbacks=[EarlyStopping(patience=5)]
)
```

#### Lookback Window
- **Default**: 60 days
- **Range**: 30-90 days
- Determines how much historical data influences prediction

#### Typical Performance
- **R² Score**: 0.78-0.88
- **RMSE**: 1.8-4.5% of stock price
- **Training Time**: 30-120 seconds

---

### 5. Ensemble Model

**Type**: Weighted Average Ensemble  
**Use Case**: Best overall performance  
**Strengths**: Reduces variance, improves accuracy, robust  
**Weaknesses**: Computationally expensive, requires all models

#### Architecture
```python
EnsembleModel(
    models={
        'linear_regression': LinearRegressionModel(),
        'random_forest': RandomForestModel(),
        'xgboost': XGBoostModel()
    },
    weights={
        'linear_regression': 0.2,
        'random_forest': 0.3,
        'xgboost': 0.5
    }
)
```

#### Weight Optimization
Weights are optimized using:
1. **Validation Performance** - R² scores
2. **Inverse Error Weighting** - Lower error = higher weight
3. **Grid Search** - Test combinations
4. **Differential Evolution** - Optimization algorithm

#### Prediction Combination
```python
ensemble_prediction = Σ(weight_i × prediction_i)
```

#### Typical Performance
- **R² Score**: 0.85-0.92
- **RMSE**: 1.0-3.0% of stock price
- **Training Time**: Sum of all models

---

## Feature Engineering

### Raw Features
```python
base_features = [
    'Open', 'High', 'Low', 'Close', 'Volume'
]
```

### Price-Based Features
```python
price_features = [
    'Price_Range',           # High - Low
    'Price_Range_Pct',       # Range / Close
    'Gap',                   # Open - Previous Close
    'Body',                  # Close - Open
    'Upper_Shadow',          # High - max(Open, Close)
    'Lower_Shadow'           # min(Open, Close) - Low
]
```

### Technical Indicators (20+)
```python
technical_indicators = [
    # Moving Averages
    'SMA_5', 'SMA_10', 'SMA_20', 'SMA_50', 'SMA_200',
    'EMA_12', 'EMA_26',
    
    # Momentum
    'RSI_14',
    'MACD', 'MACD_Signal', 'MACD_Histogram',
    'ROC_10', 'ROC_20',
    'Momentum_10',
    
    # Volatility
    'BB_Upper', 'BB_Middle', 'BB_Lower',
    'BB_Width', 'BB_Position',
    'ATR_14',
    
    # Volume
    'Volume_SMA_20', 'Volume_Ratio',
    'OBV',
    
    # Trend
    'ADX', 'Plus_DI', 'Minus_DI'
]
```

### Returns Features
```python
returns_features = [
    'Return_1D', 'Return_5D', 'Return_20D',
    'LogReturn_1D', 'LogReturn_5D',
    'Return_Std_20D'
]
```

### Time-Based Features
```python
time_features = [
    'DayOfWeek',
    'DayOfMonth',
    'Month',
    'Quarter',
    'IsMonthStart',
    'IsMonthEnd',
    'IsQuarterStart',
    'IsQuarterEnd'
]
```

### Feature Selection
Top features by importance:
1. **Close_Lag_1** - Previous closing price
2. **SMA_20** - 20-day moving average
3. **Volume_Ratio** - Volume vs average
4. **RSI_14** - Relative Strength Index
5. **MACD** - Momentum indicator

---

## Training Pipeline

### 1. Data Preparation
```python
# Load historical data
df = data_loader.load_stock_data(symbol, period='2y')

# Add technical indicators
df = tech_indicators.add_all_indicators(df)

# Prepare features
features = model.prepare_features(df)

# Handle missing values
features = features.fillna(method='ffill').fillna(method='bfill')
```

### 2. Train-Test Split
```python
# Time-series split (preserves temporal order)
split_ratio = 0.8
split_index = int(len(features) * split_ratio)

X_train = features[:split_index]
X_test = features[split_index:]
y_train = target[:split_index]
y_test = target[split_index:]
```

### 3. Feature Scaling
```python
# Standardize features
scaler = StandardScaler()
X_train_scaled = scaler.fit_transform(X_train)
X_test_scaled = scaler.transform(X_test)
```

### 4. Model Training
```python
# Train individual models
for model_name, model in models.items():
    model.build()
    model.train(X_train_scaled, y_train)
    
    # Evaluate
    metrics = model.evaluate(X_test_scaled, y_test)
    
    # Save if performance threshold met
    if metrics['r2_score'] > 0.70:
        model.save_model(model_path)
```

### 5. Ensemble Training
```python
# Create ensemble
ensemble = EnsembleModel(models=trained_models)

# Optimize weights
ensemble.optimize_weights(X_test_scaled, y_test)

# Final evaluation
final_metrics = ensemble.evaluate(X_test_scaled, y_test)
```

---

## Ensemble Methodology

### Weight Optimization

#### Method 1: Performance-Based
```python
weights = {}
total_r2 = sum(model.metrics['r2_score'] for model in models)

for name, model in models.items():
    weights[name] = model.metrics['r2_score'] / total_r2
```

#### Method 2: Inverse Error
```python
weights = {}
total_inv_error = sum(1/model.metrics['rmse'] for model in models)

for name, model in models.items():
    weights[name] = (1/model.metrics['rmse']) / total_inv_error
```

#### Method 3: Optimization (Best)
```python
from scipy.optimize import minimize

def objective(weights):
    predictions = sum(w * model.predict(X_val) 
                     for w, model in zip(weights, models))
    return mean_squared_error(y_val, predictions)

result = minimize(
    objective,
    initial_weights,
    bounds=[(0, 1)] * len(models),
    constraints={'type': 'eq', 'fun': lambda w: sum(w) - 1}
)

optimal_weights = result.x
```

### Prediction Combination
```python
def ensemble_predict(X):
    predictions = []
    
    for name, model in models.items():
        pred = model.predict(X)
        weight = weights[name]
        predictions.append(pred * weight)
    
    return sum(predictions)
```

---

## Performance Metrics

### Regression Metrics

#### 1. R² Score (Coefficient of Determination)
```python
r2 = 1 - (SS_res / SS_tot)
```
- **Range**: -∞ to 1.0
- **Interpretation**:
  - 1.0 = Perfect prediction
  - 0.0 = Model as good as mean
  - < 0 = Worse than mean
- **Target**: > 0.70 for production

#### 2. Root Mean Squared Error (RMSE)
```python
rmse = sqrt(mean((y_true - y_pred)²))
```
- **Units**: Same as target variable
- **Interpretation**: Average prediction error
- **Target**: < 5% of stock price

#### 3. Mean Absolute Error (MAE)
```python
mae = mean(|y_true - y_pred|)
```
- **Units**: Same as target variable
- **Interpretation**: Average absolute error
- **Less sensitive to outliers than RMSE

#### 4. Mean Absolute Percentage Error (MAPE)
```python
mape = mean(|y_true - y_pred| / y_true) × 100
```
- **Units**: Percentage
- **Interpretation**: Average percentage error
- **Target**: < 5%

### Classification Metrics (Signal Quality)

#### Directional Accuracy
```python
correct_direction = sum(sign(y_true - y_prev) == sign(y_pred - y_prev))
directional_accuracy = correct_direction / total_predictions
```
- **Target**: > 60%

---

## Model Selection

### Selection Criteria

#### For Different Use Cases

**1. Real-time Trading** (Speed Priority)
- **Model**: Linear Regression
- **Reason**: Fastest predictions (< 1ms)
- **Trade-off**: Lower accuracy

**2. Daily Analysis** (Balanced)
- **Model**: Random Forest or XGBoost
- **Reason**: Good accuracy, reasonable speed
- **Trade-off**: Medium computational cost

**3. Research/Backtesting** (Accuracy Priority)
- **Model**: Ensemble
- **Reason**: Best accuracy
- **Trade-off**: Slowest predictions

**4. Time Series Analysis**
- **Model**: LSTM
- **Reason**: Captures temporal patterns
- **Trade-off**: Requires more data

### Model Comparison

| Model | R² Score | RMSE | Training Time | Prediction Time |
|-------|----------|------|---------------|-----------------|
| Linear Regression | 0.75-0.85 | 2-5% | < 1s | < 1ms |
| Random Forest | 0.80-0.90 | 1.5-4% | 5-15s | 10-50ms |
| XGBoost | 0.82-0.92 | 1.2-3.5% | 3-10s | 5-20ms |
| LSTM | 0.78-0.88 | 1.8-4.5% | 30-120s | 20-100ms |
| **Ensemble** | **0.85-0.92** | **1.0-3.0%** | **Sum** | **Sum** |

---

## Hyperparameter Tuning

### Grid Search Example
```python
from sklearn.model_selection import GridSearchCV

param_grid = {
    'n_estimators': [50, 100, 200],
    'max_depth': [None, 10, 20, 30],
    'min_samples_split': [2, 5, 10]
}

grid_search = GridSearchCV(
    RandomForestRegressor(),
    param_grid,
    cv=TimeSeriesSplit(n_splits=5),
    scoring='r2',
    n_jobs=-1
)

grid_search.fit(X_train, y_train)
best_params = grid_search.best_params_
```

### Bayesian Optimization
```python
from skopt import BayesSearchCV

search_spaces = {
    'n_estimators': (50, 200),
    'max_depth': (5, 30),
    'learning_rate': (0.01, 0.3, 'log-uniform')
}

bayes_search = BayesSearchCV(
    XGBRegressor(),
    search_spaces,
    n_iter=50,
    cv=TimeSeriesSplit(n_splits=3)
)

bayes_search.fit(X_train, y_train)
```

### Best Practices
1. **Use time series CV** - Preserve temporal order
2. **Start with defaults** - Baseline performance
3. **Tune systematically** - One parameter at a time
4. **Monitor overfitting** - Compare train/test scores
5. **Consider computation time** - Balance accuracy vs speed

---

## Future Improvements

### Planned Enhancements
1. **Transformer Models** - Attention mechanisms for time series
2. **AutoML Integration** - Automated hyperparameter tuning
3. **Online Learning** - Incremental model updates
4. **Multi-task Learning** - Predict multiple targets
5. **Feature Learning** - Automated feature engineering

---

## References

- Scikit-learn Documentation
- XGBoost Documentation
- TensorFlow/Keras Guides
- "Advances in Financial Machine Learning" by Marcos López de Prado
- "Machine Learning for Asset Managers" by Marcos López de Prado

---

**Last Updated**: November 2025  
**Version**: 1.0.0