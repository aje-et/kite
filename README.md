# Kite App

A minimal Python backend server built with Flask.

## Features

- Simple status endpoint
- JSON response format
- CORS support for frontend integration
- Environment variable configuration

## Setup Instructions

1. **Install dependencies**

```bash
pip install -r requirements.txt
```

2. **Environment Variables (Optional)**

Create a `.env` file in the root directory to configure environment variables:

```
PORT=5000
```

3. **Run the server**

```bash
python kite_app.py
```

The server will start on http://localhost:5001

## API Endpoint

| Method | Endpoint | Description |
|--------|----------|--------------|
| GET | / | Server status check |

### Example Response

```json
{
  "status": "up",
  "message": "Kite App is running"
}
```