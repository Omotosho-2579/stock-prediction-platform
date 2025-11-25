# src/alerts/discord_webhook.py

import requests
from pathlib import Path
import sys

project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from src.utils.logger import Logger

class DiscordWebhook:
    def __init__(self, webhook_url=None):
        self.logger = Logger(__name__)
        self.webhook_url = webhook_url
    
    def send_message(self, content, embeds=None):
        if not self.webhook_url:
            self.logger.error("Discord webhook URL not configured")
            return False
        
        try:
            payload = {'content': content}
            
            if embeds:
                payload['embeds'] = embeds
            
            response = requests.post(self.webhook_url, json=payload, timeout=10)
            
            if response.status_code in [200, 204]:
                self.logger.info("Discord message sent successfully")
                return True
            else:
                self.logger.error(f"Discord webhook error: {response.status_code}")
                return False
        
        except Exception as e:
            self.logger.error(f"Error sending Discord message: {str(e)}")
            return False
    
    def send_price_alert(self, symbol, current_price, target_price, condition):
        embed = {
            'title': f'🔔 Price Alert: {symbol}',
            'color': 3447003,
            'fields': [
                {'name': 'Current Price', 'value': f'${current_price:.2f}', 'inline': True},
                {'name': 'Target Price', 'value': f'${target_price:.2f}', 'inline': True},
                {'name': 'Condition', 'value': condition, 'inline': False}
            ],
            'timestamp': self._get_iso_timestamp()
        }
        
        return self.send_message('', embeds=[embed])
    
    def send_trading_signal(self, symbol, signal, confidence, price):
        color = 3066993 if signal == "BUY" else 15158332 if signal == "SELL" else 16776960
        
        embed = {
            'title': f'{signal} Signal: {symbol}',
            'color': color,
            'fields': [
                {'name': 'Signal', 'value': signal, 'inline': True},
                {'name': 'Confidence', 'value': f'{confidence}%', 'inline': True},
                {'name': 'Price', 'value': f'${price:.2f}', 'inline': True}
            ],
            'timestamp': self._get_iso_timestamp()
        }
        
        return self.send_message('', embeds=[embed])
    
    def _get_iso_timestamp(self):
        from datetime import datetime
        return datetime.utcnow().isoformat()