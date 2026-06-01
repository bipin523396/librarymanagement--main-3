import os
import sys

# Add the project directory to Python path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Set Django settings module
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'bookhub_backend.settings')

# Import Django and setup
import django
django.setup()

# Import the WSGI application
from bookhub_backend.wsgi import application

# Vercel Python entry point
app = application
