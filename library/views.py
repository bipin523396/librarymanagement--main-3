from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import HttpResponseForbidden
from functools import wraps
from .models import UserProfile

# Custom decorator to restrict admin access
def admin_required(view_func):
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        # Check if user is authenticated
        if not request.user.is_authenticated:
            messages.error(request, 'You must be logged in to access the admin panel.', extra_tags='error')
            return redirect('login')
        
        # Check if user email is the admin email
        ADMIN_EMAIL = 'rahul.k140905@gmail.com'
        if request.user.email != ADMIN_EMAIL:
            messages.error(request, 'You do not have permission to access the admin panel.', extra_tags='error')
            return redirect('home')
        
        # User is authenticated and has admin email
        return view_func(request, *args, **kwargs)
    
    return wrapper

def home(request):
    return render(request, 'index.html')

@admin_required
def admin_dashboard(request):
    return render(request, 'admin.html')

def delivery_dashboard(request):
    return render(request, 'deliveryman.html')

def login_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            messages.success(request, f'Welcome back, {user.first_name or user.username}!', extra_tags='success')
            return redirect('home')
        else:
            messages.error(request, 'Invalid email/username or password.', extra_tags='error')

    return render(request, 'login.html')

def signup_view(request):
    if request.method == 'POST':
        first_name = request.POST.get('first_name', '').strip()
        last_name = request.POST.get('last_name', '').strip()
        email = request.POST.get('email', '').strip()
        phone = request.POST.get('phone', '').strip()
        pincode = request.POST.get('pincode', '').strip()
        password = request.POST.get('password', '')
        confirm_password = request.POST.get('confirm_password', '')

        # Validation
        if not all([first_name, last_name, email, phone, pincode, password, confirm_password]):
            messages.error(request, 'All fields are required.', extra_tags='error')
            return redirect('signup')

        if password != confirm_password:
            messages.error(request, 'Passwords do not match.', extra_tags='error')
            return redirect('signup')

        if len(password) < 6:
            messages.error(request, 'Password must be at least 6 characters long.', extra_tags='error')
            return redirect('signup')

        if User.objects.filter(email=email).exists():
            messages.error(request, 'Email already registered. Please login or use a different email.', extra_tags='error')
            return redirect('signup')

        if User.objects.filter(username=email).exists():
            messages.error(request, 'Email already in use.', extra_tags='error')
            return redirect('signup')

        # Create user
        user = User.objects.create_user(
            username=email,
            email=email,
            password=password,
            first_name=first_name,
            last_name=last_name
        )

        # Create user profile
        UserProfile.objects.create(
            user=user,
            phone=phone,
            pincode=pincode,
            address=''
        )

        messages.success(request, 'Account created successfully! You can now login.', extra_tags='success')
        return redirect('login')

    return render(request, 'signup.html')

def categories_view(request):
    return render(request, 'categories.html')