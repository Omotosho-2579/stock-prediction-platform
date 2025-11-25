-- src/database/migrations/003_add_predictions_table.sql

CREATE TABLE IF NOT EXISTS predictions (
    prediction_id INTEGER PRIMARY KEY AUTOINCREMENT,
    symbol TEXT NOT NULL,
    model_type TEXT NOT NULL,
    prediction_date DATE NOT NULL,
    predicted_price REAL NOT NULL,
    actual_price REAL NULL,
    confidence REAL NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_predictions_symbol ON predictions(symbol);
CREATE INDEX IF NOT EXISTS idx_predictions_model_type ON predictions(model_type);
CREATE INDEX IF NOT EXISTS idx_predictions_date ON predictions(prediction_date);