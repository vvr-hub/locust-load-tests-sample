"""
Locust Scalability & Stress Test for Authentication (/auth endpoint)
-------------------------------------------------------------------
- **Test Type:** Scalability & Stress Test
- **Purpose:** Measures the ability to handle authentication requests under high load.
- **Endpoint:** `/auth` (POST)
- **Concurrent Users:** 500 - 1000
- **spawn-rate:** 50/sec
- **Wait Time:** 0 - 1 sec
- **Duration (run-time):** 10 minutes
"""

from locust import HttpUser, task, between, events
import threading
from config import MOCK_API_BASE_URL, ENDPOINTS
from data_loader import load_data
from utils import log_auth_response

# Global storage for shared data.json content
data_lock = threading.Lock()
shared_data = None  # This will store the user data
global_user_index = -1  # Ensure correct user indexing across all threads


class AuthUser(HttpUser):
    host = MOCK_API_BASE_URL  # Uses default from config, overridden by --host
    wait_time = between(0, 1)  # Delay between requests is minimal for stress testing

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
        response = self.client.post(
            f"{self.environment.host}{ENDPOINTS['auth']}",
            json={"username": self.user["username"], "password": self.user["password"]}
        )

        log_auth_response(self.user["username"], response)


# Load data.json **ONCE** before tests start
def on_locust_init(environment, **kwargs):
    """Load user data once before the test starts"""
    global shared_data
    shared_data = load_data()

    if not shared_data or "users" not in shared_data:
        print("ERROR: Invalid data.json content")
        environment.runner.quit()


events.init.add_listener(on_locust_init)
