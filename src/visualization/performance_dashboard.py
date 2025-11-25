# src/visualization/performance_dashboard.py

import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pandas as pd
import numpy as np
from pathlib import Path
import sys

project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from app.config import CHART_HEIGHT, CHART_TEMPLATE
from src.utils.logger import Logger

class PerformanceDashboard:
    def __init__(self):
        self.logger = Logger(__name__)
        self.template = CHART_TEMPLATE
        self.height = CHART_HEIGHT
    
    def plot_prediction_vs_actual(self, y_true, y_pred, dates=None):
        fig = go.Figure()
        
        if dates is None:
            dates = list(range(len(y_true)))
        
        fig.add_trace(go.Scatter(
            x=dates,
            y=y_true,
            mode='lines+markers',
            name='Actual',
            line=dict(color='blue', width=2),
            marker=dict(size=6)
        ))
        
        fig.add_trace(go.Scatter(
            x=dates,
            y=y_pred,
            mode='lines+markers',
            name='Predicted',
            line=dict(color='red', width=2, dash='dash'),
            marker=dict(size=6)
        ))
        
        fig.update_layout(
            title='Prediction vs Actual Prices',
            xaxis_title='Date',
            yaxis_title='Price ($)',
            template=self.template,
            height=self.height,
            hovermode='x unified'
        )
        
        return fig
    
    def plot_residuals(self, y_true, y_pred, dates=None):
        residuals = y_true - y_pred
        
        if dates is None:
            dates = list(range(len(residuals)))
        
        fig = go.Figure()
        
        fig.add_trace(go.Scatter(
            x=dates,
            y=residuals,
            mode='markers',
            name='Residuals',
            marker=dict(color='purple', size=8)
        ))
        
        fig.add_hline(y=0, line_dash="dash", line_color="black")
        
        mean_residual = np.mean(residuals)
        std_residual = np.std(residuals)
        
        fig.add_hline(y=mean_residual + 2*std_residual, line_dash="dot", line_color="red")
        fig.add_hline(y=mean_residual - 2*std_residual, line_dash="dot", line_color="red")
        
        fig.update_layout(
            title='Prediction Residuals',
            xaxis_title='Date',
            yaxis_title='Residual (Actual - Predicted)',
            template=self.template,
            height=self.height
        )
        
        return fig
    
    def plot_model_comparison(self, model_metrics_dict):
        models = list(model_metrics_dict.keys())
        r2_scores = [model_metrics_dict[m]['r2_score'] for m in models]
        rmse_scores = [model_metrics_dict[m]['rmse'] for m in models]
        mae_scores = [model_metrics_dict[m]['mae'] for m in models]
        
        fig = make_subplots(
            rows=1, cols=3,
            subplot_titles=('R² Score', 'RMSE', 'MAE')
        )
        
        fig.add_trace(go.Bar(
            x=models,
            y=r2_scores,
            name='R²',
            marker_color='blue'
        ), row=1, col=1)
        
        fig.add_trace(go.Bar(
            x=models,
            y=rmse_scores,
            name='RMSE',
            marker_color='red'
        ), row=1, col=2)
        
        fig.add_trace(go.Bar(
            x=models,
            y=mae_scores,
            name='MAE',
            marker_color='green'
        ), row=1, col=3)
        
        fig.update_layout(
            title='Model Performance Comparison',
            template=self.template,
            height=self.height,
            showlegend=False
        )
        
        fig.update_yaxes(title_text="Score", row=1, col=1)
        fig.update_yaxes(title_text="Error", row=1, col=2)
        fig.update_yaxes(title_text="Error", row=1, col=3)
        
        return fig
    
    def plot_accuracy_over_time(self, predictions_history):
        dates = [p['date'] for p in predictions_history]
        accuracies = [p['accuracy'] for p in predictions_history]
        
        fig = go.Figure()
        
        fig.add_trace(go.Scatter(
            x=dates,
            y=accuracies,
            mode='lines+markers',
            name='Accuracy',
            line=dict(color='green', width=2),
            marker=dict(size=8)
        ))
        
        fig.add_hline(y=np.mean(accuracies), line_dash="dash", line_color="red", 
                     annotation_text=f"Average: {np.mean(accuracies):.2f}%")
        
        fig.update_layout(
            title='Model Accuracy Over Time',
            xaxis_title='Date',
            yaxis_title='Accuracy (%)',
            template=self.template,
            height=self.height
        )
        
        return fig
    
    def plot_error_distribution(self, y_true, y_pred):
        errors = y_true - y_pred
        
        fig = go.Figure()
        
        fig.add_trace(go.Histogram(
            x=errors,
            nbinsx=30,
            name='Error Distribution',
            marker_color='blue'
        ))
        
        fig.update_layout(
            title='Prediction Error Distribution',
            xaxis_title='Error (Actual - Predicted)',
            yaxis_title='Frequency',
            template=self.template,
            height=self.height
        )
        
        return fig
    
    def create_performance_dashboard(self, y_true, y_pred, model_name="Model"):
        from sklearn.metrics import mean_squared_error, mean_absolute_error, r2_score
        
        rmse = np.sqrt(mean_squared_error(y_true, y_pred))
        mae = mean_absolute_error(y_true, y_pred)
        r2 = r2_score(y_true, y_pred)
        mape = np.mean(np.abs((y_true - y_pred) / y_true)) * 100
        
        fig = make_subplots(
            rows=2, cols=2,
            subplot_titles=(
                'Prediction vs Actual',
                'Residual Plot',
                'Error Distribution',
                'Performance Metrics'
            ),
            specs=[[{'type': 'scatter'}, {'type': 'scatter'}],
                   [{'type': 'histogram'}, {'type': 'indicator'}]]
        )
        
        fig.add_trace(go.Scatter(
            y=y_true,
            mode='lines',
            name='Actual',
            line=dict(color='blue')
        ), row=1, col=1)
        
        fig.add_trace(go.Scatter(
            y=y_pred,
            mode='lines',
            name='Predicted',
            line=dict(color='red', dash='dash')
        ), row=1, col=1)
        
        residuals = y_true - y_pred
        fig.add_trace(go.Scatter(
            y=residuals,
            mode='markers',
            name='Residuals',
            marker=dict(color='purple')
        ), row=1, col=2)
        
        fig.add_hline(y=0, line_dash="dash", line_color="black", row=1, col=2)
        
        fig.add_trace(go.Histogram(
            x=residuals,
            name='Errors',
            marker_color='green'
        ), row=2, col=1)
        
        metrics_text = f"R²: {r2:.4f}<br>RMSE: {rmse:.4f}<br>MAE: {mae:.4f}<br>MAPE: {mape:.2f}%"
        
        fig.add_annotation(
            text=metrics_text,
            xref="x4", yref="y4",
            x=0.5, y=0.5,
            showarrow=False,
            font=dict(size=16),
            row=2, col=2
        )
        
        fig.update_layout(
            title=f'{model_name} Performance Dashboard',
            template=self.template,
            height=800,
            showlegend=True
        )
        
        return fig