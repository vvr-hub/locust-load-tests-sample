import json
import os

DATA_FILE = os.path.join(os.path.dirname(__file__), "../mock_api/data.json")

def load_data():
    """Load and validate data.json before using it in tests."""
    if not os.path.exists(DATA_FILE):
        raise RuntimeError("❌ ERROR: data.json file is missing!")

    try:
        with open(DATA_FILE, "r") as f:
            data = json.load(f)
    except json.JSONDecodeError:
        raise RuntimeError("❌ ERROR: data.json contains invalid JSON!")

    if "users" not in data or "bookings" not in data:
        raise RuntimeError("❌ ERROR: data.json is missing 'users' or 'bookings' sections!")

    return data
