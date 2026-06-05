import os
import django
import traceback

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'bookhub_backend.settings')
django.setup()

from django.test.client import Client

try:
    c = Client()
    resp = c.post('/en/library/submit-contact/', {
        'name': 'Test',
        'email': 'test@example.com',
        'subject': 'Test',
        'message': 'Test'
    })
    print(f"Post status: {resp.status_code}")
except Exception as e:
    traceback.print_exc()

