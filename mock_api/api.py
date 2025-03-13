from fastapi import FastAPI, HTTPException, Body, Request, UploadFile, File
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
async def authenticate_user(request: Request, username: str = Body(...), password: str = Body(...)):
    """Mock authentication endpoint with detailed logging"""
    data = load_data()

    print(f"🔹 AUTH REQUEST: Username: {username}, Password: {password}")

    for user in data["users"]:
        if user["username"] == username and user["password"] == password:
            token = f"fake-token-{username}"
            print(f"✅ AUTH SUCCESS: User '{username}' authenticated. Token: {token}")
            return {"token": token}

    print(f"❌ AUTH FAILURE: Invalid credentials for user '{username}'")
    raise HTTPException(status_code=401, detail="Invalid credentials")


@app.put("/update-profile/{user_id}")
async def update_profile(user_id: int, email: str = Body(...), profile_photo: UploadFile = File(...)):
    """Update user email and process profile picture (discarded)"""
    data = load_data()

    # Find the user by ID
    for user in data["users"]:
        if user["id"] == user_id:
            old_email = user["email"]
            old_photo = user.get("profile_photo", "None")

            # Process the uploaded photo (discard after reading)
            file_size = 0
            while chunk := await profile_photo.read(1024):  # Read in chunks
                file_size += len(chunk)  # Keep track of file size
            profile_photo.file.close()  # Close the file after reading

            # Update user data
            user["email"] = email
            user["profile_photo"] = profile_photo.filename  # Store only the filename for logging
            save_data(data)

            # Logging the update
            print(f"📸 PROFILE UPDATED: ID {user_id}")
            print(f"   OLD EMAIL: {old_email} ➡️ NEW EMAIL: {email}")
            print(f"   OLD PHOTO: {old_photo} ➡️ NEW PHOTO: {profile_photo.filename}")
            print(f"   📂 PHOTO UPLOADED (& PROCESSED): {profile_photo.filename}, Size: {file_size} bytes")

            return {
                "message": "Profile updated successfully",
                "user_id": user_id,
                "new_email": email,
                "new_profile_photo": profile_photo.filename,
                "photo_size_bytes": file_size
            }

    print(f"❌ ERROR: User ID {user_id} not found")
    raise HTTPException(status_code=404, detail="User not found")


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
            old_booking = booking.copy()

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

            print(f"✏️ BOOKING UPDATED: ID {booking_id}")
            print(f"   OLD DATA: {old_booking}")
            print(f"   NEW DATA: {booking}")

            return {"message": "Booking updated"}

    print(f"❌ ERROR: Booking ID {booking_id} not found")
    raise HTTPException(status_code=404, detail="Booking not found")


@app.get("/booking/{booking_id}")
async def get_booking(booking_id: int):
    """Retrieve a specific booking by ID"""
    data = load_data()
    for booking in data["bookings"]:
        if booking["id"] == booking_id:
            print(f"📄 FETCH BOOKING: {booking}")
            return booking

    print(f"❌ ERROR: Booking ID {booking_id} not found")
    raise HTTPException(status_code=404, detail="Booking not found")


@app.delete("/booking/{booking_id}")
async def delete_booking(booking_id: int):
    """Delete a booking by ID"""
    data = load_data()
    for booking in data["bookings"]:
        if booking["id"] == booking_id:
            data["bookings"].remove(booking)
            save_data(data)

            print(f"🗑️ BOOKING DELETED: ID {booking_id}")
            return {"message": "Booking deleted"}

    print(f"❌ ERROR: Booking ID {booking_id} not found")
    raise HTTPException(status_code=404, detail="Booking not found")
