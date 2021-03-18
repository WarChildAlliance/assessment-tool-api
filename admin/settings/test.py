from .base import *

TEST = True

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': get_env_value('POSTGRES_DB'),
        'USER': get_env_value('POSTGRES_USER'),
        'PASSWORD': get_env_value('POSTGRES_PASSWORD'),
        'HOST': 'postgres',
        'PORT': 5432,
        'CONN_MAX_AGE': 30
    },
}
