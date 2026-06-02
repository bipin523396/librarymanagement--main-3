import os
import django
import json

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'bookhub_backend.settings')
django.setup()

from django.contrib.auth.models import User
from library.models import Rental, Delivery, DeliveryStaff, Book, UserProfile

def test_full_assignment_flow():
    print("--- Starting Full Assignment Flow Test ---")
    
    # 1. Setup Test Data
    # Get or create a test user (customer)
    customer_user, _ = User.objects.get_or_create(username='test_customer', defaults={'email': 'customer@test.com'})
    customer_profile, _ = UserProfile.objects.get_or_create(user=customer_user)
    
    # Get or create a test delivery staff
    staff_user, _ = User.objects.get_or_create(username='test_rider', defaults={'email': 'rider@test.com'})
    delivery_staff, _ = DeliveryStaff.objects.get_or_create(
        user=staff_user, 
        defaults={'phone': '1234567890', 'vehicle_number': 'TEST-123', 'active': True}
    )
    
    # Get a book
    book = Book.objects.first()
    if not book:
        print("❌ Error: No books in DB to test with.")
        return

    # 2. Create a "Pending" Rental (as if a user just rented it)
    rental = Rental.objects.create(
        user=customer_user,
        book=book,
        duration_days=7,
        total_amount=100.0,
        rental_status='Pending'
    )
    print(f"✅ Created Pending Rental ID: {rental.id} for book: {book.title}")

    # 3. Simulate Admin Assignment
    print(f"Simulating admin assigning rental {rental.id} to rider {staff_user.username}...")
    
    # Logic from views.py:assign_delivery
    try:
        # Update or Create Delivery record
        delivery, created = Delivery.objects.get_or_create(rental=rental)
        delivery.delivery_person = staff_user # Note: we use staff_user (the User object)
        delivery.status = 'Assigned'
        delivery.save()

        # Update Rental Status (use queryset update — avoids MongoDB Decimal128 save errors)
        Rental.set_status(rental.id, Rental.STATUS_ASSIGNED)
        print("✅ Admin assignment simulation successful.")
    except Exception as e:
        print(f"❌ Error during assignment: {str(e)}")
        return

    # 4. Verify Delivery Guy Visibility
    print("Verifying if the order is visible to the delivery guy...")
    
    # Logic from views.py:delivery_dashboard
    active_deliveries = [
        d for d in Delivery.objects.filter(delivery_person=staff_user)
        if getattr(d.rental, 'rental_status', None) == Rental.STATUS_ASSIGNED
    ]
    
    visible = any(d.rental_id == rental.id for d in active_deliveries)
    if visible:
        print("✅ Order is VISIBLE in the delivery guy's active deliveries!")
    else:
        print("❌ Error: Order is NOT visible to the delivery guy.")

    # 5. Verify Rental History (for Customer/Admin)
    print("Verifying if order moved out of 'Live Rentals' (Pending)...")
    
    # Logic from views.py:admin_dashboard (Live rentals = Pending only)
    is_in_live = Rental.objects.filter(id=rental.id, rental_status='Pending').exists()
    is_in_history = Rental.objects.filter(
        id=rental.id,
        rental_status__in=[Rental.STATUS_COMPLETED, Rental.STATUS_FAILED],
    ).exists()
    
    rental.refresh_from_db()
    is_assigned = rental.rental_status == Rental.STATUS_ASSIGNED
    if not is_in_live and is_assigned and not is_in_history:
        print("✅ Order left Live Rentals and is Assigned (visible on delivery dashboard).")
    else:
        print(
            f"❌ Error: rental_status={rental.rental_status}. "
            f"Live={is_in_live}, Assigned={is_assigned}, History={is_in_history}"
        )

    # 6. Complete delivery -> rental history
    print("Simulating delivery completed...")
    Delivery.objects.filter(rental=rental).update(status='Delivered')
    Rental.set_status(rental.id, Rental.STATUS_COMPLETED, returned=True)
    rental.refresh_from_db()
    in_history = Rental.objects.filter(
        id=rental.id,
        rental_status__in=[Rental.STATUS_COMPLETED, Rental.STATUS_FAILED],
    ).exists()
    if in_history:
        print("✅ Completed rental appears in Rental History.")
    else:
        print(f"❌ Error: expected Completed in history, got {rental.rental_status}")

    # Cleanup
    # rental.delete() # Keep it for manual inspection if needed
    print("--- Test Completed ---")

if __name__ == "__main__":
    test_full_assignment_flow()
