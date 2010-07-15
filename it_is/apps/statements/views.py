from django.core import serializers
from django.http import HttpResponse, HttpResponseBadRequest, Http404
from django.shortcuts import get_object_or_404
from django.utils import simplejson
from django.views.generic import simple

from models import Statement, Tag
from utils import get_param, get_numeric_param, tag_search

def index(request):
    return simple.direct_to_template(request,
        template = "index.html"    
    )

def api_statements(request, count=None):
    """A view of a JSON-serialized, reverse-chronologically-ordered set of  
    statements.
    """
    if not count:
        raise Http404 
    count = count.isdigit() and int(count) or 0
    offset = get_numeric_param(request, "offset") or 0
    tag = get_param(request, "tag")
    if tag:
        qs = Statement.objects.published().filter(
            tag__slug=tag
        )
    else:    
        qs = Statement.objects.published()
    statements = qs.only('id', 'text', 'tag')[offset:(offset + count)]
    if len(statements) == 0:
        raise Http404, "Offset is too large."
    statements_new_keys = []
    for statement in statements:
        statements_new_keys.append(dict(
            id=statement.id, 
            statement=statement.text,
            tag=[statement.tag.slug, statement.tag.tag]
        ))
    statements = simplejson.dumps(statements_new_keys, ensure_ascii=False)
    return HttpResponse(statements, mimetype="application/json")

def api_statements_count(request):
    statements = Statement.objects.published()
    tag = get_param(request, "tag")
    if tag:
        statements = statements.filter(tag__slug=tag)
    return HttpResponse("%d" % len(statements))

def api_tags(request):
    """A view of JSON-serialized tags."""
    tags = Tag.objects.all().order_by('tag')
    json_serializer = serializers.get_serializer("json")()
    tags = json_serializer.serialize(tags,
        ensure_ascii=False,
        fields=('slug', 'tag')
    )
    return HttpResponse(tags, mimetype="application/json")

def api_tags_search(request, q=None):
    """A view of a tag search."""
    if len(q) < 2:
        return HttpResponseBadRequest((
            "Query must be at least 2 characters long."
        ))
    tags = tag_search(q)
    tags = simplejson.dumps(tags, ensure_ascii=False)
    return HttpResponse(tags, mimetype="application/json")

def api_tags_most_used(request):
    """A view of the most used tags."""
    kwargs = {'count': 20}
    if request.GET.has_key('count'):
        count = request.GET['count']
        if count.isdigit():
            kwargs['count'] = int(count)
    tags = Tag.objects.most_used(**kwargs)
    json_serializer = serializers.get_serializer("json")()
    tags = json_serializer.serialize(tags,
        fields=('slug', 'tag')
    )
    return HttpResponse(tags, mimetype="application/json")
