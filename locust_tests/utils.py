import random
import os
import logging

logging.basicConfig(level=logging.INFO)


def get_random_user(users):
    """Fetch a random user from the dataset."""
    return random.choice(users) if users else None


def get_random_booking(bookings):
    """Fetch a random booking from the dataset."""
    return random.choice(bookings) if bookings else None


def modify_booking(booking):
    """Modify at least one booking field while keeping the ID unchanged."""
    fields_to_update = ["firstname", "lastname", "totalprice", "depositpaid", "checkin", "checkout", "additionalneeds"]
    field_to_modify = random.choice(fields_to_update)
    original_value = booking[field_to_modify]

    if field_to_modify == "firstname":
        booking["firstname"] = random.choice(["Alice", "Bob", "Charlie", "David"])
    elif field_to_modify == "lastname":
        booking["lastname"] = random.choice(["Johnson", "Williams", "Brown", "Davis"])
    elif field_to_modify == "totalprice":
        booking["totalprice"] = random.randint(100, 1000)
    elif field_to_modify == "depositpaid":
        booking["depositpaid"] = not booking["depositpaid"]
    elif field_to_modify == "checkin":
        booking["checkin"] = f"2025-01-{random.randint(1, 28):02d}"
    elif field_to_modify == "checkout":
        booking["checkout"] = f"2025-02-{random.randint(1, 28):02d}"
    elif field_to_modify == "additionalneeds":
        booking["additionalneeds"] = random.choice(["Breakfast", "Lunch", "Dinner", "None"])

    if booking[field_to_modify] != original_value:
        return field_to_modify, booking[field_to_modify]
    else:
        return modify_booking(booking)  # recall the function to ensure a change.


def log_booking_update(booking_id, field_updated, new_value, response):
    """Logs booking update details"""
    if response.status_code == 200:
        logging.info(f"✅ UPDATED BOOKING {booking_id} - {field_updated}: {new_value}")
    elif response.status_code == 404:
        logging.warning(f"⚠️ Booking ID {booking_id} not found.")
    else:
        logging.error(f"❌ ERROR {response.status_code}: {response.text}")


def log_auth_response(username, response):
    """Logs authentication attempts"""
    if response.status_code == 200:
        token = response.json().get("token", "")
        logging.info(f"✅ AUTH SUCCESS: User '{username}' authenticated. Token: {token}")
    else:
        logging.error(f"❌ AUTH FAILURE: {response.status_code} - {response.text}")


def log_profile_update(user_id, old_email, new_email, old_photo, new_photo, response):
    """Log profile update details"""
    if response.status_code == 200:
        logging.info(f"📸 PROFILE UPDATED: ID {user_id}")
        logging.info(f" OLD EMAIL: {old_email} ➡️ NEW EMAIL: {new_email}")
        logging.info(f" OLD PHOTO: {old_photo} ➡️ NEW PHOTO: {new_photo}")
    else:
        logging.error(f"❌ PROFILE UPDATE FAILED: ID {user_id} - Status {response.status_code} - {response.text}")


def generate_random_email():
    """Generate a random email address"""
    domains = ["example.com", "test.com", "sample.org"]
    name = ''.join(random.choices('abcdefghijklmnopqrstuvwxyz', k=7))
    domain = random.choice(domains)
    return f"{name}@{domain}"


def select_random_photo():
    """Select a random profile photo from the available options"""
    photos_dir = os.path.join(os.path.dirname(__file__), "profile_photos")

    if not os.path.exists(photos_dir):
        raise FileNotFoundError(f"❌ ERROR: Profile photos directory not found at {photos_dir}")

    photos = [f for f in os.listdir(photos_dir) if f.endswith(('.jpg', '.jpeg', '.png'))]

    if not photos:
        raise FileNotFoundError("❌ ERROR: No profile photos found in the directory!")

    return os.path.join(photos_dir, random.choice(photos)), random.choice(photos)
