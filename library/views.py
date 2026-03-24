
from django.views.decorators.csrf import csrf_exempt
import json
from django.shortcuts import render, get_object_or_404, redirect
from .bot_engine import super_ai
from django.http import JsonResponse
from django.utils import timezone
from django.contrib.auth.models import User
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from .models import DeliveryRider, Order, Book, UserProfile, MembershipPlan

# ==========================================
# --- 1. CUSTOMER PAGES ---
# ==========================================

def home(request):
    # Fetch the 4 newest books to show in "Trending Books"
    trending_books = Book.objects.all().order_by('-id')[:4]
    return render(request, 'index.html', {'trending_books': trending_books})

def categories_view(request):
    # Support both '?category=' and '?type=' from the URL
    requested_category = request.GET.get('category') or request.GET.get('type')

    if requested_category:
        books = Book.objects.filter(category__iexact=requested_category)
        page_title = f"{requested_category.capitalize()} Books"
    else:
        books = Book.objects.all()
        page_title = "All Books"

    context = {
        'books': books,
        'page_title': page_title,
        'active_category': requested_category # Pass this to HTML so JS can check the box
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

        user = User.objects.create_user(username=email, email=email, password=password)
        user.first_name = first_name
        user.last_name = last_name
        user.save()

        UserProfile.objects.create(
            user=user,
            phone=phone,
            pincode=pincode,
            address="Not provided yet"
        )

        login(request, user)
        return redirect('home')

    return render(request, 'signup.html')


def login_view(request):
    if request.method == "POST":
        username = request.POST.get('username')
        password = request.POST.get('password')

        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            
            # SMART ROUTING
            if user.is_superuser:
                return redirect('admin_dashboard')
            elif hasattr(user, 'deliveryrider'):
                return redirect('delivery_dashboard')
            else:
                return redirect('home')
        else:
            messages.error(request, "Invalid username or password.")
            return redirect('login')

    return render(request, 'login.html')

def logout_view(request):
    logout(request)
    return redirect('login')

# ==========================================
# --- 3. ADMIN DASHBOARD ACTIONS ---
# ==========================================

def admin_dashboard(request):
    books = Book.objects.all().order_by('-id')
    riders = DeliveryRider.objects.all()
    orders = Order.objects.filter(status='Pending')
    
    try:
        members = UserProfile.objects.all()
    except:
        members = []

    low_stock_count = books.filter(copies_available__lte=2).count()

    context = {
        'total_books': books.count(),
        'active_members': len(members),
        'pending_orders': orders.count(),
        'low_stock_count': low_stock_count,
        'books': books,
        'riders': riders,
        'orders': orders,
        'members': members,
    }
    return render(request, 'admin.html', context)


def add_book(request):
    if request.method == 'POST':
        title = request.POST.get('title')
        author = request.POST.get('author')
        category = request.POST.get('category')
        isbn = request.POST.get('isbn')
        copies = request.POST.get('copies', 1)
        image_file = request.FILES.get('image') 
        
        Book.objects.create(
            title=title,
            author=author,
            category=category,
            isbn=isbn,
            copies_total=copies,
            copies_available=copies,
            image=image_file 
        )
    return redirect('admin_dashboard')


def edit_book(request, book_id):
    book = get_object_or_404(Book, id=book_id)
    
    if request.method == 'POST':
        book.title = request.POST.get('title')
        book.author = request.POST.get('author')
        book.category = request.POST.get('category')
        book.isbn = request.POST.get('isbn')
        
        if request.FILES.get('image'):
            book.image = request.FILES.get('image')
        
        old_total = book.copies_total
        new_total = int(request.POST.get('copies', old_total))
        difference = new_total - old_total
        
        book.copies_total = new_total
        book.copies_available = book.copies_available + difference
        
        book.save()
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

def delivery_dashboard(request):
    active_orders = Order.objects.filter(status__in=['Pending', 'Assigned', 'Out for Delivery']).order_by('-created_at')
    history_orders = Order.objects.filter(status__in=['Completed', 'Cancelled']).order_by('-completed_at', '-created_at')

    rider = None
    if request.user.is_authenticated:
        try:
            rider = DeliveryRider.objects.get(user=request.user)
        except DeliveryRider.DoesNotExist:
            pass 

    context = {
        'rider': rider,
        'assigned_orders': active_orders,
        'history_orders': history_orders,
    }
    return render(request, 'deliveryman.html', context)


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
    
@csrf_exempt
def chat_api(request):
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            user_message = data.get('message', '')
            has_image = data.get('has_image', False)
            
            bot_response = super_ai(user_message, has_image=has_image)
            return JsonResponse({'status': 'success', 'response': bot_response})
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)}, status=400)
    return JsonResponse({'status': 'error', 'message': 'Invalid request method'}, status=405)