import json
import os
import random
import datetime
from faker import Faker

fake = Faker()

# Define the number of users and bookings based on load test requirements
NUM_USERS = 1000  # Max for locustfile_auth.py
NUM_BOOKINGS = 500  # Max for locustfile_update_booking.py (ensuring user-to-booking mapping)

DATA_FILE = os.path.join(os.path.dirname(__file__), "data.json")


def generate_users(num_users):
    """Generate unique users with emails"""
    users = []
    for i in range(num_users):
        users.append({
            "id": i + 1,
            "username": f"user{i + 1}",
            "password": "password" + str(i + 1),  # Simple password pattern
            "email": fake.email()  # Generate unique email for each user
        })
    return users


def generate_bookings(num_bookings):
    """Generate unique bookings"""
    bookings = []
    start_date = datetime.date(2025, 1, 1)
    end_date = datetime.date(2025, 12, 31)

    for i in range(num_bookings):
        checkin = fake.date_between(start_date=start_date, end_date=end_date)
        checkout = fake.date_between(start_date=checkin, end_date=datetime.date(2026, 12, 31))

        bookings.append({
            "id": i + 1,  # Booking ID starts from 1
            "firstname": fake.first_name(),
            "lastname": fake.last_name(),
            "totalprice": random.randint(50, 500),
            "depositpaid": random.choice([True, False]),
            "checkin": checkin.isoformat(),
            "checkout": checkout.isoformat(),
            "additionalneeds": random.choice(["Breakfast", "Late checkout", "Airport transfer", "None"])
        })
    return bookings


def save_data(users, bookings):
    """Save generated users and bookings to data.json"""
    data = {"users": users, "bookings": bookings}
    with open(DATA_FILE, "w") as f:
        json.dump(data, f, indent=4)


if __name__ == "__main__":
    users = generate_users(NUM_USERS)
    bookings = generate_bookings(NUM_BOOKINGS)
    save_data(users, bookings)
    print(f"✅ Data generated: {NUM_USERS} users and {NUM_BOOKINGS} bookings saved to {DATA_FILE}")
