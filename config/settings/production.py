from .base import *

DEBUG = False

ALLOWED_HOSTS = env.list('ALLOWED_HOSTS', default=['194.163.154.154', 'localhost'])

SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True
X_FRAME_OPTIONS = 'DENY'

STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

DATABASES = {
    'default': env.db('DATABASE_URL', default='postgres://yemenportal:yemenportal@db:5432/yemenportal'),
    'legacy': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'yemenportal_legacy',
        'USER': 'yemenportal',
        'PASSWORD': 'yemenportal',
        'HOST': 'db',
        'PORT': '5432',
    }
}

try:
    import redis
    CACHES = {
        'default': {
            'BACKEND': 'django.core.cache.backends.redis.RedisCache',
            'LOCATION': 'redis://redis:6379/1',
        }
    }
except Exception:
    CACHES = {
        'default': {
            'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
        }
    }
