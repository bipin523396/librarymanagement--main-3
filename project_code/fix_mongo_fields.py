import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'bookhub_backend.settings')
django.setup()

from library.models import Book

# We can access pymongo collection via Djongo
from django.db import connection
db = connection.cursor().db_conn

# In MongoDB, the collection is library_book
# the fields are 'author' (string) and 'author_fk_id' (ObjectId)
# We want to set 'author_id' to 'author_fk_id'
collection = db['library_book']

for book in collection.find({}):
    if 'author_fk_id' in book:
        # Django ForeignKey expects author_id
        collection.update_one(
            {'_id': book['_id']},
            {'$set': {'author_id': book['author_fk_id']}}
        )

print("MongoDB fields updated.")
