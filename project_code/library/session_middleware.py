"""Restore login when Djongo leaves user.pk empty but session has username."""


class MongoAuthSessionMiddleware:
    """
    Django's session auth hash can fail when user.pk is None on MongoDB.
    Re-load user from _auth_user_id (username or ObjectId) when needed.
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        try:
            authenticated = request.user.is_authenticated
        except Exception:
            authenticated = False

        if not authenticated:
            uid = request.session.get('_auth_user_id')
            backend_path = request.session.get('_auth_user_backend')
            if uid and backend_path:
                from django.contrib.auth import load_backend

                backend = load_backend(backend_path)
                user = backend.get_user(uid)
                if user is not None:
                    request.user = user

        return self.get_response(request)
