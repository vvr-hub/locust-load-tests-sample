# Locust Load Testing Project - `locust-load-tests-sample`

## Overview

This project is a **Locust-based Load, Performance, Scalability and Stress Testing framework** for a **Mock API**. It
simulates real-world API interactions for authentication and booking updates.

Please note that this is **WORK IN PROGRESS** and has got scope for improvements and expansion.

## Features

✅ **Load & Performance Testing** for booking updates  
✅ **Scalability & Stress Testing** for authentication  
✅ **Realistic Think-Time Patterns** for better user simulation  
✅ **Chaos Testing** - simulate API failures  
✅ **Centralised Configurations** for easy setup  
✅ **Best Practices Implemented** (see list below)

---

## 🚀 **Setup Instructions**

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

```sh
cd mock_api
uvicorn api:app --host 0.0.0.0 --port 8000 --reload
```

The API will be available at: http://localhost:8000

### **4️⃣ Generate Sample Data**

Before running tests, ensure that data.json is generated with the required users and bookings:

```sh
python mock_api/generate_data.py
```

---

## 🎯 Running Locust Tests

Make sure the Mock API is running before executing any of the following Locust commands.

### **📌 1. Authentication Scalability & Stress Test**

This test simulates 1000 concurrent users authenticating.

```sh
locust -f locust_tests/locustfile_auth.py --host=http://localhost:8000 --users 1000 --spawn-rate 50 --run-time 10m
```

### **📌 2. Booking Update Load & Performance Test**

This test simulates 500 concurrent users updating bookings.

```sh
locust -f locust_tests/locustfile_update_booking.py --host=http://localhost:8000 --users 500 --spawn-rate 10 --run-time 5m
```

### **📌 3. Chaos Testing**

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

## ✅ Best Practices

The following best practices have been implemented:

✅ Avoid hardcoding base URLs & endpoints
✅ Centralised user & booking data loading
✅ Reusable utilities for authentication & data modification
✅ Logging for debugging & monitoring
✅ Separate test files for different scenarios
✅ Realistic Think-Time Patterns for better user simulation

## 🛠 Project Structure

locust-load-tests-sample/
│── mock_api/
│ ├── api.py            # Mock API with authentication & booking endpoints
│ ├── generate_data.py  # Generates test data (users & bookings)
│ ├── data.json         # Stores generated test users & bookings for the tests
│ 
│── locust_tests/
│ ├── locustfile_auth.py            # Authentication Stress Test
│ ├── locustfile_update_booking.py  # Booking Update Load Test
│ ├── config.py                     # Centralised Base URLs & Endpoints
│ ├── data_loader.py                # Loads users & bookings for tests
│ ├── utils.py                      # Common functions for reusability
│ 
│── requirements.txt                # Dependencies
│── README.md                       # Project Documentation

**NOTE:** The data.json file acts as a simple database for the Mock API.providing a static data source.
The mock_api/api.py reads and writes data from data.json.
Since the data is stored in a file, it remains the same across test runs unless manually changed.

## 📊 Viewing Locust Reports

- **Web UI:** After running any test, open `http://localhost:8089` in a browser.
- **Terminal Summary:** After execution, a summary report is displayed.

## 🛠 Why I Chose a Mock API Instead of a Public API**

We considered using a **public API**, but opted for a **custom Mock API** due to the following reasons:

| **Reason**              | **Mock API**                  | **Public API**                      |
|-------------------------|-------------------------------|-------------------------------------|
| **Control Over Data**   | ✅ Full control over test data | ❌ No control; limited modifications |
| **Consistency**         | ✅ Data persists as needed     | ❌ Data resets periodically          |
| **Performance Testing** | ✅ No rate limits              | ❌ Often has rate limits             |
| **Availability**        | ✅ Always available            | ❌ Downtime possible                 |
| **Customisation**       | ✅ Can add custom endpoints    | ❌ Limited to predefined endpoints   |

### **Key Benefits of Using a Mock API**

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

