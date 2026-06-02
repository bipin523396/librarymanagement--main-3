"""
Create a simple admin account: username=admin, password=admin123.
Run locally or on Render shell:

  python manage.py create_simple_admin

Override credentials with flags:
  python manage.py create_simple_admin --username admin --password admin123
"""

import os

from django.contrib.auth.hashers import make_password
from django.contrib.auth.models import User
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = 'Create or reset a simple admin account (username=admin, password=admin123).'

    def add_arguments(self, parser):
        parser.add_argument('--username', default='admin', help='Admin username (default: admin)')
        parser.add_argument('--password', default='admin123', help='Admin password (default: admin123)')
        parser.add_argument('--first-name', default='Admin', help='First name')
        parser.add_argument('--last-name', default='User', help='Last name')

    def _sync_mongo(self, username, password, first_name, last_name):
        """Write the admin directly to MongoDB so Djongo/Atlas sees it."""
        try:
            from bookhub_backend.mongo_config import get_mongodb_uri
            from pymongo import MongoClient

            uri = get_mongodb_uri()
            if not uri:
                self.stdout.write(self.style.WARNING('No MongoDB URI — skipping Mongo sync.'))
                return
            db_name = os.getenv('MONGODB_NAME', 'bookhub_db')
            coll = MongoClient(uri)[db_name].auth_user
            hashed = make_password(password)
            result = coll.update_one(
                {'username': username},
                {
                    '$set': {
                        'username': username,
                        'email': f'{username}@bookhub.local',
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
            if result.upserted_id:
                self.stdout.write(self.style.SUCCESS(f'  MongoDB: inserted new doc (id={result.upserted_id})'))
            else:
                self.stdout.write(self.style.SUCCESS(f'  MongoDB: updated existing doc (matched={result.matched_count})'))
        except Exception as exc:
            self.stdout.write(self.style.WARNING(f'  MongoDB sync warning: {exc}'))

    def handle(self, *args, **options):
        username = options['username'].strip()
        password = options['password']
        first_name = options['first_name']
        last_name = options['last_name']

        self.stdout.write(f'Setting up admin account: username="{username}" ...')

        user = User.objects.filter(username=username).first()

        if user:
            user.set_password(password)
            user.is_superuser = True
            user.is_staff = True
            user.is_active = True
            user.first_name = first_name
            user.last_name = last_name
            user.save()
            self.stdout.write(self.style.SUCCESS(f'  Django ORM: updated existing user (id={user.pk})'))
        else:
            user = User.objects.create_user(
                username=username,
                email=f'{username}@bookhub.local',
                password=password,
                first_name=first_name,
                last_name=last_name,
            )
            user.is_superuser = True
            user.is_staff = True
            user.is_active = True
            user.save()
            self.stdout.write(self.style.SUCCESS(f'  Django ORM: created new user (id={user.pk})'))

        self._sync_mongo(username, password, first_name, last_name)

        self.stdout.write('')
        self.stdout.write(self.style.SUCCESS('=' * 50))
        self.stdout.write(self.style.SUCCESS('Admin account ready!'))
        self.stdout.write(f'  Login URL : /en/library/login/')
        self.stdout.write(f'  Username  : {username}')
        self.stdout.write(f'  Password  : {password}')
        self.stdout.write(self.style.SUCCESS('=' * 50))
