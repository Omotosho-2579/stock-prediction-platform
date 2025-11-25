# src/visualization/comparison_plots.py

import plotly.graph_objects as go
import pandas as pd
import numpy as np
from pathlib import Path
import sys

project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from app.config import CHART_HEIGHT, CHART_TEMPLATE
from src.utils.logger import Logger

class ComparisonPlots:
    def __init__(self):
        self.logger = Logger(__name__)
        self.template = CHART_TEMPLATE
        self.height = CHART_HEIGHT
    
    def plot_normalized_prices(self, stock_data_dict):
        fig = go.Figure()
        
        colors = ['blue', 'red', 'green', 'orange', 'purple', 'brown', 'pink', 'gray', 'cyan', 'magenta']
        
        for idx, (symbol, df) in enumerate(stock_data_dict.items()):
            normalized = (df['Close'] / df['Close'].iloc[0]) * 100
            
            fig.add_trace(go.Scatter(
                x=df.index,
                y=normalized,
                mode='lines',
                name=symbol,
                line=dict(color=colors[idx % len(colors)], width=2)
            ))
        
        fig.update_layout(
            title='Normalized Stock Price Comparison (Base = 100)',
            xaxis_title='Date',
            yaxis_title='Normalized Price',
            template=self.template,
            height=self.height,
            hovermode='x unified'
        )
        
        return fig
    
    def plot_volume_comparison(self, stock_data_dict):
        fig = go.Figure()
        
        colors = ['blue', 'red', 'green', 'orange', 'purple']
        
        for idx, (symbol, df) in enumerate(stock_data_dict.items()):
            fig.add_trace(go.Bar(
                x=df.index,
                y=df['Volume'],
                name=symbol,
                marker_color=colors[idx % len(colors)],
                opacity=0.7
            ))
        
        fig.update_layout(
            title='Volume Comparison',
            xaxis_title='Date',
            yaxis_title='Volume',
            template=self.template,
            height=self.height,
            barmode='group'
        )
        
        return fig
    
    def plot_cumulative_returns(self, stock_data_dict):
        fig = go.Figure()
        
        colors = ['blue', 'red', 'green', 'orange', 'purple']
        
        for idx, (symbol, df) in enumerate(stock_data_dict.items()):
            returns = df['Close'].pct_change()
            cumulative_returns = (1 + returns).cumprod() - 1
            cumulative_returns_pct = cumulative_returns * 100
            
            fig.add_trace(go.Scatter(
                x=df.index,
                y=cumulative_returns_pct,
                mode='lines',
                name=symbol,
                line=dict(color=colors[idx % len(colors)], width=2)
            ))
        
        fig.add_hline(y=0, line_dash="dash", line_color="gray")
        
        fig.update_layout(
            title='Cumulative Returns Comparison (%)',
            xaxis_title='Date',
            yaxis_title='Cumulative Return (%)',
            template=self.template,
            height=self.height,
            hovermode='x unified'
        )
        
        return fig
    
    def plot_volatility_comparison(self, stock_data_dict, window=20):
        fig = go.Figure()
        
        colors = ['blue', 'red', 'green', 'orange', 'purple']
        
        for idx, (symbol, df) in enumerate(stock_data_dict.items()):
            returns = df['Close'].pct_change()
            volatility = returns.rolling(window=window).std() * np.sqrt(252) * 100
            
            fig.add_trace(go.Scatter(
                x=df.index,
                y=volatility,
                mode='lines',
                name=symbol,
                line=dict(color=colors[idx % len(colors)], width=2)
            ))
        
        fig.update_layout(
            title=f'Rolling Volatility Comparison ({window} days)',
            xaxis_title='Date',
            yaxis_title='Annualized Volatility (%)',
            template=self.template,
            height=self.height,
            hovermode='x unified'
        )
        
        return fig
    
    def plot_price_ratio(self, stock_data_dict):
        if len(stock_data_dict) < 2:
            return None
        
        symbols = list(stock_data_dict.keys())
        symbol1, symbol2 = symbols[0], symbols[1]
        
        df1 = stock_data_dict[symbol1]
        df2 = stock_data_dict[symbol2]
        
        ratio = df1['Close'] / df2['Close']
        
        fig = go.Figure()
        
        fig.add_trace(go.Scatter(
            x=df1.index,
            y=ratio,
            mode='lines',
            name=f'{symbol1}/{symbol2}',
            line=dict(color='blue', width=2)
        ))
        
        mean_ratio = ratio.mean()
        fig.add_hline(y=mean_ratio, line_dash="dash", line_color="red", annotation_text=f"Mean: {mean_ratio:.2f}")
        
        fig.update_layout(
            title=f'Price Ratio: {symbol1}/{symbol2}',
            xaxis_title='Date',
            yaxis_title='Ratio',
            template=self.template,
            height=self.height
        )
        
        return fig