from fastapi import FastAPI, HTTPException, Body, Request, UploadFile, File, WebSocket, WebSocketDisconnect
import json
import os
import threading
from typing import Dict
import tempfile
import shutil
import uuid
import atexit
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)

app = FastAPI()

# Define the path for the data file
DATA_FILE = os.path.join(os.path.dirname(__file__), "data.json")

# Thread lock to handle concurrent updates safely
data_lock = threading.Lock()

# In-memory cache
booking_cache: Dict[int, dict] = {}

# Temporary upload directory
temp_upload_dir = tempfile.mkdtemp(prefix="upload_")
logging.info(f"Temporary upload directory: {temp_upload_dir}")


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

    logging.info(f"🔹 AUTH REQUEST: Username: {username}, Password: {password}")

    for user in data["users"]:
        if user["username"] == username and user["password"] == password:
            token = f"fake-token-{username}"
            logging.info(f"✅ AUTH SUCCESS: User '{username}' authenticated. Token: {token}")
            return {"token": token}

    logging.error(f"❌ AUTH FAILURE: Invalid credentials for user '{username}'")
    raise HTTPException(status_code=401, detail="Invalid credentials")


@app.put("/update-profile/{user_id}")
async def update_profile(user_id: int, email: str = Body(...), profile_photo: UploadFile = File(...)):
    """Update user email and profile photo, saving to temp dir."""
    data = load_data()

    for user in data["users"]:
        if user["id"] == user_id:
            old_email = user["email"]
            old_photo = user.get("profile_photo", "None")

            try:
                if not os.path.exists(temp_upload_dir):
                    logging.error(f"Temporary directory does not exist: {temp_upload_dir}")
                    raise HTTPException(status_code=500, detail="Temporary directory not found")

                file_extension = os.path.splitext(profile_photo.filename)[1]
                unique_filename = f"{uuid.uuid4()}{file_extension}"
                file_path = os.path.join(temp_upload_dir, unique_filename)

                with open(file_path, "wb") as f:
                    while contents := await profile_photo.read(1024):
                        f.write(contents)

                with data_lock:
                    user["email"] = email
                    user["profile_photo"] = unique_filename  # Store filename
                    save_data(data)

                logging.info(f"📸 PROFILE UPDATED: ID {user_id}")
                logging.info(f" OLD EMAIL: {old_email} ➡️ NEW EMAIL: {email}")
                logging.info(f" OLD PHOTO: {old_photo} ➡️ NEW PHOTO: {unique_filename}")
                logging.info(f"File saved to: {file_path}")

                return {
                    "message": "Profile updated successfully",
                    "user_id": user_id,
                    "new_email": email,
                    "new_profile_photo": unique_filename
                }

            except FileNotFoundError as e:
                logging.error(f"File not found error: {e}")
                raise HTTPException(status_code=500, detail="File not found")
            except Exception as e:
                logging.error(f"Error saving file: {e}")
                raise HTTPException(status_code=500, detail="Internal server error")

    logging.error(f"❌ ERROR: User ID {user_id} not found")
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

            with data_lock:
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
                # clear cache when booking is updated.
                booking_cache.pop(booking_id, None)

            logging.info(f"✏️ BOOKING UPDATED: ID {booking_id}")
            logging.info(f" OLD DATA: {old_booking}")
            logging.info(f" NEW DATA: {booking}")

            return {"message": "Booking updated"}

    logging.error(f"❌ ERROR: Booking ID {booking_id} not found")
    raise HTTPException(status_code=404, detail="Booking not found")


@app.get("/booking/{booking_id}")
async def get_booking(booking_id: int):
    """Retrieve a specific booking by ID with caching"""
    if booking_id in booking_cache:
        logging.info(f"📄 FETCH BOOKING FROM CACHE: {booking_cache[booking_id]}")
        return booking_cache[booking_id]

    data = load_data()
    for booking in data["bookings"]:
        if booking["id"] == booking_id:
            booking_cache[booking_id] = booking
            logging.info(f"📄 FETCH BOOKING: {booking}")
            return booking

    logging.error(f"❌ ERROR: Booking ID {booking_id} not found")
    raise HTTPException(status_code=404, detail="Booking not found")


@app.delete("/booking/{booking_id}")
async def delete_booking(booking_id: int):
    """Delete a booking by ID"""
    data = load_data()
    for booking in data["bookings"]:
        if booking["id"] == booking_id:
            with data_lock:
                data["bookings"].remove(booking)
                save_data(data)
                # clear cache when booking is deleted.
                booking_cache.pop(booking_id, None)

            logging.info(f"🗑️ BOOKING DELETED: ID {booking_id}")
            return {"message": "Booking deleted"}

    logging.error(f"❌ ERROR: Booking ID {booking_id} not found")
    raise HTTPException(status_code=404, detail="Booking not found")


@app.post("/clear-booking-cache")
async def clear_cache():
    """Clear the booking cache."""
    booking_cache.clear()
    logging.info("🗑️ BOOKING CACHE CLEARED")
    return {"message": "Booking cache cleared"}


# -----------------------
# ✅ WebSocket Server
# -----------------------

active_connections = set()  # Keep track of connected WebSocket clients


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """Mock WebSocket Service"""
    await websocket.accept()
    active_connections.add(websocket)
    logging.info(f"🔗 NEW WEBSOCKET CONNECTION: {len(active_connections)} clients connected")

    try:
        while True:
            data = await websocket.receive_text()
            logging.info(f"📩 MESSAGE RECEIVED: {data}")

            # Echo the message back to the sender
            response = f"Echo: {data}"
            await websocket.send_text(response)

    except WebSocketDisconnect:
        active_connections.remove(websocket)
        logging.info(f"🔌 CLIENT DISCONNECTED: {len(active_connections)} clients remaining")


# Cleanup function
def cleanup_temp_dir():
    try:
        if os.path.exists(temp_upload_dir):
            shutil.rmtree(temp_upload_dir)
            logging.info(f"🧹 Temporary upload directory '{temp_upload_dir}' cleaned up.")
    except Exception as e:
        logging.error(f"⚠️ Error cleaning up temporary directory: {e}")
