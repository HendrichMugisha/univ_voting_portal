# to ensure the settings are dynamic both for development and deployment
import dj_database_url
import os 

# to read enviroment variables
from decouple import config

from pathlib import Path
from django.contrib.messages import constants as messages

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent


# ==============================================================================
# CORE SETTINGS (MOVED TO TOP)
# ==============================================================================

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = config('SECRET_KEY')

# This checks for Render's built-in environment variable
IS_PRODUCTION = os.environ.get('RENDER') == 'true'

# SECURITY WARNING: don't run with debug turned on in production!
if IS_PRODUCTION:
    DEBUG = False
else:
    DEBUG = True

ALLOWED_HOSTS = ['127.0.0.1', 'localhost']

# This code is for Render. It automatically adds Render's hostname.
RENDER_EXTERNAL_HOSTNAME = os.environ.get('RENDER_EXTERNAL_HOSTNAME')
if RENDER_EXTERNAL_HOSTNAME:
    ALLOWED_HOSTS.append(RENDER_EXTERNAL_HOSTNAME)


# ==============================================================================
# APPLICATION & MIDDLEWARE
# ==============================================================================

# Application definition
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'votingapp',
    'storages',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    # WhiteNoise middleware should be placed AFTER SecurityMiddleware
    'whitenoise.middleware.WhiteNoiseMiddleware', 
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


# ==============================================================================
# DATABASE & AUTHENTICATION
# ==============================================================================

# Reads DATABASE_URL from .env or Render's environment
DATABASES = {
    'default': dj_database_url.config(
        default=config('DATABASE_URL'),
        ssl_require=IS_PRODUCTION # Require SSL only in production
    )
}


# Password validation
# https://docs.djangoproject.com/en/5.2/ref/settings/#auth-password-validators
AUTH_PASSWORD_VALIDATORS = [
    # ... (Your validators are unchanged) ...
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]


# ==============================================================================
# INTERNATIONALIZATION
# ==============================================================================
LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = True


# ==============================================================================
# STATIC & MEDIA FILES (THE BIG FIX)
# ==============================================================================

# --- Static files (CSS, JavaScript, Images) ---

# this is to load the static files
STATIC_URL = '/static/'
# this is the folder where the static files are
STATICFILES_DIRS = [
    BASE_DIR / 'static',
]

# --- Production vs. Development Storage ---

if IS_PRODUCTION:
    # --- PRODUCTION SETTINGS (Render) ---
    
    # Static files (WhiteNoise)
    # The folder where 'collectstatic' will copy all files for production
    STATIC_ROOT = BASE_DIR / 'staticfiles'
    # The storage engine that WhiteNoise provides
    STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'
    
    # Media files (S3)
    # These are read from Render's env
    AWS_ACCESS_KEY_ID = config('AWS_ACCESS_KEY_ID')
    AWS_SECRET_ACCESS_KEY = config('AWS_SECRET_ACCESS_KEY')
    AWS_STORAGE_BUCKET_NAME = config('AWS_STORAGE_BUCKET_NAME')
    AWS_S3_REGION_NAME = config('AWS_S3_REGION_NAME')
    
    # This is the bucket's website URL
    AWS_S3_CUSTOM_DOMAIN = f'{AWS_STORAGE_BUCKET_NAME}.s3.amazonaws.com'
    AWS_S3_OBJECT_PARAMETERS = {
        'CacheControl': 'max-age=86400', # Cache files for 1 day
    }
    
    # This is the storage backend for user-uploaded files (media)
    DEFAULT_FILE_STORAGE = 'storages.backends.s3boto3.S3Boto3Storage'
    
    # We must set this so django-storages knows where to put new files
    AWS_LOCATION = 'media'
    MEDIA_URL = f'https://{AWS_S3_CUSTOM_DOMAIN}/{AWS_LOCATION}/'

else:
    # --- DEVELOPMENT SETTINGS (Local) ---
    
    # Static files (Django's built-in)
    # We don't need to set STATIC_ROOT or STATICFILES_STORAGE
    
    # Media files (Local)
    # In local development (DEBUG=True), just use the local file system.
    MEDIA_URL = '/media/'
    MEDIA_ROOT = BASE_DIR / 'media'
    

# ==============================================================================
# OTHER SETTINGS
# ==============================================================================

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# this converts standard django messages into bootstrap classes
MESSAGE_TAGS = {
    messages.DEBUG: 'alert-secondary',
    messages.INFO: 'alert-info',
    messages.SUCCESS: 'alert-success',
    messages.WARNING: 'alert-warning',
    messages.ERROR: 'alert-danger',
}

# --- Your debug print statements (keep these for now) ---
print("==================================================")
render_env_var = os.environ.get('RENDER')
print(f"--- [DEPLOY CHECK] The 'RENDER' variable is: {render_env_var} ---")
print(f"--- [DEPLOY CHECK] The type is: {type(render_env_var)} ---")
print(f"--- [DEPLOY CHECK] IS_PRODUCTION is set to: {IS_PRODUCTION} ---")
print(f"--- [DEPLOY CHECK] DEBUG is set to: {DEBUG} ---")
print("==================================================")