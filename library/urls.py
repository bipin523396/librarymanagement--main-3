from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('admin-dashboard/', views.admin_dashboard, name='admin_dashboard'),
    path('delivery/', views.delivery_dashboard, name='delivery_dashboard'),
    
    # ADD THESE PATHS:
    path('login/', views.login_view, name='login'),
    path('signup/', views.signup_view, name='signup'),
    path('categories/', views.categories_view, name='categories'),
]