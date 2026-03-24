from allauth.socialaccount.adapter import DefaultSocialAccountAdapter
from django.contrib.auth.models import User
from .models import UserProfile


class CustomSocialAccountAdapter(DefaultSocialAccountAdapter):
    """
    Custom adapter to handle UserProfile creation for social login users.

    This adapter ensures that:
    1. Users logging in with existing email are linked to their existing account
    2. New users get a UserProfile created automatically
    3. User data from social providers is properly populated
    """

    def pre_social_login(self, request, sociallogin):
        """
        Called before social login is processed.

        This method checks if a user with the provided email already exists.
        If it does, we link the social account to the existing user to prevent duplicates.
        """
        if sociallogin.is_existing:
            return

        try:
            # Get email from social provider data
            email = sociallogin.account.extra_data.get('email', '').lower()

            if not email:
                return

            # Check if user with this email already exists
            user = User.objects.get(email=email)

            # Link the social account to the existing user
            sociallogin.connect(request, user)
        except User.DoesNotExist:
            # New user will be created
            pass

    def save_user(self, request, sociallogin, form=None):
        """
        Called to save a newly created user during social signup.

        Creates the user and ensures a UserProfile exists with default values.
        """
        user = super().save_user(request, sociallogin, form)

        # Ensure UserProfile exists for all users
        if not hasattr(user, 'userprofile'):
            UserProfile.objects.create(
                user=user,
                phone='',  # User can fill in later
                address='',
                pincode='',
            )

        return user

    def populate_user(self, request, sociallogin, data):
        """
        Populate user instance with data from the social provider.

        Extracts first name and last name from the provider's data.
        """
        user = super().populate_user(request, sociallogin, data)

        # Populate first and last name from social provider
        if 'first_name' in data:
            user.first_name = data.get('first_name', '')
        if 'last_name' in data:
            user.last_name = data.get('last_name', '')

        return user
