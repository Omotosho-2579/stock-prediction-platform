# src/alerts/alert_manager.py

from datetime import datetime
from pathlib import Path
import sys

project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from src.alerts.telegram_bot import TelegramBot
from src.alerts.email_sender import EmailSender
from src.alerts.discord_webhook import DiscordWebhook
from src.data.data_loader import DataLoader
from src.utils.logger import Logger

class AlertManager:
    def __init__(self):
        self.logger = Logger(__name__)
        self.telegram = TelegramBot()
        self.email = EmailSender()
        self.discord = DiscordWebhook()
        self.data_loader = DataLoader()
        self.active_alerts = []
    
    def add_alert(self, alert_config):
        required_fields = ['symbol', 'condition', 'target_price', 'alert_type']
        
        for field in required_fields:
            if field not in alert_config:
                self.logger.error(f"Missing required field: {field}")
                return False
        
        alert_config['created_at'] = datetime.now().isoformat()
        alert_config['triggered'] = False
        
        self.active_alerts.append(alert_config)
        self.logger.info(f"Alert added for {alert_config['symbol']}")
        
        return True
    
    def remove_alert(self, alert_id):
        self.active_alerts = [a for a in self.active_alerts if a.get('id') != alert_id]
        self.logger.info(f"Alert {alert_id} removed")
    
    def check_alerts(self):
        triggered_alerts = []
        
        for alert in self.active_alerts:
            if alert.get('triggered'):
                continue
            
            symbol = alert['symbol']
            condition = alert['condition']
            target_price = alert['target_price']
            
            try:
                df = self.data_loader.load_stock_data(symbol, period='1d')
                
                if df is None or df.empty:
                    continue
                
                current_price = df['Close'].iloc[-1]
                
                is_triggered = False
                
                if condition == 'Above' and current_price >= target_price:
                    is_triggered = True
                elif condition == 'Below' and current_price <= target_price:
                    is_triggered = True
                elif condition == 'Equals' and abs(current_price - target_price) < 0.01:
                    is_triggered = True
                
                if is_triggered:
                    alert['triggered'] = True
                    alert['triggered_at'] = datetime.now().isoformat()
                    alert['triggered_price'] = current_price
                    
                    self._send_alert_notification(alert, current_price)
                    triggered_alerts.append(alert)
                    
                    self.logger.info(f"Alert triggered for {symbol}: {current_price} {condition} {target_price}")
            
            except Exception as e:
                self.logger.error(f"Error checking alert for {symbol}: {str(e)}")
        
        return triggered_alerts
    
    def _send_alert_notification(self, alert, current_price):
        symbol = alert['symbol']
        target_price = alert['target_price']
        condition = alert['condition']
        notification_methods = alert.get('notification_methods', ['telegram'])
        
        if 'telegram' in notification_methods:
            self.telegram.send_price_alert(symbol, current_price, target_price, condition)
        
        if 'email' in notification_methods and alert.get('email'):
            self.email.send_price_alert_email(alert['email'], symbol, current_price, target_price, condition)
        
        if 'discord' in notification_methods and alert.get('discord_webhook'):
            discord = DiscordWebhook(alert['discord_webhook'])
            discord.send_price_alert(symbol, current_price, target_price, condition)
    
    def get_active_alerts(self):
        return [a for a in self.active_alerts if not a.get('triggered')]
    
    def get_triggered_alerts(self):
        return [a for a in self.active_alerts if a.get('triggered')]
    
    def reset_triggered_alerts(self):
        for alert in self.active_alerts:
            if alert.get('triggered'):
                alert['triggered'] = False
                alert.pop('triggered_at', None)
                alert.pop('triggered_price', None)
        
        self.logger.info("All triggered alerts have been reset")
    
    def clear_all_alerts(self):
        count = len(self.active_alerts)
        self.active_alerts = []
        self.logger.info(f"Cleared {count} alerts")