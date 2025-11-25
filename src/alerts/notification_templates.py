# src/alerts/notification_templates.py

from datetime import datetime
from pathlib import Path
import sys

project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from src.utils.logger import Logger

class NotificationTemplates:
    def __init__(self):
        self.logger = Logger(__name__)
    
    def price_alert_template(self, symbol, current_price, target_price, condition):
        return {
            'subject': f"Price Alert: {symbol}",
            'text': f"{symbol} is now {condition} ${target_price:.2f}. Current price: ${current_price:.2f}",
            'html': f"""
            <html>
            <body>
                <h2>Price Alert Triggered</h2>
                <p><strong>Symbol:</strong> {symbol}</p>
                <p><strong>Condition:</strong> {condition}</strong>
                <p><strong>Target Price:</strong> ${target_price:.2f}</p>
                <p><strong>Current Price:</strong> ${current_price:.2f}</p>
            </body>
            </html>
            """
        }
    
    def trading_signal_template(self, symbol, signal, confidence, price, reasons):
        reasons_list = "\n".join([f"• {r}" for r in reasons])
        
        return {
            'subject': f"Trading Signal: {signal} {symbol}",
            'text': f"{signal} signal for {symbol} at ${price:.2f} (Confidence: {confidence}%)\n\nReasons:\n{reasons_list}",
            'html': f"""
            <html>
            <body>
                <h2>{signal} Signal: {symbol}</h2>
                <p><strong>Confidence:</strong> {confidence}%</p>
                <p><strong>Price:</strong> ${price:.2f}</p>
                <h3>Key Reasons:</h3>
                <ul>
                    {"".join([f"<li>{r}</li>" for r in reasons])}
                </ul>
            </body>
            </html>
            """
        }
    
    def portfolio_update_template(self, total_value, daily_change, daily_change_pct, holdings):
        holdings_text = "\n".join([f"• {h['symbol']}: ${h['value']:,.2f}" for h in holdings])
        
        return {
            'subject': "Portfolio Update",
            'text': f"Portfolio Value: ${total_value:,.2f}\nDaily Change: ${daily_change:,.2f} ({daily_change_pct:+.2f}%)\n\nHoldings:\n{holdings_text}",
            'html': f"""
            <html>
            <body>
                <h2>Portfolio Update</h2>
                <p><strong>Total Value:</strong> ${total_value:,.2f}</p>
                <p><strong>Daily Change:</strong> ${daily_change:,.2f} ({daily_change_pct:+.2f}%)</p>
                <h3>Holdings:</h3>
                <ul>
                    {"".join([f"<li>{h['symbol']}: ${h['value']:,.2f}</li>" for h in holdings])}
                </ul>
            </body>
            </html>
            """
        }
    
    def earnings_reminder_template(self, symbol, earnings_date):
        return {
            'subject': f"Earnings Reminder: {symbol}",
            'text': f"{symbol} earnings report scheduled for {earnings_date}",
            'html': f"""
            <html>
            <body>
                <h2>Upcoming Earnings Report</h2>
                <p><strong>Symbol:</strong> {symbol}</p>
                <p><strong>Date:</strong> {earnings_date}</p>
            </body>
            </html>
            """
        }
    
    def market_open_template(self, market_status, indices):
        indices_text = "\n".join([f"• {k}: {v}" for k, v in indices.items()])
        
        return {
            'subject': f"Market {market_status}",
            'text': f"Market is now {market_status}\n\nIndices:\n{indices_text}",
            'html': f"""
            <html>
            <body>
                <h2>Market {market_status}</h2>
                <h3>Major Indices:</h3>
                <ul>
                    {"".join([f"<li>{k}: {v}</li>" for k, v in indices.items()])}
                </ul>
            </body>
            </html>
            """
        }
    
    def custom_alert_template(self, title, message, priority="Normal"):
        return {
            'subject': f"[{priority}] {title}",
            'text': f"{title}\n\n{message}\n\nPriority: {priority}",
            'html': f"""
            <html>
            <body>
                <h2>{title}</h2>
                <p>{message}</p>
                <p><em>Priority: {priority}</em></p>
            </body>
            </html>
            """
        }