# config/settings/local.py
from .base import *

DEBUG = True
ALLOWED_HOSTS = ['*']

# Opsi 2: Izinkan SEMUA origin (Alternatif praktis saat dev cepat)
CORS_ALLOW_ALL_ORIGINS = True

# Izinkan pengiriman Cookie / Authorization Header (JWT / Session)
CORS_ALLOW_CREDENTIALS = True