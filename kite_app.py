# Standard library imports
import os

# Third-party imports
from dotenv import load_dotenv

# Load environment variables first - before any other imports that might use them
load_dotenv()

# Third-party imports that don't depend on environment variables
from flask import Flask, jsonify, request
from flask_cors import CORS
from apscheduler.schedulers.background import BackgroundScheduler

# Local application imports - after environment variables are loaded
from logger import get_logger
from util import (
    generate_login_url, 
    generate_access_token, 
    validate_access_code, 
    order_status_check, 
    hourly_health_check
)

# Initialize Flask app
app = Flask("Kite App")
CORS(app)  # Enable CORS for all routes

# Initialize logger after environment variables are loaded
logger = get_logger()

# Initialize scheduler
scheduler = BackgroundScheduler()

# Track execution counts
execution_counts = {
    'hourly_health_check_job': 0,
    'hourly_health_check_job_limit': 15
}

# Wrapper functions to limit executions
def limited_hourly_health_check():
    execution_counts['hourly_health_check_job'] += 1
    logger.info(f"Running hourly health check {execution_counts['hourly_health_check_job']}/{execution_counts['hourly_health_check_job_limit']}")
    
    # Run the actual function
    result = hourly_health_check()
    
    # Remove the job after max executions
    if execution_counts['hourly_health_check_job'] >= execution_counts['hourly_health_check_job_limit']:
        logger.info("Reached maximum executions for hourly health check job, removing from scheduler")
        scheduler.remove_job('hourly_health_check_job')
    
    return result

# Add jobs with wrapper functions
scheduler.add_job(order_status_check, 'interval', seconds=20, id='order_status_job')

# Schedule hourly task to run at 15 minutes past each hour (HH:15)
scheduler.add_job(limited_hourly_health_check, 'cron', minute=15, id='hourly_health_check_job')

# Start the scheduler immediately when the app is initialized
logger.info("Starting scheduler for periodic tasks")
scheduler.start()

# Single route to verify server status
@app.route('/')
def status():
    logger.info("Status endpoint accessed")
    return jsonify({
        "status": "up",
        "message": "Kite App is running"
    })


@app.route('/api/url')
def generate_url():
    logger.info("URL generation endpoint accessed")
    
    access_code = request.args.get('code', None)
    is_valid, error_response = validate_access_code(access_code)
    if not is_valid:
        return jsonify(error_response), 401
    
    result = generate_login_url()
    logger.info("Login URL generated successfully")
    return jsonify(result)

@app.route('/api/token')
def generate_token():
    logger.info("Token generation endpoint accessed")
    
    access_code = request.args.get('code', None)
    is_valid, error_response = validate_access_code(access_code)
    if not is_valid:
        return jsonify(error_response), 401
    
    request_token = request.args.get('request_token', None)
    if not request_token:
        return jsonify({
            "status": "error",
            "message": "Missing request_token parameter"
        }), 400

    result = generate_access_token(request_token)
    logger.info("Access token generation process completed")
    return jsonify(result)

# Register a function to be called when the application is shutting down
@app.teardown_appcontext
def shutdown_scheduler(exception=None):
    if scheduler.running:
        logger.info("Shutting down scheduler")
        scheduler.shutdown()

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 443))
    try:
        app.run(host='0.0.0.0', port=port, debug=True)
    except KeyboardInterrupt:
        # Make sure the scheduler is shut down when the app is stopped with Ctrl+C
        if scheduler.running:
            logger.info("Shutting down scheduler due to keyboard interrupt")
            scheduler.shutdown()
        raise
