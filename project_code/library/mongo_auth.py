"""Session login helpers for Djongo/MongoDB (user.pk often None)."""


def mongo_session_key(user):
    """Value stored in session['_auth_user_id'] — always username or email, never pk."""
    if user is None:
        return None
    return (user.get_username() or getattr(user, 'email', None) or '').strip() or None


def mongo_session_login(request, user):
    """Log in without django.contrib.auth.login() (avoids integer pk validation)."""
    key = mongo_session_key(user)
    if not key:
        raise ValueError('User has no username or email for session')
    request.session['_auth_user_id'] = key
    request.session.pop('_auth_user_hash', None)
    request.session.pop('_auth_user_backend', None)
    request.user = user


def mongo_session_logout(request):
    request.session.flush()
