"""
Force-create admin/admin123 directly in MongoDB Atlas (the production DB).
Run: python force_create_admin_atlas.py
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from dotenv import load_dotenv
load_dotenv(os.path.join(os.path.dirname(__file__), '.env'))

# --- Use ATLAS URI directly (not local) ---
ATLAS_URI = "mongodb+srv://bookhub_user:%40Sagarmatha321@cluster0.3f7teqs.mongodb.net/bookhub_db?retryWrites=true&w=majority&appName=Cluster0"
DB_NAME = "bookhub_db"

from pymongo import MongoClient
from django.contrib.auth.hashers import make_password

# We need Django only for make_password
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'bookhub_backend.settings')

# Override the DB to Atlas for this script
os.environ['MONGODB_URI'] = ATLAS_URI

django.setup()

print("=" * 60)
print("FORCE-CREATING admin/admin123 in MongoDB ATLAS")
print("=" * 60)

client = MongoClient(ATLAS_URI, serverSelectionTimeoutMS=15000)
db = client[DB_NAME]
coll = db.auth_user

hashed = make_password('admin123')

# Check if exists
existing = coll.find_one({'username': 'admin'})
if existing:
    print(f"\n[Atlas] Found existing 'admin' doc — RESETTING password & flags...")
    result = coll.update_one(
        {'username': 'admin'},
        {'$set': {
            'password': hashed,
            'is_superuser': True,
            'is_staff': True,
            'is_active': True,
            'first_name': 'Admin',
            'last_name': 'User',
            'email': 'admin@bookhub.local',
        }}
    )
    print(f"  Updated: matched={result.matched_count}, modified={result.modified_count}")
else:
    print(f"\n[Atlas] 'admin' NOT found — CREATING new doc...")
    result = coll.insert_one({
        'username': 'admin',
        'email': 'admin@bookhub.local',
        'password': hashed,
        'first_name': 'Admin',
        'last_name': 'User',
        'is_superuser': True,
        'is_staff': True,
        'is_active': True,
        'date_joined': __import__('datetime').datetime.utcnow(),
        'last_login': None,
    })
    print(f"  Inserted with id={result.inserted_id}")

# Verify
doc = coll.find_one({'username': 'admin'})
print(f"\n[Atlas] Verification:")
print(f"  username    = {doc.get('username')}")
print(f"  is_superuser= {doc.get('is_superuser')}")
print(f"  is_staff    = {doc.get('is_staff')}")
print(f"  is_active   = {doc.get('is_active')}")
print(f"  password    = {str(doc.get('password',''))[:30]}...")

print("\n" + "=" * 60)
print("Done! Try logging in at:")
print("  https://librarymanagement-main-3tx9.onrender.com/en/library/login/")
print("  Username: admin")
print("  Password: admin123")
print("=" * 60)
