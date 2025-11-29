"""
Django settings for Binder ERP System
Multi-tenant SaaS for Textile Manufacturing
"""

import os
from pathlib import Path
from datetime import timedelta
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Build paths inside the project
BASE_DIR = Path(__file__).resolve().parent.parent

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.getenv('SECRET_KEY', 'django-insecure-dev-key-change-in-production')

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

# Allow all hosts in production (Render will set this)
ALLOWED_HOSTS = [
    'localhost',
    '127.0.0.1',
    'binder-backend-0szj.onrender.com',
    '.onrender.com',  # Allows any Render subdomain
    'binder-frontend-self.vercel.app',
]


# Application definition

INSTALLED_APPS = [
    # Unfold Admin - Must be before django.contrib.admin
    "unfold",
    "unfold.contrib.filters",  # optional, for advanced filters
    "unfold.contrib.forms",  # optional, for better forms
    "unfold.contrib.import_export",  # optional, for import/export
    
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    
    # Third-party apps
    'rest_framework',
    'rest_framework_simplejwt',
    'corsheaders',
    'drf_yasg',
    
    # Local apps - 4 Pillars
    'auth_service',              # Pillar 1: Authentication & Authorization
    'inventory_management',       # Pillar 2: IMS
    'community',                  # Pillar 3: Community Forum
    'load_balancer',             # Pillar 4: Health & Monitoring
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',  # Static files
    'corsheaders.middleware.CorsMiddleware',  # CORS - must be high
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'binder_config.urls'

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

WSGI_APPLICATION = 'binder_config.wsgi.application'


# Database
# https://docs.djangoproject.com/en/5.0/ref/settings/#databases

import dj_database_url

# Database selection strategy:
# 1) If DATABASE_URL is set (Render/production), use it.
# 2) Else if DB_ENGINE=postgres or DB_HOST is set, use Postgres with provided env vars.
# 3) Else default to SQLite for local development (zero-setup).
database_url = os.getenv('DATABASE_URL',default=None)
db_engine_env = os.getenv('DB_ENGINE', '').lower()
db_host_env = os.getenv('DB_HOST', '').strip()

# if database_url:
#     DATABASES = {
#         'default': dj_database_url.config(
#             default=database_url,
#             conn_max_age=600,
#             conn_health_checks=True,
#         )
#     }
# elif db_engine_env == 'postgresql':
#     DATABASES = {
#     'default': dj_database_url.config(
#         default=os.getenv('DATABASE_URL'),
#         conn_max_age=600,
#         ssl_require=True
#     )
# }
# elif db_engine_env == 'postgres' or db_host_env:
#     DATABASES = {
#         'default': {
#             'ENGINE': 'django.db.backends.postgresql',
#             'NAME': os.getenv('DB_NAME', 'binder_db'),
#             'USER': os.getenv('DB_USER', 'postgres'),
#             'PASSWORD': os.getenv('DB_PASSWORD', 'password'),
#             'HOST': os.getenv('DB_HOST', 'localhost'),
#             'PORT': os.getenv('DB_PORT', '5432'),
#         }
#     }
# else:
#     DATABASES = {
#         'default': {
#             'ENGINE': 'django.db.backends.sqlite3',
#             'NAME': BASE_DIR / os.getenv('DB_NAME', 'db.sqlite3'),
#         }
#     }

DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': BASE_DIR / os.getenv('DB_NAME', 'db.sqlite3'),
        }
    }


# Password validation
# https://docs.djangoproject.com/en/5.0/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
        'OPTIONS': {
            'min_length': 8,
        }
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]


# Internationalization
# https://docs.djangoproject.com/en/5.0/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'Asia/Kolkata'

USE_I18N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/5.0/howto/static-files/

STATIC_URL = 'static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

MEDIA_URL = 'media/'
MEDIA_ROOT = BASE_DIR / 'media'


# Default primary key field type
# https://docs.djangoproject.com/en/5.0/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'


# Custom User Model
AUTH_USER_MODEL = 'auth_service.User'

USERNAME_FIELD = 'email'


# Django REST Framework Configuration
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework_simplejwt.authentication.JWTAuthentication',
    ],
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticated',
    ],
    'DEFAULT_RENDERER_CLASSES': [
        'rest_framework.renderers.JSONRenderer',
    ],
    'DEFAULT_PARSER_CLASSES': [
        'rest_framework.parsers.JSONParser',
        'rest_framework.parsers.MultiPartParser',
        'rest_framework.parsers.FormParser',
    ],
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 50,
    'DEFAULT_FILTER_BACKENDS': [
        'rest_framework.filters.SearchFilter',
        'rest_framework.filters.OrderingFilter',
    ],
    'EXCEPTION_HANDLER': 'shared.exceptions.custom_exception_handler',
}


# JWT Configuration
SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(minutes=int(os.getenv('JWT_ACCESS_TOKEN_LIFETIME', 60))),
    'REFRESH_TOKEN_LIFETIME': timedelta(minutes=int(os.getenv('JWT_REFRESH_TOKEN_LIFETIME', 1440))),
    'ROTATE_REFRESH_TOKENS': True,
    'BLACKLIST_AFTER_ROTATION': True,
    'UPDATE_LAST_LOGIN': True,
    'ALGORITHM': 'HS256',
    'SIGNING_KEY': SECRET_KEY,
    'VERIFYING_KEY': None,
    'AUTH_HEADER_TYPES': ('Bearer',),
    'AUTH_HEADER_NAME': 'HTTP_AUTHORIZATION',
    'USER_ID_FIELD': 'id',
    'USER_ID_CLAIM': 'user_id',
    'AUTH_TOKEN_CLASSES': ('rest_framework_simplejwt.tokens.AccessToken',),
    'TOKEN_TYPE_CLAIM': 'token_type',
}


# CORS Configuration
CORS_ALLOWED_ORIGINS = [
    'http://localhost:8000',
    'http://localhost:5173,http://localhost:3000,https://binder-frontend-self.vercel.app']
# Allow all origins in development if DEBUG is True
if DEBUG:
    CORS_ALLOW_ALL_ORIGINS = True

CORS_ALLOW_CREDENTIALS = True

CORS_ALLOW_METHODS = [
    'DELETE',
    'GET',
    'OPTIONS',
    'PATCH',
    'POST',
    'PUT',
]

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
]


# Email Configuration
EMAIL_BACKEND = os.getenv('EMAIL_BACKEND', 'django.core.mail.backends.console.EmailBackend')
EMAIL_HOST = os.getenv('EMAIL_HOST', 'smtp.gmail.com')
EMAIL_PORT = int(os.getenv('EMAIL_PORT', 587))
EMAIL_USE_TLS = os.getenv('EMAIL_USE_TLS', 'True') == 'True'
EMAIL_HOST_USER = os.getenv('EMAIL_HOST_USER', '')
EMAIL_HOST_PASSWORD = os.getenv('EMAIL_HOST_PASSWORD', '')
DEFAULT_FROM_EMAIL = os.getenv('DEFAULT_FROM_EMAIL', 'noreply@binder.com')


# Google Sheets API Configuration
GOOGLE_SHEETS_CREDENTIALS_FILE = os.getenv(
    'GOOGLE_SHEETS_CREDENTIALS_FILE',
    BASE_DIR / 'credentials.json'
)
GOOGLE_SHEETS_SPREADSHEET_ID = os.getenv('GOOGLE_SHEETS_SPREADSHEET_ID', '')


# Celery Configuration (for future async tasks)
# CELERY_BROKER_URL = os.getenv('REDIS_URL', 'redis://localhost:6379/0')
# CELERY_RESULT_BACKEND = os.getenv('REDIS_URL', 'redis://localhost:6379/0')
# CELERY_ACCEPT_CONTENT = ['json']
# CELERY_TASK_SERIALIZER = 'json'
# CELERY_RESULT_SERIALIZER = 'json'
# CELERY_TIMEZONE = TIME_ZONE


# Cache Configuration
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
        'LOCATION': 'unique-snowflake',
    }
}


# Logging Configuration
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '{levelname} {asctime} {module} {message}',
            'style': '{',
        },
    },
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'formatter': 'verbose',
        },
        'file': {
            'class': 'logging.FileHandler',
            'filename': BASE_DIR / 'logs' / 'debug.log',
            'formatter': 'verbose',
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
        'auth_service': {
            'handlers': ['console', 'file'],
            'level': 'DEBUG',
            'propagate': False,
        },
    },
}

# Create logs directory
os.makedirs(BASE_DIR / 'logs', exist_ok=True)


# Application-specific Settings
TENANT_USER_LIMIT_DEFAULT = int(os.getenv('TENANT_USER_LIMIT_DEFAULT', 40))
SESSION_TIMEOUT = int(os.getenv('SESSION_TIMEOUT', 3600))


# Security Settings for Production
if not DEBUG:
    SECURE_SSL_REDIRECT = os.getenv('SECURE_SSL_REDIRECT', 'True') == 'True'
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True
    SECURE_BROWSER_XSS_FILTER = True
    SECURE_CONTENT_TYPE_NOSNIFF = True
    SECURE_HSTS_SECONDS = 31536000
    SECURE_HSTS_INCLUDE_SUBDOMAINS = True
    SECURE_HSTS_PRELOAD = True
    X_FRAME_OPTIONS = 'DENY'
    # CSRF trusted origins for Render
    CSRF_TRUSTED_ORIGINS = [
    'https://' + host for host in ALLOWED_HOSTS if host != '*'
] + [
    'https://binder-frontend-self.vercel.app',
    'http://localhost:5173',
]


# Swagger/OpenAPI Configuration
SWAGGER_SETTINGS = {
    'SECURITY_DEFINITIONS': {
        'Bearer': {
            'type': 'apiKey',
            'name': 'Authorization',
            'in': 'header',
            'description': 'JWT authorization using Bearer scheme. Example: "Bearer {token}"'
        }
    },
    'USE_SESSION_AUTH': False,
    'JSON_EDITOR': True,
    'SUPPORTED_SUBMIT_METHODS': [
        'get',
        'post',
        'put',
        'delete',
        'patch'
    ],
}


# Twilio Configuration (Future Use - Currently Commented)
# TWILIO_ACCOUNT_SID = os.getenv('TWILIO_ACCOUNT_SID', '')
# TWILIO_AUTH_TOKEN = os.getenv('TWILIO_AUTH_TOKEN', '')
# TWILIO_PHONE_NUMBER = os.getenv('TWILIO_PHONE_NUMBER', '')


# Wati Configuration (Future Use - Currently Commented)
# WATI_API_ENDPOINT = os.getenv('WATI_API_ENDPOINT', 'https://live-server.wati.io')
# WATI_API_KEY = os.getenv('WATI_API_KEY', '')


# Unfold Admin Configuration
UNFOLD = {
    "SITE_TITLE": "Binder ERP Admin",
    "SITE_HEADER": "Binder ERP",
    "SITE_URL": "/",
    # "SITE_ICON": {
    #     "light": lambda request: static("icon-light.svg"),
    #     "dark": lambda request: static("icon-dark.svg"),
    # },
    "SIDEBAR": {
        "show_search": True,
        "show_all_applications": True,
        "navigation": [
            {
                "title": "Navigation",
                "separator": True,
                "items": [
                    {
                        "title": "Dashboard",
                        "icon": "dashboard",
                        "link": lambda request: "/admin/",
                    },
                ],
            },
        ],
    },
    "TABS": [
        {
            "models": [
                "auth.user",
                "auth.group",
            ],
            "items": [
                {
                    "title": "Users",
                    "link": lambda request: "/admin/auth/user/",
                },
                {
                    "title": "Groups",
                    "link": lambda request: "/admin/auth/group/",
                },
            ],
        },
    ],
}

# CORS_REPLACE_HTTPS_REFERER = False
# HOST_SCHEME = "http://"
# SECURE_PROXY_SSL_HEADER = None
# SECURE_SSL_REDIRECT = False
# SESSION_COOKIE_SECURE = False
# CSRF_COOKIE_SECURE = False
# SECURE_HSTS_SECONDS = None
# SECURE_HSTS_INCLUDE_SUBDOMAINS = False
# SECURE_FRAME_DENY = False

# CORS_REPLACE_HTTPS_REFERER = False


HOST_SCHEME = "http://"
SECURE_PROXY_SSL_HEADER = None
SECURE_SSL_REDIRECT = False
SESSION_COOKIE_SECURE = False
CSRF_COOKIE_SECURE = False
SECURE_HSTS_SECONDS = None
SECURE_HSTS_INCLUDE_SUBDOMAINS = False
SECURE_FRAME_DENY = False



