# Centralised API Configurations
import os

# Default base URL for the API (Used if `--host` is not provided in Locust)
DEFAULT_MOCK_API_BASE_URL = "http://localhost:8000"

# API Base URL is determined dynamically:
# - If `--host` is provided in the terminal, Locust will override it.
# - Otherwise, it falls back to `DEFAULT_MOCK_API_BASE_URL`.
MOCK_API_BASE_URL = os.getenv("LOCUST_HOST", DEFAULT_MOCK_API_BASE_URL)

ENDPOINTS = {
    "auth": "/auth",
    "booking": "/booking/{id}",
    "update_profile": "/update-profile/{id}"
}

# WebSocket URL
WEBSOCKET_URL = "ws://localhost:8000/ws"
