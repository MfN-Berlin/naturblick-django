from .basesettings import *

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = False

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.getenv('DJANGO_SECRET_KEY')

ALLOWED_HOSTS = ['staging.naturblick.museumfuernaturkunde.berlin', 'naturblick.museumfuernaturkunde.berlin', 'django']

# Database
# https://docs.djangoproject.com/en/5.1/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': os.getenv('DJANGO_POSTGRES'),
        'USER': os.getenv('DJANGO_POSTGRES_USER'),
        'PASSWORD': os.getenv('DJANGO_POSTGRES_PASSWORD'),
        'HOST': 'django-db',
        'PORT': '5432',
    }
}

LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    'formatters': {
        'naturblick': {
            'format': '{asctime} - {levelname} - {module} - {message}',
            'style': '{'
        },
    },
    "handlers": {
        "info_file": {
            "level": "INFO",
            "class": "logging.handlers.WatchedFileHandler",
            "filename": "/logs/info.log",
            "formatter": "naturblick"
        },
        "error_file": {
            "level": "ERROR",
            "class": "logging.handlers.WatchedFileHandler",
            "filename": "/logs/error.log",
            "formatter": "naturblick"
        },
    },
    "root": {
        "handlers": ["info_file", "error_file"],
        "level": "INFO",
    },
}

FORCE_SCRIPT_NAME = '/django/'
STATIC_URL = '/django/static/'

CSRF_COOKIE_SECURE = True
SESSION_COOKIE_SECURE = True
CSRF_TRUSTED_ORIGINS = ['https://staging.naturblick.museumfuernaturkunde.berlin',
                        'https://naturblick.museumfuernaturkunde.berlin']
