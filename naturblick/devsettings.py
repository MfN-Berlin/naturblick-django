from .basesettings import *

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'django-insecure-x#f7$+n+n^n!ynhb9lrym_k#$kc@b1v0kr9_rwvf0@%$4pz3r8'

ALLOWED_HOSTS = []

# Database
# https://docs.djangoproject.com/en/5.1/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        # Database file stored in the project's base directory
        'NAME': BASE_DIR / 'db.sqlite3',
    }
    # 'default': {
    #     'ENGINE': 'django.db.backends.postgresql_psycopg2',
    #     'NAME': os.getenv('DJANGO_POSTGRES'),
    #     'USER': os.getenv('DJANGO_POSTGRES_USER'),
    #     'PASSWORD': os.getenv('DJANGO_POSTGRES_PASSWORD'),
    #     'HOST': 'localhost',
    #     'PORT': '5558',
    # }
}

LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    'formatters': {
        'naturblick': {
            'format': '{asctime} - {levelname} - {name} - {message}',
            'style': '{'
        },
    },
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
            "level": "INFO",
            "formatter": "naturblick"
        },
    },
    "root": {
        "handlers": ["console"],
        "level": "INFO",
    },
}

CORS_ALLOWED_ORIGINS = [
    'http://localhost:4200',
]
