from flask import Flask, jsonify, request
from flask_cors import CORS
import os
from dotenv import load_dotenv
from apscheduler.schedulers.background import BackgroundScheduler
from util import generate_login_url, generate_access_token, validate_access_code, check_order_status, hourly_task, logger

# Load environment variables
load_dotenv()

# Initialize Flask app
app = Flask("Kite App")
CORS(app)  # Enable CORS for all routes

# Initialize scheduler
scheduler = BackgroundScheduler()

# Track execution counts
execution_counts = {
    'order_status_job': 0,
    'hourly_maintenance_job': 0
}

# Wrapper functions to limit executions
def limited_check_order_status():
    execution_counts['order_status_job'] += 1
    logger.info(f"Running order status check {execution_counts['order_status_job']}/10")
    
    # Run the actual function
    result = check_order_status()
    
    # Remove the job after max executions
    if execution_counts['order_status_job'] >= 2:
        logger.info("Reached maximum executions for order status job, removing from scheduler")
        scheduler.remove_job('order_status_job')
    
    return result

def limited_hourly_task():
    execution_counts['hourly_maintenance_job'] += 1
    logger.info(f"Running hourly task {execution_counts['hourly_maintenance_job']}/5")
    
    # Run the actual function
    result = hourly_task()
    
    # Remove the job after max executions
    if execution_counts['hourly_maintenance_job'] >= 5:
        logger.info("Reached maximum executions for hourly task, removing from scheduler")
        scheduler.remove_job('hourly_maintenance_job')
    
    return result

# Add jobs with wrapper functions
scheduler.add_job(limited_check_order_status, 'interval', seconds=20, id='order_status_job')
# Uncomment to enable hourly task
# scheduler.add_job(limited_hourly_task, 'interval', hours=1, id='hourly_maintenance_job')

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
    port = int(os.environ.get('PORT', 5001))
    try:
        app.run(host='0.0.0.0', port=port, debug=True)
    except KeyboardInterrupt:
        # Make sure the scheduler is shut down when the app is stopped with Ctrl+C
        if scheduler.running:
            logger.info("Shutting down scheduler due to keyboard interrupt")
            scheduler.shutdown()
        raise
