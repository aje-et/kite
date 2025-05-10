
import os
import logging
import json
import requests
from datetime import datetime, timezone, timedelta
import newrelic.agent
import traceback

class NewRelicLogger:
    """Singleton logger class for sending logs to New Relic"""
    
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(NewRelicLogger, cls).__new__(cls)
        return cls._instance
    
    def __init__(self):
        """Initialize the logger instance"""
        if not hasattr(self, 'initialized'):
            self.ist_timezone = timezone(timedelta(hours=5, minutes=30))
            self.LOG_API_ENDPOINT = "https://log-api.newrelic.com/log/v1"
            self.api_key = os.environ.get('NEW_RELIC_API_KEY', '')
            self.app_name = "KiteApp"
            
            if not self.api_key:
                print("New Relic API key not found. Logs will only be saved locally.")
            
            self.initialized = True
    
    def logger(self, log_type: str, message: str, attributes: dict = None):
        """Log a message to New Relic
        
        Args:
            log_type (str): Type of log (info, warning, error, critical)
            message (str): The log message
        """
        try:
            timestamp = datetime.now(self.ist_timezone).isoformat()
            
            log_entry = {
                "timestamp": timestamp,
                "message": message,
                "log.level": log_type.upper(),
                "service.name": self.app_name
            }
            
            if attributes and isinstance(attributes, dict):
                for key, value in attributes.items():
                    log_entry[key] = value
            
            payload = [{
                "common": {
                    "attributes": {
                        "service": self.app_name,
                        "environment": os.environ.get('ENVIRONMENT', 'development')
                    }
                },
                "logs": [log_entry]
            }]
            
            headers = {
                "Content-Type": "application/json",
                "Api-Key": self.api_key
            }
            
            response = requests.post(
                self.LOG_API_ENDPOINT,
                headers=headers,
                data=json.dumps(payload),
                timeout=5  # 5 second timeout
            )
            
            if response.status_code == 202:
                print("✅ Successfully sent log to New Relic")
                return True
            else:
                print(f"❌ Failed to send log to New Relic. Status code: {response.status_code}")
                return False
                
        except Exception as e:
            print(f"❌ ERROR sending log to New Relic: {str(e)}")
            print(f"Exception type: {type(e).__name__}")
            print(f"Traceback: {traceback.format_exc()}")
            return False

    def info(self, message: str):
        """Log an info message
        
        Args:
            message (str): The info message to log
        """
        return self.logger("info", message)

    def warn(self, message: str):
        """Log a warning message
        
        Args:
            message (str): The warning message to log
        """
        return self.logger("warning", message)

    def debug(self, message: str):
        """Log a debug message
        
        Args:
            message (str): The debug message to log
        """
        return self.logger("debug", message)

    def error(self, message: str):
        """Log an error message
        
        Args:
            message (str): The error message to log
        """
        return self.logger("error", message)

    def critical(self, message: str):
        """Log a critical message
        
        Args:
            message (str): The critical message to log
        """
        return self.logger("critical", message)

# Get the singleton logger instance
def get_logger():
    """Get the singleton logger instance"""
    return NewRelicLogger()

# Example usage
if __name__ == "__main__":
    # Initialize logger
    logger = get_logger()
    
    # Log messages
    logger.logger("info", "This is an info message")
    logger.logger("error", "This is an error message")
    
    # Log with attributes
    logger.logger("info", "User login successful", {
        "user_id": "123",
        "ip_address": "192.168.1.1"
    })
