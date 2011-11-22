import os
os.environ['DJANGO_SETTINGS_MODULE'] = 'it_is.settings'
import django.core.handlers.wsgi
application = django.core.handlers.wsgi.WSGIHandler()
