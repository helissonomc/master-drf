from .base import *
from .base import environ


DEBUG = True

SECRET_KEY = env('DJANGO_SECRET_KEY', default='django-insecure-6be-aq^witr#6%3u6e%q-#&hy4rbbf=%dbzj!t%@b!evp-m403')

ALLOWED_HOSTS = ['localhost', '0.0.0.0', '127.0.0.1']