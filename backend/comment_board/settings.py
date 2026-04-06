from decouple import config, Csv
import dj_database_url
from pathlib import Path
import os

# ---- Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent


# ---- Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/6.0/howto/deployment/checklist/

# ---- SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = config(
    "SECRET_KEY", default="django-insecure-build-key-change-in-production"
)
# ---- SECURITY WARNING: don't run with debug turned on in production!
DEBUG = config("DEBUG", default=False, cast=bool)

ALLOWED_HOSTS = config("ALLOWED_HOSTS", default="", cast=Csv())


# ---- Application definition

INSTALLED_APPS = [
    "daphne",  # Django Channels for WebSocket support
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    # ---- Third-party apps
    "rest_framework",
    "cacheops",
    "corsheaders",
    "captcha",
    "comments",
]

MIDDLEWARE = [
    "corsheaders.middleware.CorsMiddleware",  # Add CORS middleware at the top
    "django.middleware.security.SecurityMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",  #  Maintenance of static files in production
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "comment_board.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / "templates"],
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
# ---- WSGI application and ASGI application for WebSocket support
WSGI_APPLICATION = "comment_board.wsgi.application"
ASGI_APPLICATION = "comment_board.asgi.application"


# https://docs.djangoproject.com/en/6.0/ref/settings/#databases


DATABASE_URL = config("DATABASE_URL", default=None)

if DATABASE_URL:
    DATABASES = {
        "default": dj_database_url.config(
            default=DATABASE_URL, conn_max_age=600, conn_health_checks=True
        )
    }
else:
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.postgresql",
            "NAME": config("NAME"),
            "USER": config("USER"),
            "PASSWORD": config("PASSWORD"),
            "HOST": config("HOST"),
            "PORT": "5432",
        }
    }


# https://docs.djangoproject.com/en/6.0/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.CommonPasswordValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.NumericPasswordValidator",
    },
]


# https://docs.djangoproject.com/en/6.0/topics/i18n/

LANGUAGE_CODE = "en-us"

TIME_ZONE = "UTC"

USE_I18N = True

USE_TZ = True


# https://docs.djangoproject.com/en/6.0/howto/static-files/

STATIC_URL = "static/"
STATIC_ROOT = os.path.join(BASE_DIR, "staticfiles")

# ---- Media files (uploads)
MEDIA_URL = "media/"
MEDIA_ROOT = os.path.join(BASE_DIR, "media")

# WriteNoise for compression and caching
STATICFILES_STORAGE = "whitenoise.storage.CompressedManifestStaticFilesStorage"


# ________________________________________________________________________________________

# ---- For WebSockets
# ---- Configures the way messages are passed between WebSocket connections.
CHANNEL_LAYERS = {
    "default": {
        "BACKEND": "channels_redis.core.RedisChannelLayer",
        "CONFIG": {
            "hosts": [config("REDIS_HOST", default="redis://redis:6379/0")],
        },
    }
}
# ---- Redis cache configuration
CACHEOPS = {
    "comments.comment": {"ops": "all", "timeout": 60 * 60 * 24}  # Cache for 24 hours
}

CACHEOPS_REDIS = config("CACHEOPS_REDIS", default="redis://redis:6379/2")

# ---- Allowed origins for CORS (local dev)
CORS_ALLOWED_ORIGINS = config(
    "CORS_ALLOWED_ORIGINS",
    default="http://localhost:5173,http://127.0.0.1:5173",
    cast=Csv(),
)

# ---- Cloudinary configuration (Media files)
# ---- To upload to the cloud
STORAGES = {
    "default": {
        "BACKEND": "django.core.files.storage.FileSystemStorage",
    },
    "raw": {
        "BACKEND": "django.core.files.storage.FileSystemStorage",
    },
    "staticfiles": {
        "BACKEND": "django.contrib.staticfiles.storage.StaticFilesStorage",
    },
}
# ---- Logic to choose between local storage and Cloudinary based on environment settings
if config("USE_CLOUDINARY", default=False, cast=bool):
    INSTALLED_APPS += ["cloudinary_storage", "cloudinary"]
    STORAGES["default"]["BACKEND"] = "cloudinary_storage.storage.MediaCloudinaryStorage"
    STORAGES["raw"]["BACKEND"] = "cloudinary_storage.storage.RawMediaCloudinaryStorage"
    CLOUDINARY_STORAGE = {
        "CLOUD_NAME": config("CLOUDINARY_CLOUD_NAME"),
        "API_KEY": config("CLOUDINARY_API_KEY"),
        "API_SECRET": config("CLOUDINARY_API_SECRET"),
    }

# ---- Captcha configuration
CAPTCHA_FONT_SIZE = 36
CAPTCHA_BACKGROUND_COLOR = "#ffffff"
CAPTCHA_FOREGROUND_COLOR = "#333333"
CAPTCHA_NOISE_FUNCTIONS = ("captcha.helpers.noise_arcs",)
CAPTCHA_LENGTH = 5
