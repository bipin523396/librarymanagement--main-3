"""Auth backend that loads users safely from MongoDB/Djongo."""

from django.contrib.auth.backends import ModelBackend
from django.contrib.auth import get_user_model

User = get_user_model()


def session_user_id(user):
    """Session key for MongoDB users — always username/email, never pk."""
    from library.mongo_auth import mongo_session_key

    return mongo_session_key(user)


def resolve_user_pk(user, request=None):
    """Primary key for FK lookups when Djongo leaves user.pk empty."""
    if user is None:
        return None
    if user.pk is not None:
        return user.pk

    if request is not None:
        sid = str(request.session.get('_auth_user_id') or '').strip()
        if len(sid) == 24:
            return sid

    try:
        from bookhub_backend.mongo_config import get_shared_client
        import os

        client = get_shared_client()
        if client:
            db_name = os.getenv('MONGODB_NAME', 'bookhub_db')
            doc = client[db_name].auth_user.find_one(
                {'username': user.get_username()},
                projection={'_id': 1},
            )
            if doc and doc.get('_id') is not None:
                return str(doc['_id'])
    except Exception:
        pass

    return None


class MongoModelBackend(ModelBackend):
    """Authenticate and reload users from MongoDB without fragile last_login saves."""

    def _check_password_via_mongo(self, username, password):
        """
        Directly check username+password against MongoDB Atlas when Djongo ORM fails.
        Returns a User object or None.
        """
        try:
            from bookhub_backend.mongo_config import get_shared_client
            from django.contrib.auth.hashers import check_password as django_check_password
            import os

            client = get_shared_client()
            if not client:
                return None
            db_name = os.getenv('MONGODB_NAME', 'bookhub_db')
            db = client[db_name]

            # Try username match, then email match
            doc = db.auth_user.find_one({'username': username})
            if not doc:
                doc = db.auth_user.find_one({'email': username})
            if not doc:
                return None

            stored_hash = doc.get('password', '')
            if not stored_hash:
                return None
            if not django_check_password(password, stored_hash):
                return None
            if not doc.get('is_active', True):
                return None

            # Auth OK — load or create a User object from ORM
            real_username = doc.get('username', username)
            user = User.objects.filter(username=real_username).first()
            if user is None:
                user = User.objects.filter(email=real_username).first()
            if user is None:
                # Build an in-memory User so session login can proceed
                user = User(
                    username=real_username,
                    email=doc.get('email', ''),
                    first_name=doc.get('first_name', ''),
                    last_name=doc.get('last_name', ''),
                    is_superuser=bool(doc.get('is_superuser', False)),
                    is_staff=bool(doc.get('is_staff', False)),
                    is_active=bool(doc.get('is_active', True)),
                )
            else:
                # Sync flags from MongoDB → ORM object (in memory only, no save)
                user.is_superuser = bool(doc.get('is_superuser', user.is_superuser))
                user.is_staff = bool(doc.get('is_staff', user.is_staff))
                user.is_active = bool(doc.get('is_active', True))
            return user
        except Exception as exc:
            print(f'MongoModelBackend._check_password_via_mongo error: {exc}')
            return None

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
            print(f'MongoModelBackend.authenticate ORM error: {exc}')

        # Fallback: check password directly against MongoDB Atlas document
        # This handles cases where Djongo ORM returns stale/empty password hash
        print(f'MongoModelBackend: ORM auth failed for {login_id!r}, trying direct MongoDB check...')
        return self._check_password_via_mongo(login_id, password)


    def get_user(self, user_id):
        if user_id is None:
            return None
        uid = str(user_id).strip()
        if not uid or uid == 'None':
            return None

        # Session stores username or email (MongoAuthSessionMiddleware)
        if '@' in uid or not uid.isdigit():
            user = User.objects.filter(username=uid).first()
            if user:
                return user
            return User.objects.filter(email=uid).first()

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
                from bookhub_backend.mongo_config import get_shared_client
                import os
                client = get_shared_client()
                if client:
                    db_name = os.getenv('MONGODB_NAME', 'bookhub_db')
                    doc = client[db_name].auth_user.find_one({'_id': ObjectId(uid)})
                    if doc and doc.get('username'):
                        return User.objects.filter(username=doc['username']).first()
            except Exception:
                pass

        # Session stores username when pk is missing (Atlas/Djongo)
        return User.objects.filter(username=uid).first()
