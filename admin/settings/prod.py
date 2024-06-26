"""
Django settings for prod.
"""

from .base import *

# Pass in Production
DEBUG = True

# Get the SECRET_KEY from the environment. Needs to be set in the CI step.
SECRET_KEY = get_env_value('SECRET_KEY')
SECRET_KEY_FALLBACKS = [
    '_nnx-zxrozl5p8w58%evez(#$r0a_y8#8__)iczmlys=5iz322',   # Original local key
]

# Host
ALLOWED_HOSTS = [
    'api.gobee-education.org',  # Azure API
]

# CORS settings

CORS_ORIGIN_WHITELIST = [
    'https://play.gobee-education.org',  # Azure assessment tool
    'https://admin.gobee-education.org'  # Azure admin dashboard
]

CORS_ALLOW_METHODS = [
    'DELETE',
    'GET',
    'OPTIONS',
    'PATCH',
    'POST',
    'PUT',
]

CSRF_TRUSTED_ORIGINS = [
    'https://api.gobee-education.org'
]

# WSGI application ---> TO DO TO FINALIZE PROD
WSGI_APPLICATION = 'admin.wsgi.application'
