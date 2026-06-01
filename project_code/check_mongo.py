#!/usr/bin/env python
"""Run on Render shell: python check_mongo.py"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'bookhub_backend.settings')
django.setup()

from bookhub_backend.mongo_config import get_mongodb_uri, mask_mongodb_uri, mongodb_username_from_uri
from pymongo import MongoClient

uri = get_mongodb_uri()
print('URI (masked):', mask_mongodb_uri(uri))
print('User:', mongodb_username_from_uri(uri))
if not uri:
    print('ERROR: MONGODB_URI / DJANGO_DATABASE_URL not set')
    raise SystemExit(1)
try:
    MongoClient(uri, serverSelectionTimeoutMS=15000).admin.command('ping')
    print('OK: MongoDB ping succeeded')
except Exception as e:
    print('FAIL:', e)
    raise SystemExit(1)
