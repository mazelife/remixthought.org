from django.conf.urls.defaults import *

urlpatterns = patterns('apps.statements.views', 
    url(r'^$', 'index', name="index"),
    url(r'^add/$', 'add_statement', name="add"),
    url(r'^suggest/$', 'suggest_statement', name="suggest"),
    # API Calls:
    url(r'api/statements/$', 'api_statements_all'),
    url(r'api/statements/(?P<count>[\d]+)/?$', 'api_statements'),
    url(r'api/statements/search/(?P<tag>[^/]+)/?$', 'api_statements_search'),
    url(r'api/statements/list/(?P<pks>[\d,]+)/?$', 'api_statements_commalist'),
    url(r'api/statements/count/$', 'api_statements_count'),
    url(r'api/tags/$', 'api_tags'),
    url(r'api/tags/popular/$', 'api_tags_most_used'),
    url(r'api/tags/search/(?P<q>[\w ]+)/?$', 'api_tags_search'),    
)