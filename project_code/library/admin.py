from django.contrib import admin
from .models import (
    MembershipPlan,
    UserProfile,
    Book,
    DeliveryRider,
    Order,
    Cart,
    CartItem,
    Wishlist,
    Subscription,
    Payment,
)

# Register models for admin site
admin.site.register(MembershipPlan)
admin.site.register(UserProfile)
admin.site.register(Book)
admin.site.register(DeliveryRider)
admin.site.register(Order)
admin.site.register(Cart)
admin.site.register(CartItem)
admin.site.register(Wishlist)
admin.site.register(Subscription)
admin.site.register(Payment)
