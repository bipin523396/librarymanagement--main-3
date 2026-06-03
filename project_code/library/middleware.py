"""Keep users on their portal and remember where they were before auth expires."""

from django.shortcuts import redirect
from django.urls import reverse

from .role_utils import (
    ROLE_ADMIN,
    ROLE_DELIVERY,
    ROLE_CUSTOMER,
    home_url_name_for_role,
    user_can_admin,
    user_can_delivery,
)

# Paths any logged-in user may hit
PUBLIC_AUTH_PATHS = (
    '/login/',
    '/logout/',
    '/signup/',
    '/password-reset',
    '/health/',
    '/wake/',
    '/loading/',
    '/test-db/',
    '/i18n/',
    '/static/',
    '/media/',
    '/admin/',  # Django admin
)

ADMIN_PREFIX = '/admin-dashboard/'
DELIVERY_PREFIX = '/delivery/'
CUSTOMER_ONLY_PREFIXES = (
    '/dashboard/',
    '/profile/',
    '/settings/',
    '/cart/',
    '/wishlist/',
    '/checkout/',
    '/my-rentals/',
    '/payment',
    '/premium-checkout/',
)


def _path(request):
    return request.path or ''


def _is_public(path):
    return any(p in path for p in PUBLIC_AUTH_PATHS)


class RolePortalMiddleware:
    """
    Enforce session login_role so one account uses one portal at a time.
    Remember last URL so re-login can return to the same page.
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        path = _path(request)

        try:
            is_authenticated = request.user.is_authenticated
        except Exception:
            request.session.flush()
            is_authenticated = False

        if is_authenticated and not _is_public(path):
            request.session['last_portal_path'] = request.get_full_path()

        role = request.session.get('login_role')
        if is_authenticated and role and not _is_public(path):
            block = self._blocked_redirect(request, role, path)
            if block:
                return block

        try:
            return self.get_response(request)
        except Exception as e:
            import logging
            logger = logging.getLogger('library')
            logger.error(f"Global Middleware Exception on {path}: {e}", exc_info=True)
            
            # If the site crashes, don't show a 500. Try to redirect home or login.
            if _is_public(path):
                raise # Let public paths (like health checks) fail normally
            
            # For private paths, try to recover
            try:
                request.session.flush()
                return redirect('home')
            except Exception:
                raise e # Last resort: standard 500

    def _blocked_redirect(self, request, role, path):
        if role == ROLE_ADMIN:
            if DELIVERY_PREFIX in path:
                return redirect(home_url_name_for_role(ROLE_ADMIN))
            if path.rstrip('/').endswith('/library') or path.endswith('/library/'):
                return redirect(home_url_name_for_role(ROLE_ADMIN))
            if any(p in path for p in CUSTOMER_ONLY_PREFIXES):
                return redirect(home_url_name_for_role(ROLE_ADMIN))

        if role == ROLE_DELIVERY:
            if ADMIN_PREFIX in path and '/update-delivery/' not in path:
                return redirect(home_url_name_for_role(ROLE_DELIVERY))
            if path.rstrip('/').endswith('/library') or path.endswith('/library/'):
                return redirect(home_url_name_for_role(ROLE_DELIVERY))
            if any(p in path for p in CUSTOMER_ONLY_PREFIXES):
                return redirect(home_url_name_for_role(ROLE_DELIVERY))

        if role == ROLE_CUSTOMER:
            if ADMIN_PREFIX in path or DELIVERY_PREFIX in path:
                return redirect(home_url_name_for_role(ROLE_CUSTOMER))

        return None


class LoginNextMiddleware:
    """Send unauthenticated users to login with ?next= so refresh-after-login returns here."""

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)

        if getattr(response, 'status_code', None) == 302:
            location = response.get('Location', '')
            login_path = reverse('login')
            if login_path in location and 'next=' not in location:
                full = request.get_full_path()
                if full and full != login_path:
                    from urllib.parse import urlencode
                    sep = '&' if '?' in location else '?'
                    response['Location'] = f'{location}{sep}{urlencode({"next": full})}'

        return response
