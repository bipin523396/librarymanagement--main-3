"""Auth backend that loads users safely from MongoDB/Djongo."""

from django.contrib.auth.backends import ModelBackend
from django.contrib.auth import get_user_model

User = get_user_model()


def session_user_id(user):
    """Djongo/MongoDB often leaves user.pk as None; use username in session."""
    if user is None:
        return None
    if user.pk is not None:
        return str(user.pk)
    return user.get_username()


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
        uid = str(user_id).strip()
        if not uid or uid == 'None':
            return None

        candidates = [user_id, uid]
        try:
            candidates.append(int(uid))
        except (TypeError, ValueError):
            pass

        for pk in candidates:
            try:
                user = User.objects.filter(pk=pk).first()
                if user:
                    return user
            except Exception:
                continue

        # MongoDB ObjectId hex string (24 chars)
        if len(uid) == 24:
            try:
                from bson import ObjectId
                from pymongo import MongoClient
                from bookhub_backend.mongo_config import get_mongodb_uri

                import os
                uri = get_mongodb_uri()
                if uri:
                    db_name = os.getenv('MONGODB_NAME', 'bookhub_db')
                    doc = MongoClient(uri)[db_name].auth_user.find_one({'_id': ObjectId(uid)})
                    if doc and doc.get('username'):
                        return User.objects.filter(username=doc['username']).first()
            except Exception:
                pass

        # Session stores username when pk is missing (Atlas/Djongo)
        return User.objects.filter(username=uid).first()
