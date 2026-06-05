import os
import django
import traceback

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'bookhub_backend.settings')
django.setup()

from django.template.loader import render_to_string

try:
    print("Rendering admin.html with full context...")
    out = render_to_string('admin.html', {
        'total_books': 0,
        'active_members': 0,
        'pending_orders': 0,
        'low_stock_count': 0,
        'books': [],
        'authors': [],
        'riders': [],
        'orders': [],
        'members': [],
        'live_rentals': [],
        'history_rentals': [],
        'payments': [],
        'assigned_deliveries': [],
        'messages': [],
        'settings': None,
        'delivery_staff': []
    })
    print("Render successful. Length:", len(out))
except Exception as e:
    print("Error rendering full context:")
    traceback.print_exc()

try:
    print("Rendering admin.html with fallback context...")
    out2 = render_to_string('admin.html', {'total_books': 0})
    print("Render fallback successful. Length:", len(out2))
except Exception as e:
    print("Error rendering fallback context:")
    traceback.print_exc()

