# src/visualization/heatmaps.py

import plotly.graph_objects as go
import plotly.express as px
import numpy as np
from pathlib import Path
import sys

project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from app.config import CHART_HEIGHT, CHART_TEMPLATE
from src.utils.logger import Logger

class Heatmaps:
    def __init__(self):
        self.logger = Logger(__name__)
        self.template = CHART_TEMPLATE
        self.height = CHART_HEIGHT
    
    def plot_correlation_matrix(self, correlation_matrix):
        fig = go.Figure(data=go.Heatmap(
            z=correlation_matrix.values,
            x=correlation_matrix.columns,
            y=correlation_matrix.index,
            colorscale='RdBu',
            zmid=0,
            text=correlation_matrix.values,
            texttemplate='%{text:.2f}',
            textfont={"size": 10},
            colorbar=dict(title="Correlation")
        ))
        
        fig.update_layout(
            title='Correlation Matrix',
            template=self.template,
            height=self.height,
            xaxis={'side': 'bottom'},
            yaxis={'side': 'left'}
        )
        
        return fig
    
    def plot_sector_heatmap(self, sector_performance):
        sectors = list(sector_performance.keys())
        dates = list(sector_performance[sectors[0]].keys())
        
        z_data = []
        for sector in sectors:
            z_data.append([sector_performance[sector][date] for date in dates])
        
        fig = go.Figure(data=go.Heatmap(
            z=z_data,
            x=dates,
            y=sectors,
            colorscale='RdYlGn',
            zmid=0,
            colorbar=dict(title="Return (%)")
        ))
        
        fig.update_layout(
            title='Sector Performance Heatmap',
            xaxis_title='Date',
            yaxis_title='Sector',
            template=self.template,
            height=self.height
        )
        
        return fig
    
    def plot_returns_heatmap(self, returns_matrix):
        fig = go.Figure(data=go.Heatmap(
            z=returns_matrix.values,
            x=returns_matrix.columns,
            y=returns_matrix.index,
            colorscale='RdYlGn',
            zmid=0,
            colorbar=dict(title="Return (%)")
        ))
        
        fig.update_layout(
            title='Returns Heatmap',
            template=self.template,
            height=self.height
        )
        
        return fig
    
    def plot_volatility_heatmap(self, stocks, volatility_data):
        fig = go.Figure(data=go.Heatmap(
            z=[volatility_data],
            x=stocks,
            y=['Volatility'],
            colorscale='Reds',
            colorbar=dict(title="Volatility (%)")
        ))
        
        fig.update_layout(
            title='Stock Volatility Comparison',
            xaxis_title='Stock',
            template=self.template,
            height=400
        )
        
        return fig
    
    def plot_risk_return_heatmap(self, stocks_data):
        returns = [stocks_data[s]['return'] for s in stocks_data]
        risks = [stocks_data[s]['risk'] for s in stocks_data]
        symbols = list(stocks_data.keys())
        
        fig = go.Figure(data=go.Scatter(
            x=risks,
            y=returns,
            mode='markers+text',
            text=symbols,
            textposition='top center',
            marker=dict(
                size=15,
                color=returns,
                colorscale='RdYlGn',
                showscale=True,
                colorbar=dict(title="Return (%)")
            )
        ))
        
        fig.update_layout(
            title='Risk vs Return',
            xaxis_title='Risk (Volatility %)',
            yaxis_title='Return (%)',
            template=self.template,
            height=self.height
        )
        
        return fig