# src/visualization/technical_overlays.py

import plotly.graph_objects as go
from pathlib import Path
import sys

project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from app.config import CHART_HEIGHT, CHART_TEMPLATE
from src.utils.logger import Logger

class TechnicalOverlays:
    def __init__(self):
        self.logger = Logger(__name__)
        self.template = CHART_TEMPLATE
        self.height = CHART_HEIGHT
    
    def plot_bollinger_bands(self, df, symbol="Stock"):
        fig = go.Figure()
        
        fig.add_trace(go.Scatter(
            x=df.index,
            y=df['Close'],
            mode='lines',
            name='Close Price',
            line=dict(color='blue', width=2)
        ))
        
        if 'BB_Upper' in df.columns:
            fig.add_trace(go.Scatter(
                x=df.index,
                y=df['BB_Upper'],
                mode='lines',
                name='Upper Band',
                line=dict(color='red', width=1, dash='dash')
            ))
        
        if 'BB_Middle' in df.columns:
            fig.add_trace(go.Scatter(
                x=df.index,
                y=df['BB_Middle'],
                mode='lines',
                name='Middle Band (SMA 20)',
                line=dict(color='orange', width=1)
            ))
        
        if 'BB_Lower' in df.columns:
            fig.add_trace(go.Scatter(
                x=df.index,
                y=df['BB_Lower'],
                mode='lines',
                name='Lower Band',
                line=dict(color='green', width=1, dash='dash'),
                fill='tonexty',
                fillcolor='rgba(128, 128, 128, 0.2)'
            ))
        
        fig.update_layout(
            title=f'{symbol} - Bollinger Bands',
            xaxis_title='Date',
            yaxis_title='Price ($)',
            template=self.template,
            height=self.height,
            hovermode='x unified'
        )
        
        return fig
    
    def plot_support_resistance(self, df, symbol="Stock", levels=None):
        fig = go.Figure()
        
        fig.add_trace(go.Scatter(
            x=df.index,
            y=df['Close'],
            mode='lines',
            name='Close Price',
            line=dict(color='blue', width=2)
        ))
        
        if levels is None:
            recent_high = df['High'].tail(50).max()
            recent_low = df['Low'].tail(50).min()
            levels = {
                'Resistance': recent_high,
                'Support': recent_low
            }
        
        for level_name, level_value in levels.items():
            color = 'red' if 'Resistance' in level_name else 'green'
            fig.add_hline(
                y=level_value,
                line_dash="dash",
                line_color=color,
                annotation_text=f"{level_name}: ${level_value:.2f}",
                annotation_position="right"
            )
        
        fig.update_layout(
            title=f'{symbol} - Support & Resistance Levels',
            xaxis_title='Date',
            yaxis_title='Price ($)',
            template=self.template,
            height=self.height,
            hovermode='x unified'
        )
        
        return fig
    
    def plot_fibonacci_retracement(self, df, symbol="Stock"):
        fig = go.Figure()
        
        fig.add_trace(go.Scatter(
            x=df.index,
            y=df['Close'],
            mode='lines',
            name='Close Price',
            line=dict(color='blue', width=2)
        ))
        
        price_max = df['High'].max()
        price_min = df['Low'].min()
        diff = price_max - price_min
        
        fib_levels = {
            '0% (High)': price_max,
            '23.6%': price_max - 0.236 * diff,
            '38.2%': price_max - 0.382 * diff,
            '50%': price_max - 0.5 * diff,
            '61.8%': price_max - 0.618 * diff,
            '100% (Low)': price_min
        }
        
        colors = ['red', 'orange', 'yellow', 'lightgreen', 'green', 'darkgreen']
        
        for i, (level_name, level_value) in enumerate(fib_levels.items()):
            fig.add_hline(
                y=level_value,
                line_dash="dash",
                line_color=colors[i],
                annotation_text=f"{level_name}: ${level_value:.2f}",
                annotation_position="left"
            )
        
        fig.update_layout(
            title=f'{symbol} - Fibonacci Retracement',
            xaxis_title='Date',
            yaxis_title='Price ($)',
            template=self.template,
            height=self.height,
            hovermode='x unified'
        )
        
        return fig
    
    def plot_volume_profile(self, df, symbol="Stock"):
        from plotly.subplots import make_subplots
        
        fig = make_subplots(
            rows=1, cols=2,
            column_widths=[0.8, 0.2],
            shared_yaxes=True,
            horizontal_spacing=0.01
        )
        
        fig.add_trace(go.Candlestick(
            x=df.index,
            open=df['Open'],
            high=df['High'],
            low=df['Low'],
            close=df['Close'],
            name='OHLC'
        ), row=1, col=1)
        
        price_bins = 50
        price_min = df['Low'].min()
        price_max = df['High'].max()
        price_range = price_max - price_min
        bin_size = price_range / price_bins
        
        volume_at_price = {}
        for i in range(len(df)):
            price = df['Close'].iloc[i]
            volume = df['Volume'].iloc[i]
            bin_idx = int((price - price_min) / bin_size)
            volume_at_price[bin_idx] = volume_at_price.get(bin_idx, 0) + volume
        
        prices = [price_min + (i + 0.5) * bin_size for i in range(price_bins)]
        volumes = [volume_at_price.get(i, 0) for i in range(price_bins)]
        
        fig.add_trace(go.Bar(
            x=volumes,
            y=prices,
            orientation='h',
            name='Volume Profile',
            marker_color='rgba(100, 100, 100, 0.5)'
        ), row=1, col=2)
        
        fig.update_layout(
            title=f'{symbol} - Volume Profile',
            template=self.template,
            height=self.height,
            showlegend=False,
            xaxis_rangeslider_visible=False
        )
        
        fig.update_xaxes(title_text="Date", row=1, col=1)
        fig.update_xaxes(title_text="Volume", row=1, col=2)
        fig.update_yaxes(title_text="Price ($)", row=1, col=1)
        
        return fig