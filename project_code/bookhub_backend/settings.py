import os
from pathlib import Path
import pymysql
from dotenv import load_dotenv

pymysql.install_as_MySQLdb()

BASE_DIR = Path(__file__).resolve().parent.parent

load_dotenv(os.path.join(BASE_DIR, '.env'))
load_dotenv(os.path.join(BASE_DIR.parent, '.env'))

SECRET_KEY = os.getenv('SECRET_KEY', 'change-me-in-production')
DEBUG = os.getenv('DEBUG', 'False').lower() in ('true', '1', 'yes')

_allowed_hosts = os.getenv(
    'ALLOWED_HOSTS',
    'localhost,127.0.0.1,testserver,.onrender.com,.vercel.app',
)
ALLOWED_HOSTS = [h.strip() for h in _allowed_hosts.split(',') if h.strip()]
if 'testserver' not in ALLOWED_HOSTS:
    ALLOWED_HOSTS.append('testserver')

_render_host = os.getenv('RENDER_EXTERNAL_HOSTNAME', 'librarymanagement-main-3.onrender.com')
if _render_host and _render_host not in ALLOWED_HOSTS:
    ALLOWED_HOSTS.append(_render_host)
if 'librarymanagement-main-3.onrender.com' not in ALLOWED_HOSTS:
    ALLOWED_HOSTS.append('librarymanagement-main-3.onrender.com')
if 'librarymanagement-main-3.vercel.app' not in ALLOWED_HOSTS:
    ALLOWED_HOSTS.append('librarymanagement-main-3.vercel.app')

_vercel_url = os.getenv('VERCEL_URL', '')
if _vercel_url:
    ALLOWED_HOSTS.append(_vercel_url)

# CSRF: Django 4.x requires full https:// URLs (not bare domain names)
_csrf_extra = os.getenv('CSRF_TRUSTED_ORIGINS', '')
CSRF_TRUSTED_ORIGINS = [
    'https://*.vercel.app',
    'https://*.onrender.com',
    'https://librarymanagement-main-3.onrender.com',
    'https://librarymanagement-main-3tx9.onrender.com',
]
for _origin in _csrf_extra.split(','):
    _origin = _origin.strip()
    if not _origin:
        continue
    # Ensure it has a scheme prefix
    if not _origin.startswith(('https://', 'http://')):
        _origin = 'https://' + _origin
    if _origin not in CSRF_TRUSTED_ORIGINS:
        CSRF_TRUSTED_ORIGINS.append(_origin)

_render_public = os.getenv('RENDER_EXTERNAL_URL', '').strip()
if _render_public:
    _host = _render_public.replace('https://', '').replace('http://', '').split('/')[0]
    if _host not in ALLOWED_HOSTS:
        ALLOWED_HOSTS.append(_host)
    _csrf_render = 'https://' + _host
    if _csrf_render not in CSRF_TRUSTED_ORIGINS:
        CSRF_TRUSTED_ORIGINS.append(_csrf_render)

_frontend = os.getenv('FRONTEND_URL', '').strip()
if _frontend:
    _host = _frontend.replace('https://', '').replace('http://', '').split('/')[0]
    _csrf_frontend = 'https://' + _host
    if _csrf_frontend not in CSRF_TRUSTED_ORIGINS:
        CSRF_TRUSTED_ORIGINS.append(_csrf_frontend)

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'library.apps.LibraryConfig',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.locale.LocaleMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'library.session_middleware.MongoAuthSessionMiddleware',
    'library.middleware.RolePortalMiddleware',
    'library.middleware.LoginNextMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'bookhub_backend.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR, 'templates')],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'django.template.context_processors.i18n',
                'library.context_processors.site_urls',
            ],
        },
    },
]

WSGI_APPLICATION = 'bookhub_backend.wsgi.application'

from bookhub_backend.mongo_config import get_mongodb_uri, mask_mongodb_uri, mongodb_username_from_uri

_MONGO_URI = get_mongodb_uri()
if not _MONGO_URI and not DEBUG:
    import sys
    print('FATAL: Set MONGODB_URI and DJANGO_DATABASE_URL on Render (see DEPLOYMENT.md)', file=sys.stderr)
elif _MONGO_URI:
    print(f'MongoDB: user={mongodb_username_from_uri(_MONGO_URI)} uri={mask_mongodb_uri(_MONGO_URI)}')

DATABASES = {
    'default': {
        'ENGINE': 'library.custom_djongo_backend',
        'NAME': os.getenv('MONGODB_NAME', 'bookhub_db'),
        'ENFORCE_SCHEMA': False,
        'CLIENT': {
            'host': _MONGO_URI,
            'connectTimeoutMS': 30000,
            'socketTimeoutMS': 30000,
            'serverSelectionTimeoutMS': 30000,
            'retryWrites': True,
        },
    }
}

AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

LANGUAGE_CODE = 'en'
LANGUAGES = [
    ('en', 'English'),
    ('hi', 'Hindi'),
    ('ta', 'Tamil'),
    ('te', 'Telugu'),
    ('kn', 'Kannada'),
    ('ml', 'Malayalam'),
    ('mr', 'Marathi'),
    ('bn', 'Bengali'),
    ('ur', 'Urdu'),
    ('pa', 'Punjabi'),
    ('ne', 'Nepali'),
]
LOCALE_PATHS = [os.path.join(BASE_DIR, 'locale')]
TIME_ZONE = 'UTC'
USE_I18N = True
USE_L10N = True
USE_TZ = True

STATIC_URL = '/static/'
STATICFILES_DIRS = [os.path.join(BASE_DIR, 'library', 'static')]
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')
STATICFILES_STORAGE = 'whitenoise.storage.CompressedStaticFilesStorage'

MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

AUTHENTICATION_BACKENDS = [
    'library.auth_backend.MongoModelBackend',
    'django.contrib.auth.backends.ModelBackend',
]

SESSION_ENGINE = 'django.contrib.sessions.backends.signed_cookies'
SESSION_COOKIE_AGE = 60 * 60 * 24 * 14
SESSION_SAVE_EVERY_REQUEST = True
SESSION_EXPIRE_AT_BROWSER_CLOSE = False

X_FRAME_OPTIONS = 'SAMEORIGIN'
SECURE_CROSS_ORIGIN_OPENER_POLICY = None

USE_X_FORWARDED_HOST = True
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')

LOGIN_URL = '/en/library/login/'
LOGIN_REDIRECT_URL = '/en/library/'
LOGOUT_REDIRECT_URL = '/en/library/login/'

EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

CSRF_COOKIE_NAME = 'bookhub_csrf_token'
SESSION_COOKIE_NAME = 'bookhub_session_id'
CSRF_COOKIE_HTTPONLY = False
SESSION_COOKIE_HTTPONLY = True
SESSION_COOKIE_SAMESITE = 'Lax'
CSRF_COOKIE_SAMESITE = 'Lax'
ACCOUNT_LOGOUT_ON_GET = True

_on_render = (
    os.getenv('RENDER', '').lower() in ('true', '1', 'yes')
    or bool(os.getenv('RENDER_EXTERNAL_URL', '').strip())
)
if not DEBUG:
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True
    # Render health checks hit HTTP on $PORT; SSL redirect breaks deploy probes.
    if _on_render:
        SECURE_SSL_REDIRECT = os.getenv('SECURE_SSL_REDIRECT', 'false').lower() in ('true', '1', 'yes')
    else:
        SECURE_SSL_REDIRECT = os.getenv('SECURE_SSL_REDIRECT', 'true').lower() in ('true', '1', 'yes')
else:
    SESSION_COOKIE_SECURE = False
    CSRF_COOKIE_SECURE = False
    SECURE_SSL_REDIRECT = False
