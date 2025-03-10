from locust import HttpUser, task, between, events
import json
import os
import random
import threading

data_lock = threading.Lock()
shared_users = None

class AuthUser(HttpUser):
    wait_time = between(1, 2)  # Simulate users logging in quickly

    def on_start(self):
        """Load users from shared memory"""
        global shared_users

        if shared_users is None:
            print("ERROR: Shared users data is not loaded. Test will stop.")
            self.environment.runner.quit()
            return

    @task
    def authenticate(self):
        """Repeatedly authenticate users (one per iteration)"""
        global shared_users

        with data_lock:
            self.user = random.choice(shared_users)  # Pick any user randomly for authentication

        request_body = {"username": self.user["username"], "password": self.user["password"]}
        response = self.client.post("/auth", json=request_body)

        if response.status_code == 200:
            response_body = response.json()
            print(f"✅ SUCCESS: Authenticated user '{self.user['username']}' | Response: {response_body}")
        else:
            print(f"❌ ERROR: Authentication failed for user '{self.user['username']}' | Status: {response.status_code} | Response: {response.text}")

def on_locust_init(environment, **kwargs):
    """Load users from data.json on Locust start"""
    global shared_users
    data_path = os.path.join(os.path.dirname(__file__), "../mock_api/data.json")

    try:
        with open(data_path, "r") as f:
            data = json.load(f)
            shared_users = data.get("users", [])
    except (json.JSONDecodeError, FileNotFoundError):
        print("ERROR: Failed to load data.json")
        environment.runner.quit()

    if not shared_users:
        print("ERROR: Invalid data.json content")
        environment.runner.quit()

events.init.add_listener(on_locust_init)
