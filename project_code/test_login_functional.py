import os
# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'bookhub_backend.settings')
import django
django.setup()

from django.test import Client
from django.contrib.auth.models import User

def test_login():
    client = Client()
    
    # Create a fresh test user
    username = 'functional_test_user'
    password = 'TestPassword123!'
    email = 'testuser@example.com'
    
    # Cleanup if exists
    User.objects.filter(username=username).delete()
    
    print(f"Creating fresh test user: {username}")
    user = User.objects.create_user(username=username, password=password, email=email)
    
    print(f"Attempting login for user: {username}")
    
    # Test the actual view
    response = client.post('/en/library/login/', {
        'username': username,
        'password': password
    }, follow=True)
    
    print(f"Login response status: {response.status_code}")
    
    # Check if login was successful
    # In Django Client follow=True, it will redirect to the home page or dashboard
    is_auth = client.session.get('_auth_user_id') is not None
    
    if is_auth:
        print("✅ Login view successful! Session contains user ID.")
    else:
        # Check messages
        from django.contrib.messages import get_messages
        messages = list(get_messages(response.wsgi_request))
        if messages:
            for msg in messages:
                print(f"Message from app: {msg}")
        
        print("❌ Login view failed. User is not authenticated in session.")
        
    # Cleanup
    User.objects.filter(username=username).delete()

if __name__ == "__main__":
    test_login()
