import os
import sys

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'bookhub_backend.settings')
import django
django.setup()

from library.models import UserSettings

import traceback

try:
    count = UserSettings.objects.count()
    print(f"✅ Database connection successful. UserSettings count: {count}")
except Exception as e:
    print(f"❌ Database connection failed:")
    traceback.print_exc()
