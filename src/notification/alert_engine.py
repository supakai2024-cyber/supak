import os
import datetime
import requests
import traceback
from typing import Optional
import src.config as config

class AlertEngine:
    """
    Handles system-wide notifications and logging.
    Supports Console output, File logging, and Telegram.
    """
    def __init__(self, log_file: str = "system_alerts.log"):
        self.log_file = log_file
        self.ensure_log_dir()
        
        # Telegram Setup
        self.tg_enabled = config.TELEGRAM_ENABLED
        self.tg_token = config.TELEGRAM_BOT_TOKEN
        self.tg_chat_id = config.TELEGRAM_CHAT_ID

    def ensure_log_dir(self):
        """Ensures the directory for the log file exists."""
        if os.path.dirname(self.log_file):
            os.makedirs(os.path.dirname(self.log_file), exist_ok=True)

    def send_telegram(self, message: str):
        """Sends a message to the configured Telegram Chat."""
        if not self.tg_enabled or "YOUR_" in self.tg_token:
            return

        url = f"https://api.telegram.org/bot{self.tg_token}/sendMessage"
        payload = {
            "chat_id": self.tg_chat_id,
            "text": message,
            "parse_mode": "Markdown"
        }
        try:
            # Timeout is important to not hang the bot loop
            response = requests.post(url, json=payload, timeout=5)
            if response.status_code != 200:
                print(f"[AlertEngine] Telegram Error: {response.text}")
        except Exception as e:
            print(f"[AlertEngine] Telegram Connection Failed: {e}")

    def send_alert(self, title: str, message: str, level: str = "INFO", color: str = None):
        """
        Sends an alert/notification.
        
        Args:
            title: Short description or Category (e.g., [SIGNAL], [ERROR])
            message: The content of the alert.
            level: INFO, WARNING, ERROR, CRITICAL.
        """
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        # Format for Log/Console
        log_msg = f"[{timestamp}] [{level}] {title}: {message}"
        
        # 1. Console Output
        print(log_msg)
        
        # 2. File Log
        self.log_to_file(log_msg)
        
        # 3. Telegram Dispatch
        # We only send specific important events to avoid spamming
        should_send = False
        emoji = ""
        
        if level == "CRITICAL":
            should_send = True
            emoji = "🚨"
        elif level == "WARNING":
            should_send = True
            emoji = "⚠️"
        elif title in ["SIGNAL", "OPPORTUNITY", "EXECUTION"]:
            should_send = True
            emoji = "🚀"
        elif title == "SYSTEM" and "STARTED" in message:
             # Notify when bot starts
             should_send = True
             emoji = "🤖"

        if should_send and self.tg_enabled:
            tg_msg = f"{emoji} *{title}*\n{message}"
            self.send_telegram(tg_msg)

    def log_to_file(self, message: str):
        try:
            with open(self.log_file, "a", encoding="utf-8") as f:
                f.write(message + "\n")
        except Exception as e:
            print(f"Error writing to log file: {e}")

    def test_alert(self):
        self.send_alert("TEST", "This is a test alert.", "INFO")
