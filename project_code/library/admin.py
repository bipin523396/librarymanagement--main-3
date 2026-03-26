from django.contrib import admin
from .models import MembershipPlan, UserProfile, Book, DeliveryRider, Order

# Register your models here.
admin.site.register(MembershipPlan)
admin.site.register(UserProfile)
admin.site.register(Book)
admin.site.register(DeliveryRider)
admin.site.register(Order)