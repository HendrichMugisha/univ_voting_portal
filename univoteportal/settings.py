# ======================================================================
# IMPORTS
# ======================================================================
import os
from pathlib import Path
from decouple import config
import dj_database_url
from django.contrib.messages import constants as messages

# ======================================================================
# PATHS
# ======================================================================
BASE_DIR = Path(__file__).resolve().parent.parent

# ======================================================================
# CORE SETTINGS
# ======================================================================
SECRET_KEY = config("SECRET_KEY")

# Render sets RENDER = "true" in its environment
IS_PRODUCTION = os.environ.get("RENDER") == "true"
DEBUG = not IS_PRODUCTION

ALLOWED_HOSTS = ["127.0.0.1", "localhost"]

# Add Render's hostname if present
RENDER_EXTERNAL_HOSTNAME = os.environ.get("RENDER_EXTERNAL_HOSTNAME")
if RENDER_EXTERNAL_HOSTNAME:
    ALLOWED_HOSTS.append(RENDER_EXTERNAL_HOSTNAME)

# ======================================================================
# APPLICATION & MIDDLEWARE
# ======================================================================
INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "votingapp",
    "storages",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",  # after SecurityMiddleware
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "univoteportal.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": ["templates"],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

WSGI_APPLICATION = "univoteportal.wsgi.application"

# ======================================================================
# DATABASE
# ======================================================================
DATABASES = {
    "default": dj_database_url.config(
        default=config("DATABASE_URL"),
        ssl_require=IS_PRODUCTION,
    )
}

# ======================================================================
# PASSWORD VALIDATION
# ======================================================================
AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]

# ======================================================================
# INTERNATIONALIZATION
# ======================================================================
LANGUAGE_CODE = "en-us"
TIME_ZONE = "UTC"
USE_I18N = True
USE_TZ = True

# ======================================================================
# STATIC & MEDIA SETTINGS
# ======================================================================

# -------------------------
# STATIC FILES (always)
# -------------------------
STATIC_URL = "/static/"

STATICFILES_DIRS = [
    BASE_DIR / "static",
]

if IS_PRODUCTION:
    STATIC_ROOT = BASE_DIR / "staticfiles"
    STATICFILES_STORAGE = "whitenoise.storage.CompressedManifestStaticFilesStorage"


# -------------------------
# MEDIA FILES
# -------------------------

if IS_PRODUCTION:
    # ===========================
    # S3 CONFIG FOR PRODUCTION
    # ===========================

    AWS_ACCESS_KEY_ID = config("AWS_ACCESS_KEY_ID")
    AWS_SECRET_ACCESS_KEY = config("AWS_SECRET_ACCESS_KEY")
    AWS_STORAGE_BUCKET_NAME = config("AWS_STORAGE_BUCKET_NAME")
    AWS_S3_REGION_NAME = config("AWS_S3_REGION_NAME")

    AWS_S3_CUSTOM_DOMAIN = f"{AWS_STORAGE_BUCKET_NAME}.s3.amazonaws.com"
    AWS_QUERYSTRING_AUTH = False  # clean public URLs

    # Default S3 settings
    AWS_S3_OBJECT_PARAMETERS = {
        "CacheControl": "max-age=86400",  # 1 day cache
    }

    # Base location for media in S3
    AWS_LOCATION = "media"

    # Use **your backend file**
    DEFAULT_FILE_STORAGE = "univoteportal.storage_backends.MediaStorage"

    # Public media URL
    MEDIA_URL = f"https://{AWS_S3_CUSTOM_DOMAIN}/{AWS_LOCATION}/"

else:
    # ===========================
    # LOCAL DEVELOPMENT
    # ===========================
    MEDIA_URL = "/media/"
    MEDIA_ROOT = BASE_DIR / "media"

# ======================================================================
# MISC SETTINGS
# ======================================================================
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

MESSAGE_TAGS = {
    messages.DEBUG: "alert-secondary",
    messages.INFO: "alert-info",
    messages.SUCCESS: "alert-success",
    messages.WARNING: "alert-warning",
    messages.ERROR: "alert-danger",
}

# ======================================================================
# DEBUG PRINT (SAFE TO KEEP)
# ======================================================================
print("==================================================")
print(f"[Render] RENDER env var: {os.environ.get('RENDER')}")
print(f"[Render] IS_PRODUCTION = {IS_PRODUCTION}")
print(f"[Render] DEBUG = {DEBUG}")
print("==================================================")
