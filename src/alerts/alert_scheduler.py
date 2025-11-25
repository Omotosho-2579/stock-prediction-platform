# src/alerts/alert_scheduler.py

from datetime import datetime, time
from pathlib import Path
import sys
import threading

project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from src.alerts.alert_manager import AlertManager
from src.utils.logger import Logger

class AlertScheduler:
    def __init__(self):
        self.logger = Logger(__name__)
        self.alert_manager = AlertManager()
        self.is_running = False
        self.check_interval = 300
        self.scheduler_thread = None
    
    def start(self, interval_seconds=300):
        if self.is_running:
            self.logger.warning("Scheduler is already running")
            return
        
        self.check_interval = interval_seconds
        self.is_running = True
        
        self.scheduler_thread = threading.Thread(target=self._run_scheduler, daemon=True)
        self.scheduler_thread.start()
        
        self.logger.info(f"Alert scheduler started with {interval_seconds}s interval")
    
    def stop(self):
        if not self.is_running:
            self.logger.warning("Scheduler is not running")
            return
        
        self.is_running = False
        
        if self.scheduler_thread:
            self.scheduler_thread.join(timeout=5)
        
        self.logger.info("Alert scheduler stopped")
    
    def _run_scheduler(self):
        import time as time_module
        
        while self.is_running:
            try:
                self.logger.info("Running scheduled alert check")
                triggered = self.alert_manager.check_alerts()
                
                if triggered:
                    self.logger.info(f"Found {len(triggered)} triggered alerts")
                
                time_module.sleep(self.check_interval)
            
            except Exception as e:
                self.logger.error(f"Error in scheduler: {str(e)}")
                time_module.sleep(60)
    
    def schedule_daily_digest(self, send_time, recipient_email):
        self.logger.info(f"Daily digest scheduled for {send_time}")
    
    def check_now(self):
        return self.alert_manager.check_alerts()
    
    def get_status(self):
        return {
            'is_running': self.is_running,
            'check_interval': self.check_interval,
            'active_alerts': len(self.alert_manager.get_active_alerts()),
            'triggered_alerts': len(self.alert_manager.get_triggered_alerts())
        }