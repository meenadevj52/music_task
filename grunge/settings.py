"""
Django settings for grunge project.

Generated by 'django-admin startproject' using Django 3.1.1.

For more information on this file, see
https://docs.djangoproject.com/en/3.1/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/3.1/ref/settings/
"""

from pathlib import Path

from environ import Env
import os

ENV = Env()


DJANGO_ADMIN_ENABLED = ENV.bool("DJANGO_ADMIN_ENABLED", True)
DJANGO_API_ENABLED = ENV.bool("DJANGO_API_ENABLED", True)


# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/3.1/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = ENV.str("SECRET_KEY", "debug-secret")

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = ENV.bool("DEBUG", True)

ALLOWED_HOSTS = ENV.list("ALLOWED_HOSTS", default=["*"])
INTERNAL_IPS = ["127.0.0.1"]


# Logging
LOG_LEVEL = ENV.str("DJANGO_LOG_LEVEL", "INFO").upper()
LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "handlers": {"console": {"level": LOG_LEVEL, "class": "logging.StreamHandler"}},
    "loggers": {"grunge": {"handlers": ["console"], "level": LOG_LEVEL}},
}

# Application definition

INSTALLED_APPS = [
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "django.contrib.humanize",
    "django_filters",
    "rest_framework",
    "rest_framework.authtoken",
    "grunge",
    "django.contrib.admin",
    "corsheaders",
]

MIDDLEWARE = [
    "corsheaders.middleware.CorsMiddleware",
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

CORS_ALLOWED_ORIGINS = [
    "http://127.0.0.1:8000",
    "http://localhost:8000",
]

ROOT_URLCONF = "grunge.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [os.path.join(BASE_DIR, "templates")],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

WSGI_APPLICATION = "grunge.wsgi.application"

# Sessions
SESSION_ENGINE = ENV.str(
    "SESSION_ENGINE", "django.contrib.sessions.backends.signed_cookies"
)
SESSION_COOKIE_HTTPONLY = True
SESSION_COOKIE_NAME = ENV.str("SESSION_COOKIE_NAME", "sessionid")
SESSION_COOKIE_DOMAIN = ENV.str("SESSION_COOKIE_DOMAIN", None)
SESSION_COOKIE_SECURE = ENV.bool("REQUIRE_HTTPS", not DEBUG)

CSRF_USE_SESSIONS = True
CSRF_TRUSTED_ORIGINS = ENV.list("CSRF_TRUSTED_ORIGINS", default=[])
if SESSION_COOKIE_DOMAIN:
    CSRF_TRUSTED_ORIGINS.append(SESSION_COOKIE_DOMAIN)

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# Database
# https://docs.djangoproject.com/en/3.1/ref/settings/#databases
DATABASES = {
    "default": ENV.db_url(default="sqlite:///{}".format(BASE_DIR / "db.sqlite3"))
}

# Password validation
# https://docs.djangoproject.com/en/3.1/ref/settings/#auth-password-validators

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


# Internationalization
# https://docs.djangoproject.com/en/3.1/topics/i18n/

LANGUAGE_CODE = "en-us"

TIME_ZONE = "UTC"

USE_I18N = True

USE_L10N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/3.1/howto/static-files/
STATIC_URL = "/static/"
STATIC_ROOT = ENV.str("STATIC_ROOT", BASE_DIR / "static")

MEDIA_URL = ENV.str("MEDIA_URL", "/media/")
MEDIA_ROOT = ENV.str("MEDIA_ROOT", BASE_DIR / "media")

# API
# http://www.django-rest-framework.org/
# https://django-oauth-toolkit.readthedocs.io/en/latest/index.html
REST_FRAMEWORK = {
    "DEFAULT_VERSIONING_CLASS": "rest_framework.versioning.URLPathVersioning",
    "DEFAULT_VERSION": ENV.str("DEFAULT_API_VERSION", "v1"),
    "ALLOWED_VERSIONS": ENV.list("ALLOWED_API_VERSIONS", default=["v1"]),
    "DEFAULT_AUTHENTICATION_CLASSES": (
        "rest_framework.authentication.TokenAuthentication",
    ),
    "DEFAULT_FILTER_BACKENDS": (
        "django_filters.rest_framework.DjangoFilterBackend",
        "rest_framework.filters.OrderingFilter",
    ),
    "DEFAULT_RENDERER_CLASSES": [
        "rest_framework.renderers.JSONRenderer",
    ],
    "DEFAULT_PARSER_CLASSES": (
        "rest_framework.parsers.FormParser",
        "rest_framework.parsers.MultiPartParser",
        "rest_framework.parsers.JSONParser",
        "rest_framework.parsers.FileUploadParser",
    ),
    "DEFAULT_PAGINATION_CLASS": "grunge.pagination.PageNumberPagination",
    "PAGE_SIZE": ENV.int("API_PAGE_SIZE", 10),
}
PAGE_SIZE_QUERY_PARAM = ENV.str("PAGE_SIZE_QUERY_PARAM", "page_size")

if DEBUG:
    REST_FRAMEWORK["DEFAULT_RENDERER_CLASSES"].append(
        "rest_framework.renderers.BrowsableAPIRenderer"
    )
