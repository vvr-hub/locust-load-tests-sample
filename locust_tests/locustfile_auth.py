"""
Locust Scalability & Stress Test for Authentication (/auth endpoint)
-------------------------------------------------------------------
- **Test Type:** Scalability & Stress Test
- **Purpose:** Measures the ability to handle authentication requests under high load.
- **Endpoint:** `/auth` (POST)
- **Concurrent Users:** 500 - 1000
- **Spawn Rate:** 50/sec
- **Wait Time:** 0 - 1 sec
- **Duration (run-time):** 10 minutes
"""

from locust import HttpUser, task, between, events
import json
import os
import threading
from config import MOCK_API_BASE_URL, ENDPOINTS

# Global storage for shared data.json content
data_lock = threading.Lock()
shared_data = None  # This will store the user data
global_user_index = -1  # Ensure correct user indexing across all threads


class AuthUser(HttpUser):
    wait_time = between(0, 1)  # Minimal wait time for stress testing

    def on_start(self):
        """Load users from shared memory instead of reading file per user"""
        global global_user_index, shared_data

        if shared_data is None:
            print("ERROR: Shared data is not loaded. Test will stop.")
            self.environment.runner.quit()
            return

        with data_lock:
            global_user_index += 1
            self.user_index = global_user_index  # Assign unique index

        if self.user_index >= len(shared_data["users"]):
            print(f"ERROR: More users requested ({self.user_index}) than available")
            self.environment.runner.quit()
            return

        self.user = shared_data["users"][self.user_index]

    @task
    def authenticate_user(self):
        """Perform authentication request for the assigned user"""
        response = self.client.post(MOCK_API_BASE_URL + ENDPOINTS["auth"], json={
            "username": self.user["username"],
            "password": self.user["password"]
        })

        if response.status_code == 200:
            token = response.json().get("token", "")
            print(f"✅ AUTH SUCCESS: User '{self.user['username']}' authenticated. Token: {token}")
        else:
            print(f"❌ AUTH FAILURE: {response.status_code} - {response.text}")


# Load data.json **ONCE** before tests start
def on_locust_init(environment, **kwargs):
    global shared_data

    data_path = os.path.join(os.path.dirname(__file__), "../mock_api/data.json")

    try:
        with open(data_path, "r") as f:
            shared_data = json.load(f)
    except (json.JSONDecodeError, FileNotFoundError):
        print("ERROR: Failed to load data.json")
        environment.runner.quit()

    if not shared_data or "users" not in shared_data:
        print("ERROR: Invalid data.json content")
        environment.runner.quit()


events.init.add_listener(on_locust_init)
