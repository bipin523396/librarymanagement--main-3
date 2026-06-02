"""
seed_books.py — Seeds the database with sample books across all categories.
Uses PyMongo directly to clear old data (avoids Djongo ORM delete() bugs),
then inserts via Django ORM.
"""
import os
import sys
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'bookhub_backend.settings')
django.setup()


BOOKS_DATA = [
    # Fiction
    {
        "title": "The God of Small Things",
        "author": "Arundhati Roy",
        "category": "Fiction",
        "isbn": "9780812979657",
        "copies_total": 5,
        "copies_available": 5,
        "status": "Available",
    },
    {
        "title": "The Book of Lost Friends",
        "author": "Lisa Wingate",
        "category": "Fiction",
        "isbn": "9781984819901",
        "copies_total": 3,
        "copies_available": 3,
        "status": "Available",
    },
    {
        "title": "Midnight's Children",
        "author": "Salman Rushdie",
        "category": "Fiction",
        "isbn": "9780812976533",
        "copies_total": 4,
        "copies_available": 2,
        "status": "Low Stock",
    },
    # Business
    {
        "title": "Rich Dad Poor Dad",
        "author": "Robert Kiyosaki",
        "category": "Business",
        "isbn": "9781612680194",
        "copies_total": 8,
        "copies_available": 8,
        "status": "Available",
    },
    {
        "title": "Atomic Habits",
        "author": "James Clear",
        "category": "Business",
        "isbn": "9780735211292",
        "copies_total": 10,
        "copies_available": 9,
        "status": "Available",
    },
    # Biographies
    {
        "title": "Wings of Fire",
        "author": "A.P.J. Abdul Kalam",
        "category": "Biographies",
        "isbn": "9788173711466",
        "copies_total": 6,
        "copies_available": 6,
        "status": "Available",
    },
    {
        "title": "Steve Jobs",
        "author": "Walter Isaacson",
        "category": "Biographies",
        "isbn": "9781451648539",
        "copies_total": 4,
        "copies_available": 4,
        "status": "Available",
    },
    # Toddlers
    {
        "title": "KPop Demon Hunters",
        "author": "Golden Books",
        "category": "Toddlers",
        "isbn": "9798217233977",
        "copies_total": 5,
        "copies_available": 5,
        "status": "Available",
    },
    {
        "title": "The Very Hungry Caterpillar",
        "author": "Eric Carle",
        "category": "Toddlers",
        "isbn": "9780399226908",
        "copies_total": 7,
        "copies_available": 7,
        "status": "Available",
    },
    # Academic
    {
        "title": "Introduction to Algorithms",
        "author": "Thomas H. Cormen",
        "category": "Academic",
        "isbn": "9780262033848",
        "copies_total": 3,
        "copies_available": 3,
        "status": "Available",
    },
]


def _pymongo_clear_books():
    """Use PyMongo to bypass Djongo ORM delete() which crashes with unhashable error."""
    try:
        from pymongo import MongoClient
        from bookhub_backend.mongo_config import get_mongodb_uri

        uri = get_mongodb_uri()
        if not uri:
            print("No MongoDB URI — skipping PyMongo clear.")
            return False

        db_name = os.getenv('MONGODB_NAME', 'bookhub_db')
        db = MongoClient(uri, serverSelectionTimeoutMS=10000)[db_name]

        r_books = db['library_book'].delete_many({})
        print(f"  PyMongo: cleared {r_books.deleted_count} books from library_book.")

        r_authors = db['library_author'].delete_many({})
        print(f"  PyMongo: cleared {r_authors.deleted_count} authors from library_author.")

        return True
    except Exception as exc:
        print(f"  PyMongo clear failed: {exc}")
        return False


def _get_next_id(collection_name):
    """Get a safe integer ID for insertion by finding the max existing id."""
    try:
        from pymongo import MongoClient
        from bookhub_backend.mongo_config import get_mongodb_uri

        uri = get_mongodb_uri()
        if not uri:
            return None
        db_name = os.getenv('MONGODB_NAME', 'bookhub_db')
        db = MongoClient(uri, serverSelectionTimeoutMS=10000)[db_name]
        coll = db[collection_name]
        # Find max id field
        docs = list(coll.find({}, {'id': 1}).sort('id', -1).limit(1))
        if docs and docs[0].get('id'):
            return int(docs[0]['id']) + 1
        return 1
    except Exception:
        return 1


def seed_books():
    """Seed the database with sample books across all categories."""
    from library.models import Book, Author
    from django.utils.text import slugify

    print("=== Seeding Books ===")

    # Step 1: Clear existing data via PyMongo (avoids Djongo ORM bugs)
    print("Step 1: Clearing existing books & authors...")
    cleared = _pymongo_clear_books()
    if not cleared:
        # Fallback: try raw SQL/ORM with error catching
        try:
            from django.db import connection
            with connection.cursor() as cursor:
                cursor.execute("DELETE FROM library_book")
                cursor.execute("DELETE FROM library_author")
            print("  SQL fallback: cleared books and authors.")
        except Exception as exc:
            print(f"  SQL fallback also failed: {exc}. Proceeding anyway.")

    # Step 2: Seed Authors & Books
    print("Step 2: Seeding authors and books...")
    author_counter = 1
    book_counter = 1

    for data in BOOKS_DATA:
        author_name = data["author"]
        slug = slugify(author_name)

        # Try to find existing author first
        author_obj = None
        try:
            author_obj = Author.objects.filter(slug=slug).first()
        except Exception as exc:
            print(f"  Author lookup failed: {exc}")

        if not author_obj:
            try:
                author_obj = Author(
                    name=author_name,
                    slug=slug,
                    bio='',
                    nationality='',
                    born='',
                    website='',
                    genres='',
                    awards='',
                )
                author_obj.id = author_counter
                author_obj.save()
                print(f"  Created author [{author_counter}]: {author_name}")
                author_counter += 1
            except Exception as exc:
                print(f"  Failed to create author '{author_name}': {exc}")
                # Try without explicit id
                try:
                    author_obj = Author(name=author_name, slug=slug)
                    author_obj.save()
                    author_counter += 1
                except Exception as exc2:
                    print(f"  Author fallback also failed: {exc2}. Skipping book.")
                    continue

        # Create the book
        try:
            book_obj = Book(
                title=data["title"],
                author=author_obj,
                category=data["category"],
                isbn=data["isbn"],
                copies_total=data["copies_total"],
                copies_available=data["copies_available"],
                status=data["status"],
            )
            book_obj.id = book_counter
            book_obj.save()
            print(f"  Created book [{book_counter}]: {data['title']} ({data['category']})")
            book_counter += 1
        except Exception as exc:
            print(f"  Failed to create book '{data['title']}': {exc}")
            # Try without explicit id
            try:
                book_obj = Book(
                    title=data["title"],
                    author=author_obj,
                    category=data["category"],
                    isbn=data["isbn"],
                    copies_total=data["copies_total"],
                    copies_available=data["copies_available"],
                    status=data["status"],
                )
                book_obj.save()
                print(f"  Book (auto-id): {data['title']}")
                book_counter += 1
            except Exception as exc2:
                print(f"  Book fallback also failed: {exc2}")

    total = book_counter - 1
    print(f"=== Seeding complete: {total} books added ===")
    return total


if __name__ == '__main__':
    count = seed_books()
    print(f"Done! {count} books seeded.")
