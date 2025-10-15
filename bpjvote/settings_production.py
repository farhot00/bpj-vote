"""
Production settings for bpjvote (Django 4.2)
"""
from pathlib import Path
import os
from dotenv import load_dotenv
from django.contrib import messages

# ------------------------------------------------------------------------------
# Base
# ------------------------------------------------------------------------------
BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv(BASE_DIR / ".env")  # read /srv/bpjvote/.env

SECRET_KEY = os.getenv("SECRET_KEY", "change-me")
DEBUG = os.getenv("DEBUG", "False") == "True"

ALLOWED_HOSTS = (
    os.getenv("ALLOWED_HOSTS", "127.0.0.1,localhost").replace(" ", "").split(",")
)

CSRF_TRUSTED_ORIGINS = [
    *(os.getenv("CSRF_TRUSTED_ORIGINS", "").replace(" ", "").split(",")),
]
CSRF_TRUSTED_ORIGINS = [o for o in CSRF_TRUSTED_ORIGINS if o]

# ------------------------------------------------------------------------------
# Apps
# ------------------------------------------------------------------------------
INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",

    # third-party
    "auditlog",
    "axes",
    "django_ratelimit",
    "turnstile",
    "cachalot",
    "sorl.thumbnail",
    "django_prometheus",
    "crispy_forms",
    "crispy_bootstrap4",  # ← تم Bootstrap 4 برای crispy

    # local
    "main",
    "vote",
]

AUTH_USER_MODEL = "main.User"

# Axes backend (رفع هشدار)
AUTHENTICATION_BACKENDS = [
    "axes.backends.AxesStandaloneBackend",
    "django.contrib.auth.backends.ModelBackend",
]

# ------------------------------------------------------------------------------
# Middleware
# ------------------------------------------------------------------------------
MIDDLEWARE = [
    "django_prometheus.middleware.PrometheusBeforeMiddleware",
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    "axes.middleware.AxesMiddleware",
    "django_prometheus.middleware.PrometheusAfterMiddleware",
]

ROOT_URLCONF = "bpjvote.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / "templates"],
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

WSGI_APPLICATION = "bpjvote.wsgi.application"

# ------------------------------------------------------------------------------
# Database
# - پیش‌فرض: SQLite (بدون وابستگی اضافه)
# - اگر USE_POSTGRES=True در .env → PostgreSQL
# ------------------------------------------------------------------------------
USE_POSTGRES = os.getenv("USE_POSTGRES", "False") == "True"

if USE_POSTGRES:
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.postgresql",  # ساده؛ بدون backend پرومتئوس
            "NAME": os.getenv("POSTGRES_DB", "bpjvote"),
            "USER": os.getenv("POSTGRES_USER", "bpjvote"),
            "PASSWORD": os.getenv("POSTGRES_PASSWORD", ""),
            "HOST": os.getenv("POSTGRES_HOST", "127.0.0.1"),
            "PORT": os.getenv("POSTGRES_PORT", "5432"),
            "CONN_MAX_AGE": 60,
        }
    }
else:
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.sqlite3",
            "NAME": BASE_DIR / "db.sqlite3",
        }
    }

# ------------------------------------------------------------------------------
# I18N / TZ
# ------------------------------------------------------------------------------
LANGUAGE_CODE = "fa"
TIME_ZONE = os.getenv("TIME_ZONE", "Asia/Tehran")
USE_I18N = True
USE_TZ = True

# ------------------------------------------------------------------------------
# Static & Media
# ------------------------------------------------------------------------------
STATIC_URL = "/static/"
STATIC_ROOT = os.getenv("STATIC_ROOT", str(BASE_DIR / "static"))
STATICFILES_DIRS = [p for p in [BASE_DIR / "assets"] if p.exists()]

MEDIA_URL = "/media/"
MEDIA_ROOT = os.getenv("MEDIA_ROOT", str(BASE_DIR / "media"))

# ------------------------------------------------------------------------------
# Cache / Sessions / Ratelimit / Axes / Cachalot
# - پیش‌فرض: FileBasedCache (کش مشترک سازگار با ratelimit)
# - اگر USE_REDIS=True → Redis
# ------------------------------------------------------------------------------
USE_REDIS = os.getenv("USE_REDIS", "False") == "True"

if USE_REDIS:
    CACHES = {
        "default": {
            "BACKEND": "django_redis.cache.RedisCache",
            "LOCATION": os.getenv("REDIS_URL", "redis://127.0.0.1:6379/1"),
            "OPTIONS": {"CLIENT_CLASS": "django_redis.client.DefaultClient"},
            "KEY_PREFIX": "bpjvote",
        }
    }
else:
    CACHES = {
        "default": {
            "BACKEND": "django.core.cache.backends.filebased.FileBasedCache",
            "LOCATION": os.getenv("DJANGO_CACHE_DIR", "/var/cache/django"),
            "OPTIONS": {"MAX_ENTRIES": 100000},
            "TIMEOUT": 60 * 60,  # 1h
        }
    }

SESSION_ENGINE = "django.contrib.sessions.backends.cache"
SESSION_CACHE_ALIAS = "default"

RATELIMIT_USE_CACHE = "default"
AXES_CACHE = "default"
CACHALOT_ENABLED = True
CACHALOT_CACHE = "default"

# ------------------------------------------------------------------------------
# Crispy Forms
# ------------------------------------------------------------------------------
CRISPY_ALLOWED_TEMPLATE_PACKS = ("bootstrap", "bootstrap4", "bootstrap5")
CRISPY_TEMPLATE_PACK = os.getenv("CRISPY_TEMPLATE_PACK", "bootstrap4")

# ------------------------------------------------------------------------------
# Messages
# ------------------------------------------------------------------------------
MESSAGE_TAGS = {
    messages.DEBUG: "debug",
    messages.INFO: "info",
    messages.SUCCESS: "success",
    messages.WARNING: "warning",
    messages.ERROR: "danger",
}

# ------------------------------------------------------------------------------
# Security
# ------------------------------------------------------------------------------
SECURE_BROWSER_XSS_PROTECTION = True
SECURE_CONTENT_TYPE_NOSNIFF = True
X_FRAME_OPTIONS = "DENY"

# ------------------------------------------------------------------------------
# Logging
# ------------------------------------------------------------------------------
LOG_DIR = BASE_DIR / "logs"
os.makedirs(LOG_DIR, exist_ok=True)
LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "verbose": {"format": "[{levelname}] {asctime} {name}: {message}", "style": "{"},
        "simple": {"format": "[{levelname}] {message}", "style": "{"},
    },
    "handlers": {
        "console": {"class": "logging.StreamHandler", "formatter": "simple"},
        "error_file": {
            "class": "logging.handlers.RotatingFileHandler",
            "filename": str(LOG_DIR / "django_errors.log"),
            "maxBytes": 5 * 1024 * 1024,
            "backupCount": 5,
            "formatter": "verbose",
        },
    },
    "root": {"handlers": ["console", "error_file"], "level": "INFO" if not DEBUG else "DEBUG"},
}

# ------------------------------------------------------------------------------
# Axes / Turnstile
# ------------------------------------------------------------------------------
AXES_ENABLED = True
AXES_FAILURE_LIMIT = int(os.getenv("AXES_FAILURE_LIMIT", "5"))
AXES_LOCKOUT_PARAMETERS = ["username"]

TURNSTILE_SITE_KEY = os.getenv("TURNSTILE_SITE_KEY", "")
TURNSTILE_SECRET_KEY = os.getenv("TURNSTILE_SECRET_KEY", "")

# ------------------------------------------------------------------------------
# Voting window (الان 24/7 باز است)
# ------------------------------------------------------------------------------
NOVOTE_ALWAYS_OPEN = os.getenv("NOVOTE_ALWAYS_OPEN", "True") == "True"
FORCE_TIME = os.getenv("FORCE_TIME", "False") == "True"
NOVOTE_START_HOUR = int(os.getenv("NOVOTE_START_HOUR", "22"))  # 22:00
NOVOTE_END_HOUR   = int(os.getenv("NOVOTE_END_HOUR", "6"))     # 06:00

# ------------------------------------------------------------------------------
# Feature flags used in signals.py
# ------------------------------------------------------------------------------
SEND_EMAIL = os.getenv("SEND_EMAIL", "False") == "True"
SEND_SMS   = os.getenv("SEND_SMS", "False") == "True"

# ------------------------------------------------------------------------------
# Email (when SEND_EMAIL=True)
# ------------------------------------------------------------------------------
EMAIL_BACKEND = os.getenv(
    "EMAIL_BACKEND",
    "django.core.mail.backends.console.EmailBackend" if DEBUG else "django.core.mail.backends.smtp.EmailBackend",
)
EMAIL_HOST = os.getenv("EMAIL_HOST", "")
EMAIL_PORT = int(os.getenv("EMAIL_PORT", "587" if os.getenv("EMAIL_HOST") else "25"))
EMAIL_HOST_USER = os.getenv("EMAIL_HOST_USER", "")
EMAIL_HOST_PASSWORD = os.getenv("EMAIL_HOST_PASSWORD", "")
EMAIL_USE_TLS = os.getenv("EMAIL_USE_TLS", "True") == "True"
DEFAULT_FROM_EMAIL = os.getenv("DEFAULT_FROM_EMAIL", "noreply@example.com")

# ------------------------------------------------------------------------------
# Prometheus
#farhad
# ------------------------------------------------------------------------------
PROMETHEUS_EXPORT_MIGRATIONS = False
