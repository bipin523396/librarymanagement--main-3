"""MongoDB URI helpers for Render / Atlas."""

import os
import re
from urllib.parse import quote_plus, unquote, urlparse

# Atlas defaults (override with env on Render). Password @ is encoded when building URI.
ATLAS_USER = 'bookhub_user'
ATLAS_PASSWORD = '@Sagarmatha321'
ATLAS_CLUSTER = 'cluster0.3f7teqs.mongodb.net'
ATLAS_DB_NAME = 'bookhub_db'


def _clean_env(value):
    if not value:
        return ''
    v = value.strip()
    # Render copy/paste sometimes wraps the whole URI in quotes.
    if len(v) >= 2 and v[0] == v[-1] and v[0] in '"\'':
        v = v[1:-1].strip()
    return v


def build_atlas_uri(
    user=None,
    password=None,
    cluster=None,
    db_name=None,
):
    """Build mongodb+srv URI with correct URL-encoding for special characters in password."""
    user = quote_plus(_clean_env(user or os.getenv('MONGODB_USER', ATLAS_USER)))
    password = quote_plus(_clean_env(password or os.getenv('MONGODB_PASSWORD', ATLAS_PASSWORD)))
    cluster = _clean_env(cluster or os.getenv('MONGODB_CLUSTER', ATLAS_CLUSTER))
    db_name = _clean_env(db_name or os.getenv('MONGODB_NAME', ATLAS_DB_NAME))
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
    """
    Resolve MongoDB connection string:
    1. MONGODB_URI or DJANGO_DATABASE_URL if set
    2. Else build from MONGODB_USER / MONGODB_PASSWORD / MONGODB_CLUSTER (password @Sagarmatha321)
    """
    uri = _clean_env(os.getenv('MONGODB_URI') or os.getenv('DJANGO_DATABASE_URL') or '')
    if not uri:
        uri = build_atlas_uri()
    return _append_auth_source(uri)


def mongodb_uri_diagnostics(uri):
    """Non-secret hints when Atlas returns bad auth."""
    hints = []
    if not uri:
        hints.append(
            'Set MONGODB_URI and DJANGO_DATABASE_URL, or MONGODB_PASSWORD=@Sagarmatha321 on Render.'
        )
        return hints
    if '%2540' in uri or '%2525' in uri:
        hints.append('Password looks double-encoded (%2540). Use %40 once for @, not %2540.')
    if uri.count('@') > 1:
        hints.append('URI has more than one @ before the host — encode @ in the password as %40.')
    try:
        parsed = urlparse(uri)
        if parsed.password and unquote(parsed.password) != parsed.password and '%40' not in parsed.password:
            hints.append('Password contains encoded characters; confirm they match Atlas exactly.')
    except Exception:
        pass
    if not hints:
        hints.append(
            'Atlas rejected login. Confirm user bookhub_user password is @Sagarmatha321 '
            '(or set MONGODB_USER / MONGODB_PASSWORD on Render without URL-encoding).'
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
