
from django.views.decorators.csrf import csrf_exempt
import json
import uuid
import traceback
from decimal import Decimal
from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse
from .bot_engine import super_ai
from django.http import JsonResponse
from django.utils import timezone
from django.contrib.auth.models import User
from django.contrib import messages
from django.contrib.auth import authenticate
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

        from .mongo_auth import mongo_session_login

        mongo_session_login(request, user)
        request.session['login_role'] = detect_login_role(user)
        request.session.save()

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
            from .mongo_auth import mongo_session_login

            try:
                mongo_session_login(request, user)
                print(f"DEBUG: session login successful for: {user.username}")
            except Exception as e:
                print(f"DEBUG: session login failed: {str(e)}")
                messages.error(request, f"Login failed: {str(e)}")
                return render(request, 'login.html', {'username_value': username})

            login_as = detect_login_role(user)
            request.session['login_role'] = login_as
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
    from .mongo_auth import mongo_session_logout

    mongo_session_logout(request)
    return redirect('login')

# ==========================================
# --- 3. ADMIN DASHBOARD ACTIONS ---
# ==========================================

from django.contrib.auth.decorators import login_required, user_passes_test

@admin_portal_required
def admin_dashboard(request):
    request.session['login_role'] = ROLE_ADMIN
    import os
    from .models import Rental, Payment, Delivery, ContactMessage, SystemSettings, Author, DeliveryStaff, UserProfile
    from .safe_queries import rentals_for_admin

    try:
        dashboard_limit = int(os.getenv('ADMIN_DASHBOARD_LIMIT', '50'))

        def _load_rows(queryset, label):
            try:
                return list(queryset[:dashboard_limit])
            except Exception as exc:
                print(f'ADMIN DASHBOARD {label} sliced load failed: {exc}')
                return []

        books = _load_rows(Book.objects.select_related('author').order_by('-id'), 'books')
        riders = _load_rows(DeliveryRider.objects.select_related('user').order_by('-id'), 'riders')
        orders = _load_rows(
            Order.objects.select_related('customer__user', 'book', 'assigned_rider__user').filter(status='Pending').order_by('-created_at'),
            'orders',
        )
        try:
            # Fix members count and loading
            members = _load_rows(UserProfile.objects.select_related('user', 'membership').order_by('-id'), 'members')
        except Exception:
            members = []
            
        low_stock_count = Book.objects.filter(copies_available__lte=2).count()
        
        # Correctly load live and history rentals
        live_rentals = Rental.objects.filter(rental_status='Pending').select_related('user', 'book', 'user__userprofile').order_by('-rented_at')[:dashboard_limit]
        history_rentals = Rental.objects.exclude(rental_status='Pending').select_related('user', 'book').order_by('-rented_at')[:dashboard_limit]

        assigned_deliveries = _load_rows(
            Delivery.objects.select_related(
                'rental__book',
                'rental__user__userprofile',
                'delivery_person__deliverystaff',
            ).exclude(status='Pending').order_by('-assigned_at'),
            'assigned_deliveries',
        )
        
        context = {
            'total_books': Book.objects.count(),
            'active_members': UserProfile.objects.count(),
            'pending_orders': Order.objects.filter(status='Pending').count() + Rental.objects.filter(rental_status='Pending').count(),
            'low_stock_count': low_stock_count,
            'books': books,
            'authors': Author.objects.all().order_by('-id')[:dashboard_limit],
            'riders': riders,
            'orders': orders,
            'members': members,
            'live_rentals': live_rentals,
            'history_rentals': history_rentals,
            'payments': Payment.objects.select_related('user', 'order').order_by('-created_at')[:dashboard_limit],
            'assigned_deliveries': assigned_deliveries,
            'messages': ContactMessage.objects.order_by('-created_at')[:dashboard_limit],
            'settings': SystemSettings.objects.first(),
            'delivery_staff': DeliveryStaff.objects.select_related('user').order_by('-id')[:dashboard_limit],
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
    from .safe_queries import get_rental_or_404

    rental = get_rental_or_404(rental_id, Rental)
    delivery_boys = [staff for staff in DeliveryStaff.objects.all() if staff.active]

    if request.method == 'POST':
        delivery_staff_id = request.POST.get('delivery_person')
        if delivery_staff_id:
            try:
                candidates = [delivery_staff_id]
                try:
                    candidates.append(int(delivery_staff_id))
                except (TypeError, ValueError):
                    pass

                delivery_staff = DeliveryStaff.objects.filter(pk__in=candidates).first()
                if delivery_staff is None:
                    delivery_staff = DeliveryStaff.objects.filter(user_id__in=candidates).first()
                if delivery_staff is None:
                    try:
                        from bson import ObjectId

                        oid = ObjectId(str(delivery_staff_id))
                        delivery_staff = DeliveryStaff.objects.filter(user_id=oid).first()
                        if delivery_staff is None:
                            delivery_staff = DeliveryStaff.objects.filter(user_id=str(oid)).first()
                    except Exception:
                        pass
                if delivery_staff is None:
                    from bson import ObjectId

                    try:
                        person_id = ObjectId(str(delivery_staff_id))
                    except Exception:
                        person_id = delivery_staff_id
                else:
                    person_id = delivery_staff.user_id

                delivery, _created = Delivery.objects.get_or_create(rental_id=rental.pk)
                Delivery.objects.filter(pk=delivery.pk).update(
                    delivery_person_id=person_id,
                    status='Assigned',
                )
                try:
                    import os
                    from bson import ObjectId
                    from bookhub_backend.mongo_config import get_shared_client

                    client = get_shared_client()
                    if client:
                        db_name = os.getenv('MONGODB_NAME', 'bookhub_db')
                        rental_oid = rental.pk if isinstance(rental.pk, ObjectId) else ObjectId(str(rental.pk))
                        person_oid = person_id if isinstance(person_id, ObjectId) else ObjectId(str(person_id))
                        client[db_name].library_delivery.update_one(
                            {'rental_id': rental_oid},
                            {
                                '$set': {
                                    'rental_id': rental_oid,
                                    'delivery_person_id': person_oid,
                                    'status': 'Assigned',
                                },
                            },
                            upsert=True,
                        )
                except Exception as exc:
                    print('assign_delivery mongo sync:', exc)

                updated = Rental.set_status(rental.pk, Rental.STATUS_ASSIGNED)
                if not updated:
                    messages.error(request, 'Could not update rental status. Try again.')
                    return redirect(reverse('admin_dashboard') + '#live-rental-management')

                rider_name = str(person_id)
                if delivery_staff is not None:
                    try:
                        rider_name = delivery_staff.user.username
                    except Exception:
                        rider_name = str(delivery_staff.user_id)
                messages.success(request, f'Delivery assigned to {rider_name}')
            except DeliveryStaff.DoesNotExist:
                messages.error(request, 'Selected delivery staff does not exist.')
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
        from .safe_queries import get_delivery_or_404

        delivery = get_delivery_or_404(delivery_id, Delivery)
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

@admin_portal_required
def seed_live_data(request):
    import sys
    from django.conf import settings
    
    if str(settings.BASE_DIR) not in sys.path:
        sys.path.insert(0, str(settings.BASE_DIR))
        
    try:
        from seed_books import seed_books
        seed_books()
        messages.success(request, 'Successfully seeded the database with beautiful books for each category!')
    except Exception as e:
        messages.error(request, f'Failed to seed database: {str(e)}')
        
    return redirect('admin_dashboard')

@admin_portal_required
def add_book(request):
    if request.method == 'POST':
        title = request.POST.get('title')
        author_id = request.POST.get('author_id') or request.POST.get('author')
        category = request.POST.get('category')
        isbn = request.POST.get('isbn')
        copies = request.POST.get('copies', 1)
        image_file = request.FILES.get('image') 
        
        # Check if ISBN already exists
        if Book.objects.filter(isbn=isbn).exists():
            messages.error(request, f"Error: A book with ISBN '{isbn}' already exists in the inventory.")
            return redirect('admin_dashboard')

        if not title or not author_id or not category or not isbn:
            messages.error(request, 'Please fill in title, author, category, and ISBN.')
            return redirect('admin_dashboard')

        try:
            author_instance = Author.objects.filter(id=author_id).first()
            if author_instance is None:
                # Try fallback for string IDs if using MongoDB ObjectIds
                author_instance = Author.objects.filter(pk=author_id).first()
            
            if author_instance is None:
                messages.error(request, f"Author with ID {author_id} not found.")
                return redirect('admin_dashboard')

            copies = int(copies)
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
            import traceback
            print(traceback.format_exc())
            messages.error(request, f"Error adding book: {str(e)}")
            
    return redirect('admin_dashboard')


@admin_portal_required
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


@admin_portal_required
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
            author_id = request.POST.get('author_id') or request.POST.get('author')
            if author_id:
                author_instance = Author.objects.filter(id=author_id).first()
                if author_instance is None:
                    author_instance = Author.objects.filter(pk=author_id).first()
                
                if author_instance:
                    book.author = author_instance
            
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
            import traceback
            print(traceback.format_exc())
            messages.error(request, f"Error updating book: {str(e)}")

    return redirect('admin_dashboard')


@admin_portal_required
def delete_book(request, book_id):
    book = get_object_or_404(Book, id=book_id)
    book.delete()
    return redirect('admin_dashboard')


@admin_portal_required
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


@admin_portal_required
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

    from library.auth_backend import resolve_user_pk

    username = request.user.get_username()
    user_pk = resolve_user_pk(request.user, request)
    try:
        rider = DeliveryStaff.objects.filter(user__username=username).first()
        if rider is None and username:
            rider = DeliveryStaff.objects.filter(user__email=username).first()
        if rider is None and user_pk:
            try:
                rider = DeliveryStaff.objects.filter(user_id=user_pk).first()
            except Exception:
                rider = None

        if rider is not None or username:
            try:
                deliveries = Delivery.objects.filter(delivery_person__username=username)
            except Exception as exc:
                print('DELIVERY DASHBOARD ERROR:', exc)
                deliveries = []
            if not deliveries and user_pk:
                try:
                    deliveries = Delivery.objects.filter(delivery_person_id=user_pk)
                except Exception as exc:
                    print('DELIVERY DASHBOARD ERROR:', exc)
                    deliveries = []

            active_deliveries, history_deliveries = split_deliveries_for_dashboard(
                deliveries, Rental, assigned_status='assigned',
            )

        # Legacy orders (optional)
        try:
            rider_old = DeliveryRider.objects.filter(user__username=username).first()
            if rider_old is None:
                raise DeliveryRider.DoesNotExist
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
        from bookhub_backend.mongo_config import get_shared_client
        client = get_shared_client()
        if client:
            client.admin.command('ping')
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


def wake_up(request):
    """Ultra-fast endpoint: no DB queries, just proves the server is awake.
    Used by the loading splash page to detect when Render has warmed up."""
    return JsonResponse({'status': 'awake'})


def wake_loading_page(request):
    """Serve the loading splash page. The ?next= param tells JS where to redirect."""
    redirect_to = request.GET.get('next', '/en/library/')
    return render(request, 'wake.html', {'redirect_to': redirect_to})


def seed_and_setup(request):
    import sys
    from django.conf import settings
    from django.contrib.auth.models import User
    from library.models import DeliveryStaff, Author, Book
    from django.utils.text import slugify
    from django.contrib.auth.hashers import make_password
    from pymongo import MongoClient
    from bookhub_backend.mongo_config import get_mongodb_uri
    import os

    # 1. Seed Books Catalog
    if str(settings.BASE_DIR) not in sys.path:
        sys.path.insert(0, str(settings.BASE_DIR))
        
    try:
        from seed_books import seed_books
        seed_books()
        book_status = "Successfully seeded 10 books across all categories."
    except Exception as e:
        import traceback
        book_status = f"Book seeding warning/error: {str(e)}\n{traceback.format_exc()}"

    # 2. Setup/Reset Admin User
    admin_email = 'bipinsagarmatha123@gmail.com'
    admin_password = 'admin123'
    
    admin_user = User.objects.filter(username=admin_email).first() or User.objects.filter(email=admin_email).first()
    if admin_user:
        admin_user.set_password(admin_password)
        admin_user.is_superuser = True
        admin_user.is_staff = True
        admin_user.is_active = True
        admin_user.save()
    else:
        admin_user = User.objects.create_user(
            username=admin_email,
            email=admin_email,
            password=admin_password,
            first_name='System',
            last_name='Admin'
        )
        admin_user.is_superuser = True
        admin_user.is_staff = True
        admin_user.is_active = True
        admin_user.save()

    # Sync admin user to MongoDB
    from bookhub_backend.mongo_config import get_shared_client
    db_name = os.getenv('MONGODB_NAME', 'bookhub_db')
    client = get_shared_client()
    if client:
        try:
            db = client[db_name]
            hashed = make_password(admin_password)
            db.auth_user.update_one(
                {'username': admin_email},
                {
                    '$set': {
                        'username': admin_email,
                        'email': admin_email,
                        'password': hashed,
                        'first_name': 'System',
                        'last_name': 'Admin',
                        'is_superuser': True,
                        'is_staff': True,
                        'is_active': True,
                    },
                },
                upsert=True,
            )
            admin_status = "Admin successfully created/updated and synced to MongoDB Atlas."
        except Exception as e:
            admin_status = f"Admin MongoDB sync error: {str(e)}"
    else:
        admin_status = "Admin updated locally (no MongoDB URI set)."

    # 3. Setup/Reset Delivery User
    delivery_username = 'ram'
    delivery_password = 'ram123'
    
    delivery_user = User.objects.filter(username=delivery_username).first()
    if delivery_user:
        delivery_user.set_password(delivery_password)
        delivery_user.is_staff = True
        delivery_user.is_active = True
        delivery_user.is_superuser = False
        delivery_user.save()
    else:
        delivery_user = User.objects.create_user(
            username=delivery_username,
            password=delivery_password,
            first_name='Ram',
            last_name='Rider'
        )
        delivery_user.is_staff = True
        delivery_user.is_active = True
        delivery_user.save()

    if client:
        try:
            db = client[db_name]
            hashed = make_password(delivery_password)
            db.auth_user.update_one(
                {'username': delivery_username},
                {
                    '$set': {
                        'username': delivery_username,
                        'password': hashed,
                        'is_superuser': False,
                        'is_staff': True,
                        'is_active': True,
                    },
                },
                upsert=True,
            )
            doc = db.auth_user.find_one({'username': delivery_username})
            mongo_id = doc['_id'] if doc else None
            
            if mongo_id:
                from bson import ObjectId
                db.library_deliverystaff.update_one(
                    {'user_id': ObjectId(mongo_id)},
                    {
                        '$set': {
                            'user_id': ObjectId(mongo_id),
                            'phone': '9876543210',
                            'vehicle_number': 'DL-01-RAM',
                            'active': True,
                        },
                    },
                    upsert=True,
                )
            
            staff, _ = DeliveryStaff.objects.get_or_create(
                user=delivery_user,
                defaults={'phone': '9876543210', 'vehicle_number': 'DL-01-RAM', 'active': True}
            )
            staff.phone = '9876543210'
            staff.vehicle_number = 'DL-01-RAM'
            staff.active = True
            staff.save()
            
            delivery_status = "Delivery user 'ram' successfully created/updated and synced to MongoDB Atlas."
        except Exception as e:
            delivery_status = f"Delivery MongoDB sync error: {str(e)}"
    else:
        delivery_status = "Delivery user updated locally (no MongoDB URI set)."

    return JsonResponse({
        'status': 'success',
        'message': 'System setup, seeding, and user bootstrapping completed successfully!',
        'books_seeding': book_status,
        'admin_setup': admin_status,
        'delivery_setup': delivery_status,
        'credentials': {
            'admin': {
                'username_email': admin_email,
                'password': admin_password,
                'login_url': '/en/library/login/'
            },
            'delivery': {
                'username': delivery_username,
                'password': delivery_password,
                'login_url': '/en/library/login/'
            }
        }
    })


def setup_admin(request):
    """One-shot endpoint: create/reset admin/admin123 in both Django ORM and MongoDB.
    Hit this URL in browser: /en/library/setup-admin/
    Returns JSON so you can see exactly what happened.
    """
    import os
    from django.contrib.auth.models import User
    from django.contrib.auth.hashers import make_password
    from bookhub_backend.mongo_config import get_mongodb_uri
    from pymongo import MongoClient

    USERNAME = 'admin'
    PASSWORD = 'admin123'
    results = {}

    # Step 1: Django ORM
    try:
        user = User.objects.filter(username=USERNAME).first()
        if user:
            user.set_password(PASSWORD)
            user.is_superuser = True
            user.is_staff = True
            user.is_active = True
            user.save()
            results['orm'] = f'Updated existing user (id={user.pk})'
        else:
            user = User.objects.create_user(
                username=USERNAME,
                email='admin@bookhub.local',
                password=PASSWORD,
                first_name='Admin',
                last_name='User',
            )
            user.is_superuser = True
            user.is_staff = True
            user.is_active = True
            user.save()
            results['orm'] = f'Created new user (id={user.pk})'
    except Exception as e:
        results['orm'] = f'ERROR: {e}'

    # Step 2: MongoDB direct sync
    from bookhub_backend.mongo_config import get_shared_client
    client = get_shared_client()
    if client:
        try:
            db_name = os.getenv('MONGODB_NAME', 'bookhub_db')
            coll = client[db_name].auth_user
            hashed = make_password(PASSWORD)
            res = coll.update_one(
                {'username': USERNAME},
                {'$set': {
                    'username': USERNAME,
                    'email': 'admin@bookhub.local',
                    'password': hashed,
                    'first_name': 'Admin',
                    'last_name': 'User',
                    'is_superuser': True,
                    'is_staff': True,
                    'is_active': True,
                }},
                upsert=True,
            )
            action = 'inserted' if res.upserted_id else f'updated (matched={res.matched_count})'
            results['mongodb'] = f'OK — {action}'

            # Verify it's there
            doc = coll.find_one({'username': USERNAME}, {'username': 1, 'is_superuser': 1, 'is_active': 1})
            results['mongodb_verify'] = str(doc)
        except Exception as e:
            results['mongodb'] = f'ERROR: {e}'
    else:
        results['mongodb'] = 'Skipped — no MONGODB_URI configured'

    return JsonResponse({
        'status': 'done',
        'credentials': {'username': USERNAME, 'password': PASSWORD},
        'login_url': '/en/library/login/',
        'results': results,
    })


def reseed(request):
    """
    One-shot fix: wipe + reseed books/authors directly into MongoDB with correct
    integer FK links, then create admin/admin123.
    Visit in browser: /en/library/reseed/
    """
    import os
    import datetime
    from django.contrib.auth.models import User
    from django.contrib.auth.hashers import make_password
    from django.utils.text import slugify
    from bookhub_backend.mongo_config import get_mongodb_uri
    from pymongo import MongoClient

    results = {}

    BOOKS_DATA = [
        {"title": "The God of Small Things",      "author": "Arundhati Roy",      "category": "Fiction",      "isbn": "9780812979657", "copies_total": 5,  "copies_available": 5,  "status": "Available"},
        {"title": "The Book of Lost Friends",      "author": "Lisa Wingate",        "category": "Fiction",      "isbn": "9781984819901", "copies_total": 3,  "copies_available": 3,  "status": "Available"},
        {"title": "Midnight's Children",           "author": "Salman Rushdie",      "category": "Fiction",      "isbn": "9780812976533", "copies_total": 4,  "copies_available": 2,  "status": "Low Stock"},
        {"title": "Rich Dad Poor Dad",             "author": "Robert Kiyosaki",     "category": "Business",     "isbn": "9781612680194", "copies_total": 8,  "copies_available": 8,  "status": "Available"},
        {"title": "Atomic Habits",                 "author": "James Clear",         "category": "Business",     "isbn": "9780735211292", "copies_total": 10, "copies_available": 9,  "status": "Available"},
        {"title": "Wings of Fire",                 "author": "A.P.J. Abdul Kalam",  "category": "Biographies",  "isbn": "9788173711466", "copies_total": 6,  "copies_available": 6,  "status": "Available"},
        {"title": "Steve Jobs",                    "author": "Walter Isaacson",     "category": "Biographies",  "isbn": "9781451648539", "copies_total": 4,  "copies_available": 4,  "status": "Available"},
        {"title": "KPop Demon Hunters",            "author": "Golden Books",        "category": "Toddlers",     "isbn": "9798217233977", "copies_total": 5,  "copies_available": 5,  "status": "Available"},
        {"title": "The Very Hungry Caterpillar",   "author": "Eric Carle",          "category": "Toddlers",     "isbn": "9780399226908", "copies_total": 7,  "copies_available": 7,  "status": "Available"},
        {"title": "Introduction to Algorithms",    "author": "Thomas H. Cormen",    "category": "Academic",     "isbn": "9780262033848", "copies_total": 3,  "copies_available": 3,  "status": "Available"},
    ]

    from bookhub_backend.mongo_config import get_shared_client
    client = get_shared_client()
    if not client:
        return JsonResponse({'status': 'error', 'message': 'No MONGODB_URI set on this server'}, status=500)

    db_name = os.getenv('MONGODB_NAME', 'bookhub_db')
    db = client[db_name]

    # ── Step 1: Wipe existing books & authors ──────────────────────────────────
    try:
        db.library_book.delete_many({})
        db.library_author.delete_many({})
        results['wipe'] = 'Cleared library_book and library_author'
    except Exception as e:
        results['wipe'] = f'ERROR: {e}'

    # ── Step 2: Insert authors & books with matching integer IDs ────────────────
    now = datetime.datetime.utcnow()
    author_id = 1
    book_id = 1
    author_map = {}   # name → integer id
    books_inserted = []

    for data in BOOKS_DATA:
        aname = data['author']
        if aname not in author_map:
            slug = slugify(aname)
            db.library_author.insert_one({
                'id': author_id,
                'name': aname,
                'slug': slug,
                'bio': '',
                'nationality': '',
                'born': '',
                'website': '',
                'genres': '',
                'awards': '',
            })
            author_map[aname] = author_id
            author_id += 1

        db.library_book.insert_one({
            'id': book_id,
            'title': data['title'],
            'author_id': author_map[aname],
            'category': data['category'],
            'isbn': data['isbn'],
            'copies_total': data['copies_total'],
            'copies_available': data['copies_available'],
            'status': data['status'],
            'image': '',
        })
        books_inserted.append(data['title'])
        book_id += 1

    results['books'] = f'Inserted {len(books_inserted)} books: {books_inserted}'
    results['authors'] = f'Inserted {len(author_map)} authors'

    # ── Step 3: Create admin/admin123 ───────────────────────────────────────────
    USERNAME = 'admin'
    PASSWORD = 'admin123'
    try:
        user = User.objects.filter(username=USERNAME).first()
        if user:
            user.set_password(PASSWORD)
            user.is_superuser = True
            user.is_staff = True
            user.is_active = True
            user.save()
            results['admin_orm'] = f'Reset password for existing user (id={user.pk})'
        else:
            user = User.objects.create_user(
                username=USERNAME, email='admin@bookhub.local',
                password=PASSWORD, first_name='Admin', last_name='User',
            )
            user.is_superuser = True
            user.is_staff = True
            user.is_active = True
            user.save()
            results['admin_orm'] = f'Created new user (id={user.pk})'
    except Exception as e:
        results['admin_orm'] = f'ERROR: {e}'

    try:
        hashed = make_password(PASSWORD)
        res = db.auth_user.update_one(
            {'username': USERNAME},
            {'$set': {
                'username': USERNAME, 'email': 'admin@bookhub.local',
                'password': hashed, 'first_name': 'Admin', 'last_name': 'User',
                'is_superuser': True, 'is_staff': True, 'is_active': True,
            }},
            upsert=True,
        )
        action = 'inserted' if res.upserted_id else f'updated (matched={res.matched_count})'
        results['admin_mongodb'] = f'OK — {action}'
    except Exception as e:
        results['admin_mongodb'] = f'ERROR: {e}'

    return JsonResponse({
        'status': 'success',
        'message': 'Books reseeded + admin account ready!',
        'credentials': {'username': USERNAME, 'password': PASSWORD, 'login_url': '/en/library/login/'},
        'results': results,
    })


def debug_admin(request):
    """Debug: show exactly what Atlas has for user 'admin' and test password check.
    Visit: /en/library/debug-admin/
    """
    import os
    from django.contrib.auth.hashers import check_password
    from bookhub_backend.mongo_config import get_shared_client

    client = get_shared_client()
    if not client:
        return JsonResponse({'error': 'No MongoDB URI'}, status=500)

    db_name = os.getenv('MONGODB_NAME', 'bookhub_db')
    db = client[db_name]

    # Fetch the admin doc
    doc = db.auth_user.find_one({'username': 'admin'})
    if not doc:
        # List all users to help debug
        all_users = [
            {'username': d.get('username'), 'is_superuser': d.get('is_superuser')}
            for d in db.auth_user.find({}, {'username': 1, 'is_superuser': 1})
        ]
        return JsonResponse({'error': 'admin user NOT FOUND in MongoDB', 'all_users': all_users})

    stored_hash = doc.get('password', '')
    password_ok = check_password('admin123', stored_hash)

    return JsonResponse({
        'found': True,
        'username': doc.get('username'),
        'is_superuser': doc.get('is_superuser'),
        'is_staff': doc.get('is_staff'),
        'is_active': doc.get('is_active'),
        'password_hash_prefix': stored_hash[:30] if stored_hash else '(empty)',
        'password_check_admin123': password_ok,
        'mongo_id': str(doc.get('_id')),
    })


def debug_user(request):
    """Debug: inspect currently logged-in user in session.
    Visit: /en/library/debug-user/
    """
    from .role_utils import user_can_admin, user_can_delivery, allowed_roles_for_user
    user = request.user
    session_items = dict(request.session.items())
    
    # Hide raw password hashes or session keys from output if any
    clean_session = {k: v for k, v in session_items.items() if not k.startswith('_auth_user_hash')}

    user_info = {
        'is_authenticated': user.is_authenticated,
        'username': getattr(user, 'username', None),
        'email': getattr(user, 'email', None),
        'is_superuser': getattr(user, 'is_superuser', None),
        'is_staff': getattr(user, 'is_staff', None),
        'pk': str(getattr(user, 'pk', None)),
        'user_class': user.__class__.__name__,
    }

    return JsonResponse({
        'user': user_info,
        'session': clean_session,
        'can_admin': user_can_admin(user),
        'can_delivery': user_can_delivery(user),
        'allowed_roles': allowed_roles_for_user(user),
    })


def test_db_connection(request):
    from django.conf import settings
    from bookhub_backend.mongo_config import get_mongodb_uri, mongodb_username_from_uri, mask_mongodb_uri, get_shared_client
    uri = get_mongodb_uri()
    try:
        client = get_shared_client()
        if not client:
            return JsonResponse({'status': 'error', 'message': 'MONGODB_URI not set on server'}, status=500)
        client.admin.command('ping')
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


def _ensure_user_profile(user):
    profile, _ = UserProfile.objects.get_or_create(
        user=user,
        defaults={'phone': '', 'address': '', 'pincode': ''},
    )
    return profile

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
    
    # Calculate total and subtotal for each item
    cart_items = []
    total = 0
    for item in items:
        subtotal = item.book.price_per_day * item.quantity
        total += subtotal
        cart_items.append({
            'book': item.book,
            'quantity': item.quantity,
            'subtotal': subtotal
        })
        
    return render(request, 'view_cart.html', {'items': cart_items, 'total': total})

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
    normalized_plan = (plan or '').strip().title()
    if normalized_plan not in {'Basic', 'Premium'}:
        messages.error(request, "Invalid plan selected.")
        return redirect('settings')

    try:
        defaults = {
            'price': 0 if normalized_plan == 'Basic' else 500,
            'max_books_at_a_time': 2 if normalized_plan == 'Basic' else 10,
        }
        membership, _ = MembershipPlan.objects.get_or_create(name=normalized_plan, defaults=defaults)
    except Exception as exc:
        messages.error(request, f"Unable to select plan: {exc}")
        return redirect('settings')
    profile = _ensure_user_profile(request.user)
    subscription, created = Subscription.objects.get_or_create(user=request.user, defaults={'plan': membership, 'active': True})
    if not created:
        subscription.plan = membership
        subscription.active = True
        subscription.save()
    profile.membership = membership
    profile.save()
    messages.success(request, f"Subscribed to {normalized_plan} plan.")
    return redirect('settings')

@login_required
def payment_page(request):
    cart = Cart.objects.filter(user=request.user).first()
    if not cart:
        messages.error(request, "Your cart is empty.")
        return redirect('view_cart')
    items = cart.cartitem_set.all()
    total_amount = sum(item.book.price_per_day * item.quantity for item in items)
    
    # Convert to Decimal for model storage
    decimal_total = Decimal(str(total_amount))
    
    reference_id = str(uuid.uuid4())
    payment = Payment.objects.create(user=request.user, amount=decimal_total, reference_id=reference_id, status='initiated')
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
    profile = _ensure_user_profile(request.user)
    return render(request, 'checkout.html', {'profile': profile})

@csrf_exempt
@login_required
def process_checkout(request):
    if request.method == "POST":
        try:
            print(f"DEBUG: Process Checkout received: {request.body}")
            data = json.loads(request.body or '{}')
            book_id = data.get('book_id')
            duration = data.get('duration')
            total = data.get('total')
            payment_method = data.get('payment_method', 'razorpay')
            
            if not book_id or not duration:
                return JsonResponse({'status': 'error', 'message': 'Missing book_id or duration'}, status=400)

            book = Book.objects.get(id=book_id)
            profile, _ = UserProfile.objects.get_or_create(user=request.user)
            
            # Convert total to Decimal
            try:
                decimal_total = Decimal(str(total))
            except (TypeError, ValueError):
                decimal_total = Decimal('0.00')

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
                amount=decimal_total,
                reference_id=str(uuid.uuid4()),
                payment_type=payment_method,
                status='success' # Mocking instant success
            )
            
            # Calculate return date
            from datetime import timedelta
            try:
                days = int(duration)
            except (TypeError, ValueError):
                days = 7
            return_date = timezone.now() + timedelta(days=days)
            
            # Create Rental and Delivery entries for the professional workflow
            from .models import Rental, Delivery
            rental = Rental.objects.create(
                user=request.user,
                book=book,
                duration_days=days,
                total_amount=decimal_total,
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
            
        except Book.DoesNotExist:
            return JsonResponse({'status': 'error', 'message': 'Book not found'}, status=404)
        except Exception as e:
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
    rentals = Rental.objects.filter(user__username=request.user.get_username()).order_by('-rented_at')
    return render(request, 'my_rentals.html', {'rentals': rentals})

@login_required
def track_order(request, delivery_id):
    from .models import Delivery, DeliveryStaff
    delivery = get_object_or_404(Delivery, id=delivery_id)
    
    # Ensure the user owns this rental
    rental_user = getattr(delivery.rental, 'user', None)
    owner_name = getattr(rental_user, 'username', None) if rental_user else None
    if owner_name and owner_name != request.user.get_username():
        messages.error(request, "Unauthorized access.")
        return redirect('my_rentals')
        
    rider_profile = None
    if delivery.delivery_person_id:
        try:
            rider_profile = DeliveryStaff.objects.filter(
                user_id=delivery.delivery_person_id
            ).first()
            if rider_profile is None and delivery.delivery_person_id:
                uname = getattr(delivery.delivery_person, 'username', None)
                if uname:
                    rider_profile = DeliveryStaff.objects.filter(user__username=uname).first()
        except DeliveryStaff.DoesNotExist:
            pass
            
    return render(request, 'track_order.html', {
        'delivery': delivery,
        'rider_profile': rider_profile
    })

@login_required
def premium_checkout(request):
    profile = _ensure_user_profile(request.user)
    return render(request, 'premium_checkout.html', {'profile': profile})

@csrf_exempt
@login_required
def activate_premium(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body or '{}')
            plan_name = data.get('plan', 'Premium')
            amount = data.get('amount', 500)
            
            # Ensure amount is a Decimal for MongoDB/Django compatibility
            try:
                decimal_amount = Decimal(str(amount))
            except (TypeError, ValueError):
                decimal_amount = Decimal('500.00')
            
            # Get or create profile
            profile = _ensure_user_profile(request.user)
            
            # Get or create the membership plan
            plan, _ = MembershipPlan.objects.get_or_create(
                name=plan_name,
                defaults={'price': decimal_amount, 'max_books_at_a_time': 10 if plan_name == 'Premium' else 2}
            )
            profile.membership = plan
            
            # Set expiry date to 30 days from now
            from datetime import timedelta
            profile.membership_expiry = (timezone.now() + timedelta(days=30)).date()
            profile.save()
            
            # Record payment
            Payment.objects.create(
                user=request.user,
                amount=decimal_amount,
                reference_id='PREM-' + str(uuid.uuid4())[:8].upper(),
                status='success'
            )
            
            return JsonResponse({
                'status': 'success',
                'plan': plan_name,
                'expiry': profile.membership_expiry.strftime('%B %d, %Y')
            })
        except Exception as e:
            print(f"DEBUG: Activate Premium Error: {str(e)}")
            print(traceback.format_exc())
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

@login_required
def gift_card(request):
    profile = _ensure_user_profile(request.user)
    return render(request, 'gift_card.html', {'profile': profile})


@login_required
def gift_card_checkout(request):
    if request.method != 'POST':
        return JsonResponse({'status': 'error', 'message': 'Invalid method'}, status=405)

    try:
        data = json.loads(request.body or '{}')
        amount = data.get('amount') or 0
        
        # Ensure amount is a Decimal for MongoDB/Django compatibility
        try:
            decimal_amount = Decimal(str(amount))
        except (TypeError, ValueError):
            decimal_amount = Decimal('0.00')
            
        recipient_name = (data.get('recipient_name') or '').strip()
        recipient_email = (data.get('recipient_email') or '').strip()
        message_text = (data.get('message') or '').strip()

        if decimal_amount <= 0 or not recipient_name or not recipient_email:
            return JsonResponse({'status': 'error', 'message': 'Recipient name, email, and amount are required.'}, status=400)

        reference_id = 'GIFT-' + str(uuid.uuid4())[:8].upper()
        Payment.objects.create(
            user=request.user,
            amount=decimal_amount,
            reference_id=reference_id,
            payment_type=f'Gift Card to {recipient_name}',
            status='success',
        )

        messages.success(request, f'Gift card for {recipient_name} is ready and visible in admin payments.')
        return JsonResponse({
            'status': 'success',
            'reference_id': reference_id,
            'recipient_name': recipient_name,
            'recipient_email': recipient_email,
            'message': message_text,
        })
    except Exception as exc:
        return JsonResponse({'status': 'error', 'message': str(exc)}, status=400)

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
