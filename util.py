import requests
import pyotp
import json
import os
import datetime
import logging
from logging.handlers import RotatingFileHandler
import traceback
from kiteconnect import KiteConnect

# Custom JSON encoder to handle datetime objects
class DateTimeEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, datetime.datetime):
            return obj.strftime('%Y-%m-%d %H:%M:%S')
        elif isinstance(obj, datetime.date):
            return obj.strftime('%Y-%m-%d')
        return super(DateTimeEncoder, self).default(obj)

def setup_logger():
    """Set up the logger with a date-time based filename in the logs directory"""
    # Create logs directory if it doesn't exist
    if not os.path.exists('logs'):
        os.makedirs('logs')
    
    # Generate log filename based on current date and time
    current_time = datetime.datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
    log_filename = f"logs/kite_app_{current_time}.log"
    
    # Configure logger
    logger = logging.getLogger('kite_app')
    logger.setLevel(logging.INFO)
    
    # Create file handler
    file_handler = RotatingFileHandler(log_filename, maxBytes=10485760, backupCount=5)
    file_handler.setLevel(logging.INFO)
    
    # Create formatter
    formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
    file_handler.setFormatter(formatter)
    
    # Add handler to logger
    logger.addHandler(file_handler)
    
    return logger

# Initialize logger
logger = setup_logger()



def validate_access_code(access_code):
    logger.info(f"Validating access code")
    
    expected_code = os.environ.get('CODE', 'MM')
    if not access_code or access_code != expected_code:
        error_response = {
            "status": "error",
            "message": "Invalid or missing code"
        }
        logger.warning(f"Invalid access code attempt: {access_code}")
        return False, error_response
    
    logger.info("Access code validation successful")
    return True, None

def generate_login_url():
    logger.info("Generating login URL")
    try:
        with open("login_credentials.json", "r") as file:
            login_credentials = json.load(file)
        
        logger.info("Initializing KiteConnect and generating login URL")
        kite = KiteConnect(login_credentials["api_key"])
        url = kite.login_url()
        
        result = {
            "status": "success",
            "url": url,
            "message": "Use this URL to complete the authentication process"
        }
        logger.info("Login URL generated successfully")
        return result
    except Exception as e:
        error_result = {
            "status": "error",
            "message": str(e),
            "details": "An error occurred during URL generation"
        }
        logger.error(f"Error generating login URL: {str(e)}")
        logger.error(traceback.format_exc())
        return error_result

def generate_access_token(request_token):
    logger.info("Generating access token")
    try:
        with open("login_credentials.json", "r") as file:
            login_credentials = json.load(file)
        
        logger.info("Initializing KiteConnect and generating session")
        kite = KiteConnect(login_credentials["api_key"])
        session_data = kite.generate_session(request_token, login_credentials["api_secret"])
        
        logger.info("Session generated successfully")

        complete_session_data = {
            "status": "success",
            "request_token": request_token,
            "api_key": login_credentials["api_key"],
            "access_token": session_data["access_token"],
            "refresh_token": session_data["refresh_token"],
            "enctoken": session_data["enctoken"],
            "public_token": session_data["public_token"],   
            "generated_at": str(datetime.datetime.now())
        }
        save_session(complete_session_data)
        
        result = {
            "status": "success",
            "message": "Session generated."
        }
        logger.info("Access token generated and saved successfully")
        return result
        
    except Exception as e:
        error_result = {
            "status": "error",
            "message": str(e),
            "details": "An error occurred during token generation"
        }
        logger.error(f"Error generating access token: {str(e)}")
        logger.error(traceback.format_exc())
        return error_result

def save_session(session_data):
    logger.info(f"Saving session data.")
    try:
        with open("session.json", "w") as file:
            json.dump(session_data, file, indent=4)
        logger.info("Session data saved successfully")
        return True
    except Exception as e:
        logger.error(f"Error saving session: {str(e)}")
        logger.error(traceback.format_exc())
        return False

def load_session():
    logger.info("Loading session data")
    try:
        if os.path.exists("session.json"):
            with open("session.json", "r") as file:
                session_data = json.load(file)
            return session_data
        logger.warning("Session file does not exist")
        return None
    except Exception as e:
        logger.error(f"Error loading session: {str(e)}")
        logger.error(traceback.format_exc())
        return None

def hourly_task():
    current_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    logger.info(f"Hourly task executed at {current_time}")
    
    return {"status": "success", "message": "Hourly task completed successfully"}

def check_order_status():
    logger.info("Checking order status")
    try:
        # Import here to avoid circular imports
        from kite_api import KiteAPI
        
        # Create an instance of the KiteAPI class
        kite_api = KiteAPI()
        
        # Check if credentials were loaded successfully
        if not kite_api.kite:
            logger.warning("No active session found or failed to initialize KiteAPI")
            return {"status": "no_session", "message": "No active session found"}
        
        # Get current orders
        orders_result = kite_api.get_orders()
        # positions_result = kite_api.get_positions()
        
        if orders_result["status"] == "success":
            # Use the custom DateTimeEncoder for JSON serialization
            orders_json = json.dumps(orders_result['data'], cls=DateTimeEncoder, indent=4)
            # positions_json = json.dumps(positions_result['data'], cls=DateTimeEncoder, indent=4)
            
            logger.info(f"Successfully retrieved {orders_result['count']} orders - {orders_json}")
            # logger.info(f"Successfully retrieved {positions_result}")
        else:
            logger.warning(f"Failed to retrieve orders: {orders_result['message']}")
        
        return orders_result
    except Exception as e:
        logger.error(f"Error checking order status: {str(e)}")
        logger.error(traceback.format_exc())
        return {"status": "error", "message": f"Error checking order status: {str(e)}"}
