from pymongo import MongoClient
import sys

uri = "mongodb+srv://bookhub_user:%40Sagarmatha321@cluster0.3f7teqs.mongodb.net/bookhub_db?retryWrites=true&w=majority&authSource=admin"
client = MongoClient(uri, serverSelectionTimeoutMS=5000)
try:
    client.admin.command('ping')
    print("✅ Pinged your deployment. You successfully connected to MongoDB!")
except Exception as e:
    print("❌ Failed to connect:", e)
