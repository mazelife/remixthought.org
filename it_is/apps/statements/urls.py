from django.conf.urls.defaults import *

urlpatterns = patterns('apps.statements.views', 
    url(r'^$', 'index', name="index"),
    url(r'^add/$', 'add_statement', name="add"),
    # API Calls:
    url(r'api/statements/(?P<count>[\d]+)/?$', 'api_statements'),
    url(r'api/statements/count/$', 'api_statements_count'),
    url(r'api/tags/$', 'api_tags'),
    url(r'api/tags/popular/$', 'api_tags_most_used'),
    url(r'api/tags/search/(?P<q>[\w ]+)/?$', 'api_tags_search'),    
)    
