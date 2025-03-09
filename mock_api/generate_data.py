import json
from faker import Faker
from datetime import datetime, timedelta

fake = Faker()

DATA_FILE = "mock_api/data.json"

# Generate 200 unique users
users = [{"username": f"user{i}", "password": f"pass{i}"} for i in range(1, 201)]

# Generate 200 unique bookings with checkin and checkout fields
bookings = []
for i in range(1, 201):
    checkin_date = datetime(2025, 1, 1) + timedelta(days=fake.random_int(min=0, max=365))
    checkout_date = checkin_date + timedelta(days=fake.random_int(min=1, max=14))

    booking = {
        "id": i,
        "firstname": fake.first_name(),
        "lastname": fake.last_name(),
        "totalprice": fake.random_int(min=100, max=500),
        "depositpaid": fake.boolean(),
        "checkin": checkin_date.strftime("%Y-%m-%d"),
        "checkout": checkout_date.strftime("%Y-%m-%d"),
        "additionalneeds": fake.random_element(elements=["Breakfast", "WiFi", "Parking", "Gym", "Extra bed", "None"])
    }
    bookings.append(booking)

# Create final data structure
data = {"users": users, "bookings": bookings}

# Save to JSON file
with open(DATA_FILE, "w") as f:
    json.dump(data, f, indent=4)

print("✅ Data generation complete! 200 users and 200 bookings created.")
