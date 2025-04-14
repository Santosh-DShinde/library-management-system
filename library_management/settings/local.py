from ..base import *
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

SECRET_KEY = os.getenv("SECRET_KEY")

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = ["*"]

# Database settings for app
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.mysql",
        "NAME": os.getenv("DB_NAME"),
        "HOST": os.getenv("DB_HOST"),
        "PORT": os.getenv("DB_PORT"),
        "USER": os.getenv("DB_USER"),
        "PASSWORD": os.getenv("DB_PASSWORD"),
    }
}

CLIENT_ID = os.getenv("CLIENT_ID")
CLIENT_SECRET = os.getenv("CLIENT_SECRET")

SERVER_PROTOCOLS = "http://"

S_KEY = os.getenv("S_KEY").encode()

FRONT_END_URL = "http://127.0.0.1:8000/"
BASE_URL = "http://127.0.0.1:8000/api/v1/"

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': ['templates'],
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

MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR + "/media/"
STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR, "static")
