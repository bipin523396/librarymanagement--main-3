import os
import sys
import django
import json
from django.test.client import Client

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'bookhub_backend.settings')
django.setup()

from django.contrib.auth.models import User
from library.models import Book, Rental, Delivery

def run_test():
    client = Client()
    
    # 1. Ensure we have a user and a book
    user = User.objects.first()
    if not user:
        user = User.objects.create_user(username='testuser', password='testpassword')
        print(f"Created test user: {user.username}")
        
    book = Book.objects.first()
    if not book:
        print("No book found to rent!")
        return
        
    print(f"Testing rental for Book: {book.title} (ID: {book.id}) by User: {user.username}")
    
    # Login user
    client.force_login(user)
    
    # 2. Call process_checkout
    payload = {
        'book_id': book.id,
        'duration': 7,
        'total': 105,
        'payment_method': 'card'
    }
    
    print("Calling /en/library/checkout/process/...")
    response = client.post(
        '/en/library/checkout/process/', 
        data=json.dumps(payload),
        content_type='application/json',
        SERVER_NAME='localhost'
    )
    
    print(f"Checkout Response Status: {response.status_code}")
    if response.status_code == 200:
        print("Checkout Response Data:", response.json())
    else:
        print("Failed!")
        return

    # 3. Check if Rental was created
    rental = Rental.objects.filter(user=user, book=book).order_by('-rented_at').first()
    if rental:
        print(f"✅ SUCCESS: Rental created! ID: {rental.id}, Status: {rental.rental_status}")
    else:
        print("❌ ERROR: Rental not found in DB.")
        
    # 4. Check if Delivery was created
    if rental:
        delivery = Delivery.objects.filter(rental=rental).first()
        if delivery:
            print(f"✅ SUCCESS: Delivery created! ID: {delivery.id}, Status: {delivery.status}")
        else:
            print("❌ ERROR: Delivery not found in DB.")

if __name__ == "__main__":
    run_test()
