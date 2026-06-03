"""MongoDB URI helpers for Render / Atlas. Credentials come from env only — never hardcoded."""

import os
import re
from urllib.parse import quote_plus, unquote, urlparse


def _clean_env(value):
    if not value:
        return ''
    v = value.strip()
    if len(v) >= 2 and v[0] == v[-1] and v[0] in '"\'':
        v = v[1:-1].strip()
    return v


def build_atlas_uri(user, password, cluster, db_name=None):
    """Build mongodb+srv URI from parts (use when MONGODB_USER/PASSWORD set on Render)."""
    user = quote_plus(_clean_env(user))
    password = quote_plus(_clean_env(password))
    cluster = _clean_env(cluster)
    db_name = _clean_env(db_name or os.getenv('MONGODB_NAME', 'bookhub_db'))
    app = _clean_env(os.getenv('MONGODB_APP_NAME', 'Cluster0'))
    return (
        f'mongodb+srv://{user}:{password}@{cluster}/{db_name}'
        f'?retryWrites=true&w=majority&appName={quote_plus(app)}'
    )


def _append_auth_source(uri):
    if uri.startswith('mongodb+srv://') and 'authSource=' not in uri:
        sep = '&' if '?' in uri else '?'
        uri = f'{uri}{sep}authSource=admin'
    return uri


def get_mongodb_uri():
    """Use MONGODB_URI or DJANGO_DATABASE_URL from environment (set on Render)."""
    uri = _clean_env(os.getenv('MONGODB_URI') or os.getenv('DJANGO_DATABASE_URL') or '')
    if not uri:
        user = _clean_env(os.getenv('MONGODB_USER', ''))
        password = _clean_env(os.getenv('MONGODB_PASSWORD', ''))
        cluster = _clean_env(os.getenv('MONGODB_CLUSTER', ''))
        if user and password and cluster:
            uri = build_atlas_uri(user, password, cluster)
    if not uri:
        return ''
    return _append_auth_source(uri)


def mongodb_uri_diagnostics(uri):
    hints = []
    if not uri:
        hints.append('Set MONGODB_URI and DJANGO_DATABASE_URL on Render (same value).')
        return hints
    if '%2540' in uri:
        hints.append('Password may be double-encoded; match Atlas password exactly in the URI.')
    if uri.count('@') > 1:
        hints.append('Too many @ in URI — only encode special chars in the password if needed.')
    if not hints:
        hints.append(
            'Atlas rejected login. Password in Render must match Database Access for bookhub_user.'
        )
    return hints


def mask_mongodb_uri(uri):
    if not uri:
        return '(not set)'
    return re.sub(r':([^:@/]+)@', ':****@', uri)


def mongodb_username_from_uri(uri):
    if not uri or '://' not in uri:
        return None
    try:
        creds = uri.split('://', 1)[1].split('@', 1)[0]
        return unquote(creds.split(':', 1)[0])
    except (IndexError, ValueError):
        return None


_cached_client = None

def get_shared_client():
    """Get a shared, process-global MongoClient instance to prevent connection/socket leaks."""
    global _cached_client
    if _cached_client is None:
        from pymongo import MongoClient
        uri = get_mongodb_uri()
        if not uri:
            return None
        timeout_ms = int(os.getenv('MONGODB_TIMEOUT_MS', '3000'))
        # Set maxPoolSize to 20 to limit connections on Render free tier/Atlas M0
        _cached_client = MongoClient(
            uri,
            maxPoolSize=20,
            minPoolSize=1,
            serverSelectionTimeoutMS=timeout_ms,
            retryWrites=True
        )
    return _cached_client
