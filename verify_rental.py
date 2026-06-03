import requests
import json
import re

import time

BASE_URL = "https://librarymanagement-main-3tx9.onrender.com"
SIGNUP_URL = f"{BASE_URL}/en/library/signup/"
LOGIN_URL = f"{BASE_URL}/en/library/login/"
HOME_URL = f"{BASE_URL}/en/library/"
CHECKOUT_PROCESS_URL = f"{BASE_URL}/en/library/checkout/process/"

# Use a unique email for testing
TEST_EMAIL = f"test_user_{int(time.time())}@example.com"
TEST_PASSWORD = "TestPassword123!"

session = requests.Session()

def test_rental():
    print(f"--- Starting Rental Test on {BASE_URL} ---")
    
    # 1. Signup
    print(f"Step 1: Signing up with {TEST_EMAIL}...")
    r = session.get(SIGNUP_URL)
    csrf_match = re.search(r'name="csrfmiddlewaretoken" value="([^"]+)"', r.text)
    if not csrf_match:
        print("FAIL: Could not find CSRF token on signup page.")
        return
    csrf_token = csrf_match.group(1)
    
    signup_data = {
        "first_name": "Test",
        "last_name": "User",
        "email": TEST_EMAIL,
        "phone": "1234567890",
        "pincode": "110001",
        "password": TEST_PASSWORD,
        "csrfmiddlewaretoken": csrf_token
    }
    r = session.post(SIGNUP_URL, data=signup_data, headers={"Referer": SIGNUP_URL})
    if r.status_code == 200 and "logout" in r.text.lower():
        print("OK: Signup and auto-login successful.")
    else:
        print(f"FAIL: Signup failed. Status: {r.status_code}")
        return

    # 3. Get a book ID from Home Page
    print("Step 3: Fetching book ID from home page...")
    r = session.get(HOME_URL)
    
    # Let's find the first instance of 'id: "..."'
    matches = re.findall(r'id:\s*"([^"]+)"', r.text)
    if not matches:
        print("FAIL: Could not find any book ID in the HTML.")
        return
    
    # Filter out small integers if possible, or just take the first one
    book_id = matches[0]
    print(f"OK: Found Book IDs: {matches[:5]}")
    print(f"OK: Using Book ID: {book_id}")

    # 4. Process Checkout
    print("Step 4: Attempting to rent the book...")
    # Get fresh CSRF from cookies for the JSON POST
    csrf_token = session.cookies.get("bookhub_csrf_token") or session.cookies.get("csrftoken")
    
    checkout_payload = {
        "book_id": book_id,
        "duration": "7",
        "total": "105.00",
        "payment_method": "razorpay",
        "name": "Test User",
        "phone": "1234567890",
        "address": "123 Test Street",
        "city": "Test City",
        "pincode": "110001"
    }
    
    headers = {
        "Content-Type": "application/json",
        "X-CSRFToken": csrf_token,
        "Referer": f"{BASE_URL}/en/library/checkout/"
    }
    
    r = session.post(CHECKOUT_PROCESS_URL, json=checkout_payload, headers=headers)
    
    if r.status_code == 200:
        try:
            data = r.json()
            if data.get("status") == "success":
                print(f"SUCCESS: Book rented! Order ID: {data.get('order_id')}")
            else:
                print(f"FAIL: Checkout returned error: {data.get('message')}")
        except Exception as e:
            print(f"FAIL: Could not parse JSON response: {e}")
            print(r.text)
    else:
        print(f"FAIL: Checkout request failed with status {r.status_code}")
        print(r.text[:1000])

if __name__ == "__main__":
    test_rental()
