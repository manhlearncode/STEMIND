import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

BASE_DIR = Path(__file__).resolve().parent.parent
STATIC_DIR = BASE_DIR / 'static'

# SECURITY SETTINGS
SECRET_KEY = os.environ.get('SECRET_KEY', 'your-default-insecure-key')
DEBUG = os.environ.get('DEBUG', 'True').lower() == 'true'
ALLOWED_HOSTS = os.environ.get('ALLOWED_HOSTS', '*').split(',')

# APPLICATIONS
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    'File_sharing_platform',
    'Chatbot',  
    'Social_Platform',
    'storages',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    # 'Social_Platform.middleware.profile_completion.ProfileCompletionMiddleware',
]

ROOT_URLCONF = 'The_Chalk.urls'

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

WSGI_APPLICATION = 'The_Chalk.wsgi.application'

# DATABASE
DATABASES = {
    'default': {
        'ENGINE': os.environ.get('DB_ENGINE', 'django.db.backends.sqlite3'),
        'NAME': os.environ.get('DB_NAME', BASE_DIR / 'db.sqlite3'),
        'USER': os.environ.get('DB_USER', ''),
        'PASSWORD': os.environ.get('DB_PASSWORD', ''),
        'HOST': os.environ.get('DB_HOST', ''),
        'PORT': os.environ.get('DB_PORT', ''),

    }
}

# PASSWORD VALIDATORS
AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

# I18N
LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'Asia/Ho_Chi_Minh'
USE_I18N = True
USE_TZ = True

# STATIC & MEDIA
STATIC_URL = '/static/'
STATICFILES_DIRS = [STATIC_DIR]
STATIC_ROOT = BASE_DIR / 'staticfiles'

# AWS S3 CONFIG
AWS_ACCESS_KEY_ID = os.environ.get('AWS_ACCESS_KEY_ID')
AWS_SECRET_ACCESS_KEY = os.environ.get('AWS_SECRET_ACCESS_KEY')
AWS_STORAGE_BUCKET_NAME = os.environ.get('AWS_STORAGE_BUCKET_NAME')
AWS_S3_REGION_NAME = os.environ.get('AWS_S3_REGION_NAME', 'us-east-1')
AWS_S3_CUSTOM_DOMAIN = f"{AWS_STORAGE_BUCKET_NAME}.s3.amazonaws.com"

AWS_DEFAULT_ACL = 'public-read'
AWS_QUERYSTRING_AUTH = False
AWS_S3_FILE_OVERWRITE = False
AWS_S3_VERIFY = True
AWS_S3_SECURE_URLS = True
AWS_PRELOAD_METADATA = True
AWS_IS_GZIPPED = True

AWS_S3_OBJECT_PARAMETERS = {
    'CacheControl': 'max-age=86400',
}

AWS_GZIP_CONTENT_TYPES = [
    'text/css',
    'text/javascript',
    'application/javascript',
    'application/x-javascript',
    'image/svg+xml',
]

# FILE STORAGE (S3 BACKEND)
STORAGES = {
    "default": {
        "BACKEND": "storages.backends.s3boto3.S3Boto3Storage",
    },
    'staticfiles': {
        'BACKEND': 'django.contrib.staticfiles.storage.StaticFilesStorage',  # dùng local static
    },
    "media": {
        "BACKEND": "storages.backends.s3boto3.S3Boto3Storage",
    }
}

MEDIA_URL = f'https://{AWS_S3_CUSTOM_DOMAIN}/media/'

# DEFAULT PRIMARY KEY FIELD
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# FILE UPLOAD SETTINGS
DATA_UPLOAD_MAX_MEMORY_SIZE = 524288000  # 500MB in bytes
FILE_UPLOAD_MAX_MEMORY_SIZE = 524288000  # 500MB in bytes
DATA_UPLOAD_MAX_NUMBER_FIELDS = 1000
DATA_UPLOAD_MAX_NUMBER_FILES = 100

# CUSTOM UPLOAD LIMITS
MAX_FILE_SIZE = 524288000  # 500MB in bytes
MAX_CHATBOT_FILE_SIZE = 524288000  # 500MB for chatbot
MAX_THUMBNAIL_SIZE = 5242880  # 5MB for thumbnails

# GOOGLE GEMINI
GEMINI_API_KEY = os.environ.get('GOOGLE_API_KEY', '')

# OPTIONAL: EMAIL CONFIG
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = os.environ.get("EMAIL_HOST", "smtp.gmail.com")
EMAIL_PORT = int(os.environ.get("EMAIL_PORT", 587))
EMAIL_USE_TLS = os.environ.get("EMAIL_USE_TLS", "True").lower() == "true"
EMAIL_HOST_USER = os.environ.get("EMAIL_HOST_USER", "")
EMAIL_HOST_PASSWORD = os.environ.get("EMAIL_HOST_PASSWORD", "")

# LOGGING (BASIC)
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
        },
        'file': {
            'class': 'logging.FileHandler',
            'filename': BASE_DIR / 'debug.log',
        },
    },
    'root': {
        'handlers': ['console', 'file'],
        'level': 'INFO',
    },
}

AUTH_USER_MODEL = 'Social_Platform.CustomUser'
