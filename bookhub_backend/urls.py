from django.contrib import admin
from django.urls import path, include
from django.conf.urls.i18n import i18n_patterns

urlpatterns = [
    path('i18n/', include('django.conf.urls.i18n')), # For setting language
]

urlpatterns += i18n_patterns(
    path('admin/', admin.site.urls),          # The built-in Database Admin
    path('', include('library.urls')),        # Your custom HTML pages
    prefix_default_language=True, # Set to True for rock-solid reliability during presentations
)