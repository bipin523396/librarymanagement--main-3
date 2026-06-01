import os
from pathlib import Path
import pymysql
from dotenv import load_dotenv

pymysql.install_as_MySQLdb()

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# Load environment variables from .env file
load_dotenv(os.path.join(BASE_DIR, '.env'))

# Quick-start development settings - unsuitable for production
SECRET_KEY = os.getenv('SECRET_KEY')
DEBUG = True
ALLOWED_HOSTS = ["*"]
CSRF_TRUSTED_ORIGINS = [
    "http://127.0.0.1:8000",
    "http://localhost:8000",
    "https://librarymanagement-main-3.vercel.app",
    "https://*.vercel.app",
]

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
            ],
        },
    },
]

WSGI_APPLICATION = 'bookhub_backend.wsgi.application'

# Database
DATABASES = {
    'default': {
        'ENGINE': 'djongo',
        'NAME': os.getenv('MONGODB_NAME', 'bookhub_db'),
        'ENFORCE_SCHEMA': False,
        'CLIENT': {
            'host': os.getenv('DJANGO_DATABASE_URL', os.getenv('MONGODB_URI')),
        },
    }
}

AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.password_validation.CommonPasswordValidator'},
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
STATICFILES_DIRS = [os.path.join(BASE_DIR, 'library/static')]
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'



X_FRAME_OPTIONS = 'SAMEORIGIN'
SECURE_CROSS_ORIGIN_OPENER_POLICY = None
LOGIN_URL = '/en/library/login/'
LOGIN_REDIRECT_URL = '/'
LOGOUT_REDIRECT_URL = '/'

EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

CSRF_COOKIE_NAME = "bookhub_csrf_token"
SESSION_COOKIE_NAME = "bookhub_session_id"
ACCOUNT_LOGOUT_ON_GET = True

