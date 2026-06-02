"""End-to-end: rent -> assign to ram -> delivery dashboard (with refresh)."""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'bookhub_backend.settings')
django.setup()

from datetime import date, timedelta
from django.contrib.auth.models import User
from django.test import Client
from library.models import Rental, Delivery, DeliveryStaff, Book

AUTH_BACKEND = 'library.auth_backend.MongoModelBackend'


def run():
    client = Client(enforce_csrf_checks=False)
    ram_user = User.objects.get(username='ram')
    ram_staff = DeliveryStaff.objects.get(user=ram_user)
    admin = User.objects.get(pk=10)  # superuser admin account
    customer = User.objects.get(pk=1)
    book = Book.objects.first()

    print('1. Create pending rental...')
    rental = Rental.objects.create(
        user=customer,
        book=book,
        duration_days=7,
        total_amount=105,
        payment_status='Paid',
        rental_status='Pending',
        due_date=date.today() + timedelta(days=7),
    )
    Delivery.objects.create(rental=rental)
    print(f'   Rental #{rental.id} created')

    print('2. Admin assigns to ram...')
    admin.set_password('admin123')
    admin.save()
    resp_login = client.post('/en/library/login/', {
        'username': admin.username,
        'password': 'admin123'
    })
    assert resp_login.status_code == 302, f"Admin login failed: {resp_login.status_code}"

    resp = client.post(
        f'/en/library/admin-dashboard/assign-delivery/{rental.id}/',
        {'delivery_person': str(ram_staff.id)},
    )
    assert resp.status_code in (301, 302), resp.status_code
    rental.refresh_from_db()
    delivery = Delivery.objects.get(rental=rental)
    assert rental.rental_status == 'Assigned', rental.rental_status
    assert delivery.delivery_person_id == ram_user.pk, delivery.delivery_person_id
    print(f'   Assigned to ram (user id {ram_user.pk})')

    print('3. Ram opens delivery dashboard...')
    client.cookies.clear()
    ram_user.set_password('ram123')
    ram_user.save()
    client.post(
        '/en/library/login/',
        {
            'username': 'ram',
            'password': 'ram123',
        },
    )

    r1 = client.get('/en/library/delivery/')
    assert r1.status_code == 200, r1.status_code
    body1 = r1.content.decode()
    assert 'No active deliveries assigned to you' not in body1, 'Order missing on first load'
    assert book.title in body1 or str(rental.id) in body1
    print('   Order visible on delivery page')

    print('4. Refresh delivery page (session persistence)...')
    r2 = client.get('/en/library/delivery/')
    assert r2.status_code == 200, r2.status_code
    assert client.session.get('_auth_user_id') is not None, 'Session lost on refresh'
    body2 = r2.content.decode()
    assert 'No active deliveries assigned to you' not in body2, 'Order missing after refresh'
    print('   Still logged in and order still visible after refresh')

    print('\n✅ All delivery E2E checks passed')


if __name__ == '__main__':
    run()
