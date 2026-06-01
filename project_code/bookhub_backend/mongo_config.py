"""MongoDB URI helpers for Render / Atlas."""

import os
import re


def get_mongodb_uri():
    """Prefer MONGODB_URI, fall back to DJANGO_DATABASE_URL."""
    uri = (os.getenv('MONGODB_URI') or os.getenv('DJANGO_DATABASE_URL') or '').strip()
    if not uri:
        return ''
    # Atlas database users often require authSource=admin
    if uri.startswith('mongodb+srv://') and 'authSource=' not in uri:
        sep = '&' if '?' in uri else '?'
        uri = f'{uri}{sep}authSource=admin'
    return uri


def mask_mongodb_uri(uri):
    if not uri:
        return '(not set)'
    return re.sub(r':([^:@/]+)@', ':****@', uri)


def mongodb_username_from_uri(uri):
    if not uri or '://' not in uri:
        return None
    try:
        creds = uri.split('://', 1)[1].split('@', 1)[0]
        return creds.split(':', 1)[0]
    except (IndexError, ValueError):
        return None
