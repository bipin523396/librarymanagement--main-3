from django.contrib import admin
from django.urls import path, include
from django.shortcuts import redirect


def home_redirect(request):
    return redirect('/en/library/')


urlpatterns = [
    path('', home_redirect),
    path('admin/', admin.site.urls),
    path('en/library/', include('library.urls')),
]
