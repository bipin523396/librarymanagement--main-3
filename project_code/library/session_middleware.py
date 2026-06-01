"""MongoDB session auth — store username/email in session, never integer user pk."""

from django.contrib.auth import get_user_model
from django.contrib.auth.models import AnonymousUser
from django.utils.functional import SimpleLazyObject


class MongoAuthSessionMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        def get_user():
            username = request.session.get('_auth_user_id')
            if not username:
                return AnonymousUser()

            User = get_user_model()
            try:
                user = User.objects.filter(username=username).first()
                if user is None:
                    user = User.objects.filter(email=username).first()
                return user if user is not None else AnonymousUser()
            except Exception:
                return AnonymousUser()

        request.user = SimpleLazyObject(get_user)
        return self.get_response(request)
