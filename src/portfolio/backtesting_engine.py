# src/portfolio/backtesting_engine.py

import pandas as pd
import numpy as np
from pathlib import Path
import sys

project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from src.trading_signals.strategy_engine import StrategyEngine
from src.utils.logger import Logger

class BacktestingEngine:
    def __init__(self):
        self.logger = Logger(__name__)
        self.strategy_engine = StrategyEngine()
    
    def run_backtest(self, df, strategy_params, backtest_config):
        initial_capital = backtest_config.get('initial_capital', 10000)
        position_size = backtest_config.get('position_size', 1.0)
        commission = backtest_config.get('commission', 1.0)
        
        cash = initial_capital
        shares = 0
        trades = []
        portfolio_history = []
        
        strategy_type = strategy_params.get('type', 'ma_crossover')
        
        for i in range(1, len(df)):
            current_price = df['Close'].iloc[i]
            
            signal = self._generate_signal(df.iloc[:i+1], strategy_type, strategy_params)
            
            portfolio_value = cash + (shares * current_price)
            portfolio_history.append({
                'Date': df.index[i],
                'Portfolio Value': portfolio_value,
                'Cash': cash,
                'Shares': shares,
                'Price': current_price
            })
            
            if signal == 'BUY' and shares == 0 and cash > current_price:
                max_shares = int((cash * position_size) / current_price)
                
                if max_shares > 0:
                    shares = max_shares
                    cost = (shares * current_price) + commission
                    cash -= cost
                    
                    trades.append({
                        'Date': df.index[i],
                        'Type': 'BUY',
                        'Price': current_price,
                        'Shares': shares,
                        'Value': shares * current_price,
                        'Commission': commission
                    })
            
            elif signal == 'SELL' and shares > 0:
                proceeds = (shares * current_price) - commission
                cash += proceeds
                
                trades.append({
                    'Date': df.index[i],
                    'Type': 'SELL',
                    'Price': current_price,
                    'Shares': shares,
                    'Value': shares * current_price,
                    'Commission': commission
                })
                
                shares = 0
        
        final_value = cash + (shares * df['Close'].iloc[-1])
        
        results = self._calculate_backtest_metrics(
            initial_capital, final_value, trades, portfolio_history
        )
        
        results['trades'] = trades
        results['portfolio_history'] = pd.DataFrame(portfolio_history)
        
        return results
    
    def _generate_signal(self, df, strategy_type, params):
        if len(df) < 50:
            return 'HOLD'
        
        if strategy_type == 'ma_crossover':
            short_window = params.get('short_window', 20)
            long_window = params.get('long_window', 50)
            
            if len(df) < long_window:
                return 'HOLD'
            
            sma_short = df['Close'].rolling(window=short_window).mean()
            sma_long = df['Close'].rolling(window=long_window).mean()
            
            if sma_short.iloc[-1] > sma_long.iloc[-1] and sma_short.iloc[-2] <= sma_long.iloc[-2]:
                return 'BUY'
            elif sma_short.iloc[-1] < sma_long.iloc[-1] and sma_short.iloc[-2] >= sma_long.iloc[-2]:
                return 'SELL'
        
        elif strategy_type == 'rsi':
            period = params.get('period', 14)
            oversold = params.get('oversold', 30)
            overbought = params.get('overbought', 70)
            
            if len(df) < period:
                return 'HOLD'
            
            delta = df['Close'].diff()
            gain = delta.where(delta > 0, 0)
            loss = -delta.where(delta < 0, 0)
            
            avg_gain = gain.rolling(window=period).mean()
            avg_loss = loss.rolling(window=period).mean()
            
            rs = avg_gain / avg_loss
            rsi = 100 - (100 / (1 + rs))
            
            if rsi.iloc[-1] < oversold:
                return 'BUY'
            elif rsi.iloc[-1] > overbought:
                return 'SELL'
        
        elif strategy_type == 'macd':
            fast_period = params.get('fast_period', 12)
            slow_period = params.get('slow_period', 26)
            signal_period = params.get('signal_period', 9)
            
            if len(df) < slow_period + signal_period:
                return 'HOLD'
            
            ema_fast = df['Close'].ewm(span=fast_period, adjust=False).mean()
            ema_slow = df['Close'].ewm(span=slow_period, adjust=False).mean()
            
            macd = ema_fast - ema_slow
            macd_signal = macd.ewm(span=signal_period, adjust=False).mean()
            
            if macd.iloc[-1] > macd_signal.iloc[-1] and macd.iloc[-2] <= macd_signal.iloc[-2]:
                return 'BUY'
            elif macd.iloc[-1] < macd_signal.iloc[-1] and macd.iloc[-2] >= macd_signal.iloc[-2]:
                return 'SELL'
        
        return 'HOLD'
    
    def _calculate_backtest_metrics(self, initial_capital, final_value, trades, portfolio_history):
        total_return = ((final_value - initial_capital) / initial_capital) * 100
        
        total_trades = len(trades)
        
        winning_trades = 0
        losing_trades = 0
        total_profit = 0
        total_loss = 0
        
        buy_trades = [t for t in trades if t['Type'] == 'BUY']
        sell_trades = [t for t in trades if t['Type'] == 'SELL']
        
        for i in range(min(len(buy_trades), len(sell_trades))):
            buy_price = buy_trades[i]['Price']
            sell_price = sell_trades[i]['Price']
            
            profit_loss = (sell_price - buy_price) * buy_trades[i]['Shares']
            
            if profit_loss > 0:
                winning_trades += 1
                total_profit += profit_loss
            else:
                losing_trades += 1
                total_loss += abs(profit_loss)
        
        avg_win = total_profit / winning_trades if winning_trades > 0 else 0
        avg_loss = total_loss / losing_trades if losing_trades > 0 else 0
        
        largest_win = max([abs((sell_trades[i]['Price'] - buy_trades[i]['Price']) * buy_trades[i]['Shares']) 
                          for i in range(min(len(buy_trades), len(sell_trades)))], default=0)
        largest_loss = min([((sell_trades[i]['Price'] - buy_trades[i]['Price']) * buy_trades[i]['Shares']) 
                           for i in range(min(len(buy_trades), len(sell_trades)))], default=0)
        
        if portfolio_history:
            returns = []
            for i in range(1, len(portfolio_history)):
                ret = (portfolio_history[i]['Portfolio Value'] - portfolio_history[i-1]['Portfolio Value']) / portfolio_history[i-1]['Portfolio Value']
                returns.append(ret)
            
            if returns:
                sharpe_ratio = (np.mean(returns) / np.std(returns)) * np.sqrt(252) if np.std(returns) > 0 else 0
                
                cumulative = [portfolio_history[0]['Portfolio Value']]
                for i in range(len(returns)):
                    cumulative.append(cumulative[-1] * (1 + returns[i]))
                
                running_max = [cumulative[0]]
                for val in cumulative[1:]:
                    running_max.append(max(running_max[-1], val))
                
                drawdowns = [(cumulative[i] - running_max[i]) / running_max[i] * 100 for i in range(len(cumulative))]
                max_drawdown = min(drawdowns) if drawdowns else 0
                
                volatility = np.std(returns) * np.sqrt(252) * 100
            else:
                sharpe_ratio = 0
                max_drawdown = 0
                volatility = 0
        else:
            sharpe_ratio = 0
            max_drawdown = 0
            volatility = 0
        
        return {
            'initial_capital': initial_capital,
            'final_value': final_value,
            'total_return': total_return,
            'total_trades': total_trades,
            'winning_trades': winning_trades,
            'losing_trades': losing_trades,
            'avg_win': avg_win,
            'avg_loss': avg_loss,
            'largest_win': largest_win,
            'largest_loss': largest_loss,
            'sharpe_ratio': sharpe_ratio,
            'max_drawdown': max_drawdown,
            'volatility': volatility
        }
    
    def plot_strategy_vs_buy_hold(self, portfolio_history, original_df):
        import plotly.graph_objects as go
        
        buy_hold_initial = original_df['Close'].iloc[0]
        buy_hold_values = (original_df['Close'] / buy_hold_initial) * portfolio_history['Portfolio Value'].iloc[0]
        
        fig = go.Figure()
        
        fig.add_trace(go.Scatter(
            x=portfolio_history['Date'],
            y=portfolio_history['Portfolio Value'],
            mode='lines',
            name='Strategy',
            line=dict(color='blue', width=2)
        ))
        
        fig.add_trace(go.Scatter(
            x=original_df.index,
            y=buy_hold_values,
            mode='lines',
            name='Buy & Hold',
            line=dict(color='green', width=2, dash='dash')
        ))
        
        fig.update_layout(
            title='Strategy Performance vs Buy & Hold',
            xaxis_title='Date',
            yaxis_title='Portfolio Value ($)',
            hovermode='x unified',
            height=500
        )
        
        return fig 