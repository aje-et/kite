import requests
import json
import os
import datetime
from kiteconnect import KiteConnect
from util import load_session
from logger import get_logger

# Initialize logger
logger = get_logger()

class KiteAPI:
    # Constants
    BASE_URL = "https://api.kite.trade"
    ORDER_API = "/orders"
    POSITION_API = "/positions"

    def __init__(self):
        """Initialize the KiteAPI class with session data"""
        self.session_data = None
        self.kite = None
        self.access_token = None
        self.api_key = None
        self.headers = None
        self.load_credentials()
    
    def load_credentials(self):
        """Load credentials from session.json"""
        try:
            logger.info("Loading credentials from session")
            self.session_data = load_session()
            
            if not self.session_data:
                logger.error("No session data found")
                return False
            
            self.api_key = self.session_data.get("api_key")
            self.access_token = self.session_data.get("access_token")
            
            if not self.api_key or not self.access_token:
                logger.error("Missing API key or access token in session data")
                return False
            
            # Initialize KiteConnect with API key and access token
            self.kite = KiteConnect(api_key=self.api_key)
            self.kite.set_access_token(self.access_token)
            
            # Set up headers for direct API calls
            self.headers = {
                "X-Kite-Version": "3",
                "Authorization": f"token {self.api_key}:{self.access_token}"
            }
            
            logger.info("Successfully loaded credentials and initialized KiteConnect")
            return True
            
        except Exception as e:
            logger.error(f"Error loading credentials: {str(e)}")
            return False
    
    def get_orders(self):
        """Get all orders for the user"""
        try:
            if not self.kite:
                if not self.load_credentials():
                    return {"status": "error", "message": "Failed to load credentials"}
            
            logger.info("Fetching orders")
            orders = self.kite.orders()
            
            return {
                "status": "success",
                "data": orders,
                "count": len(orders)
            }
            
        except Exception as e:
            logger.error(f"Error fetching orders: {str(e)}")
            return {"status": "error", "message": str(e)}
    
    def get_positions(self):
        """Get current positions for the user"""
        try:
            if not self.kite:
                if not self.load_credentials():
                    return {"status": "error", "message": "Failed to load credentials"}
            
            logger.info("Fetching positions")
            positions = self.kite.positions()
            
            return {
                "status": "success",
                "data": positions,
                "net": len(positions.get("net", [])),
                "day": len(positions.get("day", []))
            }
            
        except Exception as e:
            logger.error(f"Error fetching positions: {str(e)}")
            return {"status": "error", "message": str(e)}

