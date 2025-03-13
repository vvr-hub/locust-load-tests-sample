import random


def get_random_user(users):
    """Fetch a random user from the dataset."""
    return random.choice(users) if users else None


def get_random_booking(bookings):
    """Fetch a random booking from the dataset."""
    return random.choice(bookings) if bookings else None


def modify_booking(booking):
    """Modify at least one booking field while keeping the ID unchanged."""
    fields_to_update = ["firstname", "lastname", "totalprice", "depositpaid", "checkin", "checkout", "additionalneeds"]

    while True:
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


def log_booking_update(booking_id, field_updated, new_value, response):
    """Logs booking update details"""
    if response.status_code == 200:
        print(f"✅ UPDATED BOOKING {booking_id} - {field_updated}: {new_value}")
    elif response.status_code == 404:
        print(f"⚠️ Booking ID {booking_id} not found.")
    else:
        print(f"❌ ERROR {response.status_code}: {response.text}")


def log_auth_response(username, response):
    """Logs authentication attempts"""
    if response.status_code == 200:
        token = response.json().get("token", "")
        print(f"✅ AUTH SUCCESS: User '{username}' authenticated. Token: {token}")
    else:
        print(f"❌ AUTH FAILURE: {response.status_code} - {response.text}")


def log_profile_update(user_id, old_email, new_email, old_photo, new_photo, response):
    """Log profile update details"""
    if response.status_code == 200:
        print(f"📸 PROFILE UPDATED: ID {user_id}")
        print(f"   OLD EMAIL: {old_email} ➡️ NEW EMAIL: {new_email}")
        print(f"   OLD PHOTO: {old_photo} ➡️ NEW PHOTO: {new_photo}")
    else:
        print(f"❌ PROFILE UPDATE FAILED: ID {user_id} - Status {response.status_code} - {response.text}")
