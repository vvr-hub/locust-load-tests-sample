from locust import HttpUser, task, between, events
import json
import os
import random

class BookingUser(HttpUser):
    wait_time = between(1, 3)  # Adds a delay between requests

    def on_start(self):
        """Load users and bookings from data.json safely and authenticate"""
        data_path = os.path.join(os.path.dirname(__file__), "../mock_api/data.json")

        # Handle JSON decoding errors
        try:
            with open(data_path) as f:
                data = json.load(f)
        except (json.JSONDecodeError, FileNotFoundError) as e:
            print(f"ERROR: {e}")
            self.environment.runner.quit()  # Stop Locust gracefully
            return

        self.users = data.get("users", [])
        self.bookings = data.get("bookings", [])

        if not self.users or not self.bookings:
            print("ERROR: data.json is missing users or bookings")
            self.environment.runner.quit()  # Stop Locust gracefully
            return

        # Select a random user and authenticate
        user = random.choice(self.users)
        response = self.client.post("/auth", json={"username": user["username"], "password": user["password"]})

        if response.status_code == 200:
            self.token = response.json().get("token", "")
        else:
            print(f"ERROR: Authentication failed for user {user['username']}")
            self.environment.runner.quit()  # Stop Locust gracefully
            return

    @task
    def update_booking(self):
        """Update a random booking with valid data"""
        if not hasattr(self, "token") or not self.token:
            print("ERROR: No authentication token available")
            return

        booking = random.choice(self.bookings)
        headers = {
            "Authorization": f"Bearer {self.token}",
            "Content-Type": "application/json"
        }
        payload = {
            "firstname": booking.get("firstname", "Test"),
            "lastname": booking.get("lastname", "User"),
            "totalprice": booking.get("totalprice", 200),
            "depositpaid": booking.get("depositpaid", True),
            "checkin": booking.get("checkin", "2025-01-01"),
            "checkout": booking.get("checkout", "2025-01-10"),
            "additionalneeds": booking.get("additionalneeds", "None")
        }

        response = self.client.put(f"/booking/{booking['id']}", headers=headers, json=payload)

        if response.status_code not in [200, 404]:
            print(f"ERROR: {response.status_code} - {response.text}")

# Initialize the custom error count attribute
@events.init.add_listener
def on_locust_init(environment, **kwargs):
    environment.json_error_count = 0

# Reset error count at the start of each test
@events.test_start.add_listener
def on_test_start(environment, **kwargs):
    environment.json_error_count = 0

# Track JSON errors and stop Locust if too many occur
@events.request.add_listener
def on_request(request_type, name, response_time, response_length, response, context, exception, **kwargs):
    if exception and isinstance(exception, json.JSONDecodeError):
        environment = kwargs.get('environment')
        if environment:
            environment.json_error_count += 1
            if environment.json_error_count >= 5:
                print("ERROR: Too many JSON decoding errors. Stopping test.")
                environment.runner.quit()  # Stop Locust gracefully
