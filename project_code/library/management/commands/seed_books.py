"""Add sample books if the database is empty (run on Render Shell if homepage shows no books)."""

from django.core.management.base import BaseCommand

from library.models import Author, Book


SAMPLES = [
    ('sudha-murty', 'Sudha Murty', 'The Magic of the Lost Temple', 'Fiction'),
    ('ruskin-bond', 'Ruskin Bond', 'The Blue Umbrella', 'Fiction'),
    ('jk-rowling', 'J.K. Rowling', "Harry Potter and the Philosopher's Stone", 'Fiction'),
    ('james-clear', 'James Clear', 'Atomic Habits', 'Business'),
    ('amish-tripathi', 'Amish Tripathi', 'The Immortals of Meluha', 'Fiction'),
]


class Command(BaseCommand):
    help = 'Seed sample books when Atlas/DB has zero books'

    def handle(self, *args, **options):
        if Book.objects.exists():
            self.stdout.write(self.style.WARNING(
                f'Database already has {Book.objects.count()} book(s). Skipping seed.'
            ))
            return

        created = 0
        for slug, author_name, title, category in SAMPLES:
            author, _ = Author.objects.get_or_create(
                slug=slug,
                defaults={'name': author_name, 'genres': category},
            )
            _, was_created = Book.objects.get_or_create(
                isbn=f'SEED-{slug}',
                defaults={
                    'title': title,
                    'author': author,
                    'category': category,
                    'copies_total': 10,
                    'copies_available': 10,
                    'status': 'Available',
                },
            )
            if was_created:
                created += 1

        self.stdout.write(self.style.SUCCESS(f'Created {created} sample books.'))
