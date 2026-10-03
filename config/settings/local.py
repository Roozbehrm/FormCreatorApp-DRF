from .base import *

DEBUG = True
ALLOWED_HOSTS = env.list("DJANGO_ALLOWED_HOSTS", default=["*"])
USE_SQLITE = env.bool("USE_SQLITE", default=True)
if not USE_SQLITE:
    DATABASES = {"default": env.db("DATABASE_URL")}
else:
    DATABASES = {"default": {"ENGINE": "django.db.backends.sqlite3", "NAME": BASE_DIR / "db.sqlite3"}}

USE_REDIS_CACHE = env.bool("USE_REDIS_CACHE", default=False)
if USE_REDIS_CACHE:
    CACHES = {
        "default": {
            "BACKEND": "django_redis.cache.RedisCache",
            "LOCATION": REDIS_URL,
            "OPTIONS": {"CLIENT_CLASS": "django_redis.client.DefaultClient"},
            "KEY_PREFIX": "formflow",
        }
    }
else:
    CACHES = {
        "default": {
            "BACKEND": "django.core.cache.backends.locmem.LocMemCache",
            "LOCATION": "formflow-local",
        }
    }

CHANNEL_LAYERS = (
    {"default": {"BACKEND": "channels_redis.core.RedisChannelLayer", "CONFIG": {"hosts": [CHANNELS_REDIS_URL]}}}
    if env.bool("USE_REDIS_CACHE", default=False)
    else {"default": {"BACKEND": "channels.layers.InMemoryChannelLayer"}}
)

CELERY_TASK_ALWAYS_EAGER = env.bool("CELERY_TASK_ALWAYS_EAGER", default=True)
CELERY_TASK_EAGER_PROPAGATES = True
SMS_BACKEND = env("SMS_BACKEND", default="console")
EMAIL_BACKEND = env("EMAIL_BACKEND", default="django.core.mail.backends.console.EmailBackend")
INSTALLED_APPS += ["django_extensions"]
SECURE_SSL_REDIRECT = False
SESSION_COOKIE_SECURE = False
CSRF_COOKIE_SECURE = False
