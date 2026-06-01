"""Auth backend that loads users safely from MongoDB/Djongo."""

from django.contrib.auth.backends import ModelBackend
from django.contrib.auth import get_user_model

User = get_user_model()


class MongoModelBackend(ModelBackend):
    """Authenticate and reload users from MongoDB without fragile last_login saves."""

    def authenticate(self, request, username=None, password=None, **kwargs):
        if username is None or password is None:
            return None
        login_id = (username or '').strip()
        if not login_id:
            return None
        try:
            user = None
            if '@' in login_id:
                user = User.objects.filter(email=login_id).first()
            if user is None:
                user = User.objects.filter(username=login_id).first()
            if user is None and '@' in login_id:
                user = User.objects.filter(username=login_id).first()
            if user and user.check_password(password) and self.user_can_authenticate(user):
                return user
        except Exception as exc:
            print(f'MongoModelBackend.authenticate error: {exc}')
        return None

    def get_user(self, user_id):
        if user_id is None:
            return None
        candidates = [user_id]
        try:
            candidates.append(int(user_id))
        except (TypeError, ValueError):
            pass
        for pk in candidates:
            try:
                user = User.objects.filter(pk=pk).first()
                if user:
                    return user
            except Exception:
                continue
        return None
