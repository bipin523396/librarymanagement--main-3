"""MongoDB session auth — store username/email in session, never integer user pk."""

from django.contrib.auth import get_user_model
from django.contrib.auth.models import AnonymousUser
from django.utils.functional import SimpleLazyObject


class MongoAuthSessionMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        def get_user():
            # Avoid duplicate lookups in the same request
            if hasattr(request, '_cached_user'):
                return request._cached_user

            sid = str(request.session.get('_auth_user_id') or '').strip()
            if not sid:
                return AnonymousUser()

            User = get_user_model()
            user = None
            try:
                # Optimized lookup strategy: try most likely fields first
                # Use filter().first() to avoid exceptions and potentially use indexes better
                
                # 1) Try username (most common for this app)
                user = User.objects.filter(username=sid).first()
                
                # 2) If not found and sid looks like an email
                if not user and '@' in sid:
                    user = User.objects.filter(email=sid).first()
                
                # 3) If not found and sid is digit (legacy/ORM pk)
                if not user and sid.isdigit():
                    user = User.objects.filter(pk=int(sid)).first()

                # 4) Last resort: MongoDB ObjectId lookup (only if sid is 24-char hex)
                if not user and len(sid) == 24 and all(c in '0123456789abcdef' for c in sid.lower()):
                    try:
                        from bson import ObjectId
                        from bookhub_backend.mongo_config import get_shared_client
                        import os
                        client = get_shared_client()
                        if client:
                            db_name = os.getenv('MONGODB_NAME', 'bookhub_db')
                            doc = client[db_name].auth_user.find_one({'_id': ObjectId(sid)}, {'username': 1})
                            if doc and doc.get('username'):
                                user = User.objects.filter(username=doc['username']).first()
                    except Exception:
                        pass

                final_user = user or AnonymousUser()
                request._cached_user = final_user
                return final_user
            except Exception:
                return AnonymousUser()

        request.user = SimpleLazyObject(get_user)
        return self.get_response(request)
