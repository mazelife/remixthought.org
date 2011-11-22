from itertools import tee
from random import shuffle
from threading import Thread

from django.core.cache import cache
from django.db.models.signals import post_save

from models import Statement, Tag

"""
This module provides some utilities for working with Statements and Tags.
"""

def decode_cookie_string(cs, split_on=','):
    """Safely return a list of statement ids."""
    pks = filter(lambda pk: pk.isdigit(), cs.split(split_on))
    return map(int, pks)

def async_export_csv():
    """
    Exports a CSV data file of all statements in a separate thread. With 
    this, users can spawn a thread to generate a new CSV without having to
    wait for the result.
    """
    class ExportCSVThread(Thread):

        def __init__ (self):
            Thread.__init__(self)

        def run(self):
            Statement.objects.export_csv()

    thread = ExportCSVThread()
    thread.start()


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
    if not globals().has_key(_TAG_LIST_GLOBAL_KEY):
        _create_tag_set()
    tags_origin = globals()[_TAG_LIST_GLOBAL_KEY]
    # tags_origin is a generator which, once used, cannot be rewound, so we'll 
    # copy it using itertools.tee().
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


class StatementCache(object):
    
    """
    A method of storing statements in cache rather than retrieving from the 
    database. Cuts an average of 10ms from the lookup.
    """
    cache_key = 'statement_list'
    ttl = 60 * 60 * 12
    
    def __init__(self):
        self._set_satetements()
    
    def _set_satetements(self):
        """
        Create a list of dicts representing statements from the DB.
        Store it using Django's low-level cache framwork.
        """
        statements = Statement.objects.published().only(
            'id', 'text', 'tag'
        )
        statement_list = []
        for statement in statements:
            statement_list.insert(0, {
                'id': statement.id,
                'statement': statement.text,
                'tag': [
                    statement.tag.slug, 
                    statement.tag.tag, 
                    statement.tag.color
                ]
            })
        cache.set(self.cache_key, statement_list, self.ttl)
        return statement_list
    
    def get_statements(self):
        """Randomly shuffle statement list and return it."""
        statements = cache.get(self.cache_key)
        if not statements:
            statements = self._set_satetements()
        shuffle(statements)
        return statements
    
    def statements_update_reciever(self, sender, **kwargs):
        """
        A method suitable for receiving a signal when statement(s)
        or tags(s) have changed and updating everything accordingly.
        
        """
        self._set_satetements()

statement_cache = StatementCache()
post_save.connect(statement_cache.statements_update_reciever, sender=Statement)
post_save.connect(statement_cache.statements_update_reciever, sender=Tag)