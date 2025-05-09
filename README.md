# Kite App

A secure Flask-based backend server for Zerodha Kite Connect authentication and trading API integration.

## Features

- Secure authentication with Zerodha Kite Connect API
- Token generation and management
- Background task scheduling
- Comprehensive logging system
- API wrapper for Kite Connect
- Access code protection for sensitive endpoints
- JSON response format
- CORS support for frontend integration

## Setup Instructions

1. **Install dependencies**

```bash
pip install -r requirements.txt
```

2. **Environment Variables**

Create a `.env` file in the root directory to configure environment variables:

```
PORT=5001
CODE=YOUR_ACCESS_CODE
```

3. **Configure Credentials**

Create a `login_credentials.json` file with your Zerodha API credentials:

```json
{
    "api_key": "your_kite_api_key",
    "api_secret": "your_kite_api_secret",
    "twofa_key": "your_totp_key"
}
```

4. **Run the server**

```bash
python kite_app.py
```

The server will start on http://localhost:5001 (or the port specified in your .env file)

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|--------------|
| GET | / | Server status check |
| GET | /api/url?code=SECRET_CODE | Generate a Kite Connect login URL |
| GET | /api/token?code=SECRET_CODE&request_token=REQUEST_TOKEN | Generate and save access token using request token |

### Example Responses

#### Status Endpoint
```json
{
  "status": "up",
  "message": "Kite App is running"
}
```

#### Generate URL Endpoint
```json
{
  "status": "success",
  "url": "https://kite.trade/connect/login?api_key=your_api_key&v=3",
  "message": "Use this URL to complete the authentication process"
}
```

#### Generate Token Endpoint
```json
{
  "status": "success",
  "message": "Session generated."
}
```

**Note:** The access token is not returned in the API response. It is securely stored in the `session.json` file.

## Scheduled Tasks

The application includes a background scheduler that runs periodic tasks:

1. **Order Status Check**: Runs every 20 seconds to check the status of orders using the Kite API
2. **Hourly Maintenance**: Runs every hour to perform system maintenance tasks

The scheduler is configured to start automatically when the application launches and is properly shut down when the application exits.

## Logging System

The application includes a comprehensive logging system that:

1. **Creates Date-Based Log Files**: Log files are created in the `logs` directory with filenames based on the current date and time
2. **Sanitizes Sensitive Data**: Automatically redacts sensitive information like tokens and API keys
3. **Logs API Operations**: All API calls and their results are logged
4. **Logs Scheduler Activities**: Scheduler start, stop, and task execution are logged

Log files can be found in the `logs` directory.

### Usage

The authentication process follows a two-step workflow:

#### Step 1: Generate a login URL
```
GET /api/url?code=YOUR_ACCESS_CODE
```

This returns a URL that the user must visit to complete the authentication process. After successful authentication, the user will be redirected to a URL containing a `request_token` parameter.

#### Step 2: Generate and save the access token
```
GET /api/token?code=YOUR_ACCESS_CODE&request_token=YOUR_REQUEST_TOKEN
```

This generates an access token using the request token and saves it to the `session.json` file for future use.

**Note:** For both endpoints, you must provide the correct access code that matches the CODE environment variable. If an invalid or missing code is provided, you'll receive a 401 Unauthorized error.

## KiteAPI Class

The application includes a `KiteAPI` class that provides a convenient wrapper around the Kite Connect API:

```python
from kite_api import KiteAPI

# Create an instance
kite_api = KiteAPI()

# Get orders
orders = kite_api.get_orders()

# Get positions
positions = kite_api.get_positions()
```

The class automatically loads credentials from the session.json file and handles authentication with the Kite Connect API.
