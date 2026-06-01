import os
import sys

# Add the project directory to Python path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Set Django settings module
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'bookhub_backend.settings')

# Import Django and setup
import django
django.setup()

from django.core.wsgi import get_wsgi_application
application = get_wsgi_application()
app = application

def handler(event, context):
    return application(event, context)
