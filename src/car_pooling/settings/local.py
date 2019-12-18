from .base import *

DEBUG = True

ALLOWED_HOSTS = [LOCAL_IP, 'web', 'localhost', '0.0.0.0', 'pooling', ]

ROOT_URLCONF = 'car_pooling.urls'

CACHES = {
    'default': {
            'BACKEND': 'django.core.cache.backends.dummy.DummyCache',
        }
}

