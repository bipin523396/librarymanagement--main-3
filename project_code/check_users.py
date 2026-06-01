import os
from pymongo import MongoClient
from dotenv import load_dotenv

load_dotenv()

uri = os.getenv('MONGODB_URI')
client = MongoClient(uri)
db = client.get_default_database()
users = list(db['auth_user'].find({}, {'username': 1, 'email': 1}))

print(f"Total users in auth_user: {len(users)}")
for user in users:
    print(f"- {user.get('username')} ({user.get('email')})")
