# src/alerts/telegram_bot.py

import requests
from pathlib import Path
import sys

project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from app.config import TELEGRAM_BOT_TOKEN, TELEGRAM_CHAT_ID
from src.utils.logger import Logger

class TelegramBot:
    def __init__(self):
        self.logger = Logger(__name__)
        self.bot_token = TELEGRAM_BOT_TOKEN
        self.chat_id = TELEGRAM_CHAT_ID
        self.base_url = f"https://api.telegram.org/bot{self.bot_token}"
    
    def send_message(self, message, chat_id=None, parse_mode='HTML'):
        if not self.bot_token:
            self.logger.error("Telegram bot token not configured")
            return False
        
        target_chat_id = chat_id or self.chat_id
        
        if not target_chat_id:
            self.logger.error("No chat ID provided")
            return False
        
        try:
            url = f"{self.base_url}/sendMessage"
            payload = {
                'chat_id': target_chat_id,
                'text': message,
                'parse_mode': parse_mode
            }
            
            response = requests.post(url, json=payload, timeout=10)
            
            if response.status_code == 200:
                self.logger.info("Telegram message sent successfully")
                return True
            else:
                self.logger.error(f"Telegram API error: {response.status_code} - {response.text}")
                return False
        
        except Exception as e:
            self.logger.error(f"Error sending Telegram message: {str(e)}")
            return False
    
    def send_price_alert(self, symbol, current_price, target_price, condition):
        message = f"""
<b>🔔 Price Alert Triggered</b>

<b>Symbol:</b> {symbol}
<b>Current Price:</b> ${current_price:.2f}
<b>Target Price:</b> ${target_price:.2f}
<b>Condition:</b> {condition}

<i>Alert triggered at {self._get_timestamp()}</i>
"""
        return self.send_message(message)
    
    def send_trading_signal(self, symbol, signal, confidence, price):
        emoji = "🟢" if signal == "BUY" else "🔴" if signal == "SELL" else "🟡"
        
        message = f"""
<b>{emoji} Trading Signal</b>

<b>Symbol:</b> {symbol}
<b>Signal:</b> {signal}
<b>Confidence:</b> {confidence}%
<b>Current Price:</b> ${price:.2f}

<i>Signal generated at {self._get_timestamp()}</i>
"""
        return self.send_message(message)
    
    def send_portfolio_update(self, total_value, daily_change, daily_change_pct):
        emoji = "📈" if daily_change > 0 else "📉"
        
        message = f"""
<b>{emoji} Portfolio Update</b>

<b>Total Value:</b> ${total_value:,.2f}
<b>Daily Change:</b> ${daily_change:,.2f} ({daily_change_pct:+.2f}%)

<i>Update as of {self._get_timestamp()}</i>
"""
        return self.send_message(message)
    
    def send_custom_alert(self, title, body, priority="Normal"):
        priority_emoji = {
            "Low": "ℹ️",
            "Normal": "📢",
            "High": "⚠️",
            "Critical": "🚨"
        }
        
        emoji = priority_emoji.get(priority, "📢")
        
        message = f"""
<b>{emoji} {title}</b>

{body}

<i>Priority: {priority}</i>
<i>Sent at {self._get_timestamp()}</i>
"""
        return self.send_message(message)
    
    def _get_timestamp(self):
        from datetime import datetime
        return datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    
    def test_connection(self):
        try:
            url = f"{self.base_url}/getMe"
            response = requests.get(url, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                if data.get('ok'):
                    bot_name = data.get('result', {}).get('username', 'Unknown')
                    self.logger.info(f"Telegram bot connected: @{bot_name}")
                    return True
            
            return False
        
        except Exception as e:
            self.logger.error(f"Telegram connection test failed: {str(e)}")
            return False