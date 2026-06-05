import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'bookhub_backend.settings')
django.setup()

from library.models import UserProfile
from django.db.models.query import QuerySet

# My monkeypatch is already applied in library/apps.py
print("Current get method:", QuerySet.get)

# Let's force a MultipleObjectsReturned in the original method by calling it with no args, 
# but my patch should catch it!
try:
    # Normally, UserProfile.objects.get() throws MultipleObjectsReturned if >1 object, 
    # but my database is empty or cannot be reached (ServerSelectionTimeout).
    # I can't test DB queries.
    pass
except Exception as e:
    print("Error:", type(e))

