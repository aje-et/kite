from flask import Flask, jsonify
from flask_cors import CORS
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Initialize Flask app
app = Flask("Kite App")
CORS(app)  # Enable CORS for all routes

# Single route to verify server status
@app.route('/')
def status():
    return jsonify({
        "status": "up",
        "message": "Kite App is running"
    })

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0'', port=port, debug=True)
