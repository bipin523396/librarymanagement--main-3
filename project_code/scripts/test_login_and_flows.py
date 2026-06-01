#!/usr/bin/env python3
"""Test login page, auth, admin/delivery dashboards, and assignment flow."""
import os
import sys

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'bookhub_backend.settings')

import django

django.setup()

from datetime import date, timedelta
from django.contrib.auth import authenticate
from django.contrib.auth.models import User
from django.test import Client

from library.models import Author, Book, Delivery, DeliveryStaff, Rental

PASS = 0
FAIL = 0


def ok(msg):
    global PASS
    PASS += 1
    print(f'  OK  {msg}')


def bad(msg):
    global FAIL
    FAIL += 1
    print(f'  FAIL {msg}')


def section(title):
    print(f'\n--- {title} ---')


def _mongo_db():
    import os
    from pymongo import MongoClient
    from bookhub_backend.mongo_config import get_mongodb_uri

    uri = get_mongodb_uri()
    if not uri:
        return None
    return MongoClient(uri)[os.getenv('MONGODB_NAME', 'bookhub_db')]


def _create_pending_rental_id(customer):
    """Insert pending rental in MongoDB; return str(ObjectId) for assign URL."""
    from datetime import datetime, timedelta, timezone
    from bson import ObjectId

    db = _mongo_db()
    if db is None or not customer or not customer.pk:
        return None
    book = db.library_book.find_one({'isbn': 'TEST-E2E-001'}) or db.library_book.find_one()
    if not book:
        return None
    user_oid = customer.pk if isinstance(customer.pk, ObjectId) else ObjectId(str(customer.pk))
    rid = db.library_rental.insert_one(
        {
            'user_id': user_oid,
            'book_id': book['_id'],
            'duration_days': 7,
            'total_amount': '50.00',
            'rental_status': Rental.STATUS_PENDING,
            'payment_status': 'Pending',
            'due_date': datetime.now(timezone.utc) + timedelta(days=7),
            'returned': False,
        }
    ).inserted_id
    return str(rid)


def ensure_ram_delivery(password='ram123'):
    """Ensure delivery credentials + staff row (MongoDB may have duplicate/broken user FKs)."""
    from django.core.management import call_command

    call_command('bootstrap_delivery', username='ram', password=password, verbosity=0)
    staff = DeliveryStaff.objects.filter(vehicle_number='DL-01').order_by('-id').first()
    if not staff:
        staff = DeliveryStaff.objects.order_by('-id').first()
    if not staff:
        raise RuntimeError('bootstrap_delivery did not create DeliveryStaff')
    ram_user = authenticate(username='ram', password=password)
    if ram_user is None:
        raise RuntimeError('ram does not authenticate after bootstrap_delivery')
    return ram_user, staff, staff.user_id


def main():
    section('Login page (GET)')
    c = Client()
    r = c.get('/en/library/login/')
    if r.status_code == 200:
        ok(f'Login page HTTP 200')
    else:
        bad(f'Login page HTTP {r.status_code}')
    html = r.content.decode('utf-8', errors='replace')
    if 'password' in html.lower() and ('username' in html.lower() or 'email' in html.lower()):
        ok('Login form fields present')
    else:
        bad('Login form missing fields')

    section('Bad credentials')
    r = c.post('/en/library/login/', {'username': 'invalid_user_xyz', 'password': 'wrong'})
    if r.status_code == 200:
        ok('Failed login re-renders login page')
    else:
        bad(f'Failed login HTTP {r.status_code}')

    section('Admin login (email + password)')
    admin_email = 'bipinsagarmatha123@gmail.com'
    admin_password = 'Test123@'
    c_admin = Client(enforce_csrf_checks=False)
    c_admin.post('/en/library/login/', {'username': admin_email, 'password': admin_password})
    r = c_admin.get('/en/library/admin-dashboard/')
    if r.status_code == 200:
        ok('Admin login + dashboard HTTP 200')
        user = authenticate(username=admin_email, password=admin_password)
        if user:
            ok(f'Admin authenticates ({user.username})')
    else:
        bad(f'Admin dashboard HTTP {r.status_code} — run bootstrap_admin on this database')

    section('Delivery login (ram)')
    ensure_ram_delivery('ram123')
    c_ram = Client(enforce_csrf_checks=False)
    ram_logged = False
    for pwd in ('ram123', 'Test123@', 'ram', 'pass'):
        c_try = Client(enforce_csrf_checks=False)
        c_try.post('/en/library/login/', {'username': 'ram', 'password': pwd})
        r = c_try.get('/en/library/delivery/')
        if r.status_code == 200:
            c_ram = c_try
            ram_logged = True
            ok('ram login + delivery dashboard HTTP 200')
            break
    if not ram_logged:
        bad('Delivery login failed — ensure user ram exists with password ram123')

    section('Customer home (logged out)')
    c_home = Client()
    r = c_home.get('/en/library/')
    if r.status_code == 200:
        ok(f'Home page HTTP 200 ({len(r.content)} bytes)')
    else:
        bad(f'Home HTTP {r.status_code}')

    section('Root redirect')
    r = c_home.get('/')
    if r.status_code in (301, 302) and '/en/library/' in r.get('Location', ''):
        ok(f'Root redirects to /en/library/')
    else:
        bad(f'Root redirect: {r.status_code} {r.get("Location", "")}')

    section('Database test endpoint')
    r = c_home.get('/en/library/test-db/')
    if r.status_code == 200:
        import json
        data = json.loads(r.content)
        if data.get('status') == 'success':
            ok(f"test-db: {data.get('message', '')[:60]}")
        else:
            bad(f"test-db: {data.get('message', data)}")
    else:
        bad(f'test-db HTTP {r.status_code}')

    section('Assignment flow')
    r_admin = c_admin.get('/en/library/admin-dashboard/')
    if r_admin.status_code != 200:
        bad('Skip assignment — admin not logged in')
    else:
        customer = User.objects.filter(username='bipinsagarmatha123@gmail.com').exclude(pk=None).first()
        if customer is None:
            customer = User.objects.exclude(pk=None).first()
        ram_user, staff, ram_pk = ensure_ram_delivery('ram123')
        rental_id = _create_pending_rental_id(customer)
        db = _mongo_db()
        if rental_id and staff and db is not None:
            from bson import ObjectId

            c_admin.post(
                f'/en/library/admin-dashboard/assign-delivery/{rental_id}/',
                {'delivery_person': str(ram_pk)},
            )
            doc = db.library_rental.find_one({'_id': ObjectId(rental_id)})
            status = (doc or {}).get('rental_status')
            if status == Rental.STATUS_ASSIGNED:
                ok('Assign sets rental_status Assigned')
            else:
                bad(f'Assign status={status}')
            if status != Rental.STATUS_PENDING:
                ok('Removed from live pending')
            else:
                bad('Still in live pending')
            delivery = db.library_delivery.find_one({'rental_id': ObjectId(rental_id)})
            if delivery and str(delivery.get('delivery_person_id')) == str(ram_pk):
                ok('Shows on delivery dashboard query')
            else:
                bad('Not on delivery dashboard')
            if delivery:
                d_id = str(delivery['_id'])
                c_admin.post(
                    f'/en/library/admin-dashboard/update-delivery/{d_id}/',
                    {'status': 'Delivered'},
                )
                doc = db.library_rental.find_one({'_id': ObjectId(rental_id)})
                if (doc or {}).get('rental_status') == Rental.STATUS_COMPLETED:
                    ok('Delivered -> Completed')
                else:
                    bad(f'After deliver status={(doc or {}).get("rental_status")}')
            else:
                bad('No delivery row after assign')
            db.library_delivery.delete_many({'rental_id': ObjectId(rental_id)})
            db.library_rental.delete_one({'_id': ObjectId(rental_id)})
        else:
            bad('Need pending rental + ram DeliveryStaff for assignment test')

    print(f'\n{"=" * 50}')
    print(f'Results: {PASS} passed, {FAIL} failed')
    print(f'{"=" * 50}')
    return 1 if FAIL else 0


if __name__ == '__main__':
    sys.exit(main())
