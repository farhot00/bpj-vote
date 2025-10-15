cat > bpjvote/settings_production.py << 'PY'
"""
Django settings for bpjvote project (production-friendly).
"""
import os
from pathlib import Path
from dotenv import load_dotenv
from django.contrib import messages

BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv(BASE_DIR / ".env")

SECRET_KEY = os.getenv("SECRET_KEY", "change-me-in-env")
DEBUG = os.getenv("DEBUG", "False") == "True"

_allowed = os.getenv("ALLOWED_HOSTS", "")
ALLOWED_HOSTS = [h.strip() for h in _allowed.split(",") if h.strip()] or ["127.0.0.1", "localhost"]

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    # "django.contrib.sessions",
    "qsessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",

    "auditlog",
    "axes",
    "django_ratelimit",
    # "django_recaptcha",
    "turnstile",
    "cachalot",
    "sorl.thumbnail",
    "django_prometheus",

    "main",
    "vote",
]

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

# Database: شروع سریع با SQLite (بعداً اگر خواستی Postgres می‌ذاریم)
DATABASES = {
    "default": {"ENGINE": "django.db.backends.sqlite3", "NAME": BASE_DIR / "db.sqlite3"}
}

# کاربر سفارشی شما
AUTH_USER_MODEL = "main.User"

# بک‌اندهای احراز هویت (Axes + پیش‌فرض جنگو)
AUTHENTICATION_BACKENDS = [
    "axes.backends.AxesStandaloneBackend",
    "django.contrib.auth.backends.ModelBackend",
]

AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]

LANGUAGE_CODE = "en-us"
TIME_ZONE = "UTC"
USE_I18N = True
USE_TZ = True

STATIC_URL = "/static/"
STATIC_ROOT = BASE_DIR / "static"
MEDIA_URL = "/media/"
MEDIA_ROOT = BASE_DIR / "media"
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# Sessions via qsessions
SESSION_ENGINE = "qsessions.backends.cached_db"
SESSION_COOKIE_AGE = 60 * 60 * 24 * 7

# Cache: Redis (سازگار با ratelimit/axes/cachalot)
CACHES = {
    "default": {
        "BACKEND": "django_redis.cache.RedisCache",
        "LOCATION": "redis://127.0.0.1:6379/1",
        "OPTIONS": {"CLIENT_CLASS": "django_redis.client.DefaultClient"},
        "KEY_PREFIX": "bpjvote",
    }
}
RATELIMIT_USE_CACHE = "default"
AXES_CACHE = "default"
CACHALOT_ENABLED = True
CACHALOT_CACHE = "default"

MESSAGE_TAGS = {
    messages.DEBUG: "debug",
    messages.INFO: "info",
    messages.SUCCESS: "success",
    messages.WARNING: "warning",
    messages.ERROR: "danger",
}

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

AXES_ENABLED = True
AXES_FAILURE_LIMIT = int(os.getenv("AXES_FAILURE_LIMIT", "5"))
AXES_LOCKOUT_PARAMETERS = ["username"]

TURNSTILE_SITE_KEY = os.getenv("TURNSTILE_SITE_KEY", "")
TURNSTILE_SECRET_KEY = os.getenv("TURNSTILE_SECRET_KEY", "")
PY
