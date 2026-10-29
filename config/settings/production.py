from .base import *

DEBUG = False


ALLOWED_HOSTS = ['yemenportal.net', 'www.yemenportal.net', '194.163.154.154', 'localhost', '127.0.0.1']

CSRF_TRUSTED_ORIGINS = [
    'http://yemenportal.net',
    'https://yemenportal.net',
    'http://www.yemenportal.net',
    'https://www.yemenportal.net',
    'http://194.163.154.154',
]

SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
USE_X_FORWARDED_HOST = True


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

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '[{asctime}] {levelname} {name}: {message}',
            'style': '{',
        },
    },
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'formatter': 'verbose',
        },
    },
    'root': {
        'handlers': ['console'],
        'level': 'WARNING',
    },
    'loggers': {
        'django.request': {
            'handlers': ['console'],
            'level': 'ERROR',
            'propagate': False,
        },
        'allauth': {
            'handlers': ['console'],
            'level': 'INFO',
            'propagate': False,
        },
    },
}
