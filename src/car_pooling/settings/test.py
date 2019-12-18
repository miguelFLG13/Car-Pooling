from .base import *

DEBUG = True

ALLOWED_HOSTS = [LOCAL_IP]

ROOT_URLCONF = 'car_pooling.urls'

CACHES = {
    'default': {
            'BACKEND': 'django.core.cache.backends.dummy.DummyCache',
        }
}
