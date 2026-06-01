from functools import wraps

from django.contrib.auth.views import redirect_to_login
from django.shortcuts import redirect

from .role_utils import (
    ROLE_ADMIN,
    ROLE_DELIVERY,
    home_url_name_for_role,
    user_can_admin,
    user_can_delivery,
)


def portal_login_required(view_func):
    """Like login_required but always preserves ?next= for return after login."""

    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect_to_login(request.get_full_path(), 'login')
        return view_func(request, *args, **kwargs)

    return wrapper


def admin_portal_required(view_func):
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect_to_login(request.get_full_path(), 'login')
        if not user_can_admin(request.user):
            role = request.session.get('login_role')
            if role == ROLE_DELIVERY and user_can_delivery(request.user):
                return redirect(home_url_name_for_role(ROLE_DELIVERY))
            return redirect('home')
        if request.session.get('login_role') not in (None, ROLE_ADMIN):
            return redirect(home_url_name_for_role(ROLE_ADMIN))
        return view_func(request, *args, **kwargs)

    return wrapper


def delivery_portal_required(view_func):
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect_to_login(request.get_full_path(), 'login')
        if not user_can_delivery(request.user):
            return redirect('home')
        if request.session.get('login_role') not in (None, ROLE_DELIVERY):
            return redirect(home_url_name_for_role(ROLE_DELIVERY))
        return view_func(request, *args, **kwargs)

    return wrapper
