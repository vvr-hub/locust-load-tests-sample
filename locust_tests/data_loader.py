import json
import os
from threading import Lock
from config import DATA_FILE

data_lock = Lock()
shared_data = None


def load_data():
    """Load user and booking data from JSON once."""
    global shared_data
    if shared_data is None:
        with data_lock:
            if shared_data is None:
                try:
                    with open(os.path.join(os.path.dirname(__file__), DATA_FILE), "r") as f:
                        shared_data = json.load(f)
                except (json.JSONDecodeError, FileNotFoundError) as e:
                    print(f"ERROR: Failed to load data.json - {e}")
                    return None
    return shared_data


def get_users():
    """Fetch users from loaded data."""
    data = load_data()
    return data.get("users", []) if data else []


def get_bookings():
    """Fetch bookings from loaded data."""
    data = load_data()
    return data.get("bookings", []) if data else []
