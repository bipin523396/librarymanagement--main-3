from django.contrib import admin
from django.urls import path
from library import views  # Make sure this matches your app name
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/chat/', views.chat_api, name='chat_api'),# Default Django admin
    
    # Main Pages
    path('', views.home, name='home'),
    path('index.html', views.home, name='home_html'),
    path('admin-dashboard/', views.admin_dashboard, name='admin_dashboard'),
    path('delivery/', views.delivery_dashboard, name='delivery_dashboard'),
    path('login/', views.login_view, name='login'),
    path('signup/', views.signup_view, name='signup'),
    path('categories/', views.categories_view, name='categories'),
    
    # User Profile Pages
    path('dashboard/', views.dashboard, name='dashboard'),
    path('profile/', views.profile, name='profile'),
    path('settings/', views.settings_view, name='settings'),

    # Delivery Action
    path('update-order-status/', views.update_order_status, name='update_order_status'),

    # Admin Dashboard Actions
    path('admin-dashboard/add-book/', views.add_book, name='add_book'),
    path('admin-dashboard/delete-book/<int:book_id>/', views.delete_book, name='delete_book'),
    path('admin-dashboard/edit-book/<int:book_id>/', views.edit_book, name='edit_book'),
    path('admin-dashboard/add-rider/', views.add_rider, name='add_rider'),
    path('admin-dashboard/assign-order/', views.assign_order, name='assign_order'),
]

# CRITICAL FOR DISPLAYING UPLOADED IMAGES IN DEVELOPMENT
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)