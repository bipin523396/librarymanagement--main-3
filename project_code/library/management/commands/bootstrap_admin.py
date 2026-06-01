"""
Create or reset an admin account (use on Render shell).

  python manage.py bootstrap_admin --email admin@bookhub.com --password YourPassword123
"""

import os

from django.contrib.auth.hashers import make_password
from django.contrib.auth.models import User
from django.core.management.base import BaseCommand
from pymongo import MongoClient

from bookhub_backend.mongo_config import get_mongodb_uri


class Command(BaseCommand):
    help = 'Create or update a superuser for login (MongoDB-safe).'

    def add_arguments(self, parser):
        parser.add_argument('--email', required=True, help='Login email (used as username)')
        parser.add_argument('--password', required=True, help='Login password')
        parser.add_argument('--first-name', default='Admin', help='First name')
        parser.add_argument('--last-name', default='User', help='Last name')

    def _sync_mongo_user(self, email, password, first_name, last_name):
        uri = get_mongodb_uri()
        if not uri:
            return
        db_name = os.getenv('MONGODB_NAME', 'bookhub_db')
        coll = MongoClient(uri)[db_name].auth_user
        hashed = make_password(password)
        coll.update_one(
            {'username': email},
            {
                '$set': {
                    'username': email,
                    'email': email,
                    'password': hashed,
                    'first_name': first_name,
                    'last_name': last_name,
                    'is_superuser': True,
                    'is_staff': True,
                    'is_active': True,
                },
            },
            upsert=True,
        )

    def handle(self, *args, **options):
        email = options['email'].strip()
        password = options['password']
        first_name = options['first_name']
        last_name = options['last_name']

        user = User.objects.filter(username=email).first() or User.objects.filter(email=email).first()

        if user:
            user.set_password(password)
            user.is_superuser = True
            user.is_staff = True
            user.is_active = True
            user.email = email
            user.first_name = first_name
            user.last_name = last_name
            user.save()
            self.stdout.write(self.style.SUCCESS(f'Updated admin: {email} (id={user.pk})'))
        else:
            user = User.objects.create_user(
                username=email,
                email=email,
                password=password,
                first_name=first_name,
                last_name=last_name,
            )
            user.is_superuser = True
            user.is_staff = True
            user.is_active = True
            user.save()
            self.stdout.write(self.style.SUCCESS(f'Created admin: {email} (id={user.pk})'))

        self._sync_mongo_user(email, password, first_name, last_name)
        self.stdout.write(self.style.SUCCESS('Synced admin flags to MongoDB (is_superuser=True).'))
        self.stdout.write('Login at /en/library/login/ with this email and password.')
