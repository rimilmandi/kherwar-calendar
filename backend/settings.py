import os
from pathlib import Path
import dj_database_url  # Railway PostgreSQL এর জন্য

BASE_DIR = Path(__file__).resolve().parent.parent

# ⚠️ Railway ড্যাশবোর্ড থেকে Secret Key সেট করুন। লোকালে টেস্ট করার জন্য নিচেরটা ব্যবহার করুন।
SECRET_KEY = os.environ.get('SECRET_KEY', 'change-this-in-production')

# ⚠️ Railway-এ ডিপ্লয় করার পর DEBUG অবশ্যই False হতে হবে
DEBUG = os.environ.get('DEBUG', 'False') == 'True'

# Railway-এর অটো ডোমেইন, আপনার কাস্টম ডোমেইন এবং লোকালহোস্ট
ALLOWED_HOSTS = ['127.0.0.1', 'localhost', '.railway.app', 'kherwarcalendar.co.in', 'www.kherwarcalendar.co.in'] 
# 👆 'your-domain.com' এর জায়গায় আপনার আসল ডোমেইন বসান। Railway অটোমেটিক .railway.app ডোমেইন পেয়ে যাবে।

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'store',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',  # ✅ Static ফাইল সার্ভ করার জন্য (CSS/JS) জরুরি
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
]

ROOT_URLCONF = 'backend.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'backend.wsgi.application'

# ✅ ডাটাবেজ কনফিগারেশন (Railway অটোমেটিক PostgreSQL কানেকশন স্ট্রিং দেয়)
DATABASES = {
    'default': dj_database_url.config(
        default=f"sqlite:///{BASE_DIR / 'db.sqlite3'}",  # লোকালে SQLite
        conn_max_age=600
    )
}

AUTH_PASSWORD_VALIDATORS = []

LANGUAGE_CODE = 'bn'
TIME_ZONE = 'Asia/Kolkata'
USE_I18N = True
USE_TZ = True

# ✅ স্ট্যাটিক ফাইল কনফিগারেশন
STATIC_URL = '/static/'
STATICFILES_DIRS = [BASE_DIR / 'static']
STATIC_ROOT = BASE_DIR / 'staticfiles'   # Railway/সার্ভারে static ফাইল এখানে জমা হবে
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# Railway-এর ডোমেইনের জন্য CSRF সেটআপ
CSRF_TRUSTED_ORIGINS = [
    'https://web-production-a2a89.up.railway.app',
    'https://kherwarcalendar.co.in',
    'https://www.kherwarcalendar.co.in',
]

# লগইন এবং লগআউট সেটিংস
LOGIN_URL = '/login/'
LOGIN_REDIRECT_URL = '/admin-panel/'   # লগইন সফল হলে অ্যাডমিন প্যানেলে যাবে
LOGOUT_REDIRECT_URL = '/'


