import requests
import time

BASE_URL = 'http://127.0.0.1:8000/en/library'

def get_csrf(session, url):
    resp = session.get(url)
    csrf = session.cookies.get('csrftoken') or session.cookies.get('bookhub_csrf_token')
    return csrf, resp

# Start a session
session = requests.Session()

# 1. Get signup page to fetch CSRF
csrf_token, _ = get_csrf(session, f'{BASE_URL}/signup/')

# 2. Perform signup (unique email)
import string, random
email = f"test_{''.join(random.choice(string.ascii_lowercase) for _ in range(8))}@example.com"
password = 'TestPassword123!'
signup_data = {
    'csrfmiddlewaretoken': csrf_token,
    'first_name': 'Test',
    'last_name': 'User',
    'email': email,
    'phone': '1234567890',
    'pincode': '123456',
    'password': password,
}
resp = session.post(f'{BASE_URL}/signup/', data=signup_data, headers={'Referer': f'{BASE_URL}/signup/'}, allow_redirects=False)
print('Signup status:', resp.status_code, resp.headers.get('Location'))

# 3. Login
csrf_token = session.cookies.get('csrftoken') or session.cookies.get('bookhub_csrf_token')
login_data = {'csrfmiddlewaretoken': csrf_token, 'username': email, 'password': password}
resp = session.post(f'{BASE_URL}/login/', data=login_data, headers={'Referer': f'{BASE_URL}/login/'}, allow_redirects=False)
print('Login status:', resp.status_code, resp.headers.get('Location'))

# Helper to GET a page and print status
pages = [
    '/admin-dashboard/',
    '/delivery/',
    '/dashboard/',
    '/profile/',
    '/settings/',
    '/categories/',
]
for p in pages:
    resp = session.get(f'{BASE_URL}{p}')
    print(f'GET {p} ->', resp.status_code)

# Logout
session.get(f'{BASE_URL}/logout/', allow_redirects=False)
