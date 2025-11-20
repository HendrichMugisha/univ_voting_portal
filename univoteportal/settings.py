# ======================================================================
# IMPORTS
# ======================================================================
import os
from pathlib import Path
from decouple import config
import dj_database_url
from django.contrib.messages import constants as messages

# ======================================================================
# PATHS & CORE SETUP
# ======================================================================
BASE_DIR = Path(__file__).resolve().parent.parent

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = config('SECRET_KEY')

# --- ENVIRONMENT LOGIC ---
# We check if we are on Render to set IS_PRODUCTION.
IS_PRODUCTION = config('RENDER', default=False, cast=bool)

# Debug is True locally, False in production (unless forced)
DEBUG = config('DEBUG', default=not IS_PRODUCTION, cast=bool)

# --- HOSTS ---
ALLOWED_HOSTS = ['127.0.0.1', 'localhost']

# 1. If on Render, add the internal hostname
RENDER_EXTERNAL_HOSTNAME = os.environ.get('RENDER_EXTERNAL_HOSTNAME')
if RENDER_EXTERNAL_HOSTNAME:
    ALLOWED_HOSTS.append(RENDER_EXTERNAL_HOSTNAME)

# 2. If in production, allow the live URL (or '*' for simplicity in demos)
if IS_PRODUCTION:
    ALLOWED_HOSTS.append('*')


# ======================================================================
# APPLICATION DEFINITION
# ======================================================================
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    # Third-party apps
    'storages',   # For S3
    # Your apps
    'votingapp',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware', # MUST be after SecurityMiddleware
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'univoteportal.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': ['templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'univoteportal.wsgi.application'


# ======================================================================
# DATABASE
# ======================================================================
DATABASES = {
    'default': dj_database_url.config(
        default=config('DATABASE_URL'),
        ssl_require=IS_PRODUCTION # Require SSL only in production
    )
}


# ======================================================================
# AUTHENTICATION & PASSWORD VALIDATORS
# ======================================================================
AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]


# ======================================================================
# INTERNATIONALIZATION
# ======================================================================
LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = True


# ======================================================================
# STATIC & MEDIA FILES (New Django 4.2+ STORAGES Configuration)
# ======================================================================

# Base Static Settings (Used everywhere)
STATIC_URL = '/static/'
STATICFILES_DIRS = [BASE_DIR / 'static']

if IS_PRODUCTION:
    # --- PRODUCTION SETTINGS (Render) ---
    
    # 1. AWS S3 Settings
    AWS_ACCESS_KEY_ID = config('AWS_ACCESS_KEY_ID')
    AWS_SECRET_ACCESS_KEY = config('AWS_SECRET_ACCESS_KEY')
    AWS_STORAGE_BUCKET_NAME = config('AWS_STORAGE_BUCKET_NAME')
    AWS_S3_REGION_NAME = config('AWS_S3_REGION_NAME')
    AWS_S3_CUSTOM_DOMAIN = f'{AWS_STORAGE_BUCKET_NAME}.s3.amazonaws.com'
    AWS_S3_OBJECT_PARAMETERS = {'CacheControl': 'max-age=86400'}

    # 2. Storage Configuration (The Modern Way)
    STORAGES = {
        # "default" controls Media files (uploads) -> Goes to S3
        "default": {
            "BACKEND": "storages.backends.s3boto3.S3Boto3Storage",
            "OPTIONS": {
                "location": "media", # Save files to 'media/' folder in bucket
            },
        },
        # "staticfiles" controls Static CSS/JS -> Goes to WhiteNoise
        "staticfiles": {
            "BACKEND": "whitenoise.storage.CompressedStaticFilesStorage",
        },
    }

    # URLs for Production
    MEDIA_URL = f'https://{AWS_S3_CUSTOM_DOMAIN}/media/'
    STATIC_ROOT = BASE_DIR / 'staticfiles'

else:
    # --- LOCAL SETTINGS (Development) ---
    
    STORAGES = {
        "default": {
            "BACKEND": "django.core.files.storage.FileSystemStorage",
        },
        "staticfiles": {
            "BACKEND": "django.contrib.staticfiles.storage.StaticFilesStorage",
        },
    }

    # URLs for Local Dev
    MEDIA_URL = '/media/'
    MEDIA_ROOT = BASE_DIR / 'media'


# ======================================================================
# MISC SETTINGS
# ======================================================================
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# Bootstrap Alert Classes
MESSAGE_TAGS = {
    messages.DEBUG: 'alert-secondary',
    messages.INFO: 'alert-info',
    messages.SUCCESS: 'alert-success',
    messages.WARNING: 'alert-warning',
    messages.ERROR: 'alert-danger',
}

# ======================================================================
# DEBUG CHECKS (Visible in Render Logs)
# ======================================================================
print("==================================================")
print(f"--- [SETTINGS CHECK] IS_PRODUCTION: {IS_PRODUCTION}")
print(f"--- [SETTINGS CHECK] DEBUG: {DEBUG}")
print(f"--- [SETTINGS CHECK] Database Configured: {bool(DATABASES['default'])}")
print("==================================================")