from django.apps import AppConfig


class LibraryConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'library'

    def ready(self):
        from django.contrib.auth.models import update_last_login
        from django.contrib.auth.signals import user_logged_in

        # MongoDB users may lack a stable PK for last_login updates — disable signal
        try:
            user_logged_in.disconnect(update_last_login)
        except Exception:
            pass
        try:
            user_logged_in.disconnect(dispatch_uid='update_last_login')
        except Exception:
            pass
        print('✅ update_last_login disconnected for MongoDB compatibility')

        # Patch Django's AutoField to support MongoDB ObjectIds
        from django.db.models import AutoField, BigAutoField
        def auto_field_get_prep_value(self, value):
            return value
        AutoField.get_prep_value = auto_field_get_prep_value
        BigAutoField.get_prep_value = auto_field_get_prep_value

        # Patch djongo to not close the PyMongo client per request
        try:
            from djongo.base import DatabaseWrapper
            DatabaseWrapper._close = lambda self: None
        except ImportError:
            pass

        # Patch PyMongo 4.x Collection class for legacy methods used by Djongo
        try:
            from pymongo.collection import Collection
            if not hasattr(Collection, 'update'):
                def legacy_update(self, spec, document, multi=False, **kwargs):
                    if multi:
                        return self.update_many(spec, document, **kwargs)
                    else:
                        return self.update_one(spec, document, **kwargs)
                Collection.update = legacy_update

            if not hasattr(Collection, 'insert'):
                def legacy_insert(self, doc_or_docs, **kwargs):
                    if isinstance(doc_or_docs, list):
                        return self.insert_many(doc_or_docs, **kwargs)
                    else:
                        return self.insert_one(doc_or_docs, **kwargs)
                Collection.insert = legacy_insert

            if not hasattr(Collection, 'remove'):
                def legacy_remove(self, spec_or_id=None, **kwargs):
                    if spec_or_id is None:
                        spec_or_id = {}
                    if isinstance(spec_or_id, dict):
                        return self.delete_many(spec_or_id, **kwargs)
                    else:
                        return self.delete_one({'_id': spec_or_id}, **kwargs)
                Collection.remove = legacy_remove
        except Exception:
            pass

        # Patch MongoClient.close was removed to avoid socket leaks on manual clients
        pass

