import cStringIO
import csv
import datetime
from os import rename

from django.db import models
from django.db.models import Count
from django.template.defaultfilters import slugify

from app_settings import CSV_DATA_FILE_PATH
from color import color_picker

class StatementManager(models.Manager):

    def published(self):
        return self.get_query_set().select_related().filter(
                status='p'
            ).exclude(
                date_created__gt=datetime.datetime.now()
            )
    
    def get_random_set(self, count=None):
        """ Get a random set of statements the length of ``count``."""
        if count:
            return self.published().order_by("?")[:count]
        else:
            return self.published().order_by("?")
    
    def get_csv(self, id_list=[]):
        """
        Get a CSV-formatted string of all statements, or restrict to a list of 
        ids with ``id_list``.
        """
        if id_list:
            statements = ((s.text, s.tag.tag) for s in \
                self.published().filter(id__in=id_list).only('text', 'tag'))
        else:
            statements = ((s.text, s.tag.tag) for s in \
                self.published().only('text', 'tag'))
        fh = cStringIO.StringIO()
        csv_writer = csv.writer(fh)
        for statement, tag in statements:
            # CSV doesn't grok unicode, so we convert entities and encode 
            # as UTF-8, which it can handle. 
            statement = unescape(statement).encode('utf-8')
            tag = unescape(tag).encode('utf-8')
            csv_writer.writerow((statement, tag))        
        fh.reset()
        retval = fh.read()
        fh.close()
        return retval
        
    def export_csv(self):
        """
        Export a CSV file of all statements to the media directory.
        """
        statements = ((s.text, s.tag.tag) for s in \
            self.published().only('text', 'tag'))
        fh = open(CSV_DATA_FILE_PATH + ".tmp", 'w')
        csv_writer = csv.writer(fh)
        for statement, tag in statements:
            # CSV doesn't grok unicode, so we convert entities and encode 
            # as UTF-8, which it can handle. 
            statement = unescape(statement).encode('utf-8')
            tag = unescape(tag).encode('utf-8')
            csv_writer.writerow((statement, tag))
        fh.close()
        rename(CSV_DATA_FILE_PATH + ".tmp", CSV_DATA_FILE_PATH)


def unescape(text):
    """
    Convert HTML entities to unicode equivalents.
    By Frederick Lundh: effbot.org/zone/re-sub.html#unescape-html
    """
    import re, htmlentitydefs
    def fixup(m):
        text = m.group(0)
        if text[:2] == "&#":
            # character ref
            try:
                if text[:3] == "&#x":
                    return unichr(int(text[3:-1],1))
                else:
                    return unichr(int(text[2:-1]))
            except ValueError:
                pass
        else:
            #named entity
            try:
                text = unichr(htmlentitydefs.name2codepoint[text[1:-1]])
            except KeyError:
                pass
        return text
    return re.sub("&#?\w+;", fixup, text)


class TagManager(models.Manager):

    def most_used(self, count=20):
        """
        Return a list of the most-used tags (limited by the ``limit`` 
        argument).
        """
        qs = self.get_query_set().annotate(
            times_used=Count('statement')).order_by('times_used').reverse()
        return qs[:count]
    
    def get_or_create_from_tag(self, tag):
        """
        Tries to see if a tag matching ``tag`` exists, creates it if it does 
        not. Returns the match or newly-created tag. This works a bit 
        differently from the standard ``get_or_create`` method in that it will
        generate the slug automatically from the given tag.
        """
        slug = slugify(tag)
        tag = tag.title()
        obj, created = self.get_or_create(slug=slug, tag=tag)
        if created:
            obj.color = color_picker.get_color()
            obj.save()
        return obj, created