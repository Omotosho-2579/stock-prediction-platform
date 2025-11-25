# src/alerts/email_sender.py

import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from pathlib import Path
import sys

project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from app.config import EMAIL_SENDER, EMAIL_PASSWORD, SMTP_SERVER, SMTP_PORT
from src.utils.logger import Logger

class EmailSender:
    def __init__(self):
        self.logger = Logger(__name__)
        self.sender_email = EMAIL_SENDER
        self.sender_password = EMAIL_PASSWORD
        self.smtp_server = SMTP_SERVER
        self.smtp_port = SMTP_PORT
    
    def send_email(self, recipient_email, subject, body, html=True):
        if not self.sender_email or not self.sender_password:
            self.logger.error("Email credentials not configured")
            return False
        
        try:
            message = MIMEMultipart('alternative')
            message['From'] = self.sender_email
            message['To'] = recipient_email
            message['Subject'] = subject
            
            if html:
                html_part = MIMEText(body, 'html')
                message.attach(html_part)
            else:
                text_part = MIMEText(body, 'plain')
                message.attach(text_part)
            
            with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                server.starttls()
                server.login(self.sender_email, self.sender_password)
                server.send_message(message)
            
            self.logger.info(f"Email sent successfully to {recipient_email}")
            return True
        
        except Exception as e:
            self.logger.error(f"Error sending email: {str(e)}")
            return False
    
    def send_price_alert_email(self, recipient, symbol, current_price, target_price, condition):
        subject = f"Price Alert: {symbol} {condition} ${target_price:.2f}"
        
        body = f"""
        <html>
        <body style="font-family: Arial, sans-serif;">
            <h2 style="color: #1f77b4;">🔔 Price Alert Triggered</h2>
            <p><strong>Symbol:</strong> {symbol}</p>
            <p><strong>Current Price:</strong> ${current_price:.2f}</p>
            <p><strong>Target Price:</strong> ${target_price:.2f}</p>
            <p><strong>Condition:</strong> {condition}</p>
            <hr>
            <p style="color: #666; font-size: 12px;">
                This is an automated alert from Stock Prediction Platform
            </p>
        </body>
        </html>
        """
        
        return self.send_email(recipient, subject, body, html=True)
    
    def send_trading_signal_email(self, recipient, symbol, signal, confidence, price, reasons):
        subject = f"Trading Signal: {signal} {symbol}"
        
        color = "#28a745" if signal == "BUY" else "#dc3545" if signal == "SELL" else "#ffc107"
        
        reasons_html = "<ul>" + "".join([f"<li>{r}</li>" for r in reasons]) + "</ul>"
        
        body = f"""
        <html>
        <body style="font-family: Arial, sans-serif;">
            <h2 style="color: {color};">{signal} Signal: {symbol}</h2>
            <p><strong>Confidence:</strong> {confidence}%</p>
            <p><strong>Current Price:</strong> ${price:.2f}</p>
            <h3>Key Reasons:</h3>
            {reasons_html}
            <hr>
            <p style="color: #666; font-size: 12px;">
                This is an AI-generated signal. Not financial advice.
            </p>
        </body>
        </html>
        """
        
        return self.send_email(recipient, subject, body, html=True)
    
    def send_daily_digest(self, recipient, portfolio_summary, top_movers, alerts_triggered):
        subject = f"Daily Digest - {self._get_date()}"
        
        portfolio_html = f"""
        <div style="background-color: #f8f9fa; padding: 15px; border-radius: 5px; margin: 10px 0;">
            <h3>Portfolio Summary</h3>
            <p><strong>Total Value:</strong> ${portfolio_summary.get('total_value', 0):,.2f}</p>
            <p><strong>Daily Change:</strong> 
                <span style="color: {'green' if portfolio_summary.get('daily_change', 0) > 0 else 'red'};">
                    ${portfolio_summary.get('daily_change', 0):,.2f} ({portfolio_summary.get('daily_change_pct', 0):+.2f}%)
                </span>
            </p>
        </div>
        """
        
        movers_html = "<ul>"
        for mover in top_movers[:5]:
            movers_html += f"<li><strong>{mover['symbol']}:</strong> {mover['change']:+.2f}%</li>"
        movers_html += "</ul>"
        
        body = f"""
        <html>
        <body style="font-family: Arial, sans-serif;">
            <h2 style="color: #1f77b4;">📊 Daily Market Digest</h2>
            {portfolio_html}
            <h3>Top Movers</h3>
            {movers_html}
            <h3>Alerts Triggered Today</h3>
            <p>{len(alerts_triggered)} alerts were triggered</p>
            <hr>
            <p style="color: #666; font-size: 12px;">
                Daily digest from Stock Prediction Platform
            </p>
        </body>
        </html>
        """
        
        return self.send_email(recipient, subject, body, html=True)
    
    def _get_date(self):
        from datetime import datetime
        return datetime.now().strftime('%Y-%m-%d')
    
    def test_connection(self):
        try:
            with smtplib.SMTP(self.smtp_server, self.smtp_port, timeout=10) as server:
                server.starttls()
                server.login(self.sender_email, self.sender_password)
            
            self.logger.info("Email connection test successful")
            return True
        
        except Exception as e:
            self.logger.error(f"Email connection test failed: {str(e)}")
            return False