from locust import HttpUser, task, between, events
import json
import os
import threading

# Global storage for shared data.json content
data_lock = threading.Lock()
shared_data = None  # This will store the user and booking data
global_user_index = -1  # Ensure correct user indexing across all threads


class BookingUser(HttpUser):
    wait_time = between(1, 3)  # Adds a delay between requests

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
            print(f"ERROR: More users requested ({self.user_index}) than available")
            self.environment.runner.quit()
            return

        self.user = shared_data["users"][self.user_index]
        self.booking = shared_data["bookings"][self.user_index]

        # Authenticate the user
        response = self.client.post("/auth",
                                    json={"username": self.user["username"], "password": self.user["password"]})
        if response.status_code == 200:
            self.token = response.json().get("token", "")
        else:
            print(f"ERROR: Authentication failed for user {self.user['username']}")
            self.environment.runner.quit()
            return

    @task
    def update_booking(self):
        """Update the assigned booking ID"""
        if not hasattr(self, "token") or not self.token:
            print(f"ERROR: No authentication token available for user {self.user['username']}")
            return

        headers = {
            "Authorization": f"Bearer {self.token}",
            "Content-Type": "application/json"
        }
        payload = {
            "firstname": self.booking.get("firstname", "Test"),
            "lastname": self.booking.get("lastname", "User"),
            "totalprice": self.booking.get("totalprice", 200),
            "depositpaid": self.booking.get("depositpaid", True),
            "checkin": self.booking.get("checkin", "2025-01-01"),
            "checkout": self.booking.get("checkout", "2025-01-10"),
            "additionalneeds": self.booking.get("additionalneeds", "None")
        }

        response = self.client.put(f"/booking/{self.booking['id']}", headers=headers, json=payload)

        if response.status_code not in [200, 404]:
            print(f"ERROR: {response.status_code} - {response.text}")


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

    if not shared_data or "users" not in shared_data or "bookings" not in shared_data:
        print("ERROR: Invalid data.json content")
        environment.runner.quit()


events.init.add_listener(on_locust_init)
