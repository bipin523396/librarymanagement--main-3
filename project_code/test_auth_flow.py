import requests
import string
import random

def generate_random_string(length=8):
    letters = string.ascii_lowercase
    return ''.join(random.choice(letters) for i in range(length))

session = requests.Session()

print("1. Fetching signup page...")
response = session.get('http://127.0.0.1:8000/en/library/signup/')
csrf_token = session.cookies.get('csrftoken') or session.cookies.get('bookhub_csrf_token')

if not csrf_token:
    print("Could not find CSRF token in cookies:", session.cookies.get_dict())
    exit(1)

print(f"CSRF Token: {csrf_token}")

email = f"test_{generate_random_string()}@example.com"
password = "TestPassword123!"

signup_data = {
    'csrfmiddlewaretoken': csrf_token,
    'first_name': 'Test',
    'last_name': 'User',
    'email': email,
    'phone': '1234567890',
    'pincode': '123456',
    'password': password
}

print(f"2. Submitting signup form for {email}...")
post_resp = session.post(
    'http://127.0.0.1:8000/en/library/signup/', 
    data=signup_data,
    headers={'Referer': 'http://127.0.0.1:8000/en/library/signup/'},
    allow_redirects=False
)

print(f"Signup Response Status: {post_resp.status_code}")
if post_resp.status_code in [301, 302]:
    print(f"Redirected to: {post_resp.headers.get('Location')}")
else:
    print("Failed to redirect after signup. Content:")
    print(post_resp.text[:500])

print("3. Logging out...")
session.get('http://127.0.0.1:8000/en/library/logout/', allow_redirects=False)
print("Logged out successfully.")

print("4. Fetching login page...")
login_resp = session.get('http://127.0.0.1:8000/en/library/login/')
csrf_token = session.cookies.get('csrftoken') or session.cookies.get('bookhub_csrf_token')

login_data = {
    'csrfmiddlewaretoken': csrf_token,
    'username': email,
    'password': password
}

print("5. Submitting login form...")
post_login = session.post(
    'http://127.0.0.1:8000/en/library/login/',
    data=login_data,
    headers={'Referer': 'http://127.0.0.1:8000/en/library/login/'},
    allow_redirects=False
)

print(f"Login Response Status: {post_login.status_code}")
if post_login.status_code in [301, 302]:
    print(f"Redirected to: {post_login.headers.get('Location')}")
else:
    print("Failed to redirect after login. Content:")
    print(post_login.text[:500])
