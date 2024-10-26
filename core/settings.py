import os
from decouple import config
from unipath import Path

# Build paths
BASE_DIR = Path(__file__).parent.parent
CORE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Security settings
SECRET_KEY = config('SECRET_KEY', default='S#perS3crEt_1122')
DEBUG = config('DEBUG', default=True, cast=bool)
ALLOWED_HOSTS = ['localhost', '127.0.0.1', config('SERVER', default='127.0.0.1')]

# Application definition
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.humanize',
    
    # Third party apps
    'crispy_forms',
    
    # Local apps
    'apps.home',
    'apps.authentication',
    'apps.stock_analysis',
    'apps.predictions',
]

# Middleware configuration
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'apps.stock_analysis.middleware.RequestLoggingMiddleware',
]

# URL configuration
ROOT_URLCONF = 'core.urls'
LOGIN_URL = '/auth/login/'
LOGIN_REDIRECT_URL = "home"
LOGOUT_REDIRECT_URL = "home"

# Template configuration
TEMPLATE_DIR = os.path.join(CORE_DIR, "apps/templates")
TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [TEMPLATE_DIR],
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

WSGI_APPLICATION = 'core.wsgi.application'

# Database configuration
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': 'db.sqlite3',
    }
}

# Cache configuration
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
        'LOCATION': 'unique-snowflake',
    }
}

# Password validation
AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

# Internationalization
LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'Asia/Ho_Chi_Minh'
USE_I18N = True
USE_L10N = True
USE_TZ = True

# Static files configuration
STATIC_URL = '/static/'
STATICFILES_DIRS = [
    os.path.join(BASE_DIR, 'apps/static'),  # Cập nhật đường dẫn này
]
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')

# Logging configuration
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
            'level': 'DEBUG',
            'class': 'logging.FileHandler',
            'filename': 'debug.log',
            'formatter': 'verbose',
        },
        'console': {
            'level': 'INFO',
            'class': 'logging.StreamHandler',
            'formatter': 'simple',
        },
    },
    'loggers': {
        'django': {
            'handlers': ['file', 'console'],
            'level': 'INFO',
            'propagate': True,
        },
        'stock_analysis': {
            'handlers': ['file', 'console'],
            'level': 'DEBUG',
            'propagate': True,
        },
    },
}

# Third party apps configuration
CRISPY_TEMPLATE_PACK = 'bootstrap4'
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

STOCK_DATA_CACHE_TIMEOUT = 300  # 5 minutes
TECHNICAL_INDICATORS_CACHE_TIMEOUT = 600  # 10 minutes

ALPHA_VANTAGE_API_KEY = "GGO8XKMA3V6UUNV6"  # Replace with your actual API key

# Celery Configuration
CELERY_BROKER_URL = 'redis://localhost:6379'
CELERY_RESULT_BACKEND = 'redis://localhost:6379'
CELERY_ACCEPT_CONTENT = ['application/json']
CELERY_TASK_SERIALIZER = 'json'
CELERY_RESULT_SERIALIZER = 'json'
CELERY_TIMEZONE = 'Asia/Ho_Chi_Minh'

# Add retry and timeout configuration for requests
VNSTOCK_REQUEST_TIMEOUT = 30  # seconds
VNSTOCK_MAX_RETRIES = 3

# Add proxy configuration if needed
VNSTOCK_PROXY = None  # or {'http': 'http://proxy:port', 'https': 'https://proxy:port'}

# vnstock3 configuration
VNSTOCK_SETTINGS = {
    'REQUEST_TIMEOUT': 30,
    'MAX_RETRIES': 3,
    'RETRY_DELAY': 1,
    'USER_AGENT': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
    'PROXY': None,  # Or {'http': 'http://proxy:port', 'https': 'https://proxy:port'}
}

# Celery Configuration
CELERY_BEAT_SCHEDULE = {
    'update_historical_data': {
        'task': 'apps.stock_analysis.tasks.update_historical_data',
        'schedule': 3600.0,  # Chạy mỗi giờ
    },
    'update_recommendations': {
        'task': 'apps.stock_analysis.tasks.update_recommendations',
        'schedule': 604800.0,  # Chạy mỗi tuần
    },
}
