import os
import django
import json
import uuid
from django.test import Client

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'bookhub_backend.settings')
django.setup()

from django.contrib.auth.models import User
from library.models import Book

def test_checkout_api():
    client = Client()
    
    # Create test user and login
    username = 'checkout_test_user'
    password = 'TestPassword123!'
    User.objects.filter(username=username).delete()
    user = User.objects.create_user(username=username, password=password)
    client.login(username=username, password=password)
    
    # Get a book
    book = Book.objects.first()
    if not book:
        print("❌ No books found in database.")
        return

    print(f"Testing checkout for book: {book.title}")
    
    # Test POST request
    data = {
        'book_id': book.id,
        'duration': 7,
        'total': 14.00,
        'payment_method': 'Khalti'
    }
    
    response = client.post('/en/library/checkout/process/', 
                           data=json.dumps(data), 
                           content_type='application/json')
    
    print(f"Checkout Status Code: {response.status_code}")
    print(f"Response: {response.json()}")
    
    if response.status_code == 200:
        print("✅ Checkout API successful!")
    else:
        print(f"❌ Checkout API failed with status {response.status_code}")

    # Cleanup
    User.objects.filter(username=username).delete()

if __name__ == "__main__":
    test_checkout_api()
