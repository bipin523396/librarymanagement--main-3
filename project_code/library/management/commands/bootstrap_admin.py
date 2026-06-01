"""
Create or reset an admin account (use on Render shell).

  python manage.py bootstrap_admin --email admin@bookhub.com --password YourPassword123
"""

from django.core.management.base import BaseCommand
from django.contrib.auth.models import User


class Command(BaseCommand):
    help = 'Create or update a superuser for login (MongoDB-safe).'

    def add_arguments(self, parser):
        parser.add_argument('--email', required=True, help='Login email (used as username)')
        parser.add_argument('--password', required=True, help='Login password')
        parser.add_argument('--first-name', default='Admin', help='First name')
        parser.add_argument('--last-name', default='User', help='Last name')

    def handle(self, *args, **options):
        email = options['email'].strip()
        password = options['password']
        user = User.objects.filter(username=email).first() or User.objects.filter(email=email).first()

        if user:
            user.set_password(password)
            user.is_superuser = True
            user.is_staff = True
            user.is_active = True
            user.email = email
            user.first_name = options['first_name']
            user.last_name = options['last_name']
            user.save()
            self.stdout.write(self.style.SUCCESS(f'Updated admin: {email} (id={user.pk})'))
        else:
            user = User.objects.create_user(
                username=email,
                email=email,
                password=password,
                first_name=options['first_name'],
                last_name=options['last_name'],
            )
            user.is_superuser = True
            user.is_staff = True
            user.is_active = True
            user.save()
            self.stdout.write(self.style.SUCCESS(f'Created admin: {email} (id={user.pk})'))

        self.stdout.write('Login at /en/library/login/ with this email and password.')
