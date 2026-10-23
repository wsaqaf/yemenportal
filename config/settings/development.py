from .base import *

DEBUG = True

ALLOWED_HOSTS = ['*']

# Additional development apps
INSTALLED_APPS += [
    'debug_toolbar',
]

MIDDLEWARE += [
    'debug_toolbar.middleware.DebugToolbarMiddleware',
]

INTERNAL_IPS = [
    '127.0.0.1',
]

# Email backend for development
#EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

# Use SQLite for easy local testing
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}
