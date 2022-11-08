"""
Django settings for local development.
"""

from .base import *

# Host
ALLOWED_HOSTS = [
    'localhost',
    'glmt-api.development.humanitarian.tech',
]

# CORS settings

CORS_ORIGIN_WHITELIST = [
    'http://localhost:4200',
    'http://localhost:4300',
    'http://localhost:8080',
    'http://127.0.0.1:8080',
    'https://glmt-admin.development.humanitarian.tech',
    'https://glmt-main.development.humanitarian.tech',
]

CORS_ALLOWED_ORIGIN_REGEXES = [
    r'^http://172\.(?:1[6-9]|2[0-9]|3[01]).(\d|\.)*:8080$',
    r'^http://192\.168.(\d|\.)*:8080$'
]

CSRF_TRUSTED_ORIGINS = [
    'https://glmt-api.development.humanitarian.tech'
]