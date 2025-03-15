"""
Locust Load Test for Booking Retrieval with Caching (/booking/{id} endpoint)
---------------------------------------------------------------------------
- **Test Type:** Load Test to Assess Caching Impact on Booking Retrieval
- **Purpose:** Simulates users repeatedly retrieving the same booking to test cache efficiency.
- **Endpoint:** `/booking/{id}` (GET)
- **Caching:** Assumes the API uses in-memory caching for booking retrieval.
- **Concurrent Users:** [200 - 500]
- **spawn-rate:** [10/sec]
- **Wait Time:** 1 - 3 sec
- **Duration (run-time):** [3 - 5 minutes]
"""

from locust import HttpUser, task, between, events
import threading
from config import MOCK_API_BASE_URL, ENDPOINTS
from data_loader import load_data
import logging

logging.basicConfig(level=logging.INFO)

data_lock = threading.Lock()
shared_data = None
global_user_index = -1


class BookingCacheUser(HttpUser):
    host = MOCK_API_BASE_URL
    wait_time = between(1, 3)

    def on_start(self):
        global global_user_index, shared_data
        if shared_data is None:
            logging.error("❌ ERROR: Shared data is not loaded. Test will stop.")
            self.environment.runner.quit()
            return

        with data_lock:
            global_user_index += 1
            self.user_index = global_user_index

        if self.user_index >= len(shared_data["users"]):
            logging.error(f"❌ ERROR: More users requested ({self.user_index}) than available.")
            self.environment.runner.quit()
            return

        self.user = shared_data["users"][self.user_index]
        self.booking = shared_data["bookings"][self.user_index]

        response = self.client.post(
            f"{self.environment.host}{ENDPOINTS['auth']}",
            json={"username": self.user["username"], "password": self.user["password"]},
        )

        if response.status_code == 200:
            self.token = response.json().get("token", "")
        else:
            logging.error(f"❌ ERROR: Authentication failed for user {self.user['username']}")
            self.environment.runner.quit()
            return

    @task
    def get_booking_with_cache(self):
        if not hasattr(self, "token") or not self.token:
            logging.error(f"❌ ERROR: No authentication token available for user {self.user['username']}")
            return

        headers = {
            "Authorization": f"Bearer {self.token}"
        }

        response = self.client.get(
            f"{self.environment.host}{ENDPOINTS['booking'].format(id=self.booking['id'])}",
            headers=headers
        )

        if response.status_code == 200:
            logging.info(f"✅ Booking fetched successfully: {self.booking['id']}")
        else:
            logging.error(f"❌ ERROR fetching booking: {response.status_code}")


# Load data.json **ONCE** before tests start
def on_locust_init(environment, **kwargs):
    global shared_data
    try:
        shared_data = load_data()
    except Exception as e:
        logging.error(f"❌ ERROR: Failed to load data.json: {e}")
        environment.runner.quit()

    if not shared_data or "users" not in shared_data or "bookings" not in shared_data:
        logging.error("❌ ERROR: Invalid data.json content")
        environment.runner.quit()
    else:
        logging.info("✅ Data loaded successfully")


events.init.add_listener(on_locust_init)
