# Django settings for it_is project.

import project_utils

DEBUG = False
TEMPLATE_DEBUG = DEBUG

ADMINS = (
    ('James Stevenson', 'james.m.stevenson@gmail.com'),
)

MANAGERS = ADMINS

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.', # Add 'postgresql_psycopg2', 'postgresql', 'mysql', 'sqlite3' or 'oracle'.
        'NAME': '',                      # Or path to database file if using sqlite3.
        'USER': '',                      # Not used with sqlite3.
        'PASSWORD': '',                  # Not used with sqlite3.
        'HOST': '',                      # Set to empty string for localhost. Not used with sqlite3.
        'PORT': '',                      # Set to empty string for default. Not used with sqlite3.
    }
}


TIME_ZONE = 'America/New_York'
LANGUAGE_CODE = 'en-us'

SITE_ID = 1
USE_I18N = True
USE_L10N = True

MEDIA_ROOT = project_utils.get_folder_path('static')
MEDIA_URL = ''
ADMIN_MEDIA_PREFIX = '/static/admin/'

SECRET_KEY = 'wd3p7sqoeu^+$s4@)!-erdl5&jzi0a_c!yn(!jf&@@4#ft%m#h'

TEMPLATE_LOADERS = (
    'django.template.loaders.filesystem.Loader',
    'django.template.loaders.app_directories.Loader',
)

MIDDLEWARE_CLASSES = (
    'django.middleware.common.CommonMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'recaptcha_django.middleware.ReCaptchaMiddleware',
    'django.contrib.flatpages.middleware.FlatpageFallbackMiddleware'
)

ROOT_URLCONF = 'it_is.urls'

TEMPLATE_DIRS = (
   project_utils.get_folder_path('templates'), 
)

INSTALLED_APPS = (
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.sites',
    'django.contrib.staticfiles',
    'django.contrib.messages',
    'django.contrib.admin',
    'django.contrib.flatpages',
    'apps.statements'
)

GOOGLE_ANALYTICS_ACCOUNT = None
SHARE_THIS_ACCOUNT = None

try:
    from local_settings import *
except ImportError:
    pass

try:
    TEMPLATE_DIRS = TEMPLATE_DIRS + LOCAL_TEMPLATE_DIRS
except NameError:
    pass
try:
    INSTALLED_APPS = INSTALLED_APPS + LOCAL_INSTALLED_APPS
except NameError:
    pass
try:
    TEMPLATE_CONTEXT_PROCESSORS += LOCAL_TEMPLATE_CONTEXT_PROCESSORS
except NameError:
    pass
try:
    MIDDLEWARE_CLASSES += LOCAL_MIDDLEWARE_CLASSES
except NameError:
    pass