#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
========================================
SETTINGS DE PRODUCCIÓN PARA PYTHONANYWHERE
========================================

Configuración optimizada específicamente para el despliegue en PythonAnywhere.
Este archivo extiende la configuración base y añade configuraciones específicas
para el entorno de producción.

Uso:
- Copia este archivo como settings_production.py
- Configura las variables de entorno en tu archivo .env
- Usa DJANGO_SETTINGS_MODULE=autolavados_plataforma.settings_production
"""

import os
import sys
from pathlib import Path
from dotenv import load_dotenv

# ========================================
# CONFIGURACIÓN BASE
# ========================================
# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# Cargar variables de entorno
load_dotenv(BASE_DIR / '.env')

# ========================================
# CONFIGURACIÓN DE SEGURIDAD
# ========================================
# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.getenv('SECRET_KEY', 'django-insecure-change-this-in-production')

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = os.getenv('DEBUG', 'False').lower() == 'true'

# Hosts permitidos para PythonAnywhere
ALLOWED_HOSTS = [
    'localhost',
    '127.0.0.1',
    '0.0.0.0',
    'testserver',
    # Agregar tu dominio de PythonAnywhere
    f"{os.getenv('PYTHONANYWHERE_USERNAME', 'tu_usuario')}.pythonanywhere.com",
    # Dominio personalizado si tienes uno
    os.getenv('CUSTOM_DOMAIN', ''),
]

# Filtrar hosts vacíos
ALLOWED_HOSTS = [host for host in ALLOWED_HOSTS if host]

# ========================================
# CONFIGURACIÓN DE APLICACIONES
# ========================================
DJANGO_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
]

THIRD_PARTY_APPS = [
    'rest_framework',
    'rest_framework.authtoken',
    'corsheaders',
    'django_extensions',  # Para PythonAnywhere
]

LOCAL_APPS = [
    'autenticacion',
    'clientes',
    'reservas',
    'notificaciones',
    'empleados',
]

INSTALLED_APPS = DJANGO_APPS + THIRD_PARTY_APPS + LOCAL_APPS

# ========================================
# CONFIGURACIÓN DE MIDDLEWARE
# ========================================
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',  # Para archivos estáticos
    'django.contrib.sessions.middleware.SessionMiddleware',
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    # Middleware personalizado
    'autolavados_plataforma.middleware.CSRFDebugMiddleware',
    'autolavados_plataforma.middleware.AJAXExceptionMiddleware',
    'autolavados_plataforma.middleware.LoginRequiredMiddleware',
    'autolavados_plataforma.timezone_middleware.TimezoneMiddleware',
]

ROOT_URLCONF = 'autolavados_plataforma.urls'

# ========================================
# CONFIGURACIÓN DE TEMPLATES
# ========================================
TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'autolavados_plataforma.wsgi.application'

# ========================================
# CONFIGURACIÓN DE BASE DE DATOS
# ========================================
# Configuración optimizada para MySQL en PythonAnywhere
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': os.getenv('DB_NAME', f"{os.getenv('PYTHONANYWHERE_USERNAME', 'tu_usuario')}$autolavados"),
        'USER': os.getenv('DB_USER', os.getenv('PYTHONANYWHERE_USERNAME', 'tu_usuario')),
        'PASSWORD': os.getenv('DB_PASSWORD', ''),
        'HOST': os.getenv('DB_HOST', f"{os.getenv('PYTHONANYWHERE_USERNAME', 'tu_usuario')}.mysql.pythonanywhere-services.com"),
        'PORT': os.getenv('DB_PORT', '3306'),
        'OPTIONS': {
            'init_command': "SET sql_mode='STRICT_TRANS_TABLES', time_zone='-05:00'",
            'charset': 'utf8mb4',
            'use_unicode': True,
            # Configuraciones específicas para PythonAnywhere
            'connect_timeout': 60,
            'read_timeout': 60,
            'write_timeout': 60,
        },
        'CONN_MAX_AGE': 60,  # Reutilizar conexiones
    }
}

# ========================================
# CONFIGURACIÓN DE CACHE
# ========================================
# Cache con Redis si está disponible, sino usar cache local
CACHES = {
    'default': {
        'BACKEND': 'django_redis.cache.RedisCache',
        'LOCATION': os.getenv('REDIS_URL', 'redis://127.0.0.1:6379/1'),
        'OPTIONS': {
            'CLIENT_CLASS': 'django_redis.client.DefaultClient',
        },
        'KEY_PREFIX': 'autolavados',
        'TIMEOUT': 300,
    }
} if os.getenv('REDIS_URL') else {
    'default': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
        'LOCATION': 'autolavados-cache',
    }
}

# ========================================
# CONFIGURACIÓN DE ARCHIVOS ESTÁTICOS
# ========================================
STATIC_URL = '/static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'
STATICFILES_DIRS = [BASE_DIR / 'static']

# Configuración de WhiteNoise para archivos estáticos
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

# Archivos de medios
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

# ========================================
# CONFIGURACIÓN DE EMAIL
# ========================================
# Configuración de email para PythonAnywhere
EMAIL_BACKEND = os.getenv('EMAIL_BACKEND', 'django.core.mail.backends.smtp.EmailBackend')
EMAIL_HOST = os.getenv('EMAIL_HOST', 'smtp.gmail.com')
EMAIL_PORT = int(os.getenv('EMAIL_PORT', '587'))
EMAIL_HOST_USER = os.getenv('EMAIL_HOST_USER', '')
EMAIL_HOST_PASSWORD = os.getenv('EMAIL_HOST_PASSWORD', '')
EMAIL_USE_TLS = os.getenv('EMAIL_USE_TLS', 'True').lower() == 'true'
EMAIL_USE_SSL = os.getenv('EMAIL_USE_SSL', 'False').lower() == 'true'

DEFAULT_FROM_EMAIL = os.getenv('DEFAULT_FROM_EMAIL', 'noreply@premiumcardetailing.com')
SERVER_EMAIL = DEFAULT_FROM_EMAIL

# ========================================
# CONFIGURACIÓN DE SEGURIDAD
# ========================================
# Configuraciones de seguridad para producción
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True
X_FRAME_OPTIONS = 'DENY'

# HTTPS settings (descomenta si usas HTTPS)
# SECURE_SSL_REDIRECT = True
# SECURE_HSTS_SECONDS = 31536000
# SECURE_HSTS_INCLUDE_SUBDOMAINS = True
# SECURE_HSTS_PRELOAD = True
# SESSION_COOKIE_SECURE = True
# CSRF_COOKIE_SECURE = True

# ========================================
# CONFIGURACIÓN DE LOGGING
# ========================================
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '{levelname} {asctime} {module} {process:d} {thread:d} {message}',
            'style': '{',
        },
        'simple': {
            'format': '{levelname} {message}',
            'style': '{',
        },
    },
    'handlers': {
        'file': {
            'level': 'INFO',
            'class': 'logging.FileHandler',
            'filename': BASE_DIR / 'logs' / 'django.log',
            'formatter': 'verbose',
        },
        'console': {
            'level': 'INFO',
            'class': 'logging.StreamHandler',
            'formatter': 'simple',
        },
    },
    'root': {
        'handlers': ['console', 'file'],
        'level': 'INFO',
    },
    'loggers': {
        'django': {
            'handlers': ['console', 'file'],
            'level': 'INFO',
            'propagate': False,
        },
        'autolavados_plataforma': {
            'handlers': ['console', 'file'],
            'level': 'INFO',
            'propagate': False,
        },
    },
}

# Crear directorio de logs si no existe
(BASE_DIR / 'logs').mkdir(exist_ok=True)

# ========================================
# CONFIGURACIÓN DE INTERNACIONALIZACIÓN
# ========================================
LANGUAGE_CODE = 'es-co'
TIME_ZONE = 'America/Bogota'
USE_I18N = True
USE_TZ = False  # Deshabilitado para evitar problemas con MySQL

# ========================================
# CONFIGURACIÓN DE REST FRAMEWORK
# ========================================
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework.authentication.TokenAuthentication',
        'rest_framework.authentication.SessionAuthentication',
    ],
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticated',
    ],
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 20,
    'DEFAULT_THROTTLE_CLASSES': [
        'rest_framework.throttling.AnonRateThrottle',
        'rest_framework.throttling.UserRateThrottle'
    ],
    'DEFAULT_THROTTLE_RATES': {
        'anon': '100/hour',
        'user': '1000/hour'
    }
}

# ========================================
# CONFIGURACIÓN DE CORS
# ========================================
CORS_ALLOWED_ORIGINS = [
    f"https://{os.getenv('PYTHONANYWHERE_USERNAME', 'tu_usuario')}.pythonanywhere.com",
    os.getenv('CUSTOM_DOMAIN', ''),
]
CORS_ALLOWED_ORIGINS = [origin for origin in CORS_ALLOWED_ORIGINS if origin]

CORS_ALLOW_CREDENTIALS = True

# ========================================
# CONFIGURACIÓN DE NEQUI
# ========================================
SITE_URL = os.getenv('SITE_URL', f"https://{os.getenv('PYTHONANYWHERE_USERNAME', 'tu_usuario')}.pythonanywhere.com")

NEQUI_API_KEY = os.getenv('NEQUI_API_KEY', '')
NEQUI_CLIENT_ID = os.getenv('NEQUI_CLIENT_ID', '')
NEQUI_CLIENT_SECRET = os.getenv('NEQUI_CLIENT_SECRET', '')
NEQUI_BASE_URL = os.getenv('NEQUI_BASE_URL', 'https://api.nequi.com.co')
NEQUI_SANDBOX = os.getenv('NEQUI_SANDBOX', 'False').lower() == 'true'
NEQUI_WEBHOOK_URL = os.getenv('NEQUI_WEBHOOK_URL', f"{SITE_URL}/reservas/callback/nequi/")
NEQUI_SUCCESS_URL = os.getenv('NEQUI_SUCCESS_URL', f"{SITE_URL}/reservas/confirmar-pago/")
NEQUI_CANCEL_URL = os.getenv('NEQUI_CANCEL_URL', f"{SITE_URL}/reservas/cancelar-pago/")

# ========================================
# CONFIGURACIÓN DE VALIDACIÓN DE CONTRASEÑAS
# ========================================
AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

# ========================================
# CONFIGURACIÓN ADICIONAL
# ========================================
# Default primary key field type
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# Configuración de sesiones
SESSION_ENGINE = 'django.contrib.sessions.backends.cached_db'
SESSION_CACHE_ALIAS = 'default'
SESSION_COOKIE_AGE = 86400  # 24 horas

# Configuración de mensajes
from django.contrib.messages import constants as messages
MESSAGE_TAGS = {
    messages.DEBUG: 'debug',
    messages.INFO: 'info',
    messages.SUCCESS: 'success',
    messages.WARNING: 'warning',
    messages.ERROR: 'error',
}

print("✅ Settings de producción para PythonAnywhere cargados correctamente")