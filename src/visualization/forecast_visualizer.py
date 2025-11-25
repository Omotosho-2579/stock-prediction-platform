# src/visualization/forecast_visualizer.py

import plotly.graph_objects as go
import numpy as np
import pandas as pd
from pathlib import Path
import sys

project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from app.config import CHART_HEIGHT, CHART_TEMPLATE
from src.utils.logger import Logger

class ForecastVisualizer:
    def __init__(self):
        self.logger = Logger(__name__)
        self.template = CHART_TEMPLATE
        self.height = CHART_HEIGHT
    
    def plot_forecast(self, historical_data, predictions, forecast_days, symbol="Stock", confidence_level=95):
        fig = go.Figure()
        
        fig.add_trace(go.Scatter(
            x=historical_data.index,
            y=historical_data['Close'],
            mode='lines',
            name='Historical',
            line=dict(color='blue', width=2)
        ))
        
        last_date = historical_data.index[-1]
        future_dates = pd.date_range(start=last_date, periods=forecast_days + 1, freq='D')[1:]
        
        colors = ['red', 'green', 'orange', 'purple', 'brown']
        
        for idx, (model_name, pred_values) in enumerate(predictions.items()):
            fig.add_trace(go.Scatter(
                x=future_dates,
                y=pred_values,
                mode='lines',
                name=f'{model_name} Forecast',
                line=dict(color=colors[idx % len(colors)], width=2, dash='dash')
            ))
        
        if len(predictions) > 1:
            ensemble_pred = np.mean(list(predictions.values()), axis=0)
            std_dev = np.std(list(predictions.values()), axis=0)
            
            z_score = 1.96 if confidence_level == 95 else 2.576
            upper_bound = ensemble_pred + (z_score * std_dev)
            lower_bound = ensemble_pred - (z_score * std_dev)
            
            fig.add_trace(go.Scatter(
                x=future_dates,
                y=upper_bound,
                mode='lines',
                name=f'{confidence_level}% Upper Bound',
                line=dict(color='gray', width=1, dash='dot'),
                showlegend=False
            ))
            
            fig.add_trace(go.Scatter(
                x=future_dates,
                y=lower_bound,
                mode='lines',
                name=f'{confidence_level}% Lower Bound',
                line=dict(color='gray', width=1, dash='dot'),
                fill='tonexty',
                fillcolor='rgba(128, 128, 128, 0.2)',
                showlegend=True
            ))
        
        fig.update_layout(
            title=f'{symbol} - Price Forecast ({forecast_days} Days)',
            xaxis_title='Date',
            yaxis_title='Price ($)',
            template=self.template,
            height=self.height,
            hovermode='x unified'
        )
        
        return fig
    
    def plot_forecast_with_scenarios(self, historical_data, forecast_data, symbol="Stock"):
        fig = go.Figure()
        
        fig.add_trace(go.Scatter(
            x=historical_data.index,
            y=historical_data['Close'],
            mode='lines',
            name='Historical',
            line=dict(color='blue', width=2)
        ))
        
        last_date = historical_data.index[-1]
        forecast_days = len(forecast_data['base'])
        future_dates = pd.date_range(start=last_date, periods=forecast_days + 1, freq='D')[1:]
        
        fig.add_trace(go.Scatter(
            x=future_dates,
            y=forecast_data['optimistic'],
            mode='lines',
            name='Optimistic',
            line=dict(color='green', width=2, dash='dash')
        ))
        
        fig.add_trace(go.Scatter(
            x=future_dates,
            y=forecast_data['base'],
            mode='lines',
            name='Base Case',
            line=dict(color='orange', width=2, dash='dash')
        ))
        
        fig.add_trace(go.Scatter(
            x=future_dates,
            y=forecast_data['pessimistic'],
            mode='lines',
            name='Pessimistic',
            line=dict(color='red', width=2, dash='dash')
        ))
        
        fig.update_layout(
            title=f'{symbol} - Forecast Scenarios',
            xaxis_title='Date',
            yaxis_title='Price ($)',
            template=self.template,
            height=self.height,
            hovermode='x unified'
        )
        
        return fig
    
    def plot_prediction_intervals(self, historical_data, predictions, lower_bound, upper_bound, symbol="Stock"):
        fig = go.Figure()
        
        historical_len = len(historical_data)
        full_dates = list(range(historical_len + len(predictions)))
        
        fig.add_trace(go.Scatter(
            x=list(range(historical_len)),
            y=historical_data['Close'],
            mode='lines',
            name='Historical',
            line=dict(color='blue', width=2)
        ))
        
        forecast_x = list(range(historical_len, historical_len + len(predictions)))
        
        fig.add_trace(go.Scatter(
            x=forecast_x,
            y=predictions,
            mode='lines',
            name='Forecast',
            line=dict(color='red', width=2)
        ))
        
        fig.add_trace(go.Scatter(
            x=forecast_x,
            y=upper_bound,
            mode='lines',
            name='Upper Bound',
            line=dict(color='gray', width=1, dash='dot'),
            showlegend=False
        ))
        
        fig.add_trace(go.Scatter(
            x=forecast_x,
            y=lower_bound,
            mode='lines',
            name='Prediction Interval',
            line=dict(color='gray', width=1, dash='dot'),
            fill='tonexty',
            fillcolor='rgba(128, 128, 128, 0.3)'
        ))
        
        fig.update_layout(
            title=f'{symbol} - Forecast with Prediction Intervals',
            xaxis_title='Time Period',
            yaxis_title='Price ($)',
            template=self.template,
            height=self.height
        )
        
        return fig
    
    def plot_forecast_fan_chart(self, historical_data, forecast_mean, forecast_std, symbol="Stock", periods=30):
        fig = go.Figure()
        
        fig.add_trace(go.Scatter(
            x=historical_data.index,
            y=historical_data['Close'],
            mode='lines',
            name='Historical',
            line=dict(color='blue', width=2)
        ))
        
        last_date = historical_data.index[-1]
        future_dates = pd.date_range(start=last_date, periods=periods + 1, freq='D')[1:]
        
        percentiles = [10, 25, 50, 75, 90]
        colors_alpha = [0.1, 0.2, 0.3, 0.2, 0.1]
        
        for i, percentile in enumerate(percentiles):
            if percentile == 50:
                fig.add_trace(go.Scatter(
                    x=future_dates,
                    y=forecast_mean,
                    mode='lines',
                    name='Median Forecast',
                    line=dict(color='red', width=2, dash='dash')
                ))
            else:
                z_score = np.percentile(np.random.standard_normal(10000), percentile)
                bound = forecast_mean + (z_score * forecast_std)
                
                fig.add_trace(go.Scatter(
                    x=future_dates,
                    y=bound,
                    mode='lines',
                    name=f'{percentile}th Percentile',
                    line=dict(width=0),
                    fillcolor=f'rgba(255, 0, 0, {colors_alpha[i]})',
                    fill='tonexty' if i > 0 else None,
                    showlegend=False
                ))
        
        fig.update_layout(
            title=f'{symbol} - Forecast Fan Chart',
            xaxis_title='Date',
            yaxis_title='Price ($)',
            template=self.template,
            height=self.height
        )
        
        return fig