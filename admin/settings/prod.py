"""
Django settings for prod.
"""

from .base import *

# Pass in Production
DEBUG = False

# Get the SECRET_KEY from the environment. Needs to be set in the CI step.
SECRET_KEY = get_env_value('SECRET_KEY')

# Host
ALLOWED_HOSTS = [
    'api.gobee-education.org', # Azure API
]

# CORS settings

CORS_ORIGIN_WHITELIST = [
    'https://play.gobee-education.org', # Azure assessment tool
    'https://admin.gobee-education.org' # Azure admin dashboard
]

CORS_ALLOW_METHODS = [
    'DELETE',
    'GET',
    'OPTIONS',
    'PATCH',
    'POST',
    'PUT',
]

# WSGI application ---> TO DO TO FINALIZE PROD
WSGI_APPLICATION = 'admin.wsgi.application'
