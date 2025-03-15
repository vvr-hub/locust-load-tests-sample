import json
import random
import os
import datetime
from faker import Faker

fake = Faker()

DATA_FILE = os.path.join(os.path.dirname(__file__), "data.json")


def generate_data(num_users=1000, num_bookings=500):
    """Generates realistic sample user and booking data with configurability & error handling."""

    users = []
    bookings = []

    # Generate Users
    for i in range(num_users):
        user = {
            "id": i + 1,
            "username": f"user{i + 1}",
            "password": "password",
            "email": f"user{i + 1}@example.com",
            "profile_photo": f"photo{random.randint(1, 5)}.jpg"  # Assuming 5 available images
        }
        users.append(user)

    # Generate Bookings
    today = datetime.date.today()
    for i in range(num_bookings):
        checkin_date = today + datetime.timedelta(days=random.randint(1, 30))
        checkout_date = checkin_date + datetime.timedelta(days=random.randint(1, 10))

        booking = {
            "id": i + 1,
            "firstname": fake.first_name(),  # More diversity
            "lastname": fake.last_name(),  # More diversity
            "totalprice": random.randint(100, 1000),
            "depositpaid": random.choice([True, False]),
            "checkin": checkin_date.strftime("%Y-%m-%d"),
            "checkout": checkout_date.strftime("%Y-%m-%d"),
            "additionalneeds": random.choice(["Breakfast", "Lunch", "Dinner", "None"])
        }
        bookings.append(booking)

    data = {"users": users, "bookings": bookings}

    try:
        with open(DATA_FILE, "w") as f:
            json.dump(data, f, indent=4)
        print(f"✅ Data generated and saved to {DATA_FILE} with {num_users} users and {num_bookings} bookings.")
    except IOError as e:
        print(f"❌ Error saving data to {DATA_FILE}: {e}")
    except TypeError as e:
        print(f"❌ Error dumping json data: {e}")
    except Exception as e:
        print(f"❌ An unexpected error occurred: {e}")


if __name__ == "__main__":
    num_users = int(os.getenv("NUM_USERS", 1000))  # Configurable via env variables
    num_bookings = int(os.getenv("NUM_BOOKINGS", 500))  # Configurable via env variables
    generate_data(num_users, num_bookings)
