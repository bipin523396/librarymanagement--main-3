import os
import django

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'bookhub_backend.settings')
django.setup()

from django.test import Client
from django.contrib.auth import get_user_model
from library.models import UserSettings

User = get_user_model()

# Ensure a test user exists
username = 'testuser'
email = 'testuser@example.com'
password = 'TestPass123'
if not User.objects.filter(username=username).exists():
    User.objects.create_user(username=username, email=email, password=password)
    print('Created test user')
else:
    print('Test user already exists')

client = Client()
# Attempt login via POST to the login URL (adjust URL if needed)
login_url = '/en/library/login/'
login_data = {
    'username': username,
    'password': password,
    'remember_me': 'on',
}
response = client.post(login_url, login_data, follow=True)
print('Login POST status code:', response.status_code)
print('Login successful (client.login):', client.login(username=username, password=password))

# Access a protected page (home)
home_resp = client.get('/')
print('Home page status:', home_resp.status_code)

# Check UserSettings count for the test user
try:
    settings = UserSettings.objects.filter(user__username=username)
    print('UserSettings count for test user:', settings.count())
except Exception as e:
    print('Error fetching UserSettings:', e)
