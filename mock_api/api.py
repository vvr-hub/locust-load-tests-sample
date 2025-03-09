from fastapi import FastAPI, HTTPException, Body
import json
import os

app = FastAPI()

# Define the path for the data file
DATA_FILE = os.path.join(os.path.dirname(__file__), "data.json")


# Load data function
def load_data():
    """Load data from data.json"""
    if not os.path.exists(DATA_FILE):
        raise HTTPException(status_code=500, detail="Data file not found")

    with open(DATA_FILE, "r") as f:
        return json.load(f)


# Save data function
def save_data(data):
    """Save data to data.json"""
    with open(DATA_FILE, "w") as f:
        json.dump(data, f, indent=4)


@app.post("/auth")
async def authenticate_user(username: str = Body(...), password: str = Body(...)):
    """Mock authentication endpoint"""
    data = load_data()
    for user in data["users"]:
        if user["username"] == username and user["password"] == password:
            return {"token": f"fake-token-{username}"}
    raise HTTPException(status_code=401, detail="Invalid credentials")


@app.post("/booking")
async def create_booking(
        firstname: str = Body(...),
        lastname: str = Body(...),
        totalprice: int = Body(...),
        depositpaid: bool = Body(...),
        checkin: str = Body(...),
        checkout: str = Body(...),
        additionalneeds: str = Body(...)
):
    """Create a new booking"""
    data = load_data()
    new_booking_id = max([b["id"] for b in data["bookings"]], default=0) + 1
    new_booking = {
        "id": new_booking_id,
        "firstname": firstname,
        "lastname": lastname,
        "totalprice": totalprice,
        "depositpaid": depositpaid,
        "checkin": checkin,
        "checkout": checkout,
        "additionalneeds": additionalneeds
    }
    data["bookings"].append(new_booking)
    save_data(data)
    return {"message": "Booking created", "booking": new_booking}


@app.put("/booking/{booking_id}")
async def update_booking(
        booking_id: int,
        firstname: str = Body(...),
        lastname: str = Body(...),
        totalprice: int = Body(...),
        depositpaid: bool = Body(...),
        checkin: str = Body(...),
        checkout: str = Body(...),
        additionalneeds: str = Body(...)
):
    """Update an existing booking"""
    data = load_data()
    for booking in data["bookings"]:
        if booking["id"] == booking_id:
            booking.update({
                "firstname": firstname,
                "lastname": lastname,
                "totalprice": totalprice,
                "depositpaid": depositpaid,
                "checkin": checkin,
                "checkout": checkout,
                "additionalneeds": additionalneeds
            })
            save_data(data)
            return {"message": "Booking updated"}

    raise HTTPException(status_code=404, detail="Booking not found")


@app.get("/booking/{booking_id}")
async def get_booking(booking_id: int):
    """Retrieve a specific booking by ID"""
    data = load_data()
    for booking in data["bookings"]:
        if booking["id"] == booking_id:
            return booking
    raise HTTPException(status_code=404, detail="Booking not found")


@app.delete("/booking/{booking_id}")
async def delete_booking(booking_id: int):
    """Delete a booking by ID"""
    data = load_data()
    for booking in data["bookings"]:
        if booking["id"] == booking_id:
            data["bookings"].remove(booking)
            save_data(data)
            return {"message": "Booking deleted"}

    raise HTTPException(status_code=404, detail="Booking not found")
