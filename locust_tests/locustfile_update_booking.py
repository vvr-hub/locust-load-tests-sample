"""
Locust Load & Performance Test for Update Booking (/booking/{id} endpoint)
---------------------------------------------------------------------------
- **Test Type:** Load & Performance Test
- **Purpose:** Simulates real-world booking updates with logged-in users.
- **Endpoint:** `/booking/{id}` (PUT)
- **Concurrent Users:** 200 - 500
- **Spawn Rate:** 10/sec
- **Wait Time:** 1 - 3 sec
- **Duration (run-time):** 3 - 5 minutes
"""

from locust import HttpUser, task, between, events
import threading
import random
from config import MOCK_API_BASE_URL, ENDPOINTS
from data_loader import load_data
from utils import log_booking_update

# Global storage for shared data.json content
data_lock = threading.Lock()
shared_data = None  # Stores user and booking data
global_user_index = -1  # Ensures unique user indexing across all threads


class BookingUser(HttpUser):
    host = MOCK_API_BASE_URL  # Uses default from config, overridden by --host
    wait_time = between(1, 3)  # Adds a delay between requests, common for load tests

    def on_start(self):
        """Load users and bookings from shared memory instead of reading file per user"""
        global global_user_index, shared_data

        if shared_data is None:
            print("ERROR: Shared data is not loaded. Test will stop.")
            self.environment.runner.quit()
            return

        with data_lock:
            global_user_index += 1
            self.user_index = global_user_index  # Assign unique index

        if self.user_index >= len(shared_data["users"]):
            print(f"ERROR: More users requested ({self.user_index}) than available.")
            self.environment.runner.quit()
            return

        self.user = shared_data["users"][self.user_index]
        self.booking = shared_data["bookings"][self.user_index]

        # Authenticate the user
        response = self.client.post(
            f"{self.environment.host}{ENDPOINTS['auth']}",
            json={"username": self.user["username"], "password": self.user["password"]}
        )

        if response.status_code == 200:
            self.token = response.json().get("token", "")
        else:
            print(f"ERROR: Authentication failed for user {self.user['username']}")
            self.environment.runner.quit()
            return

    @task
    def update_booking(self):
        """Update the assigned booking ID with at least one changed field"""
        if not hasattr(self, "token") or not self.token:
            print(f"ERROR: No authentication token available for user {self.user['username']}")
            return

        headers = {
            "Authorization": f"Bearer {self.token}",
            "Content-Type": "application/json"
        }

        # Define the possible changes while keeping the 'id' unchanged
        updated_booking = self.booking.copy()

        fields_to_update = [
            "firstname", "lastname", "totalprice", "depositpaid", "checkin", "checkout", "additionalneeds"
        ]

        # Ensure at least one field is changed
        field_to_modify = random.choice(fields_to_update)

        if field_to_modify == "firstname":
            updated_booking["firstname"] = random.choice(["Alice", "Bob", "Charlie", "David"])
        elif field_to_modify == "lastname":
            updated_booking["lastname"] = random.choice(["Johnson", "Williams", "Brown", "Davis"])
        elif field_to_modify == "totalprice":
            updated_booking["totalprice"] = random.randint(100, 1000)
        elif field_to_modify == "depositpaid":
            updated_booking["depositpaid"] = not updated_booking["depositpaid"]
        elif field_to_modify == "checkin":
            updated_booking["checkin"] = f"2025-01-{random.randint(1, 28):02d}"
        elif field_to_modify == "checkout":
            updated_booking["checkout"] = f"2025-02-{random.randint(1, 28):02d}"
        elif field_to_modify == "additionalneeds":
            updated_booking["additionalneeds"] = random.choice(["Breakfast", "Lunch", "Dinner", "None"])

        response = self.client.put(
            f"{self.environment.host}{ENDPOINTS['booking'].format(id=self.booking['id'])}",
            headers=headers,
            json=updated_booking
        )

        log_booking_update(self.booking["id"], field_to_modify, updated_booking[field_to_modify], response)


# Load data.json **ONCE** before tests start
def on_locust_init(environment, **kwargs):
    """Load user and booking data once before the test starts"""
    global shared_data
    shared_data = load_data()

    if not shared_data or "users" not in shared_data or "bookings" not in shared_data:
        print("ERROR: Invalid data.json content")
        environment.runner.quit()


events.init.add_listener(on_locust_init)
