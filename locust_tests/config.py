import os

# API Base URL Configuration
DEFAULT_MOCK_API_BASE_URL = "http://localhost:8000"
MOCK_API_BASE_URL = os.getenv("LOCUST_HOST", DEFAULT_MOCK_API_BASE_URL)

# API Endpoints
ENDPOINTS = {
    "auth": "/auth",
    "booking": "/booking/{id}",
    "update_profile": "/update-profile/{id}",
}

# WebSocket Configuration
WEBSOCKET_URL = os.getenv("WEBSOCKET_URL", "ws://localhost:8000/ws")

# Data File Location
DATA_FILE = os.getenv("DATA_FILE", "../mock_api/data.json")
