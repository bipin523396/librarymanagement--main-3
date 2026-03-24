from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import User
from .models import UserProfile


@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    """
    Signal handler to automatically create UserProfile when a User is created.

    This ensures that all users have a UserProfile, regardless of how they were created
    (traditional signup, social auth, admin, or via fixtures).

    This provides redundancy to the CustomSocialAccountAdapter.save_user() method.
    """
    if created:
        if not hasattr(instance, 'userprofile'):
            UserProfile.objects.create(
                user=instance,
                phone='',
                address='',
                pincode='',
            )


@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    """
    Signal handler to save UserProfile when the User is saved.

    This ensures that any changes to the related UserProfile are persisted.
    """
    if hasattr(instance, 'userprofile'):
        instance.userprofile.save()
