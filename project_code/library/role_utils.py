"""Role helpers: one login session = one portal (admin, delivery, or customer)."""

ROLE_ADMIN = 'admin'
ROLE_DELIVERY = 'delivery'
ROLE_CUSTOMER = 'customer'

ADMIN_HOME = 'admin_dashboard'
DELIVERY_HOME = 'delivery_dashboard'
CUSTOMER_HOME = 'home'


def user_can_admin(user):
    return user.is_authenticated and user.is_superuser


def user_can_delivery(user):
    if not user.is_authenticated:
        return False
    try:
        if user.deliverystaff.active:
            return True
    except Exception:
        pass
    try:
        return bool(user.deliveryrider)
    except Exception:
        return False


def user_can_customer(user):
    return user.is_authenticated


def allowed_roles_for_user(user):
    roles = []
    if user_can_admin(user):
        roles.append(ROLE_ADMIN)
    if user_can_delivery(user):
        roles.append(ROLE_DELIVERY)
    if not user_can_admin(user) and not user_can_delivery(user):
        roles.append(ROLE_CUSTOMER)
    return roles


def validate_role_login(user, role):
    if role == ROLE_ADMIN:
        return user_can_admin(user)
    if role == ROLE_DELIVERY:
        return user_can_delivery(user)
    if role == ROLE_CUSTOMER:
        return (
            user_can_customer(user)
            and not user_can_admin(user)
            and not user_can_delivery(user)
        )
    return False


def detect_login_role(user):
    """Pick portal from account type (admin → delivery → reader)."""
    if user_can_admin(user):
        return ROLE_ADMIN
    if user_can_delivery(user):
        return ROLE_DELIVERY
    return ROLE_CUSTOMER


def home_url_name_for_role(role):
    if role == ROLE_ADMIN:
        return ADMIN_HOME
    if role == ROLE_DELIVERY:
        return DELIVERY_HOME
    return CUSTOMER_HOME
