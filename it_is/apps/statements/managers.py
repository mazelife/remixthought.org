import datetime

from django.db import models
from django.db.models import Count
from django.template.defaultfilters import slugify

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
        obj, created = self.get_or_create(slug=slug, tag=tag)
        if created:
            obj.color = color_picker.get_color()
            obj.save()
        return obj, created