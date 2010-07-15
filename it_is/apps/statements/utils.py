from itertools import tee

from models import Tag

"""
This module provides some utilities for working with Statements and Tags.
"""

def get_param(request, param, method='GET'):
    """One-liner for fetching a value from a request."""
    return getattr(request, method).get(param, None)

def get_numeric_param(request, param, method='GET'):
    """Extends ``get_param`` to add some type checking."""
    param = get_param(request, param, method=method)
    if not param:
        return param
    return param.isdigit() and int(param) or None

_TAG_LIST_GLOBAL_KEY = "tags_list"

def tag_search(q, limit=None):
    """
    Returns a list of all tags matching ``q`` in the form:
    
        ({{slug}}, {{tag}})
    
    Searches a list of tags stored as a generator in the global namespace.
    Benchmarking indicates that this is about 170x faster than doing the same 
    query in SQL (i.e. ``Tag.objects.filter(tag__istartswith=q)``).
    """
    if len(q) < 2:
        return None
    if not globals().has_key(_TAG_LIST_GLOBAL_KEY):
        _create_tag_set()
    tags_origin = globals()[_TAG_LIST_GLOBAL_KEY]
    # tags_origin is a generator which, once used, cannot be rewound, so we'll 
    # copy it usint itertools.tee().
    globals()[_TAG_LIST_GLOBAL_KEY], tags = tee(tags_origin) 
    matches = []
    q = q.lower()
    for slug, tag, search_str in tags:
        if search_str.startswith(q):
            matches.append((slug, tag))
            if limit and len(matches) == limit:
                break
    return matches

def _create_tag_set():
    """
    Creates a generator containing all tags, stores it in the global namespace 
    with the name of ``TAG_LIST_GLOBAL_KEY``.
    """
    tags = Tag.objects.all().order_by('tag').values('slug', 'tag')
    tags = ((tag['slug'], tag['tag'], tag['tag'].lower()) for tag in tags)
    globals()[_TAG_LIST_GLOBAL_KEY] = tags