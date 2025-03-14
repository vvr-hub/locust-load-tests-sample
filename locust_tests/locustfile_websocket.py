"""
Locust Load Test for WebSocket Service
--------------------------------------
- **Test Type:** Load & Scalability Test for WebSocket Communication
- **Purpose:** Simulates multiple users connecting and exchanging messages via WebSockets.
- **WebSocket Endpoint:** `/ws`
- **Concurrent Users:** 200 - 500
- **Spawn Rate:** 10/sec
- **Wait Time:** 1 - 3 sec
- **Duration (run-time):** 3 - 5 minutes
"""

from locust import User, task, between, events
import websocket
import threading
import json
import time
from config import WEBSOCKET_URL
from data_loader import load_data
import logging

logging.basicConfig(level=logging.INFO)

# Global Data Storage
data_lock = threading.Lock()
shared_data = None  # Stores shared user data
global_user_index = -1  # Ensures unique user indexing across all threads


class WebSocketUser(User):
    wait_time = between(1, 3)  # Adds a delay between WebSocket messages

    def on_start(self):
        """Establish WebSocket Connection on User Start"""
        global global_user_index, shared_data

        if shared_data is None:
            logging.error("❌ ERROR: Shared data is not loaded. Test will stop.")
            self.environment.runner.quit()
            return

        with data_lock:
            global_user_index += 1
            self.user_index = global_user_index

        if self.user_index >= len(shared_data["users"]):
            logging.error(f"❌ ERROR: More users requested ({self.user_index}) than available.")
            self.environment.runner.quit()
            return

        self.user = shared_data["users"][self.user_index]
        self.ws = websocket.WebSocket()

        try:
            self.ws.connect(WEBSOCKET_URL)
            logging.info(f"✅ CONNECTED: User {self.user['id']} connected to WebSocket")
        except Exception as e:
            logging.error(f"❌ CONNECTION ERROR: {e}")
            self.environment.runner.quit()

    @task
    def send_receive_message(self):
        """Send and Receive Messages via WebSocket"""
        if not hasattr(self, "ws") or not self.ws.connected:
            logging.error(f"❌ ERROR: WebSocket not connected for user {self.user['id']}")
            return

        message = json.dumps({"user_id": self.user["id"], "action": "ping"})
        start_time = time.time()

        try:
            self.ws.send(message)
            response = self.ws.recv()
            response_time = round((time.time() - start_time) * 1000)  # Convert seconds to ms
            response_length = len(response)

            logging.info(f"📩 MESSAGE SENT: {message} | RESPONSE: {response}")

            # Fire Locust request event for WebSocket messages
            self.environment.events.request.fire(
                request_type="WebSocket",
                name="send_message",
                response_time=response_time,
                response_length=response_length,
                exception=None if response else "No Response"
            )

        except Exception as e:
            logging.error(f"❌ ERROR SENDING MESSAGE: {e}")
            self.environment.events.request.fire(
                request_type="WebSocket",
                name="send_message",
                response_time=0,
                response_length=0,
                exception=str(e)
            )

    def on_stop(self):
        """Close WebSocket Connection"""
        if hasattr(self, "ws") and self.ws.connected:
            self.ws.close()
            logging.info(f"🔌 DISCONNECTED: User {self.user['id']} closed WebSocket connection")


# Load Data.json **Once** Before Tests Start
def on_locust_init(environment, **kwargs):
    """Load user data before the test starts"""
    global shared_data
    try:
        shared_data = load_data()
    except Exception as e:
        logging.error(f"❌ ERROR: Failed to load data.json: {e}")
        environment.runner.quit()

    if not shared_data or "users" not in shared_data:
        logging.error("❌ ERROR: Invalid data.json content")
        environment.runner.quit()
    else:
        logging.info("✅ Data loaded successfully")


events.init.add_listener(on_locust_init)
