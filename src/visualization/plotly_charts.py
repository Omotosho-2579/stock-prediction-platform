# src/visualization/plotly_charts.py

import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
from pathlib import Path
import sys

project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from app.config import CHART_HEIGHT, CHART_TEMPLATE, PRIMARY_COLOR, SECONDARY_COLOR
from src.utils.logger import Logger

class PlotlyCharts:
    def __init__(self):
        self.logger = Logger(__name__)
        self.template = CHART_TEMPLATE
        self.height = CHART_HEIGHT
    
    def plot_line_chart(self, df, x_col, y_col, title="Stock Price", color=PRIMARY_COLOR):
        fig = go.Figure()
        
        fig.add_trace(go.Scatter(
            x=df[x_col],
            y=df[y_col],
            mode='lines',
            name=y_col,
            line=dict(color=color, width=2),
            hovertemplate='<b>Date</b>: %{x}<br><b>Price</b>: $%{y:.2f}<extra></extra>'
        ))
        
        fig.update_layout(
            title=title,
            xaxis_title=x_col,
            yaxis_title=y_col,
            template=self.template,
            height=self.height,
            hovermode='x unified',
            showlegend=True
        )
        
        return fig
    
    def plot_area_chart(self, df, x_col, y_col, title="Stock Price Area"):
        fig = go.Figure()
        
        fig.add_trace(go.Scatter(
            x=df[x_col],
            y=df[y_col],
            mode='lines',
            name=y_col,
            fill='tozeroy',
            line=dict(color=PRIMARY_COLOR, width=2),
            fillcolor=f'rgba(31, 119, 180, 0.3)'
        ))
        
        fig.update_layout(
            title=title,
            xaxis_title=x_col,
            yaxis_title=y_col,
            template=self.template,
            height=self.height,
            hovermode='x unified'
        )
        
        return fig
    
    def plot_bar_chart(self, df, x_col, y_col, title="Bar Chart"):
        fig = go.Figure()
        
        fig.add_trace(go.Bar(
            x=df[x_col],
            y=df[y_col],
            name=y_col,
            marker_color=PRIMARY_COLOR
        ))
        
        fig.update_layout(
            title=title,
            xaxis_title=x_col,
            yaxis_title=y_col,
            template=self.template,
            height=self.height
        )
        
        return fig
    
    def plot_moving_averages(self, df, symbol="Stock"):
        fig = go.Figure()
        
        fig.add_trace(go.Scatter(
            x=df.index,
            y=df['Close'],
            mode='lines',
            name='Close Price',
            line=dict(color='blue', width=2)
        ))
        
        if 'SMA_20' in df.columns:
            fig.add_trace(go.Scatter(
                x=df.index,
                y=df['SMA_20'],
                mode='lines',
                name='SMA 20',
                line=dict(color='orange', width=1.5)
            ))
        
        if 'SMA_50' in df.columns:
            fig.add_trace(go.Scatter(
                x=df.index,
                y=df['SMA_50'],
                mode='lines',
                name='SMA 50',
                line=dict(color='red', width=1.5)
            ))
        
        if 'EMA_12' in df.columns:
            fig.add_trace(go.Scatter(
                x=df.index,
                y=df['EMA_12'],
                mode='lines',
                name='EMA 12',
                line=dict(color='green', width=1, dash='dash')
            ))
        
        fig.update_layout(
            title=f"{symbol} - Price with Moving Averages",
            xaxis_title="Date",
            yaxis_title="Price ($)",
            template=self.template,
            height=self.height,
            hovermode='x unified'
        )
        
        return fig
    
    def plot_rsi(self, df, symbol="Stock"):
        fig = go.Figure()
        
        fig.add_trace(go.Scatter(
            x=df.index,
            y=df['RSI'],
            mode='lines',
            name='RSI',
            line=dict(color='purple', width=2)
        ))
        
        fig.add_hline(y=70, line_dash="dash", line_color="red", annotation_text="Overbought (70)")
        fig.add_hline(y=30, line_dash="dash", line_color="green", annotation_text="Oversold (30)")
        fig.add_hline(y=50, line_dash="dot", line_color="gray", annotation_text="Neutral")
        
        fig.update_layout(
            title=f"{symbol} - RSI Indicator",
            xaxis_title="Date",
            yaxis_title="RSI",
            template=self.template,
            height=self.height,
            yaxis=dict(range=[0, 100]),
            hovermode='x unified'
        )
        
        return fig
    
    def plot_macd(self, df, symbol="Stock"):
        fig = go.Figure()
        
        fig.add_trace(go.Scatter(
            x=df.index,
            y=df['MACD'],
            mode='lines',
            name='MACD',
            line=dict(color='blue', width=2)
        ))
        
        fig.add_trace(go.Scatter(
            x=df.index,
            y=df['MACD_Signal'],
            mode='lines',
            name='Signal',
            line=dict(color='red', width=2)
        ))
        
        fig.add_trace(go.Bar(
            x=df.index,
            y=df['MACD_Histogram'],
            name='Histogram',
            marker_color='gray'
        ))
        
        fig.add_hline(y=0, line_dash="dash", line_color="black")
        
        fig.update_layout(
            title=f"{symbol} - MACD Indicator",
            xaxis_title="Date",
            yaxis_title="MACD",
            template=self.template,
            height=self.height,
            hovermode='x unified'
        )
        
        return fig
    
    def plot_volume(self, df, symbol="Stock"):
        colors = ['red' if df['Close'].iloc[i] < df['Open'].iloc[i] else 'green' 
                  for i in range(len(df))]
        
        fig = go.Figure()
        
        fig.add_trace(go.Bar(
            x=df.index,
            y=df['Volume'],
            name='Volume',
            marker_color=colors
        ))
        
        fig.update_layout(
            title=f"{symbol} - Trading Volume",
            xaxis_title="Date",
            yaxis_title="Volume",
            template=self.template,
            height=self.height
        )
        
        return fig
    
    def plot_technical_analysis(self, df, symbol="Stock"):
        from plotly.subplots import make_subplots
        
        fig = make_subplots(
            rows=3, cols=1,
            shared_xaxes=True,
            vertical_spacing=0.05,
            row_heights=[0.5, 0.25, 0.25],
            subplot_titles=(f'{symbol} Price', 'RSI', 'MACD')
        )
        
        fig.add_trace(go.Scatter(
            x=df.index, y=df['Close'],
            mode='lines', name='Close',
            line=dict(color='blue', width=2)
        ), row=1, col=1)
        
        if 'SMA_20' in df.columns:
            fig.add_trace(go.Scatter(
                x=df.index, y=df['SMA_20'],
                mode='lines', name='SMA 20',
                line=dict(color='orange', width=1)
            ), row=1, col=1)
        
        if 'RSI' in df.columns:
            fig.add_trace(go.Scatter(
                x=df.index, y=df['RSI'],
                mode='lines', name='RSI',
                line=dict(color='purple', width=2)
            ), row=2, col=1)
            
            fig.add_hline(y=70, line_dash="dash", line_color="red", row=2, col=1)
            fig.add_hline(y=30, line_dash="dash", line_color="green", row=2, col=1)
        
        if 'MACD' in df.columns:
            fig.add_trace(go.Scatter(
                x=df.index, y=df['MACD'],
                mode='lines', name='MACD',
                line=dict(color='blue', width=2)
            ), row=3, col=1)
            
            fig.add_trace(go.Scatter(
                x=df.index, y=df['MACD_Signal'],
                mode='lines', name='Signal',
                line=dict(color='red', width=2)
            ), row=3, col=1)
        
        fig.update_layout(
            height=900,
            template=self.template,
            showlegend=True,
            hovermode='x unified'
        )
        
        fig.update_yaxes(title_text="Price ($)", row=1, col=1)
        fig.update_yaxes(title_text="RSI", row=2, col=1)
        fig.update_yaxes(title_text="MACD", row=3, col=1)
        
        return fig