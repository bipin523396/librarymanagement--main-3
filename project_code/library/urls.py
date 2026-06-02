from django.contrib import admin
from django.urls import path, include
from library import views  # Make sure this matches your app name
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.auth import views as auth_views

urlpatterns = [
# admin path moved to root urls, removed to avoid duplicate namespace
    path('api/chat/', views.chat_api, name='chat_api'),# Default Django admin
    path('health/', views.health_check, name='health_check'),
    path('wake/', views.wake_up, name='wake_up'),
    path('loading/', views.wake_loading_page, name='wake_loading'),
    path('test-db/', views.test_db_connection, name='test_db_connection'),
    path('seed-and-setup/', views.seed_and_setup, name='seed_and_setup'),
    path('setup-admin/', views.setup_admin, name='setup_admin'),
    path('reseed/', views.reseed, name='reseed'),
    
    # Main Pages
    path('', views.home, name='home'),
    path('admin-dashboard/', views.admin_dashboard, name='admin_dashboard'),
    path('delivery/', views.delivery_dashboard, name='delivery_dashboard'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('signup/', views.signup_view, name='signup'),
    path('categories/', views.categories_view, name='categories'),
    
    # User Profile Pages
    path('dashboard/', views.dashboard, name='dashboard'),
    path('profile/', views.profile, name='profile'),
    path('settings/', views.settings_view, name='settings'),

    # Password Reset URLs
    path('password-reset/', 
         auth_views.PasswordResetView.as_view(template_name='password_reset.html', email_template_name='password_reset_email.html'), 
         name='password_reset'),
    path('password-reset/done/', 
         auth_views.PasswordResetDoneView.as_view(template_name='password_reset_done.html'), 
         name='password_reset_done'),
    path('password-reset-confirm/<uidb64>/<token>/', 
         auth_views.PasswordResetConfirmView.as_view(template_name='password_reset_confirm.html'), 
         name='password_reset_confirm'),
    path('password-reset-complete/', 
         auth_views.PasswordResetCompleteView.as_view(template_name='password_reset_complete.html'), 
         name='password_reset_complete'),



    # Delivery Action
    path('update-order-status/', views.update_order_status, name='update_order_status'),

    # Admin Dashboard Actions
    path('admin-dashboard/add-book/', views.add_book, name='add_book'),
    path('admin-dashboard/add-author/', views.add_author, name='add_author'),
    path('admin-dashboard/delete-book/<int:book_id>/', views.delete_book, name='delete_book'),
    path('admin-dashboard/edit-book/<int:book_id>/', views.edit_book, name='edit_book'),
    path('admin-dashboard/add-rider/', views.add_rider, name='add_rider'),
    path('admin-dashboard/assign-order/', views.assign_order, name='assign_order'),
# New backend routes
    path('book/<int:id>/', views.book_detail, name='book_detail'),
    path('rent/<int:id>/', views.rent_book, name='rent_book'),
    path('cart/add/<int:id>/', views.add_to_cart, name='add_to_cart'),
    path('cart/', views.view_cart, name='view_cart'),
    path('wishlist/add/<int:id>/', views.add_to_wishlist, name='add_to_wishlist'),
    path('wishlist/', views.view_wishlist, name='view_wishlist'),
    path('category/<slug:slug>/', views.books_by_category, name='books_by_category'),
    path('author/<slug:slug>/', views.books_by_author, name='books_by_author'),
    path('plan/<str:plan>/', views.select_plan, name='select_plan'),
    path('payment/', views.payment_page, name='payment_page'),
    path('payment/callback/', views.payment_callback, name='payment_callback'),
    path('checkout/', views.checkout_view, name='checkout'),
    path('checkout/process/', views.process_checkout, name='process_checkout'),
    path('checkout/success/', views.checkout_success, name='checkout_success'),
    path('payment-success/<int:book_id>/', views.payment_success, name='payment_success'),
    path('admin-dashboard/assign-delivery/<str:rental_id>/', views.assign_delivery, name='assign_delivery'),
    path('admin-dashboard/update-delivery/<str:delivery_id>/', views.update_delivery_status, name='update_delivery_status'),
    path('admin-dashboard/add-delivery-staff/', views.add_delivery_staff, name='add_delivery_staff'),
    path('admin-dashboard/add-admin/', views.add_admin, name='add_admin'),
    path('admin-dashboard/resolve-message/<int:message_id>/', views.resolve_message, name='resolve_message'),
    path('admin-dashboard/seed-live-data/', views.seed_live_data, name='seed_live_data'),
    path('my-rentals/', views.my_rentals, name='my_rentals'),
    path('track-order/<int:delivery_id>/', views.track_order, name='track_order'),
    path('premium-checkout/', views.premium_checkout, name='premium_checkout'),
    path('premium-checkout/activate/', views.activate_premium, name='activate_premium'),
    path('search/', views.search, name='search'),
    path('services/', views.services, name='services'),
    path('branches/', views.branches, name='branches'),
    path('gift-card/', views.gift_card, name='gift_card'),
    path('about/', views.about, name='about'),
    path('contact/', views.contact, name='contact'),
    path('submit-contact/', views.submit_contact, name='submit_contact'),
    path('impact/', views.impact, name='impact'),
    path('author-list/', views.author_list, name='author_list'),
    ]

# CRITICAL FOR DISPLAYING UPLOADED IMAGES IN DEVELOPMENT
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)