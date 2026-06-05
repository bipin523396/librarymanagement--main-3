import os
import django
import traceback

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'bookhub_backend.settings')
django.setup()

from django.contrib.auth.models import User

try:
    print("Testing get with one field:")
    u = User.objects.filter(username="testadmin").first()
    print("OK", u)
except Exception as e:
    print("Error 1:", e)

try:
    print("Testing get_or_create with one field:")
    u, c = User.objects.get_or_create(username="testadmin")
    print("OK", u)
except Exception as e:
    print("Error 2:", type(e))

