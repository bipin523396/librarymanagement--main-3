from django.contrib import admin
from django.urls import path, include
from django.conf.urls.i18n import i18n_patterns
from library.views import home

urlpatterns = [
    path('i18n/', include('django.conf.urls.i18n')),
    path('', home, name='home'),
]

urlpatterns += i18n_patterns(
    path('admin/', admin.site.urls),
    path('library/', include('library.urls')), # Moved the main app to /library/ or kept at root if needed
    prefix_default_language=True,
)