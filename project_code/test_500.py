import os
import django
import traceback

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'bookhub_backend.settings')
django.setup()

from django.test.client import Client
from django.contrib.auth.models import User

try:
    c = Client()
    # Create user
    user, created = User.objects.get_or_create(username="testadmin", email="testadmin@example.com")
    user.set_password("admin123")
    user.is_superuser = True
    user.is_staff = True
    user.save()
    
    logged_in = c.login(username="testadmin", password="admin123")
    print(f"Logged in: {logged_in}")
    
    resp = c.get('/en/library/admin-dashboard/')
    print(f"Admin dashboard status: {resp.status_code}")
    
except Exception as e:
    traceback.print_exc()

