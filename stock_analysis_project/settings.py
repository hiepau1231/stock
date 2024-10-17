INSTALLED_APPS = [
    # Existing apps...
    'rest_framework',
    'channels',
    'apps.authentication',
    'apps.stock_analysis',
    'apps.predictions',
    'apps.real_time_services',
]
# At the end of the file
ASGI_APPLICATION = 'stock_analysis_project.asgi.application'

CHANNEL_LAYERS = {
    'default': {
        'BACKEND': 'channels.layers.InMemoryChannelLayer',
    },
}

REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework.authentication.SessionAuthentication',
        'rest_framework.authentication.TokenAuthentication',
    ),
    'DEFAULT_PERMISSION_CLASSES': (
        'rest_framework.permissions.IsAuthenticated',
    ),
}
# Existing settings...
AUTH_USER_MODEL = 'authentication.CustomUser'
# Existing settings...
import os
from decouple import config

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': config('DB_NAME'),
        'USER': config('DB_USER'),
        'PASSWORD': config('DB_PASSWORD'),
        'HOST': config('DB_HOST', default='localhost'),
        'PORT': config('DB_PORT', default='5432'),
    }
}
