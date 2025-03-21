# Locust Load Testing Project - `locust-load-tests-sample`

## Overview

This project is a **Locust-based Load Performance Testing framework** for a **Mock Server** for **Websockets & API**
endpoints.  
It simulates real-time communication service and real-world API interactions for user auth, profile photo upload & (
hotel) booking updates.  
This project includes tests for endurance, recovery (after API failures), and for **evaluating cache performance & reset
functionality**.  
Please note that this is **WORK IN PROGRESS** and has got scope for improvements and expansion.

## Features

✅ **Load & Performance Testing** for profile photo uploads and booking updates  
✅ **Scalability & Stress Testing** for user authentication  
✅ **WebSocket Load Testing** for real-time communication services  
✅ **Chaos Testing** - simulate API failures  
✅ **Centralised Configurations** for easy setup  
✅ **Configurable Test Environment** - Easily switch between different environments (Example: local mock API, staging,
demo)  
✅ **Caching and Cache Reset** Performance Tests for booking retrievals  
✅ **Realistic Think-Time Patterns** for better user simulation  
✅ **Best Practices Implemented** (see list below)  

---

### API Endpoints Tested

- `/auth` (POST): User authentication.
- `/update-profile/{id}` (PUT): Update user profile (email and photo).
- `/booking/{id}` (PUT): Update an existing booking.
- `/booking/{id}` (GET): Retrieve a specific booking by ID (with in-memory caching).
- `/booking/{id}` (DELETE): Delete a booking by ID.
- `/ws` (WebSocket): WebSocket communication.
- `/clear-booking-cache` (POST): Clear the booking cache.

#### 💡 Note:

The `/booking/{id}` endpoint uses a simple in-memory cache for demonstration purposes. In a production environment, a
more robust caching solution like Redis or Memcached would be recommended.

---

## 🚀 **Setup Instructions**

### 🔧 **Recommended IDE**

For optimal coding experience with this project, I recommend using **PyCharm Community Edition**.

### **1️⃣ Create and Activate Virtual Environment**

Before installing dependencies, create and activate a **Python virtual environment**.

   ```sh
   pipenv install
   pipenv shell
   
   python3 -m venv .venv
   source .venv/bin/activate
   ```

To make the virtual environment auto-activate in zsh, add the following to your ~/.zshrc file:

   ```sh
export VIRTUAL_ENV_DISABLE_PROMPT=1
source /path/to/your/project/.venv/bin/activate
   ```

Then run:

   ```sh
source ~/.zshrc
   ```

Now, every time you navigate to your project folder, the virtual environment activates automatically.

### **2️⃣ Install Dependencies**

Run the following command inside your virtual environment:

```sh
pip install -r requirements.txt
```

### **3️⃣ Start the Mock API**

The Mock API serves as the backend for testing.
It provides authentication, booking updates, user profile photo updates and WebSocket communication.

Run the following command from the project root:

```sh
uvicorn mock_api.api:app --host 0.0.0.0 --port 8000 --reload
```

Alternatively, if you are inside `mock_api/` directory, use:

```sh
uvicorn api:app --host 0.0.0.0 --port 8000 --reload
```

✔️ This will start both the **WebSocket** and other **REST API** endpoints.  
✔️ Both WebSocket (/ws) and other REST API endpoints will be available for load testing.  
🔹 The API will be available at `http://localhost:8000/`  
🔹 WebSocket server will be available at `ws://localhost:8000/ws`  

### **4️⃣ Generate Sample Data**

Before running tests, ensure that `data.json` is populated with the required users and bookings:

```sh
python mock_api/generate_data.py
```

This will generate:

- 1000 Users
- 500 Bookings

**Customising Data Generation** - You can modify the number of users/bookings via environment variables:

```sh
cd mock_api
NUM_USERS=2000 NUM_BOOKINGS=1000 python generate_data.py
```

This makes it **configurable** for different test scenarios.

---

## 🎯 Running Locust Tests

Make sure the Mock API is running before executing any of the following Locust commands.

### 🔗 TEST1 - Run WebSocket Load Test

To simulate **500 concurrent WebSocket users** with a **spawn rate of 10 users per second** for **5 minutes,** run:

```sh
locust -f locustfile_websocket.py --users 500 --spawn-rate 10 --run-time 5m
```

📌 What Happens?

- Users connect to the WebSocket server at `ws://localhost:8000/ws`
- Each user sends a `ping` message and waits for a response.
- The test simulates real-time messaging under load.
- Logs show activity.

### 🏆 TEST2 - Authentication Scalability & Stress Test (`/auth` endpoint)

Simulates multiple users logging in simultaneously

```sh
locust -f locustfile_auth.py --users 1000 --spawn-rate 50 --run-time 10m --stop-timeout 5
```

### 🛠 TEST3 - Load & Performance Test for Uploading Profile Photo (`/update-profile/{user_id}` endpoint)

Below test is for load testing the endpoint for **updating profile photo & email** together using `multipart/form-data`

```sh
locust -f locustfile_update_profile.py --users 500 --spawn-rate 10 --run-time 5m --stop-timeout 10
```

### 🔄 TEST4 - Load & Performance Test for Updating Bookings (`/booking/{id}` endpoint)

Simulates users modifying their bookings.  
Run the below command for load testing the endpoint for **updating booking**  

```sh
locust -f locustfile_update_booking.py --users 500 --spawn-rate 10 --run-time 5m --stop-timeout 10
```

### 🔗 TEST5 & TEST6 - Caching Tests

There are tests to evaluate the API's caching behavior for the `/booking/{id}` endpoint.

- **`locustfile_booking_cache.py`:**
    - This test simulates users repeatedly retrieving the same booking to assess the impact of caching on performance.
    - It assumes the API uses in-memory caching.
    - It measures the latency of subsequent requests to verify caching effectiveness.
    - Run
      `locust -f locust_tests/locustfile_booking_cache.py --users 500 --spawn-rate 10 --run-time 5m --stop-timeout 10`
- **`locustfile_booking_cache_reset.py`:**
    - This test evaluates the cache reset functionality by simulating users retrieving a booking, resetting the cache
      using the `/clear-booking-cache` endpoint, and then retrieving the booking again.
    - It measures the latency difference before and after the cache reset to ensure the cache is working as expected.
    - Run
      `locust -f locust_tests/locustfile_booking_cache_reset.py --users 500 --spawn-rate 10 --run-time 5m --stop-timeout 10`

These tests help to ensure that the API's caching mechanism is functioning correctly and improving performance as
intended.

### 🧑‍💻 TEST7 - Chaos Testing

To test system **recovery after API failures** with some manual intervention:

1. **Start the Mock API:** `uvicorn api:app --host 0.0.0.0 --port 8000 --reload`
2. **Run Load Test:**
   `locust -f locust_tests/locustfile_update_booking.py --host=http://localhost:8000 --users 500 --spawn-rate 10 --run-time 5m`
3. **Kill the API after 2 minutes** (`CTRL+C` in API terminal)
4. You will notice the failures (`# Fails`) increasing rapidly in the Locust 'Statistics' in browser
5. **Restart API:** `uvicorn api:app --host 0.0.0.0 --port 8000 --reload`
6. Note down the number of Failures (`# Fails`) in the Locust 'Statistics'
7. Observe Locust’s behavior - test how the system handles failures.
8. There shouldn't be new failures after the API resumption.

### 🔹 TEST8 - Endurance (Soak) Tests

**Endurance testing (soak testing)** evaluates how a system behaves under **sustained load over an extended period.**  
These tests run for hours to simulate real-world, long-term load scenarios.  
It helps identify memory leaks, performance degradation, slow resource releases or DB connection exhaustion that might
only appear after prolonged execution.  
All existing tests in this project can be run as **endurance tests without modifying the code** simply by adjusting the
`--run-time` parameter to a longer duration.

To perform an **endurance test** on the `/auth` endpoint (for example), run the following command:

```sh
locust -f locustfile_auth.py --users 1000 --spawn-rate 5 --run-time 2h
```


## 💡 Specifying the Test Environment using `host` parameter:

- If you **do not specify `--host`**, the tests will use the **default Mock API URL** from `config.py`.
- If you **explicitly specify `--host`**, the tests will use the provided URL instead.
- Running with `http://xyz-abc.def.com` as `--host` will result in failed requests, as it is a non-existent URL.

| **Test Scenario and Test Environment**                                                                                       | **Command**                                                                                                                        |
|------------------------------------------------------------------------------------------------------------------------------|------------------------------------------------------------------------------------------------------------------------------------|
| **Test without specifying the host parameter.** Locust will use the default (Mock API) from `config.py`.                     | `locust -f locustfile_update_booking.py --users 500 --spawn-rate 10 --run-time 5m --stop-timeout 10`                               |
| **Test specifying the host parameter explicitly as the (default) Mock API URL.** This is the same as the one in `config.py`. | `locust -f locustfile_update_booking.py --host=http://localhost:8000 --users 500 --spawn-rate 10 --run-time 5m --stop-timeout 10`  |
| **Test specifying the host parameter to a non-existent URL (for demonstration).** Note: All requests will fail.              | `locust -f locustfile_update_booking.py --host=http://xyz-abc.def.com --users 500 --spawn-rate 10 --run-time 5m --stop-timeout 10` |

## 📌 Other Locust Parameters:

Locust provides several parameters to fine-tune test execution:

| Parameter      | Description                                                                                                                                                |
|----------------|------------------------------------------------------------------------------------------------------------------------------------------------------------|
| **`--users <N>`** | Defines the total number of concurrent users simulated in the test. Example: `--users 500` will simulate **500 users** sending requests.                   |
| **`--spawn-rate <R>`** | Specifies how many new users will be added per sec, during the ramp-up phase. Example: `--spawn-rate 10` means Locust adds **10 users per second** until reaching the target user count. |
| **`--run-time <T>`** | Defines the total test duration. Example: `--run-time 5m` runs the test for **5 minutes**.                                                                 |
| **`--stop-timeout <S>`** | Allows active requests to complete before stopping the test. Example: `--stop-timeout 5` waits **5 seconds** before forcing users to stop.                 |
| **`--headless`** | Runs the test **without** starting the Locust web UI. Useful for CI/CD and automated performance tests. **Requires** `--host` param **to be specified**. Example: `--headless --host = http://localhost:8000` |
| **`--csv <filename>`** | Generates CSV reports containing test results. Example: `--csv=load_test` will create files like `load_test_stats.csv`, etc, storing performance metrics.  |

#### 📋 Notes:

- **The `--stop-timeout <S>` parameter** allows users to gracefully stop all active tasks before shutting down the test.
- When you manually stop the test (`Ctrl + C`) or when the test reaches the specified `run-time`, Locust will **wait up
  to the specified timeout (Example: `5s`)** before terminating.
- This ensures **active requests** can complete before shut down, improving result accuracy.   


- The `--headless` **mode** is ideal for running tests in **automated environments** (for example, CI/CD pipelines). However, you must explicitly provide the `--host` parameter when using `--headless`, as the web UI is disabled.
- The `--csv` **parameter** allows you to store performance results for later analysis, but it is **not required for every test** unless reports are needed.
- By default, Locust saves the CSV files in the current working directory. However, you can **specify a folder** by providing a path before the filename.  
**Example** (Saving CSV files in a "reports" folder):

```sh
locust -f locustfile_auth.py --users 500 --spawn-rate 10 --run-time 5m --csv=reports/auth_test
```
The folder **must exist before running the test**. Locust does **not** automatically create the directory.  
This will generate the below files inside `locust_tests/reports/`:
```
locust_tests/reports/
  ├── auth_test_stats.csv
  ├── auth_test_failures.csv
  ├── auth_test_exceptions.csv
  ├── auth_test_distribution.csv
```

## ✅ Best Practices

The following best practices have been implemented:

- Avoid hardcoding base URLs & endpoints (Centralized in `config.py`)
- Centralised user & booking data loading (`data_loader.py`)
- Reusable utilities for authentication & data modification (`utils.py`)
- Logging for debugging & monitoring (API logs + Locust stats)
- Separate test files for different scenarios (user auth, upload profile pic, update booking, caching-specific tests)
- Configurable Test Environment - Supports running tests against different environments (mock API, staging, etc)
- Enhanced Error Handling - Robust error handling throughout the test suite.
- Realistic Think-Time Patterns for better user simulation

## 🛠 Project Structure

```
📦 locust-load-tests-sample/
├── 📂 mock_api/
│ ├── api.py            # Mock API with auth, profile & booking endpoints
│ ├── generate_data.py  # Generates test data (users & bookings)
│ ├── data.json         # Stores generated test users & bookings for the tests
│ 
├── 📂 locust_tests/
│ ├── locustfile_auth.py                # Authentication Stress Test
│ ├── locustfile_update_profile.py      # Profile Photo Upload Load Test
│ ├── locustfile_update_booking.py      # Booking Update Load Test
│ ├── locustfile_booking_cache.py       # Load Test for Booking Retrieval with Caching
│ ├── locustfile_booking_cache_reset.py # Test for Booking Retrieval with Cache Reset
│ ├── locustfile_websocket.py           # WebSocket Load Test
│ ├── config.py                         # Centralised Base URLs & Endpoints
│ ├── data_loader.py                    # Loads users & bookings for tests
│ ├── utils.py                          # Common functions for reusability
│ ├── 📂 profile_photos/
│ 
│── requirements.txt                # Dependencies
│── README.md                       # Project Documentation
├── 📂 docs/                        # Screenshots of Logs, Reports, Failures, etc.
```

**NOTE:** The data.json file acts as a simple database for the Mock API providing a static data source.
The mock_api/api.py reads and writes data from data.json.

## 📊 Viewing Locust Reports

- **Web UI:** After running any test, open `http://localhost:8089` in a browser.
- **Terminal Summary:** After execution and keyboard interrupt, a summary report is displayed.

## 📂 Analyzing Locust Test Results

| **Metric**              | **Meaning**                          |
|-------------------------|--------------------------------------|
| **# Requests**          | Total number of requests sent        |
| **# Fails**             | Failed requests count                |
| **Median (ms)**         | Middle response time of all requests |
| **95%ile (ms)**         | 95th percentile response time        |
| **99%ile (ms)**         | 99th percentile response time        |
| **Average (ms)**        | Average response time                |
| **Min (ms) / Max (ms)** | Fastest & slowest responses          |


## ✔️ Screenshots of Locust Web UI, Mock Server, Test Logs & Reports

`/locust-load-tests-sample/docs` directory contains **screenshots** of Mock Server Logs, Locust Test Logs, Locust Web UI at **various stages and situations**.


## 🛠 Why I chose a Mock API instead of a Public API

We considered using a **public API**, but opted for a **custom Mock API** due to the following reasons:

| **Reason**              | **Mock API**                  | **Public API**                      |
|-------------------------|-------------------------------|-------------------------------------|
| **Control Over Data**   | ✅ Full control over test data | ❌ No control; limited modifications |
| **Consistency**         | ✅ Data persists as needed     | ❌ Data resets periodically          |
| **Performance Testing** | ✅ No rate limits              | ❌ Often has rate limits             |
| **Availability**        | ✅ Always available            | ❌ Downtime possible                 |
| **Customisation**       | ✅ Can add custom endpoints    | ❌ Limited to predefined endpoints   |

## **Key Benefits of Using a Mock API**

- **Predictability**: We control the data, ensuring reliable test results.
- **Scalability**: No external rate limits, allowing stress testing at higher loads.
- **Resilience Testing**: I can simulate failures (API downtime, timeouts, etc).
- **Flexibility**: Modify API behavior (for example, return different responses for edge cases).
- **Independence**: No dependency on third-party API availability.

By using my **own Mock API**, I gain **better control, stability, and flexibility**, making it ideal for **load,
performance and chaos testing**.

## 🙏 Thanks And Acknowledgement

Created the mock API using the API documentation of the **restful-booker** at:
https://restful-booker.herokuapp.com/apidoc/index.html
