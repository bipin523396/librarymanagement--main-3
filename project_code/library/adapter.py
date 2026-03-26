from allauth.socialaccount.adapter import DefaultSocialAccountAdapter
from django.contrib.auth import get_user_model
from django.conf import settings

User = get_user_model()

class MySocialAccountAdapter(DefaultSocialAccountAdapter):
    def get_connect_redirect_url(self, request, sociallogin):
        # Force the redirect URL to use 127.0.0.1 to match Google Console exactly
        url = super().get_connect_redirect_url(request, sociallogin)
        return url.replace('localhost', '127.0.0.1')

    def get_callback_url(self, request, app):
        # Force the callback URL domain to 127.0.0.1
        callback_url = super().get_callback_url(request, app)
        if 'localhost' in callback_url:
            callback_url = callback_url.replace('localhost', '127.0.0.1')
        return callback_url

    def populate_user(self, request, sociallogin, data):
        user = super().populate_user(request, sociallogin, data)
        # Ensure username is the email for consistency
        user.username = data.get('email')
        return user

    def pre_social_login(self, request, sociallogin):
        """
        Auto login if a user with this email already exists manually
        """
        if sociallogin.is_existing:
            return

        # Try to find user by email
        email = sociallogin.account.extra_data.get('email')
        if not email:
            return

        try:
            user = User.objects.get(email=email)
            # Connect the social account to the existing user
            sociallogin.connect(request, user)
        except User.DoesNotExist:
            pass
