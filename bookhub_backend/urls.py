from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),          # The built-in Database Admin
    path('accounts/', include('allauth.urls')),  # Django-allauth URLs
    path('', include('library.urls')),        # Your custom HTML pages
]