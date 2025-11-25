# src/visualization/portfolio_visualizer.py

import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
from pathlib import Path
import sys

project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from app.config import CHART_HEIGHT, CHART_TEMPLATE
from src.utils.logger import Logger

class PortfolioVisualizer:
    def __init__(self):
        self.logger = Logger(__name__)
        self.template = CHART_TEMPLATE
        self.height = CHART_HEIGHT
    
    def plot_allocation_pie(self, allocation_df):
        fig = go.Figure(data=[go.Pie(
            labels=allocation_df['Symbol'],
            values=allocation_df['Value'],
            hole=0.4,
            textinfo='label+percent',
            hovertemplate='<b>%{label}</b><br>Value: $%{value:,.2f}<br>Percentage: %{percent}<extra></extra>'
        )])
        
        fig.update_layout(
            title='Portfolio Allocation',
            template=self.template,
            height=self.height,
            showlegend=True
        )
        
        return fig
    
    def plot_sector_allocation(self, sector_data):
        fig = go.Figure(data=[go.Pie(
            labels=list(sector_data.keys()),
            values=list(sector_data.values()),
            hole=0.3
        )])
        
        fig.update_layout(
            title='Sector Allocation',
            template=self.template,
            height=self.height
        )
        
        return fig
    
    def plot_portfolio_performance(self, portfolio_history):
        if isinstance(portfolio_history, dict):
            dates = list(portfolio_history.keys())
            values = list(portfolio_history.values())
        else:
            dates = portfolio_history['Date']
            values = portfolio_history['Value']
        
        fig = go.Figure()
        
        fig.add_trace(go.Scatter(
            x=dates,
            y=values,
            mode='lines',
            name='Portfolio Value',
            line=dict(color='green', width=3),
            fill='tozeroy',
            fillcolor='rgba(0, 128, 0, 0.2)'
        ))
        
        fig.update_layout(
            title='Portfolio Value Over Time',
            xaxis_title='Date',
            yaxis_title='Portfolio Value ($)',
            template=self.template,
            height=self.height,
            hovermode='x unified'
        )
        
        return fig
    
    def plot_holdings_comparison(self, holdings_df):
        fig = go.Figure(data=[
            go.Bar(
                x=holdings_df['Symbol'],
                y=holdings_df['Value'],
                text=holdings_df['Value'],
                texttemplate='$%{text:,.0f}',
                textposition='outside',
                marker_color='blue'
            )
        ])
        
        fig.update_layout(
            title='Holdings Value Comparison',
            xaxis_title='Stock Symbol',
            yaxis_title='Value ($)',
            template=self.template,
            height=self.height
        )
        
        return fig
    
    def plot_gains_losses(self, holdings_df):
        colors = ['green' if x > 0 else 'red' for x in holdings_df['Gain/Loss']]
        
        fig = go.Figure(data=[
            go.Bar(
                x=holdings_df['Symbol'],
                y=holdings_df['Gain/Loss'],
                marker_color=colors,
                text=holdings_df['Gain/Loss'],
                texttemplate='$%{text:,.2f}',
                textposition='outside'
            )
        ])
        
        fig.add_hline(y=0, line_dash="dash", line_color="black")
        
        fig.update_layout(
            title='Gains/Losses by Position',
            xaxis_title='Stock Symbol',
            yaxis_title='Gain/Loss ($)',
            template=self.template,
            height=self.height
        )
        
        return fig
    
    def plot_diversification_chart(self, allocation_df):
        fig = go.Figure(data=[go.Treemap(
            labels=allocation_df['Symbol'],
            parents=['Portfolio'] * len(allocation_df),
            values=allocation_df['Value'],
            textinfo='label+value+percent parent',
            marker=dict(colorscale='Blues')
        )])
        
        fig.update_layout(
            title='Portfolio Diversification (Treemap)',
            template=self.template,
            height=self.height
        )
        
        return fig
    
    def plot_returns_distribution(self, returns):
        fig = go.Figure()
        
        fig.add_trace(go.Histogram(
            x=returns,
            nbinsx=30,
            name='Returns',
            marker_color='blue'
        ))
        
        fig.add_vline(x=returns.mean(), line_dash="dash", line_color="red", 
                     annotation_text=f"Mean: {returns.mean():.2f}%")
        
        fig.update_layout(
            title='Portfolio Returns Distribution',
            xaxis_title='Return (%)',
            yaxis_title='Frequency',
            template=self.template,
            height=self.height
        )
        
        return fig