# config/settings/production.py
from .base import *

DEBUG = False

ALLOWED_HOSTS = ['your-public-ip', 'api.yourdomain.com']

# Hanya izinkan origin domain frontend produksi Anda
CORS_ALLOWED_ORIGINS = [
    "http://192.168.1.100",           # Contoh IP Public / Lokal Server Frontend
    "https://your-frontend-app.com",  # Domain Frontend Vercel/Netlify/S3
]

CORS_ALLOW_CREDENTIALS = True