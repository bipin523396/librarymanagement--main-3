"""Role helpers: one login session = one portal (admin, delivery, or customer)."""

ROLE_ADMIN = 'admin'
ROLE_DELIVERY = 'delivery'
ROLE_CUSTOMER = 'customer'

ADMIN_HOME = 'admin_dashboard'
DELIVERY_HOME = 'delivery_dashboard'
CUSTOMER_HOME = 'home'


def user_can_admin(user):
    if user is None:
        return False
    try:
        if not user.is_authenticated:
            return False
    except Exception:
        return False
    return bool(getattr(user, 'is_superuser', False))


def _delivery_staff_active_in_mongo(username):
    try:
        import os
        from bookhub_backend.mongo_config import get_shared_client

        client = get_shared_client()
        if not client:
            return False
        db_name = os.getenv('MONGODB_NAME', 'bookhub_db')
        db = client[db_name]
        auth = db.auth_user.find_one({'username': username}, projection={'_id': 1})
        if not auth:
            return False
        uid = auth['_id']
        return db.library_deliverystaff.find_one({'user_id': uid, 'active': True}) is not None
    except Exception:
        return False


def user_can_delivery(user):
    if not user.is_authenticated:
        return False
    if _delivery_staff_active_in_mongo(user.get_username()):
        return True
    try:
        if user.deliverystaff.active:
            return True
    except Exception:
        pass
    try:
        from bson import ObjectId
        from library.models import DeliveryStaff
        from library.auth_backend import resolve_user_pk

        uid = resolve_user_pk(user)
        if uid:
            ids = [uid]
            try:
                ids.append(ObjectId(str(uid)))
            except Exception:
                pass
            if DeliveryStaff.objects.filter(user_id__in=ids, active=True).exists():
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
