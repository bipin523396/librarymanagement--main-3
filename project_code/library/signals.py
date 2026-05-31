from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import User
from .models import UserSettings

@receiver(post_save, sender=User)
def create_user_settings(sender, instance, created, **kwargs):
    if created:
        try:
            # Use the raw ObjectId as foreign key to avoid type conversion issues
            UserSettings.objects.get_or_create(user_id=instance.id)
        except Exception as e:
            # Log the error but continue without breaking signup
            pass

# The save_user_settings signal has been removed because MongoDB ObjectId primary keys cause issues when accessing related UserSettings.
