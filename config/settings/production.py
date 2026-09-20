from .base import *
import os

# ==========================================
# 1. KEAMANAN & HOSTING
# ==========================================
# Gunakan fallback rahasia jika .env belum sempat dibuat
SECRET_KEY = os.environ.get("SECRET_KEY", "c@pst0ne-d1c0ding-2026!a*#z9b!k$x2-sementara")

DEBUG = os.environ.get("DEBUG", "True") == "True"

# Ganti 'your-public-ip' dengan IP asli Biznet Anda
ALLOWED_HOSTS = ['103.93.135.137', 'localhost', '127.0.0.1','student-ews-api.duckdns.org']

# ==========================================
# 2. KONFIGURASI CORS (UNTUK FRONTEND VERCEL)
# ==========================================
CORS_ALLOWED_ORIGINS = [
    "http://localhost:3000",
    "http://localhost:5173",
    # "https://nama-proyek-frontend.vercel.app",  <-- Masukkan link Vercel nanti di sini
]

CORS_ALLOW_CREDENTIALS = True
