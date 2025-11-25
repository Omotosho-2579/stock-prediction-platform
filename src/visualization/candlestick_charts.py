# src/visualization/candlestick_charts.py

import plotly.graph_objects as go
from plotly.subplots import make_subplots
from pathlib import Path
import sys

project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from app.config import CHART_HEIGHT, CHART_TEMPLATE
from src.utils.logger import Logger

class CandlestickCharts:
    def __init__(self):
        self.logger = Logger(__name__)
        self.template = CHART_TEMPLATE
        self.height = CHART_HEIGHT
    
    def plot_candlestick(self, df, symbol="Stock", show_volume=True):
        if show_volume:
            fig = make_subplots(
                rows=2, cols=1,
                shared_xaxes=True,
                vertical_spacing=0.03,
                row_heights=[0.7, 0.3],
                subplot_titles=(f'{symbol} Price', 'Volume')
            )
        else:
            fig = go.Figure()
        
        candlestick = go.Candlestick(
            x=df.index,
            open=df['Open'],
            high=df['High'],
            low=df['Low'],
            close=df['Close'],
            name='OHLC',
            increasing_line_color='green',
            decreasing_line_color='red'
        )
        
        if show_volume:
            fig.add_trace(candlestick, row=1, col=1)
        else:
            fig.add_trace(candlestick)
        
        if show_volume:
            colors = ['red' if df['Close'].iloc[i] < df['Open'].iloc[i] else 'green' 
                      for i in range(len(df))]
            
            fig.add_trace(go.Bar(
                x=df.index,
                y=df['Volume'],
                name='Volume',
                marker_color=colors,
                showlegend=False
            ), row=2, col=1)
        
        fig.update_layout(
            title=f'{symbol} - Candlestick Chart',
            xaxis_title='Date',
            yaxis_title='Price ($)',
            template=self.template,
            height=self.height if not show_volume else 600,
            xaxis_rangeslider_visible=False,
            hovermode='x unified'
        )
        
        if show_volume:
            fig.update_yaxes(title_text="Price ($)", row=1, col=1)
            fig.update_yaxes(title_text="Volume", row=2, col=1)
        
        return fig
    
    def plot_candlestick_with_indicators(self, df, symbol="Stock"):
        fig = make_subplots(
            rows=3, cols=1,
            shared_xaxes=True,
            vertical_spacing=0.03,
            row_heights=[0.5, 0.25, 0.25],
            subplot_titles=(f'{symbol} Price', 'Volume', 'RSI')
        )
        
        fig.add_trace(go.Candlestick(
            x=df.index,
            open=df['Open'],
            high=df['High'],
            low=df['Low'],
            close=df['Close'],
            name='OHLC',
            increasing_line_color='green',
            decreasing_line_color='red'
        ), row=1, col=1)
        
        if 'SMA_20' in df.columns:
            fig.add_trace(go.Scatter(
                x=df.index,
                y=df['SMA_20'],
                mode='lines',
                name='SMA 20',
                line=dict(color='orange', width=1.5)
            ), row=1, col=1)
        
        if 'SMA_50' in df.columns:
            fig.add_trace(go.Scatter(
                x=df.index,
                y=df['SMA_50'],
                mode='lines',
                name='SMA 50',
                line=dict(color='blue', width=1.5)
            ), row=1, col=1)
        
        colors = ['red' if df['Close'].iloc[i] < df['Open'].iloc[i] else 'green' 
                  for i in range(len(df))]
        
        fig.add_trace(go.Bar(
            x=df.index,
            y=df['Volume'],
            name='Volume',
            marker_color=colors,
            showlegend=False
        ), row=2, col=1)
        
        if 'RSI' in df.columns:
            fig.add_trace(go.Scatter(
                x=df.index,
                y=df['RSI'],
                mode='lines',
                name='RSI',
                line=dict(color='purple', width=2),
                showlegend=False
            ), row=3, col=1)
            
            fig.add_hline(y=70, line_dash="dash", line_color="red", row=3, col=1)
            fig.add_hline(y=30, line_dash="dash", line_color="green", row=3, col=1)
        
        fig.update_layout(
            title=f'{symbol} - Technical Analysis',
            template=self.template,
            height=800,
            xaxis_rangeslider_visible=False,
            hovermode='x unified'
        )
        
        fig.update_yaxes(title_text="Price ($)", row=1, col=1)
        fig.update_yaxes(title_text="Volume", row=2, col=1)
        fig.update_yaxes(title_text="RSI", row=3, col=1)
        
        return fig
    
    def plot_ohlc(self, df, symbol="Stock"):
        fig = go.Figure(data=go.Ohlc(
            x=df.index,
            open=df['Open'],
            high=df['High'],
            low=df['Low'],
            close=df['Close'],
            name='OHLC'
        ))
        
        fig.update_layout(
            title=f'{symbol} - OHLC Chart',
            xaxis_title='Date',
            yaxis_title='Price ($)',
            template=self.template,
            height=self.height,
            xaxis_rangeslider_visible=False
        )
        
        return fig