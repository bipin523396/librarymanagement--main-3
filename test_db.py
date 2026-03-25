import os
import sys
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'bookhub_backend.settings')
django.setup()

from django.db import connection

try:
    connection.ensure_connection()
    print('SUCCESS')
except Exception as e:
    print('ERROR_CLASS:', type(e).__name__)
    print('ERROR_STR:', str(e))
    sys.exit(1)
