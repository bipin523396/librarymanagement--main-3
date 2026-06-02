import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'bookhub_backend.settings')
django.setup()

from library.models import Book

def seed_books():
    books_data = [
        # Fiction
        {
            "title": "The God of Small Things",
            "author": "Arundhati Roy",
            "category": "Fiction",
            "isbn": "9780812979657",
            "copies_total": 5,
            "copies_available": 5,
            "status": "Available",
            "image_url": "https://images4.penguinrandomhouse.com/cover/9780812979657"
        },
        {
            "title": "The Book of Lost Friends",
            "author": "Lisa Wingate",
            "category": "Fiction",
            "isbn": "9781984819901",
            "copies_total": 3,
            "copies_available": 3,
            "status": "Available",
            "image_url": "https://images4.penguinrandomhouse.com/cover/9781984819901"
        },
        {
            "title": "Midnight's Children",
            "author": "Salman Rushdie",
            "category": "Fiction",
            "isbn": "9780812976533",
            "copies_total": 4,
            "copies_available": 2,
            "status": "Low Stock",
            "image_url": "https://images4.penguinrandomhouse.com/cover/9780812976533"
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
            "image_url": "https://images-na.ssl-images-amazon.com/images/I/81bwtQdkWGL.jpg"
        },
        {
            "title": "Atomic Habits",
            "author": "James Clear",
            "category": "Business",
            "isbn": "9780735211292",
            "copies_total": 10,
            "copies_available": 9,
            "status": "Available",
            "image_url": "https://images-na.ssl-images-amazon.com/images/I/91bYsX41hL.jpg"
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
            "image_url": "https://images-na.ssl-images-amazon.com/images/I/81dDw1YqByL.jpg"
        },
        {
            "title": "Steve Jobs",
            "author": "Walter Isaacson",
            "category": "Biographies",
            "isbn": "9781451648539",
            "copies_total": 4,
            "copies_available": 0,
            "status": "Out of Stock",
            "image_url": "https://images-na.ssl-images-amazon.com/images/I/41dKpzcoamL._SX323_BO1,204,203,200_.jpg"
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
            "image_url": "https://images3.penguinrandomhouse.com/cover/9798217233977"
        },
        {
            "title": "The Very Hungry Caterpillar",
            "author": "Eric Carle",
            "category": "Toddlers",
            "isbn": "9780399226908",
            "copies_total": 7,
            "copies_available": 7,
            "status": "Available",
            "image_url": "https://images-na.ssl-images-amazon.com/images/I/71Koy6rWv7L.jpg"
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
            "image_url": "https://images-na.ssl-images-amazon.com/images/I/61Mw352+WPL.jpg"
        }
    ]

    print("Clearing existing books and authors...")
    try:
        from pymongo import MongoClient
        from bookhub_backend.mongo_config import get_mongodb_uri
        import os
        uri = get_mongodb_uri()
        if uri:
            db_name = os.getenv('MONGODB_NAME', 'bookhub_db')
            db = MongoClient(uri)[db_name]
            res_books = db.library_book.delete_many({})
            print(f"Bypassed Django delete: cleared {res_books.deleted_count} books from Atlas.")
            res_authors = db.library_author.delete_many({})
            print(f"Bypassed Django delete: cleared {res_authors.deleted_count} authors from Atlas.")
        else:
            Book.objects.all().delete()
    except Exception as e:
        print(f"PyMongo bypass failed, fallback to Django: {e}")
        Book.objects.all().delete()

    print("Seeding books...")
    from library.models import Author
    from django.utils.text import slugify

    author_id_counter = 1
    book_id_counter = 1
    for data in books_data:
        author_name = data["author"]
        slug = slugify(author_name)
        try:
            author_obj = Author.objects.get(slug=slug)
            if not author_obj.id:
                author_obj.id = author_id_counter
                author_obj.save()
                author_id_counter += 1
        except Author.DoesNotExist:
            author_obj = Author.objects.create(
                id=author_id_counter,
                name=author_name,
                slug=slug
            )
            author_id_counter += 1

        Book.objects.create(
            id=book_id_counter,
            title=data["title"],
            author=author_obj,
            category=data["category"],
            isbn=data["isbn"],
            copies_total=data["copies_total"],
            copies_available=data["copies_available"],
            status=data["status"],
            image=None
        )
        book_id_counter += 1
    print("Successfully seeded database with beautiful books!")

if __name__ == '__main__':
    seed_books()
