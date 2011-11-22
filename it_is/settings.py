import json
from  project_utils import get_env_setting, get_folder_path


try:
    with open('/home/dotcloud/environment.json') as f:
        env = json.load(f)
except IOError:
    env = {}


DEBUG = get_env_setting(env, "DEBUG", default=True)
TEMPLATE_DEBUG = DEBUG

ADMINS = (
    ('James Stevenson', 'james.m.stevenson@gmail.com'),
)

MANAGERS = ADMINS


DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': 'it_is',
        'USER': get_env_setting(env, 'DB_SQL_LOGIN'),
        'PASSWORD': get_env_setting(env, 'SQL_PASSWORD'),
        'HOST': get_env_setting(env, 'DOTCLOUD_DB_SQL_HOST'),
        'PORT': int(get_env_setting(env, 'DOTCLOUD_DB_SQL_PORT', default=0))
    }
}



TIME_ZONE = 'America/New_York'
LANGUAGE_CODE = 'en-us'

SITE_ID = 1
USE_I18N = True
USE_L10N = True

MEDIA_ROOT = get_folder_path('media')
MEDIA_URL = '/media/'
ADMIN_MEDIA_PREFIX = '/static/admin/'

MEDIA_ROOT = '/home/dotcloud/data/media/'
MEDIA_URL = '/media/'
STATIC_ROOT = '/home/dotcloud/data/static/'
STATIC_URL = '/static/'
ADMIN_MEDIA_PREFIX = '/static/admin/'

STATICFILES_FINDERS = (
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
)
STATICFILES_DIRS = (
    get_folder_path('static'),
)

if 'SECRET_KEY' in env:
    SECRET_KEY = env['SECRET_KEY']
else:
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
   get_folder_path('templates'), 
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
    'it_is.apps.statements'
)

GOOGLE_ANALYTICS_ACCOUNT = get_env_setting(env, "GOOGLE_ANALYTICS_ACCOUNT")
SHARE_THIS_ACCOUNT = get_env_setting(env, "SHARE_THIS_ACCOUNT")
RECAPTCHA_PUBLIC_KEY = get_env_setting(env, "RECAPTCHA_PUBLIC_KEY")
RECAPTCHA_PRIVATE_KEY = get_env_setting(env, "RECAPTCHA_PRIVATE_KEY")



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