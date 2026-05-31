import os
from pymongo import MongoClient
from dotenv import load_dotenv

load_dotenv()

uri = os.getenv('MONGODB_URI')
if not uri:
    print('MONGODB_URI not set')
    raise SystemExit(1)

client = MongoClient(uri, serverSelectionTimeoutMS=5000)
try:
    # Trigger a server selection
    client.server_info()
    print('Connected to MongoDB successfully')
    db = client.get_default_database()
    print('Database:', db.name)
    print('Collections:', db.list_collection_names())
except Exception as e:
    print('Failed to connect to MongoDB:', e)
    raise

