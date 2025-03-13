"""
Locust Load Test for Updating User Profile (/update-profile/{id} endpoint)
---------------------------------------------------------------------------
- **Test Type:** Load Test for Simulating User Profile Updates
- **Purpose:** Simulates users uploading profile photos and updating emails under load.
- **Endpoint:** `/update-profile/{id}` (PUT)
- **Concurrent Users:** 200 - 500
- **spawn-rate:** 10/sec
- **Wait Time:** 1 - 3 sec
- **Duration (run-time):** 3 - 5 minutes
"""

from locust import HttpUser, task, between, events
import os
import random
import threading
from config import MOCK_API_BASE_URL, ENDPOINTS
from data_loader import load_data

# Global variables
data_lock = threading.Lock()
shared_data = None
global_user_index = -1  # Ensures each user is assigned a unique ID


def generate_random_email():
    """Generate a random email address"""
    domains = ["example.com", "test.com", "sample.org"]
    name = ''.join(random.choices('abcdefghijklmnopqrstuvwxyz', k=7))
    domain = random.choice(domains)
    return f"{name}@{domain}"


def select_new_photo(current_photo):
    """Select a new profile photo that is different from the current one"""
    photos_dir = os.path.join(os.path.dirname(__file__), "profile_photos")
    if not os.path.exists(photos_dir):
        raise FileNotFoundError(f"❌ ERROR: Profile photos directory not found at {photos_dir}")

    photos = [f for f in os.listdir(photos_dir) if f.endswith(('.jpg', '.jpeg', '.png'))]
    if not photos:
        raise FileNotFoundError("❌ ERROR: No profile photos found in the directory!")

    # Ensure we select a new photo different from the current one
    new_photo = current_photo
    while new_photo == current_photo:
        new_photo = random.choice(photos)

    return os.path.join(photos_dir, new_photo), new_photo


class UpdateProfileUser(HttpUser):
    host = MOCK_API_BASE_URL  # Uses default from config, overridden by --host
    wait_time = between(1, 3)  # Adds a delay between requests, common for load tests

    def on_start(self):
        """Load users from shared memory instead of reading file per user"""
        global global_user_index, shared_data

        if shared_data is None:
            print("ERROR: Shared data is not loaded. Test will stop.")
            self.environment.runner.quit()
            return

        with data_lock:
            global_user_index += 1
            self.user_index = global_user_index

            if self.user_index >= len(shared_data["users"]):
                print(f"ERROR: More users requested ({self.user_index}) than available.")
                self.environment.runner.quit()
                return

            self.user = shared_data["users"][self.user_index]

        # Authenticate the user
        response = self.client.post(
            f"{self.environment.host}{ENDPOINTS['auth']}",
            json={"username": self.user["username"], "password": self.user["password"]},
        )

        if response.status_code == 200:
            self.token = response.json().get("token", "")
        else:
            print(f"❌ AUTHENTICATION FAILED: User '{self.user['username']}' - Status {response.status_code}")
            self.environment.runner.quit()
            return

    @task
    def update_profile(self):
        """Update user profile with a new email and profile photo"""
        if not hasattr(self, "token") or not self.token:
            print(f"ERROR: No authentication token available for user {self.user['username']}")
            return

        headers = {
            "Authorization": f"Bearer {self.token}"
        }

        new_email = generate_random_email()

        # Get the current profile photo from shared data
        current_photo = self.user.get("profile_photo", "")

        try:
            photo_path, photo_name = select_new_photo(current_photo)
        except FileNotFoundError as e:
            print(f"❌ ERROR: {e}")
            return

        with open(photo_path, 'rb') as photo_file:
            files = {
                "email": (None, new_email),
                "profile_photo": (photo_name, photo_file, 'image/jpeg')
            }
            response = self.client.put(
                f"{self.environment.host}{ENDPOINTS['update_profile'].format(id=self.user['id'])}",
                headers=headers,
                files=files
            )

        if response.status_code == 200:
            print(f"📸 PROFILE UPDATED: ID {self.user['id']}")
            print(f"   OLD EMAIL: {self.user.get('email', 'N/A')} ➡️ NEW EMAIL: {new_email}")
            print(f"   OLD PHOTO: {current_photo} ➡️ NEW PHOTO: {photo_name}")

            # Update shared data with new email & photo
            self.user["email"] = new_email
            self.user["profile_photo"] = photo_name

        else:
            print(f"❌ PROFILE UPDATE FAILED: User {self.user['id']} - Status {response.status_code} - {response.text}")


# Load data.json once before tests start
@events.init.add_listener
def on_locust_init(environment, **kwargs):
    """Load user data once before the test starts"""
    global shared_data
    shared_data = load_data()

    if not shared_data or "users" not in shared_data:
        print("ERROR: Invalid data.json content")
        environment.runner.quit()
