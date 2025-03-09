import json
import os
import random

DATA_FILE = os.path.join(os.path.dirname(__file__), "data.json")

# Generate 200 unique users
users = [{"username": f"user{i}", "password": f"pass{i}"} for i in range(1, 201)]

# Generate 200 unique bookings, each linked to a specific user
bookings = [
    {
        "id": i,
        "firstname": random.choice(["John", "Alice", "Mike", "Emma", "David"]),
        "lastname": random.choice(["Doe", "Smith", "Brown", "Johnson", "Williams"]),
        "totalprice": random.randint(100, 500),
        "depositpaid": random.choice([True, False]),
        "checkin": f"2025-01-{str(random.randint(1, 28)).zfill(2)}",
        "checkout": f"2025-02-{str(random.randint(1, 28)).zfill(2)}",
        "additionalneeds": random.choice(["Breakfast", "WiFi", "Parking", "None"]),
    }
    for i in range(1, 201)  # Ensure bookings have unique IDs from 1 to 200
]

# Save data to JSON file
with open(DATA_FILE, "w") as f:
    json.dump({"users": users, "bookings": bookings}, f, indent=4)

print("✅ Successfully generated 200 users and 200 matching bookings!")
