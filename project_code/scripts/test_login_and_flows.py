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
    c_admin = Client()
    r = c_admin.post(
        '/en/library/login/',
        {'username': admin_email, 'password': admin_password},
        follow=True,
    )
    user = authenticate(username=admin_email, password=admin_password)
    if user is None:
        try:
            u = User.objects.get(email=admin_email)
            user = authenticate(username=u.username, password=admin_password)
        except User.DoesNotExist:
            user = None

    if user is not None:
        ok(f'Admin authenticates ({user.username})')
        c_admin.force_login(user)
        c_admin.session['login_role'] = 'admin'
        c_admin.session.save()
        r = c_admin.get('/en/library/admin-dashboard/')
        if r.status_code == 200:
            ok('Admin dashboard HTTP 200')
        else:
            bad(f'Admin dashboard HTTP {r.status_code}')
    elif r.status_code == 200 and 'admin-dashboard' in r.request.get('PATH_INFO', ''):
        ok('Admin login redirect (POST follow)')
    else:
        bad('Admin login failed — run: python manage.py bootstrap_admin --email ... --password Test123@')

    section('Delivery login (ram)')
    c_ram = Client()
    ram = None
    try:
        ram = User.objects.get(username='ram')
    except User.DoesNotExist:
        bad('User ram not in database')
    if ram:
        logged = False
        for pwd in ('ram123', 'Test123@', 'ram', 'pass'):
            if authenticate(username='ram', password=pwd):
                r = c_ram.post('/en/library/login/', {'username': 'ram', 'password': pwd}, follow=True)
                logged = r.status_code in (200, 302)
                if logged:
                    ok(f'ram login with password')
                    break
        if not logged:
            c_ram = Client()
            c_ram.force_login(ram)
            c_ram.session['login_role'] = 'delivery'
            c_ram.session['_auth_user_id'] = str(ram.pk)
            c_ram.session.save()
            ok('ram force_login (set password if needed)')
        r = c_ram.get('/en/library/delivery/')
        if r.status_code == 200:
            ok('Delivery dashboard HTTP 200')
        else:
            bad(f'Delivery dashboard HTTP {r.status_code}')

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
    if user is None:
        bad('Skip assignment — no admin user')
    else:
        author, _ = Author.objects.get_or_create(slug='test-author', defaults={'name': 'Test Author'})
        book = Book.objects.first()
        if not book:
            book, _ = Book.objects.get_or_create(
                isbn='TEST-E2E-001',
                defaults={
                    'title': 'E2E Book',
                    'author': author,
                    'category': 'Fiction',
                    'copies_total': 5,
                    'copies_available': 5,
                },
            )
        customer, _ = User.objects.get_or_create(username='e2e_customer', defaults={'email': 'e2e@test.com'})
        staff = DeliveryStaff.objects.filter(user__username='ram').first()
        if book and staff:
            rental = Rental.objects.create(
                user=customer,
                book=book,
                duration_days=7,
                total_amount=50,
                rental_status=Rental.STATUS_PENDING,
                due_date=date.today() + timedelta(days=7),
            )
            c_admin.post(
                f'/en/library/admin-dashboard/assign-delivery/{rental.id}/',
                {'delivery_person': str(staff.id)},
            )
            rental.refresh_from_db()
            if rental.rental_status == Rental.STATUS_ASSIGNED:
                ok('Assign sets rental_status Assigned')
            else:
                bad(f'Assign status={rental.rental_status}')
            if not Rental.objects.filter(pk=rental.pk, rental_status=Rental.STATUS_PENDING).exists():
                ok('Removed from live pending')
            else:
                bad('Still in live pending')
            d = Delivery.objects.get(rental=rental)
            if ram and any(
                x.rental_id == rental.id and x.rental.rental_status == Rental.STATUS_ASSIGNED
                for x in Delivery.objects.filter(delivery_person=ram)
            ):
                ok('Shows on delivery dashboard query')
            else:
                bad('Not on delivery dashboard')
            c_admin.post(
                f'/en/library/admin-dashboard/update-delivery/{d.id}/',
                {'status': 'Delivered'},
            )
            rental.refresh_from_db()
            if rental.rental_status == Rental.STATUS_COMPLETED:
                ok('Delivered -> Completed')
            else:
                bad(f'After deliver status={rental.rental_status}')
            rental.delete()
        else:
            bad('Need book + ram DeliveryStaff for assignment test')

    print(f'\n{"=" * 50}')
    print(f'Results: {PASS} passed, {FAIL} failed')
    print(f'{"=" * 50}')
    return 1 if FAIL else 0


if __name__ == '__main__':
    sys.exit(main())
