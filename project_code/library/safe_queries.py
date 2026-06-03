"""Safe ORM helpers for Djongo/MongoDB (avoid crashes on broken relations)."""

import logging
import os

logger = logging.getLogger(__name__)


class _DisplayImage:
    def __init__(self, url):
        url = str(url or '')
        if url and not url.startswith(('http://', 'https://', '/')):
            url = '/media/' + url
        self.url = url

    def __bool__(self):
        return bool(self.url)


class _DisplayAuthor:
    def __init__(self, name='Unknown Author', slug='unknown'):
        self.name = name or 'Unknown Author'
        self.slug = slug or 'unknown'

    def __str__(self):
        return self.name


class _DisplayBook:
    def __init__(self, doc, author):
        self.id = doc.get('id') or str(doc.get('_id', ''))
        self.pk = self.id
        self.title = doc.get('title') or ''
        self.author = author
        self.category = doc.get('category') or ''
        self.isbn = doc.get('isbn') or ''
        self.copies_available = doc.get('copies_available') or 0
        self.status = doc.get('status') or 'Available'
        self.image = _DisplayImage(doc.get('image') or '')

    @property
    def price_per_day(self):
        prices = {
            'Fiction': 15.00,
            'Business': 25.00,
            'Toddlers': 10.00,
            'Biographies': 20.00,
            'Academic': 30.00,
        }
        return prices.get(self.category, 15.00)


def normalize_rental_status(value):
    return str(value or '').strip().lower()


def get_rental_or_404(rental_id, rental_model):
    """Load rental by Djongo pk or MongoDB ObjectId string."""
    from django.http import Http404

    rid = str(rental_id).strip()
    if not rid:
        raise Http404
    candidates = [rental_id, rid]
    try:
        candidates.append(int(rid))
    except (TypeError, ValueError):
        pass
    for pk in candidates:
        rental = rental_model.objects.filter(pk=pk).first()
        if rental:
            return rental
    try:
        from bson import ObjectId
        from bookhub_backend.mongo_config import get_shared_client
        import os

        client = get_shared_client()
        if client:
            db_name = os.getenv('MONGODB_NAME', 'bookhub_db')
            # Fix: rid might not be a valid ObjectId hex string
            try:
                oid = ObjectId(rid)
            except Exception:
                oid = None

            if oid:
                doc = client[db_name].library_rental.find_one({'_id': oid})
                if doc:
                    rental = rental_model(pk=oid)
                    rental.rental_status = doc.get('rental_status', rental_model.STATUS_PENDING)
                    return rental
    except Exception as exc:
        logger.warning('get_rental_or_404: %s', exc)
    raise Http404


def get_delivery_or_404(delivery_id, delivery_model):
    """Load delivery by pk or MongoDB ObjectId string."""
    from django.http import Http404

    did = str(delivery_id).strip()
    if not did:
        raise Http404
    candidates = [delivery_id, did]
    try:
        candidates.append(int(did))
    except (TypeError, ValueError):
        pass
    for pk in candidates:
        delivery = delivery_model.objects.filter(pk=pk).first()
        if delivery:
            return delivery
    try:
        from bson import ObjectId
        from bookhub_backend.mongo_config import get_shared_client
        import os

        client = get_shared_client()
        if client:
            db_name = os.getenv('MONGODB_NAME', 'bookhub_db')
            try:
                oid = ObjectId(did)
            except Exception:
                oid = None

            if oid:
                doc = client[db_name].library_delivery.find_one({'_id': oid})
                if doc:
                    delivery = delivery_model(pk=oid)
                    delivery.rental_id = doc.get('rental_id')
                    delivery.status = doc.get('status', 'Pending')
                    delivery.delivery_person_id = doc.get('delivery_person_id')
                    return delivery
    except Exception as exc:
        logger.warning('get_delivery_or_404: %s', exc)
    raise Http404



def rental_for_delivery(delivery, rental_model):
    """Resolve rental for a delivery without raising."""
    rental = getattr(delivery, 'rental', None)
    if rental is not None:
        return rental
    rental_id = getattr(delivery, 'rental_id', None)
    if not rental_id:
        return None
    try:
        return rental_model.objects.filter(pk=rental_id).first()
    except Exception as exc:
        logger.warning('rental_for_delivery failed: %s', exc)
        return None


def split_deliveries_for_dashboard(deliveries, rental_model, assigned_status='assigned'):
    """Return (active, history) delivery lists; never raises."""
    active = []
    history = []
    for delivery in deliveries:
        try:
            rental = rental_for_delivery(delivery, rental_model)
            if not rental:
                continue
            status = normalize_rental_status(getattr(rental, 'rental_status', ''))
            if status == assigned_status:
                active.append(delivery)
            elif status in ('completed', 'failed'):
                history.append(delivery)
        except Exception as exc:
            logger.warning('DELIVERY DASHBOARD ERROR: %s', exc)
            continue
    return active, history


def _author_lookup_query(author_ids):
    if not author_ids:
        return {}

    object_ids = []
    try:
        from bson import ObjectId
        for aid in author_ids:
            sid = str(aid)
            if len(sid) == 24:
                try:
                    object_ids.append(ObjectId(sid))
                except Exception:
                    pass
    except Exception:
        pass

    query = {'id': {'$in': list(author_ids)}}
    if object_ids:
        query = {'$or': [query, {'_id': {'$in': object_ids}}]}
    return query


def _books_for_display_from_mongo():
    from bookhub_backend.mongo_config import get_shared_client

    client = get_shared_client()
    if not client:
        return None

    db_name = os.getenv('MONGODB_NAME', 'bookhub_db')
    limit = int(os.getenv('HOME_BOOK_LIMIT', '60'))
    db = client[db_name]

    projection = {
        'id': 1,
        'title': 1,
        'author_id': 1,
        'category': 1,
        'isbn': 1,
        'copies_available': 1,
        'status': 1,
        'image': 1,
    }
    raw_books = list(db.library_book.find({}, projection).sort('id', 1).limit(limit))

    author_ids = {book.get('author_id') for book in raw_books if book.get('author_id') is not None}
    authors_by_key = {}
    if author_ids:
        for author_doc in db.library_author.find(
            _author_lookup_query(author_ids),
            {'id': 1, 'name': 1, 'slug': 1},
        ):
            author = _DisplayAuthor(author_doc.get('name'), author_doc.get('slug'))
            if author_doc.get('id') is not None:
                authors_by_key[str(author_doc.get('id'))] = author
            authors_by_key[str(author_doc.get('_id'))] = author

    books = []
    categories = set()
    for doc in raw_books:
        if not doc.get('title'):
            continue
        author = authors_by_key.get(str(doc.get('author_id'))) or _DisplayAuthor()
        book = _DisplayBook(doc, author)
        books.append(book)
        if book.category:
            categories.add(book.category)

    return books, sorted(categories), None


def books_for_display(book_model, author_model=None):
    """Load books for homepage; never skip books, and avoid slow FK scans on Render."""
    try:
        mongo_result = _books_for_display_from_mongo()
        if mongo_result is not None:
            return mongo_result
    except Exception as exc:
        logger.warning('books_for_display direct Mongo load failed: %s', exc)
        return [], [], str(exc)

    books = []
    categories = set()
    try:
        limit = int(os.getenv('HOME_BOOK_LIMIT', '60'))
        qs = book_model.objects.all().order_by('id')[:limit]
    except Exception as exc:
        logger.warning('books_for_display query failed: %s', exc)
        return [], [], str(exc)

    for book in qs:
        try:
            title = getattr(book, 'title', None)
            if not title:
                continue

            # Try to resolve author — but NEVER skip the book if it fails
            if author_model is not None:
                try:
                    author = getattr(book, 'author', None)
                    if author is None and getattr(book, 'author_id', None):
                        aid = book.author_id
                        for lookup in [
                            lambda: author_model.objects.filter(pk=aid).first(),
                            lambda: author_model.objects.filter(id=aid).first(),
                            lambda: author_model.objects.filter(id=int(aid)).first(),
                        ]:
                            try:
                                author = lookup()
                                if author:
                                    break
                            except Exception:
                                pass

                    # If still None, try a direct MongoDB lookup by ObjectId
                    if author is None:
                        try:
                            from bson import ObjectId
                            from bookhub_backend.mongo_config import get_shared_client
                            client = get_shared_client()
                            if client:
                                db_name = os.getenv('MONGODB_NAME', 'bookhub_db')
                                db = client[db_name]
                                # Find the author doc for this book's author_id
                                book_doc = db.library_book.find_one(
                                    {'id': getattr(book, 'id', None)},
                                    {'author_id': 1}
                                )
                                if book_doc and book_doc.get('author_id'):
                                    aid = book_doc['author_id']
                                    author_doc = db.library_author.find_one({'id': aid})
                                    if author_doc:
                                        author = author_model(
                                            name=author_doc.get('name', 'Unknown'),
                                            slug=author_doc.get('slug', ''),
                                        )
                        except Exception:
                            pass

                    # If still no author, attach a placeholder so book still shows
                    if author is None:
                        author = author_model(name='Unknown Author', slug='unknown')
                        book.author = author

                except Exception as exc:
                    logger.warning('Author resolve failed for book %s: %s', getattr(book, 'pk', '?'), exc)
                    book.author = author_model(name='Unknown Author', slug='unknown')

            books.append(book)
            cat = getattr(book, 'category', None)
            if cat:
                categories.add(cat)
        except Exception as exc:
            logger.warning('Skipping book id=%s: %s', getattr(book, 'pk', '?'), exc)
            continue
    return books, sorted(categories), None


def rentals_for_admin(rental_model, status_filter, limit=50):
    """Load bounded rental rows for admin tables without expensive relation scans."""
    rows = []
    allowed = None
    simple_filter = dict(status_filter)
    if 'rental_status__in' in simple_filter:
        allowed = set(simple_filter.pop('rental_status__in'))
    try:
        try:
            qs = rental_model.objects.filter(**simple_filter).select_related('user', 'book').order_by('-rented_at')
        except Exception:
            qs = rental_model.objects.filter(**simple_filter).order_by('-rented_at')
        try:
            qs = qs[:limit]
        except Exception:
            pass
    except Exception as exc:
        logger.warning('rentals_for_admin failed: %s', exc)
        return rows
    for rental in qs:
        try:
            if allowed is not None and getattr(rental, 'rental_status', None) not in allowed:
                continue
            rows.append(rental)
        except Exception as exc:
            logger.warning('Skipping rental id=%s: %s', getattr(rental, 'pk', '?'), exc)
    return rows
