# config/settings/local.py
from .base import *

DEBUG = True

# Izinkan semua HOST untuk bypass Host Header Validation (Termasuk URL Ngrok)
ALLOWED_HOSTS = ['*']

# --- CORS CONFIGURATION UNTUK DEV & NGROK ---

# 1. HARUS False agar tidak diblokir browser saat ALLOW_CREDENTIALS aktif
CORS_ALLOW_ALL_ORIGINS = False

# 2. Trik Dev: Gunakan Regex untuk mengizinkan SEMUA origin secara dinamis
#    (Mengatasi bentrokan browser tanpa perlu mendaftarkan IP satu per satu)
CORS_ALLOWED_ORIGIN_REGEXES = [
    r"^http://.*$",
    r"^https://.*$",
]

# 3. Izinkan pengiriman Authorization Header / JWT / Cookies
CORS_ALLOW_CREDENTIALS = True

# 4. Tambahkan header yang diizinkan (Wajib ada Authorization & ngrok header)
CORS_ALLOW_HEADERS = [
    'accept',
    'accept-encoding',
    'authorization',
    'content-type',
    'dnt',
    'origin',
    'user-agent',
    'x-csrftoken',
    'x-requested-with',
    'ngrok-skip-browser-warning',
]

# 5. CSRF Trusted Origins untuk method POST/PUT/DELETE
CSRF_TRUSTED_ORIGINS = [
    "https://*.ngrok-free.app",
    "https://*.ngrok.io",
    "http://localhost:*",
    "http://127.0.0.1:*",
    "http://192.168.*:*",
]