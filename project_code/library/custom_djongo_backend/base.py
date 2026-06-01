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
        # Safely close the underlying connection without invoking bool()
        conn = getattr(self, "connection", None)
        if conn is not None:
            try:
                conn.close()
            except Exception:
                # Silently ignore any error during close to prevent migration crashes
                pass
