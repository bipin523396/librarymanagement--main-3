"""Safe ORM helpers for Djongo/MongoDB (avoid crashes on broken relations)."""

import logging

logger = logging.getLogger(__name__)


def normalize_rental_status(value):
    return str(value or '').strip().lower()


def get_rental_or_404(rental_id, rental_model):
    """Load rental by Djongo pk or MongoDB ObjectId string."""
    from django.http import Http404

    rid = str(rental_id).strip()
    if not rid:
        raise Http404
    for pk in (rental_id, rid):
        rental = rental_model.objects.filter(pk=pk).first()
        if rental:
            return rental
    try:
        from bson import ObjectId

        oid = ObjectId(rid)
        rental = rental_model.objects.filter(pk=oid).first()
        if rental:
            return rental
        from pymongo import MongoClient
        from bookhub_backend.mongo_config import get_mongodb_uri
        import os

        uri = get_mongodb_uri()
        if uri:
            db_name = os.getenv('MONGODB_NAME', 'bookhub_db')
            doc = MongoClient(uri)[db_name].library_rental.find_one({'_id': oid})
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
    for pk in (delivery_id, did):
        delivery = delivery_model.objects.filter(pk=pk).first()
        if delivery:
            return delivery
    try:
        from bson import ObjectId

        oid = ObjectId(did)
        delivery = delivery_model.objects.filter(pk=oid).first()
        if delivery:
            return delivery
        from pymongo import MongoClient
        from bookhub_backend.mongo_config import get_mongodb_uri
        import os

        uri = get_mongodb_uri()
        if uri:
            db_name = os.getenv('MONGODB_NAME', 'bookhub_db')
            doc = MongoClient(uri)[db_name].library_delivery.find_one({'_id': oid})
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


def books_for_display(book_model, author_model=None):
    """Load books for homepage; skip rows with broken author relations."""
    books = []
    categories = set()
    try:
        qs = book_model.objects.all()
    except Exception as exc:
        logger.warning('books_for_display query failed: %s', exc)
        return [], [], str(exc)

    for book in qs:
        try:
            title = getattr(book, 'title', None)
            if not title:
                continue
            if author_model is not None:
                try:
                    author = getattr(book, 'author', None)
                    if author is None and getattr(book, 'author_id', None):
                        author = author_model.objects.filter(pk=book.author_id).first()
                    if author is None:
                        continue
                    _ = author.name
                except Exception:
                    continue
            books.append(book)
            cat = getattr(book, 'category', None)
            if cat:
                categories.add(cat)
        except Exception as exc:
            logger.warning('Skipping book id=%s: %s', getattr(book, 'pk', '?'), exc)
            continue
    return books, sorted(categories), None


def rentals_for_admin(rental_model, status_filter):
    """Load rentals for admin tables without select_related (Djongo-safe)."""
    rows = []
    allowed = None
    simple_filter = dict(status_filter)
    if 'rental_status__in' in simple_filter:
        allowed = set(simple_filter.pop('rental_status__in'))
    try:
        qs = rental_model.objects.filter(**simple_filter).order_by('-rented_at')
    except Exception as exc:
        logger.warning('rentals_for_admin failed: %s', exc)
        return rows
    for rental in qs:
        try:
            if allowed is not None and getattr(rental, 'rental_status', None) not in allowed:
                continue
            if getattr(rental, 'user_id', None):
                _ = rental.user
            if getattr(rental, 'book_id', None):
                _ = rental.book
            rows.append(rental)
        except Exception as exc:
            logger.warning('Skipping rental id=%s: %s', getattr(rental, 'pk', '?'), exc)
    return rows
