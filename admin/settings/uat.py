"""
Django settings for local development.
"""

from .base import *

# Host
ALLOWED_HOSTS = [
    'glmt-api.development.humanitarian.tech',
]

# CORS settings

CORS_ORIGIN_WHITELIST = [
    'https://glmt-admin.development.humanitarian.tech',
    'https://glmt-main.development.humanitarian.tech',
]

CSRF_TRUSTED_ORIGINS = [
    'https://glmt-api.development.humanitarian.tech'
]