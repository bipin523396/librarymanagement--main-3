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
    path('payment.html', views.payment_view, name='payment'),
    path('payment/', views.payment_view, name='payment_clean'),
    path('book-details.html', views.book_details_view, name='book_details'),
    path('book-details/', views.book_details_view, name='book_details_clean'),
    path('gift.html', views.gift_view, name='gift'),
    path('gift/', views.gift_view, name='gift_clean'),
    path('gift-details.html', views.gift_details_view, name='gift_details'),
    path('gift-details/', views.gift_details_view, name='gift_details_clean'),
    
    # Store Cart & Checkout
    path('cart/', views.view_cart, name='view_cart'),
    path('add-to-cart/<int:book_id>/', views.add_to_cart, name='add_to_cart'),
    path('update-cart/<int:item_id>/', views.update_cart, name='update_cart'),
    path('remove-from-cart/<int:item_id>/', views.remove_from_cart, name='remove_from_cart'),
    path('checkout/', views.checkout, name='checkout'),
    path('payment/<int:order_id>/', views.payment_view, name='payment_with_order'),
    path('process-payment/<int:order_id>/', views.process_payment, name='process_payment'),

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