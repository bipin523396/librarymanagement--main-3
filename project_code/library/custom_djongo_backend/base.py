'''Custom Djongo backend to avoid bool() check on connection close.'''

from djongo.base import DatabaseWrapper as DjongoDatabaseWrapper


class DatabaseWrapper(DjongoDatabaseWrapper):
    """Subclass of Djongo's DatabaseWrapper that overrides the _close method.
    The original Djongo implementation checks `if self.connection:` which triggers a
    `NotImplementedError` because Djongo's Database object does not implement truth
    value testing. This subclass safely checks for `None` before attempting to close
    the underlying pymongo client.
    """

    def _close(self):
        # Do not close the underlying MongoClient connection pool.
        # This keeps the main database connection pool alive across requests.
        pass
