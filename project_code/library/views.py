
from django.views.decorators.csrf import csrf_exempt
import json
import uuid
from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse
from .bot_engine import super_ai
from django.http import JsonResponse
from django.utils import timezone
from django.contrib.auth.models import User
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from .models import DeliveryRider, Order, Book, UserProfile, MembershipPlan, Author
from .role_utils import (
    ROLE_ADMIN,
    ROLE_CUSTOMER,
    ROLE_DELIVERY,
    detect_login_role,
    home_url_name_for_role,
)
from .decorators import admin_portal_required, delivery_portal_required, portal_login_required

AUTH_BACKEND = 'library.auth_backend.MongoModelBackend'


def _is_delivery_staff(user):
    if not user.is_authenticated:
        return False
    try:
        return user.deliverystaff.active
    except Exception:
        return False


def _is_delivery_rider(user):
    if not user.is_authenticated:
        return False
    try:
        return bool(user.deliveryrider)
    except Exception:
        return False


# ==========================================
# --- 1. CUSTOMER PAGES ---
# ==========================================

def home(request):
    from .safe_queries import books_for_display
    from .models import Author
    books, categories, err = books_for_display(Book, Author)
    return render(request, "index.html", {
        "books": books,
        "categories": categories,
        "error": err,
    })

def categories_view(request):
    # Support both '?category=' and '?type=' from the URL
    requested_category = request.GET.get('category') or request.GET.get('type')

    # Always pass all books for JS real-time filtering
    all_books = Book.objects.all()
    
    if requested_category:
        page_title = f"{requested_category.capitalize()} Books"
    else:
        page_title = "All Books"

    # Get distinct categories for navigation
    categories = Book.objects.values_list('category', flat=True).distinct()

    context = {
        'all_books': all_books,
        'page_title': page_title,
        'active_category': requested_category,
        'categories': categories,
    }
    return render(request, 'categories.html', context)

# ==========================================
# --- 2. SIGNUP AND LOGIN ---
# ==========================================

def signup_view(request):
    if request.method == "POST":
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        email = request.POST.get('email')
        phone = request.POST.get('phone')
        pincode = request.POST.get('pincode')
        password = request.POST.get('password')

        if User.objects.filter(username=email).exists():
            messages.error(request, "An account with this email already exists.")
            return redirect('signup')

        user = User.objects.create_user(
            username=email, 
            email=email, 
            password=password,
            first_name=first_name,
            last_name=last_name
        )

        UserProfile.objects.create(
            user=user,
            phone=phone,
            pincode=pincode,
            address="Not provided yet"
        )

        original_save = getattr(user, "save", None)
        try:
            user.save = lambda *args, **kwargs: None
            login(request, user, backend=AUTH_BACKEND)
        finally:
            if original_save is not None:
                user.save = original_save

        return redirect('home')

    return render(request, 'signup.html')


def login_view(request):
    if request.user.is_authenticated:
        role = request.session.get('login_role') or detect_login_role(request.user)
        return redirect(home_url_name_for_role(role))

    if request.method == "POST":
        username = request.POST.get('username')
        password = request.POST.get('password')
        
        print(f"DEBUG: Login attempt for username: {username}")

        try:
            user = authenticate(request, username=username, password=password)
        except Exception as e:
            print(f"DEBUG: Authenticate error: {str(e)}")
            user = None
        
        # Fallback: if username was actually an email, lookup the user's real username
        if user is None and '@' in username:
            print(f"DEBUG: Username '{username}' not found, trying as email...")
            try:
                user_obj = User.objects.get(email=username)
                print(f"DEBUG: Found user with email: {user_obj.username}")
                user = authenticate(request, username=user_obj.username, password=password)
            except User.DoesNotExist:
                print(f"DEBUG: No user found with email: {username}")
            except Exception as e:
                print(f"DEBUG: Email fallback error: {str(e)}")

        if user is not None:
            print(f"DEBUG: Authentication successful for: {user.username}")
            try:
                login(request, user, backend=AUTH_BACKEND)
                print(f"DEBUG: login() call successful for: {user.username}")
            except Exception as e:
                print(f"DEBUG: login() call failed: {str(e)}")
                messages.error(request, f"Login failed: {str(e)}")
                return render(request, 'login.html', {'username_value': username})

            login_as = detect_login_role(user)
            request.session['login_role'] = login_as
            request.session['_auth_user_backend'] = AUTH_BACKEND
            from library.auth_backend import session_user_id
            request.session['_auth_user_id'] = session_user_id(user)
            request.session.save()
            if request.POST.get('remember_me'):
                request.session.set_expiry(60 * 60 * 24 * 14)
            else:
                request.session.set_expiry(0)

            next_url = request.POST.get('next') or request.session.get('last_portal_path')
            if next_url and next_url.startswith('/'):
                return redirect(next_url)
            return redirect(home_url_name_for_role(login_as))

        print(f"DEBUG: Authentication failed for: {username}")
        messages.error(request, "Invalid username or password. Check email/username and password.")
        return render(request, 'login.html', {'username_value': username})

    return render(request, 'login.html')

def logout_view(request):
    logout(request)
    return redirect('login')

# ==========================================
# --- 3. ADMIN DASHBOARD ACTIONS ---
# ==========================================

from django.contrib.auth.decorators import login_required, user_passes_test

@admin_portal_required
def admin_dashboard(request):
    request.session['login_role'] = ROLE_ADMIN
    from .models import Rental, Payment, Delivery, ContactMessage, SystemSettings, Author, DeliveryStaff
    from .safe_queries import rentals_for_admin

    try:
        books = list(Book.objects.all().order_by('-id'))
        riders = list(DeliveryRider.objects.all())
        orders = list(Order.objects.filter(status='Pending'))
        try:
            members = list(UserProfile.objects.all())
        except Exception:
            members = []
        low_stock_count = sum(1 for b in books if getattr(b, 'copies_available', 0) <= 2)
        live_rentals = rentals_for_admin(Rental, {'rental_status': Rental.STATUS_PENDING})
        history_rentals = rentals_for_admin(
            Rental,
            {'rental_status__in': [Rental.STATUS_COMPLETED, Rental.STATUS_FAILED]},
        )
        assigned_deliveries = list(Delivery.objects.exclude(status='Pending'))
        context = {
            'total_books': len(books),
            'active_members': len(members),
            'pending_orders': len(orders),
            'low_stock_count': low_stock_count,
            'books': books,
            'authors': Author.objects.all(),
            'riders': riders,
            'orders': orders,
            'members': members,
            'live_rentals': live_rentals,
            'history_rentals': history_rentals,
            'payments': Payment.objects.all().order_by('-created_at'),
            'assigned_deliveries': assigned_deliveries,
            'messages': ContactMessage.objects.all().order_by('-created_at'),
            'settings': SystemSettings.objects.first(),
            'delivery_staff': DeliveryStaff.objects.all(),
        }
        return render(request, 'admin.html', context)
    except Exception as exc:
        import traceback
        traceback.print_exc()
        messages.error(request, f'Admin dashboard error: {exc}')
        return render(request, 'admin.html', {
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
            'delivery_staff': [],
        })

@admin_portal_required
def assign_delivery(request, rental_id):
    from django.urls import reverse
    from .models import Rental, Delivery, DeliveryStaff
    rental = get_object_or_404(Rental, id=rental_id)
    delivery_boys = [staff for staff in DeliveryStaff.objects.all() if staff.active]

    if request.method == 'POST':
        delivery_staff_id = request.POST.get('delivery_person')
        if delivery_staff_id:
            try:
                delivery_staff = DeliveryStaff.objects.get(id=int(delivery_staff_id))
                
                delivery, _created = Delivery.objects.get_or_create(rental=rental)
                Delivery.objects.filter(pk=delivery.pk).update(
                    delivery_person_id=delivery_staff.user_id,
                    status='Assigned',
                )

                updated = Rental.set_status(rental.pk, Rental.STATUS_ASSIGNED)
                if not updated:
                    messages.error(request, 'Could not update rental status. Try again.')
                    return redirect(reverse('admin_dashboard') + '#live-rental-management')
                
                messages.success(request, f"Delivery assigned to {delivery_staff.user.username}")
            except DeliveryStaff.DoesNotExist:
                messages.error(request, "Selected delivery staff does not exist.")
            except Exception as e:
                import traceback
                print(traceback.format_exc())
                messages.error(request, f"Error: {str(e)}")
        else:
            messages.error(request, "Please select a delivery person.")
                
        return redirect(reverse('admin_dashboard') + '#live-rental-management')

    return render(request, 'assign_delivery.html', {
        'rental': rental,
        'delivery_boys': delivery_boys
    })

@portal_login_required
def update_delivery_status(request, delivery_id):
    from django.urls import reverse
    from .models import Delivery, Rental
    if request.method == 'POST':
        delivery = get_object_or_404(Delivery, id=delivery_id)
        new_status = request.POST.get('status')
        if new_status:
            Delivery.objects.filter(pk=delivery.pk).update(status=new_status)

            rental_id = delivery.rental_id
            if new_status == 'Delivered':
                Rental.set_status(rental_id, Rental.STATUS_COMPLETED, returned=True)
            elif new_status in ('Cancelled', 'Failed'):
                Rental.set_status(rental_id, Rental.STATUS_FAILED)
            # Keep rental_status Assigned during Picked Up / Out For Delivery

            messages.success(request, "Delivery status updated!")

    if _is_delivery_staff(request.user):
        return redirect('delivery_dashboard')
    return redirect(reverse('admin_dashboard') + '#history-rental-management')

def add_delivery_staff(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        phone = request.POST.get('phone')
        vehicle = request.POST.get('vehicle')
        
        if User.objects.filter(username=username).exists():
            messages.error(request, 'Username already exists!')
        else:
            # Create user with is_staff=True
            user = User.objects.create_user(username=username, password=password)
            user.is_staff = True
            user.save()
            
            # Create linked DeliveryStaff
            from .models import DeliveryStaff
            DeliveryStaff.objects.create(
                user=user,
                phone=phone,
                vehicle_number=vehicle
            )
            messages.success(request, f'Delivery staff {username} added successfully!')
    return redirect(reverse('admin_dashboard') + '#delivery-staff-management')

def add_admin(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')
        first_name = request.POST.get('first_name', '')
        last_name = request.POST.get('last_name', '')
        
        user_exists = User.objects.filter(username=email).first() or User.objects.filter(email=email).first()
        
        if user_exists:
            # Upgrade existing user to admin
            user_exists.is_superuser = True
            user_exists.is_staff = True
            user_exists.first_name = first_name
            user_exists.last_name = last_name
            user_exists.set_password(password)
            user_exists.save()
            messages.success(request, f'Existing account {email} was successfully upgraded to Admin!')
        else:
            # Create superuser using email as username
            user = User.objects.create_superuser(username=email, password=password, email=email)
            user.first_name = first_name
            user.last_name = last_name
            user.save()
            messages.success(request, f'New Admin {first_name} {last_name} ({email}) created successfully!')
    return redirect(reverse('admin_dashboard') + '#settings-management')

def resolve_message(request, message_id):
    from .models import ContactMessage
    if request.method == 'POST':
        msg = get_object_or_404(ContactMessage, id=message_id)
        msg.status = 'Resolved'
        msg.save()
        messages.success(request, 'Message marked as resolved.')
    return redirect(reverse('admin_dashboard') + '#contact-management')

def add_book(request):
    if request.method == 'POST':
        title = request.POST.get('title')
        author_id = request.POST.get('author_id')
        category = request.POST.get('category')
        isbn = request.POST.get('isbn')
        copies = request.POST.get('copies', 1)
        image_file = request.FILES.get('image') 
        
        # Check if ISBN already exists
        if Book.objects.filter(isbn=isbn).exists():
            messages.error(request, f"Error: A book with ISBN '{isbn}' already exists in the inventory.")
            return redirect('admin_dashboard')

        try:
            author_instance = Author.objects.get(id=author_id)
            Book.objects.create(
                title=title,
                author=author_instance,
                category=category,
                isbn=isbn,
                copies_total=copies,
                copies_available=copies,
                image=image_file 
            )
            messages.success(request, f"Success: '{title}' has been added to the inventory.")
        except Exception as e:
            messages.error(request, f"Error adding book: {str(e)}")
            
    return redirect('admin_dashboard')


def add_author(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        bio = request.POST.get('bio')
        genres = request.POST.get('genres')
        nationality = request.POST.get('nationality')
        image = request.FILES.get('image')
        
        from django.utils.text import slugify
        slug = slugify(name)
        
        if Author.objects.filter(slug=slug).exists():
            # append a suffix if slug exists
            import random
            slug = f"{slug}-{random.randint(1000, 9999)}"
            
        try:
            Author.objects.create(
                name=name,
                slug=slug,
                bio=bio,
                genres=genres,
                nationality=nationality,
                image=image
            )
            messages.success(request, f"Success: Author '{name}' has been added.")
        except Exception as e:
            messages.error(request, f"Error adding author: {str(e)}")
            
    return redirect('admin_dashboard')


def edit_book(request, book_id):
    book = get_object_or_404(Book, id=book_id)
    
    if request.method == 'POST':
        new_isbn = request.POST.get('isbn')
        
        # Check if ISBN already exists on ANOTHER book
        if Book.objects.filter(isbn=new_isbn).exclude(id=book_id).exists():
            messages.error(request, f"Error: Cannot update. ISBN '{new_isbn}' is already assigned to another book.")
            return redirect('admin_dashboard')

        try:
            book.title = request.POST.get('title')
            author_id = request.POST.get('author')
            if author_id:
                book.author = Author.objects.get(id=author_id)
            book.category = request.POST.get('category')
            book.isbn = new_isbn
            
            if request.FILES.get('image'):
                book.image = request.FILES.get('image')
            
            # Adjust copies_available based on total change
            old_total = book.copies_total
            new_total = int(request.POST.get('copies', old_total))
            difference = new_total - old_total
            
            book.copies_total = new_total
            book.copies_available = book.copies_available + difference
            
            book.save()
            messages.success(request, f"Success: '{book.title}' has been updated.")
        except Exception as e:
            messages.error(request, f"Error updating book: {str(e)}")

    return redirect('admin_dashboard')


def delete_book(request, book_id):
    book = get_object_or_404(Book, id=book_id)
    book.delete()
    return redirect('admin_dashboard')


def add_rider(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        phone = request.POST.get('phone')
        vehicle_details = request.POST.get('vehicle_details')
        username = request.POST.get('username') 
        
        user, created = User.objects.get_or_create(username=username, defaults={'first_name': name})
        if created:
            user.set_password('defaultpassword123')
            user.save()
        
        DeliveryRider.objects.get_or_create(
            user=user,
            defaults={'phone': phone, 'vehicle_details': vehicle_details, 'status': 'Offline'}
        )
    return redirect('admin_dashboard')


def assign_order(request):
    if request.method == 'POST':
        order_id = request.POST.get('order_id')
        rider_id = request.POST.get('rider_id')
        
        order = get_object_or_404(Order, id=order_id)
        rider = get_object_or_404(DeliveryRider, id=rider_id)
        
        order.assigned_rider = rider
        order.status = 'Assigned'
        order.save()
        
    return redirect('admin_dashboard')

# ==========================================
# --- 4. DELIVERY DASHBOARD ACTIONS ---
# ==========================================

@delivery_portal_required
def delivery_dashboard(request):
    request.session['login_role'] = ROLE_DELIVERY
    from .models import Delivery, DeliveryStaff, DeliveryRider, Order, Rental
    from .safe_queries import split_deliveries_for_dashboard

    rider = None
    active_deliveries = []
    history_deliveries = []

    try:
        try:
            rider = DeliveryStaff.objects.get(user_id=request.user.pk)
        except DeliveryStaff.DoesNotExist:
            rider = None

        if rider is not None:
            try:
                deliveries = Delivery.objects.filter(delivery_person_id=request.user.pk)
            except Exception as exc:
                print('DELIVERY DASHBOARD ERROR:', exc)
                deliveries = []

            active_deliveries, history_deliveries = split_deliveries_for_dashboard(
                deliveries, Rental, assigned_status='assigned',
            )

        # Legacy orders (optional)
        try:
            rider_old = DeliveryRider.objects.get(user=request.user)
            if rider is None:
                rider = rider_old
            for o in Order.objects.filter(assigned_rider=rider_old):
                try:
                    template_status = o.status
                    if o.status == 'Out for Delivery':
                        template_status = 'Out For Delivery'
                    customer_user = getattr(getattr(o, 'customer', None), 'user', None)
                    if o.status in ('Pending', 'Assigned', 'Out for Delivery') and customer_user:
                        active_deliveries.append({
                            'id': o.order_id,
                            'tracking_id': o.order_id,
                            'status': template_status,
                            'rental': {'user': customer_user, 'book': o.book},
                            'is_legacy': True,
                        })
                    elif customer_user:
                        history_deliveries.append({
                            'id': o.order_id,
                            'tracking_id': o.order_id,
                            'status': template_status,
                            'rental': {'user': customer_user, 'book': o.book},
                            'is_legacy': True,
                        })
                except Exception as exc:
                    print('DELIVERY DASHBOARD ERROR:', exc)
                    continue
        except DeliveryRider.DoesNotExist:
            pass

        return render(request, 'deliveryman.html', {
            'rider': rider,
            'assigned_orders': active_deliveries,
            'history_orders': history_deliveries,
            'debug_info': (
                f'Found {len(active_deliveries)} active and {len(history_deliveries)} '
                f'history orders for user {request.user.username}'
            ),
        })
    except Exception as exc:
        import traceback
        traceback.print_exc()
        return render(request, 'deliveryman.html', {
            'rider': rider,
            'assigned_orders': [],
            'history_orders': [],
            'debug_info': f'Dashboard safe mode: {exc}',
        })


def update_order_status(request):
    if request.method == "POST":
        order_id = request.POST.get('order_id')
        new_status = request.POST.get('status')
        
        order = get_object_or_404(Order, order_id=order_id)
        valid_statuses = [choice[0] for choice in Order.STATUS_CHOICES]
        
        if new_status in valid_statuses:
            order.status = new_status
            if new_status in ['Completed', 'Cancelled']:
                order.completed_at = timezone.now()
            order.save()
            return JsonResponse({'status': 'success', 'new_status': new_status})
        return JsonResponse({'status': 'error', 'message': 'Invalid status.'}, status=400)
    return JsonResponse({'status': 'error', 'message': 'Invalid request.'}, status=405)
    
def render_liveness(request):
    """Fast liveness probe — no DB (Render health check must not fail on Mongo)."""
    return JsonResponse({'status': 'ok', 'service': 'bookhub'})


def health_check(request):
    """App health + optional MongoDB status (?db=1)."""
    from bookhub_backend.mongo_config import get_mongodb_uri, mongodb_username_from_uri
    payload = {'status': 'ok', 'service': 'bookhub'}
    if request.GET.get('db') != '1':
        return JsonResponse(payload)

    db_status = 'unknown'
    uri = get_mongodb_uri()
    try:
        from pymongo import MongoClient
        if uri:
            MongoClient(uri, serverSelectionTimeoutMS=8000).admin.command('ping')
            db_status = 'connected'
        else:
            db_status = 'no_uri'
    except Exception as exc:
        msg = str(exc).lower()
        if 'authentication failed' in msg or 'bad auth' in msg:
            db_status = 'auth_failed'
        else:
            db_status = f'error: {exc.__class__.__name__}'
    payload['database'] = db_status
    payload['mongo_user'] = mongodb_username_from_uri(uri)
    return JsonResponse(payload)


def test_db_connection(request):
    from django.conf import settings
    from bookhub_backend.mongo_config import get_mongodb_uri, mongodb_username_from_uri, mask_mongodb_uri
    try:
        from pymongo import MongoClient
        uri = get_mongodb_uri()
        if not uri:
            return JsonResponse({'status': 'error', 'message': 'MONGODB_URI not set on server'}, status=500)
        MongoClient(uri, serverSelectionTimeoutMS=10000).admin.command('ping')
        from .models import Book
        count = Book.objects.count()
        return JsonResponse({
            'status': 'success',
            'message': f'Connected to DB. Book count: {count}',
            'mongo_user': mongodb_username_from_uri(uri),
        })
    except Exception as e:
        payload = {
            'status': 'error',
            'message': str(e) or 'Database connection failed',
            'mongo_user': mongodb_username_from_uri(uri),
            'uri_preview': mask_mongodb_uri(uri),
        }
        if settings.DEBUG:
            import traceback
            payload['traceback'] = traceback.format_exc()
        if 'authentication failed' in str(e).lower() or 'bad auth' in str(e).lower():
            from bookhub_backend.mongo_config import mongodb_uri_diagnostics
            payload['hints'] = mongodb_uri_diagnostics(uri)
        return JsonResponse(payload, status=500)

@csrf_exempt
def chat_api(request):
    if request.method == "POST":
        try:
            print(f"DEBUG: Chat API received: {request.body}")
            data = json.loads(request.body)
            user_message = data.get('message', '')
            has_image = data.get('has_image', False)
            
            bot_response = super_ai(user_message, has_image=has_image)
            return JsonResponse({'status': 'success', 'response': bot_response})
        except Exception as e:
            import traceback
            print(f"DEBUG: Chat API Error: {str(e)}")
            print(traceback.format_exc())
            return JsonResponse({'status': 'error', 'message': str(e)}, status=400)
    return JsonResponse({'status': 'error', 'message': 'Invalid request method'}, status=405)

@login_required
def dashboard(request):
    from .models import Book, Payment, Wishlist
    
    # Get active rentals for this user
    try:
        profile = UserProfile.objects.get(user=request.user)
        orders = Order.objects.filter(customer=profile).order_by('-created_at')
    except UserProfile.DoesNotExist:
        orders = []
    
    # Split into active and completed
    active_orders = [o for o in orders if o.status not in ['Completed', 'Cancelled']]
    past_orders = [o for o in orders if o.status in ['Completed', 'Cancelled']]
    
    # Get payments for this user
    payments = Payment.objects.filter(user=request.user).order_by('-created_at')[:5]
    
    # Get wishlist
    wishlist = Wishlist.objects.filter(user=request.user).first()
    wishlist_books = wishlist.books.all() if wishlist else []
    
    context = {
        'active_orders': active_orders,
        'past_orders': past_orders,
        'payments': payments,
        'wishlist_books': wishlist_books,
        'total_rented': len(orders),
    }
    return render(request, 'dashboard.html', context)

@login_required
def profile(request):
    profile, created = UserProfile.objects.get_or_create(user=request.user)
    
    if request.method == "POST":
        request.user.first_name = request.POST.get('first_name', '')
        request.user.last_name = request.POST.get('last_name', '')
        # Django's user model email is also tied to username in our signup flow
        # But we'll just update first and last name for now to be safe
        request.user.save()
        
        profile.phone = request.POST.get('phone', '')
        profile.address = request.POST.get('address', '')
        profile.pincode = request.POST.get('pincode', '')
        profile.save()
        
        messages.success(request, "Your profile has been successfully updated.")
        return redirect('profile')
        
    return render(request, 'profile.html', {'profile': profile})

from django.contrib.auth.decorators import login_required
from django.urls import reverse
import uuid
from .models import Cart, CartItem, Wishlist, Subscription, Payment, Order, UserProfile, Book

# --- NEW VIEW FUNCTIONS ---

@login_required
def book_detail(request, id):
    book = get_object_or_404(Book, id=id)
    return render(request, 'book_detail.html', {'book': book})

@login_required
def rent_book(request, id):
    # Add to cart then go to payment page
    return add_to_cart(request, id)

@login_required
def add_to_cart(request, id):
    book = get_object_or_404(Book, id=id)
    cart, created = Cart.objects.get_or_create(user=request.user)
    cart_item, created = CartItem.objects.get_or_create(cart=cart, book=book)
    if not created:
        cart_item.quantity += 1
        cart_item.save()
    messages.success(request, f"Added '{book.title}' to your cart.")
    return redirect('view_cart')

@login_required
def view_cart(request):
    cart = Cart.objects.filter(user=request.user).first()
    items = cart.cartitem_set.all() if cart else []
    total = sum(item.book.price_per_day * item.quantity for item in items)
    return render(request, 'cart.html', {'items': items, 'total': total})

@login_required
def add_to_wishlist(request, id):
    book = get_object_or_404(Book, id=id)
    wishlist, created = Wishlist.objects.get_or_create(user=request.user)
    wishlist.books.add(book)
    messages.success(request, f"Added '{book.title}' to your wishlist.")
    return redirect('view_wishlist')

@login_required
def view_wishlist(request):
    wishlist = Wishlist.objects.filter(user=request.user).first()
    books = wishlist.books.all() if wishlist else []
    return render(request, 'wishlist.html', {'books': books})

def books_by_category(request, slug):
    books = Book.objects.filter(category__iexact=slug)
    return render(request, 'categories.html', {'books': books, 'page_title': f"{slug.capitalize()} Books", 'active_category': slug})

def books_by_author(request, slug):
    from .models import Author
    
    # Try to find a proper Author profile
    author_profile = None
    try:
        author_profile = Author.objects.get(slug=slug)
        # Filter books by Author object
        books = Book.objects.filter(author=author_profile)
    except Author.DoesNotExist:
        # Fallback: use slug as a name search (replace hyphens with spaces)
        author_name = slug.replace('-', ' ')
        books = Book.objects.filter(author__name__icontains=author_name)
    
    return render(request, 'author_detail.html', {
        'author_profile': author_profile,
        'author_slug': slug,
        'author_name': author_profile.name if author_profile else slug.replace('-', ' ').title(),
        'books': books,
    })

@login_required
def select_plan(request, plan):
    # plan is 'free' or 'premium'
    try:
        membership = MembershipPlan.objects.get(name__iexact=plan)
    except MembershipPlan.DoesNotExist:
        messages.error(request, "Invalid plan selected.")
        return redirect('settings')
    subscription, created = Subscription.objects.get_or_create(user=request.user, defaults={'plan': membership, 'active': plan != 'free'})
    if not created:
        subscription.plan = membership
        subscription.active = plan != 'free'
        subscription.save()
    messages.success(request, f"Subscribed to {plan.title()} plan.")
    return redirect('settings')

@login_required
def payment_page(request):
    cart = Cart.objects.filter(user=request.user).first()
    if not cart:
        messages.error(request, "Your cart is empty.")
        return redirect('view_cart')
    items = cart.cartitem_set.all()
    total_amount = sum(item.book.price_per_day * item.quantity for item in items)
    reference_id = str(uuid.uuid4())
    payment = Payment.objects.create(user=request.user, amount=total_amount, reference_id=reference_id, status='initiated')
    # In a real app, integrate with Stripe/Razorpay here.
    return render(request, 'payment.html', {'payment': payment, 'total': total_amount})

def payment_callback(request):
    # Dummy callback – in real case verify provider response.
    ref = request.GET.get('ref')
    try:
        payment = Payment.objects.get(reference_id=ref)
        payment.status = 'success'
        payment.save()
        # Create order(s) from cart
        cart = Cart.objects.filter(user=payment.user).first()
        if cart:
            for item in cart.cartitem_set.all():
                # Generate unique order ID
                order_id = str(uuid.uuid4())[:20]
                # Get or create UserProfile for the user
                profile, _ = UserProfile.objects.get_or_create(user=payment.user)
                Order.objects.create(
                    order_id=order_id,
                    customer=profile,
                    book=item.book,
                    order_type='Delivery Only',
                    status='pending'
                )
            cart.delete()
        messages.success(request, "Payment successful and order placed.")
        return redirect('admin_dashboard')
    except Payment.DoesNotExist:
        messages.error(request, "Invalid payment reference.")
        return redirect('view_cart')

@login_required
def checkout_view(request):
    return render(request, 'checkout.html')

@csrf_exempt
@login_required
def process_checkout(request):
    if request.method == "POST":
        try:
            print(f"DEBUG: Process Checkout received: {request.body}")
            data = json.loads(request.body)
            book_id = data.get('book_id')
            duration = data.get('duration')
            total = data.get('total')
            payment_method = data.get('payment_method')
            
            book = Book.objects.get(id=book_id)
            profile, _ = UserProfile.objects.get_or_create(user=request.user)
            
            # Generate unique order ID
            order_id = "RNT-" + str(uuid.uuid4())[:8].upper()
            
            # Create Order
            order = Order.objects.create(
                order_id=order_id,
                customer=profile,
                book=book,
                order_type='Delivery Only',
                status='Pending'
            )
            
            # Create Payment record
            Payment.objects.create(
                user=request.user,
                order=order,
                amount=total,
                reference_id=str(uuid.uuid4()),
                payment_type=payment_method,
                status='success' # Mocking instant success
            )
            
            # Calculate return date
            from datetime import timedelta
            return_date = timezone.now() + timedelta(days=int(duration))
            
            # Create Rental and Delivery entries for the professional workflow
            from .models import Rental, Delivery
            rental = Rental.objects.create(
                user=request.user,
                book=book,
                duration_days=int(duration),
                total_amount=total,
                payment_status='Paid',
                rental_status='Pending',
                due_date=return_date.date()
            )
            Delivery.objects.create(rental=rental)
            
            print(f"DEBUG: Checkout successful for Order ID: {order_id}")
            return JsonResponse({
                'status': 'success',
                'order_id': order_id,
                'return_date': return_date.strftime("%B %d, %Y")
            })
            
        except Exception as e:
            import traceback
            print(f"DEBUG: Checkout Error: {str(e)}")
            print(traceback.format_exc())
            return JsonResponse({'status': 'error', 'message': str(e)}, status=400)
    return JsonResponse({'status': 'error', 'message': 'Invalid method'}, status=405)

@login_required
def checkout_success(request):
    order_id = request.GET.get('order_id')
    return_date = request.GET.get('return_date')
    return render(request, 'checkout_success.html', {
        'order_id': order_id,
        'return_date': return_date
    })

from datetime import date, timedelta

@login_required
def payment_success(request, book_id):
    book = get_object_or_404(Book, id=book_id)
    duration = 7
    total = 105
    
    from .models import Rental, Delivery
    rental = Rental.objects.create(
        user=request.user,
        book=book,
        duration_days=duration,
        total_amount=total,
        payment_status='Paid',
        rental_status='Pending',
        due_date=date.today() + timedelta(days=duration)
    )
    Delivery.objects.create(rental=rental)
    return redirect('my_rentals')

@login_required
def my_rentals(request):
    from .models import Rental
    rentals = Rental.objects.filter(user=request.user).select_related('book', 'delivery').order_by('-rented_at')
    return render(request, 'my_rentals.html', {'rentals': rentals})

@login_required
def track_order(request, delivery_id):
    from .models import Delivery, DeliveryStaff
    delivery = get_object_or_404(Delivery, id=delivery_id)
    
    # Ensure the user owns this rental
    if delivery.rental.user != request.user:
        messages.error(request, "Unauthorized access.")
        return redirect('my_rentals')
        
    rider_profile = None
    if delivery.delivery_person:
        try:
            rider_profile = DeliveryStaff.objects.get(user=delivery.delivery_person)
        except DeliveryStaff.DoesNotExist:
            pass
            
    return render(request, 'track_order.html', {
        'delivery': delivery,
        'rider_profile': rider_profile
    })

@login_required
def premium_checkout(request):
    return render(request, 'premium_checkout.html')

@csrf_exempt
@login_required
def activate_premium(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            plan_name = data.get('plan', 'Premium')
            amount = data.get('amount', 500)
            
            # Get or create profile
            profile, _ = UserProfile.objects.get_or_create(user=request.user)
            
            # Get or create the membership plan
            plan, _ = MembershipPlan.objects.get_or_create(
                name=plan_name,
                defaults={'price': amount, 'max_books_at_a_time': 10 if plan_name == 'Premium' else 2}
            )
            profile.membership = plan
            
            # Set expiry date to 30 days from now
            from datetime import timedelta
            profile.membership_expiry = (timezone.now() + timedelta(days=30)).date()
            profile.save()
            
            # Record payment
            Payment.objects.create(
                user=request.user,
                amount=amount,
                reference_id='PREM-' + str(uuid.uuid4())[:8].upper(),
                status='success'
            )
            
            return JsonResponse({
                'status': 'success',
                'plan': plan_name,
                'expiry': profile.membership_expiry.strftime('%B %d, %Y')
            })
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)}, status=400)
    return JsonResponse({'status': 'error', 'message': 'Invalid method'}, status=405)

def search(request):
    query = request.GET.get('q', '')
    books = Book.objects.filter(title__icontains=query) if query else []
    return render(request, 'search_results.html', {'books': books, 'query': query})

def services(request):
    return render(request, 'services.html')

def branches(request):
    return render(request, 'branches.html')

def gift_card(request):
    return render(request, 'gift_card.html')

@login_required
def settings_view(request):
    from .models import UserSettings
    from django.utils import translation
    
    settings, created = UserSettings.objects.get_or_create(user=request.user)

    if request.method == "POST":
        # Check if we're only updating language (from the immediate JS submit)
        # or the full form (including notifications)
        lang_code = request.POST.get("language")
        if lang_code:
            settings.language = lang_code
            
            # Sync with Django's i18n system
            translation.activate(lang_code)
            request.session['_language'] = lang_code
            
        if "notifications" in request.POST or request.method == "POST":
            # If notifications checkbox is missing in POST (because it's unchecked), 
            # and we are doing a full save, set it to False.
            # However, since language change auto-submits, we must distinguish.
            if "notifications_form" in request.POST:
                settings.notifications = request.POST.get("notifications") == "on"
            
        settings.save()
        messages.success(request, "Settings updated!")

    return render(request, "settings.html", {"settings": settings})

def about(request):
    return render(request, 'about.html')

def contact(request):
    return render(request, 'contact.html')

def impact(request):
    return render(request, 'impact.html')

def submit_contact(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        email = request.POST.get('email')
        subject = request.POST.get('subject')
        message = request.POST.get('message')
        
        from .models import ContactMessage
        ContactMessage.objects.create(
            name=name,
            email=email,
            subject=subject,
            message=message
        )
        messages.success(request, 'Your message has been sent successfully. We will get back to you soon.')
        return redirect('contact')
    return redirect('contact')

def author_list(request):
    from .models import Author
    authors = Author.objects.all()
    return render(request, 'author_list.html', {'authors': authors})
