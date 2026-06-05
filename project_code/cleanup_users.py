import os
import sys

sys.path.append('/Users/bipinyadav/Desktop/librarymanagement--main-3/project_code')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'bookhub_backend.settings')

import django
django.setup()

from bookhub_backend.mongo_config import get_shared_client
from django.contrib.auth.models import User

client = get_shared_client()
if client:
    db = client[os.getenv('MONGODB_NAME', 'bookhub_db')]
    
    # We want to keep 'bipin' and 'ram' and 'admin'
    users_to_keep = ['bipin', 'ram', 'admin']
    
    # Find all users NOT in this list
    all_users = list(db.auth_user.find({'username': {'$nin': users_to_keep}}))
    
    for u in all_users:
        uid = u.get('id') or u.get('_id')
        username = u.get('username')
        
        # Check if they have a userprofile
        has_profile = db.library_userprofile.find_one({'user_id': uid})
        
        # Check if they have rentals
        has_rentals = db.library_rental.find_one({'user_id': uid})
        
        if not has_profile and not has_rentals:
            print(f"Deleting user {username}")
            db.auth_user.delete_one({'_id': u['_id']})
    
    print("Cleanup done!")
else:
    print("No mongo client")
