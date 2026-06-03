"""MongoDB session auth — store username/email in session, never integer user pk."""

from django.contrib.auth import get_user_model
from django.contrib.auth.models import AnonymousUser
from django.utils.functional import SimpleLazyObject


class MongoAuthSessionMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        def get_user():
            # Normalize the stored session value to a string for flexible lookup.
            sid = str(request.session.get('_auth_user_id') or '').strip()
            if not sid:
                return AnonymousUser()

            User = get_user_model()
            try:
                # 1) If sid looks like an integer primary key, try pk lookup
                try:
                    if sid.isdigit():
                        user = User.objects.filter(pk=int(sid)).first()
                        if user:
                            return user
                except Exception:
                    pass

                # 2) Try username lookup
                user = User.objects.filter(username=sid).first()
                if user:
                    return user

                # 3) If it contains '@', try email lookup
                if '@' in sid:
                    user = User.objects.filter(email=sid).first()
                    if user:
                        return user

                # 4) If it's a 24-char hex string, it may be an ObjectId — try DB lookup
                if len(sid) == 24:
                    try:
                        from bson import ObjectId
                        from bookhub_backend.mongo_config import get_shared_client
                        import os

                        client = get_shared_client()
                        if client:
                            db_name = os.getenv('MONGODB_NAME', 'bookhub_db')
                            doc = client[db_name].auth_user.find_one({'_id': ObjectId(sid)})
                            if doc and doc.get('username'):
                                user = User.objects.filter(username=doc['username']).first()
                                if user:
                                    return user
                    except Exception:
                        pass

                return AnonymousUser()
            except Exception:
                return AnonymousUser()

        request.user = SimpleLazyObject(get_user)
        return self.get_response(request)
