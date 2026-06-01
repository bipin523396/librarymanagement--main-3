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
    author = models.ForeignKey('Author', on_delete=models.CASCADE)
    category = models.CharField(max_length=50, choices=CATEGORY_CHOICES)
    isbn = models.CharField(max_length=20, unique=True)
    copies_total = models.IntegerField(default=1)
    copies_available = models.IntegerField(default=1)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Available')
    image = models.ImageField(upload_to='book_images/', null=True, blank=True)

    def __str__(self):
        return self.title

    @property
    def price_per_day(self):
        if self.category == 'Fiction':
            return 15.00
        elif self.category == 'Business':
            return 25.00
        elif self.category == 'Toddlers':
            return 10.00
        elif self.category == 'Biographies':
            return 20.00
        elif self.category == 'Academic':
            return 30.00
        else:
            return 15.00


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

# 6. CART & CART ITEMS
class Cart(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='cart')
    # ManyToMany through CartItem
    books = models.ManyToManyField(Book, through='CartItem')

    def __str__(self):
        return f"Cart of {self.user.username}"

class CartItem(models.Model):
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE)
    book = models.ForeignKey(Book, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)

    def __str__(self):
        return f"{self.quantity} x {self.book.title}"

# 7. SUBSCRIPTION
class Subscription(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='subscription')
    plan = models.ForeignKey(MembershipPlan, on_delete=models.SET_NULL, null=True)
    start_date = models.DateField(auto_now_add=True)
    end_date = models.DateField(null=True, blank=True)
    active = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.user.username} - {self.plan.name if self.plan else 'No Plan'}"

# 8. PAYMENT
class Payment(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    order = models.ForeignKey(Order, on_delete=models.SET_NULL, null=True, blank=True)
    payment_type = models.CharField(max_length=50, default='Book Rental')
    amount = models.DecimalField(max_digits=8, decimal_places=2)
    reference_id = models.CharField(max_length=100, unique=True)
    status = models.CharField(max_length=20, choices=[('initiated', 'Initiated'), ('success', 'Success'), ('failed', 'Failed')], default='initiated')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Payment {self.reference_id} - {self.status}"


class Wishlist(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='wishlist')
    books = models.ManyToManyField(Book, related_name='wishlisted_by')

    def __str__(self):
        return f"Wishlist of {self.user.username}"


# 9. AUTHOR PROFILES
class Author(models.Model):
    name = models.CharField(max_length=150)
    slug = models.SlugField(unique=True)
    bio = models.TextField(blank=True)
    image = models.ImageField(upload_to='authors/', null=True, blank=True)
    nationality = models.CharField(max_length=100, blank=True)
    born = models.CharField(max_length=50, blank=True)
    website = models.URLField(blank=True)
    genres = models.CharField(max_length=200, blank=True, help_text='Comma-separated genres')
    awards = models.TextField(blank=True, help_text='One award per line')

    def __str__(self):
        return self.name

    def get_genres_list(self):
        return [g.strip() for g in self.genres.split(',') if g.strip()]

    def get_awards_list(self):
        return [a.strip() for a in self.awards.splitlines() if a.strip()]


# 10. RENTAL MANAGEMENT
class Rental(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    book = models.ForeignKey(Book, on_delete=models.CASCADE)
    duration_days = models.IntegerField(default=7)
    total_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    payment_status = models.CharField(max_length=50, default='Pending')
    rental_status = models.CharField(max_length=50, default='Pending')
    rented_at = models.DateTimeField(auto_now_add=True)
    due_date = models.DateField()
    returned = models.BooleanField(default=False)
    late_fee = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    def __str__(self):
        return f"{self.user.username} rented {self.book.title}"

    @classmethod
    def set_status(cls, pk, status, **extra):
        """Update status without full save (avoids MongoDB Decimal128 errors on other fields)."""
        return cls.objects.filter(pk=pk).update(rental_status=status, **extra)


# 11. DELIVERY STAFF
class DeliveryStaff(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    phone = models.CharField(max_length=20)
    vehicle_number = models.CharField(max_length=50)
    active = models.BooleanField(default=True)
    current_latitude = models.DecimalField(max_digits=9, decimal_places=6, default=28.6139) # Default to New Delhi
    current_longitude = models.DecimalField(max_digits=9, decimal_places=6, default=77.2090)

    def __str__(self):
        return f"Delivery Staff: {self.user.username}"


# 12. DELIVERY LOGISTICS
class Delivery(models.Model):
    rental = models.OneToOneField(Rental, on_delete=models.CASCADE)
    delivery_person = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    status = models.CharField(max_length=50, default='Pending')
    tracking_id = models.CharField(max_length=100, blank=True)
    assigned_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Delivery {self.tracking_id} - {self.status}"


# 13. CONTACT MESSAGES
class ContactMessage(models.Model):
    name = models.CharField(max_length=100)
    email = models.EmailField()
    subject = models.CharField(max_length=200)
    message = models.TextField()
    status = models.CharField(max_length=50, default='Pending')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Message from {self.name} - {self.subject}"


# 13. SYSTEM SETTINGS
class SystemSettings(models.Model):
    delivery_charge = models.DecimalField(max_digits=6, decimal_places=2, default=50.00)
    late_fee_per_day = models.DecimalField(max_digits=6, decimal_places=2, default=10.00)
    rental_limit = models.IntegerField(default=3)

    def __str__(self):
        return "Global System Settings"