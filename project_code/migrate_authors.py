import os
import django
from django.utils.text import slugify

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'bookhub_backend.settings')
django.setup()

from library.models import Book, Author

books = Book.objects.all()
for book in books:
    if book.author and isinstance(book.author, str):
        slug = slugify(book.author)
        author_obj, created = Author.objects.get_or_create(
            slug=slug,
            defaults={'name': book.author}
        )
        book.author_fk = author_obj
        book.save()
        print(f"Migrated book '{book.title}' to Author '{author_obj.name}'")
print("Migration completed.")
