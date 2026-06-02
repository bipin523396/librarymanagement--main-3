"""
Test script: check what's in MongoDB for user 'admin' and try auth directly.
Run: python test_admin_login.py
"""
import os
import sys
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'bookhub_backend.settings')
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Load .env
from dotenv import load_dotenv
load_dotenv(os.path.join(os.path.dirname(__file__), '.env'))

django.setup()

from django.contrib.auth.models import User
from django.contrib.auth import authenticate

print("=" * 60)
print("TEST: Checking admin user in DATABASE")
print("=" * 60)

# Check via Django ORM
try:
    users = User.objects.filter(username='admin')
    print(f"\n[ORM] Users with username='admin': {users.count()}")
    for u in users:
        print(f"  id={u.pk}, username={u.username}, is_superuser={u.is_superuser}, is_active={u.is_active}")
except Exception as e:
    print(f"[ORM] Error: {e}")

# Check via MongoDB directly
print("\n[MongoDB] Checking auth_user collection directly...")
try:
    from bookhub_backend.mongo_config import get_mongodb_uri
    from pymongo import MongoClient

    uri = get_mongodb_uri()
    db_name = os.getenv('MONGODB_NAME', 'bookhub_db')
    if uri:
        db = MongoClient(uri)[db_name]
        doc = db.auth_user.find_one({'username': 'admin'})
        if doc:
            print(f"  Found: username={doc.get('username')}, is_superuser={doc.get('is_superuser')}, is_active={doc.get('is_active')}")
            print(f"  password hash starts with: {str(doc.get('password',''))[:20]}...")
        else:
            print("  NOT FOUND — 'admin' user does NOT exist in MongoDB!")
            print("\n  All usernames in auth_user:")
            for d in db.auth_user.find({}, {'username': 1, 'is_superuser': 1}):
                print(f"    - {d.get('username')} (superuser={d.get('is_superuser')})")
    else:
        print("  No MongoDB URI — using local SQLite/ORM only")
except Exception as e:
    print(f"  MongoDB error: {e}")

# Test authenticate
print("\n[AUTH] Testing authenticate(username='admin', password='admin123')...")
try:
    user = authenticate(request=None, username='admin', password='admin123')
    if user:
        print(f"  SUCCESS! user={user.username}, is_superuser={user.is_superuser}")
    else:
        print("  FAILED — authenticate() returned None")
except Exception as e:
    print(f"  ERROR: {e}")

print("\n" + "=" * 60)
