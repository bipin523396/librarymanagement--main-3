from django.db import models
from django.contrib.auth.models import User

# 1. MEMBERSHIP PLANS
class MembershipPlan(models.Model):
    name = models.CharField(max_length=50) # e.g., Basic, Regular, Premium
    price = models.DecimalField(max_digits=6, decimal_places=2)
    max_books_at_a_time = models.IntegerField()

    def __str__(self):
        return self.name

# 2. USER PROFILE (Extends default Django User)
class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    phone = models.CharField(max_length=15)
    address = models.TextField()
    pincode = models.CharField(max_length=10)
    membership = models.ForeignKey(MembershipPlan, on_delete=models.SET_NULL, null=True, blank=True)
    membership_expiry = models.DateField(null=True, blank=True)

    def __str__(self):
        return self.user.username

# 3. BOOKS & INVENTORY
class Book(models.Model):
    CATEGORY_CHOICES = [
        ('Fiction', 'Fiction'),
        ('Business', 'Business'),
        ('Toddlers', 'Toddlers'),
        ('Academic', 'Academic')
    ]
    STATUS_CHOICES = [
        ('Available', 'Available'),
        ('Low Stock', 'Low Stock'),
        ('Out of Stock', 'Out of Stock')
    ]

    title = models.CharField(max_length=200)
    author = models.CharField(max_length=100)
    category = models.CharField(max_length=50, choices=CATEGORY_CHOICES)
    isbn = models.CharField(max_length=20, unique=True)
    copies_total = models.IntegerField(default=1)
    copies_available = models.IntegerField(default=1)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Available')
    image = models.ImageField(upload_to='book_images/', null=True, blank=True)

    def __str__(self):
        return self.title

# 4. DELIVERY RIDERS
class DeliveryRider(models.Model):
    STATUS_CHOICES = [('Online', 'Online'), ('Offline', 'Offline')]
    
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    phone = models.CharField(max_length=15)
    vehicle_details = models.CharField(max_length=100)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Offline')

    def __str__(self):
        return self.user.get_full_name() or self.user.username

# 5. ORDERS / RENTALS
class Order(models.Model):
    TYPE_CHOICES = [
        ('Delivery Only', 'Delivery Only'),
        ('Pickup Only', 'Pickup Only'),
        ('Exchange', 'Exchange (Drop & Pick)')
    ]
    STATUS_CHOICES = [
        ('Pending', 'Pending'),
        ('Assigned', 'Assigned to Rider'),
        ('Out for Delivery', 'Out for Delivery'),
        ('Completed', 'Completed'),
        ('Cancelled', 'Cancelled')
    ]

    order_id = models.CharField(max_length=20, unique=True)
    customer = models.ForeignKey(UserProfile, on_delete=models.CASCADE)
    book = models.ForeignKey(Book, on_delete=models.CASCADE)
    order_type = models.CharField(max_length=50, choices=TYPE_CHOICES)
    status = models.CharField(max_length=50, choices=STATUS_CHOICES, default='Pending')
    
    assigned_rider = models.ForeignKey(DeliveryRider, on_delete=models.SET_NULL, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"{self.order_id} - {self.customer.user.username}"


class UserSettings(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='usersettings')
    language = models.CharField(max_length=20, default='English')
    notifications = models.BooleanField(default=True)

    def __str__(self):
        return self.user.username