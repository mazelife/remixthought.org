import datetime

from django.db import models
from django.db.models import Count


class StatementManager(models.Manager):
    """
    This manager can be used for blog and tumblelog entries becuase the 
    conditions for an entry being published in either are the same.
    """
    def published(self):
        """
        A tumblelog entry is published if its status is in the 
        PUBLISHED_ENTRY_STATES list in BloggingSettings (which can be overriden
        in the main settings file by setting BLOGGING_PUBLISHED_ENTRY_STATES) 
        the pub_date attribute is not in the future.
        """
        return self.get_query_set().filter(
                status='p'
            ).exclude(
                date_created__gt=datetime.datetime.now()
            )
    
    def get_random_set(self, count):
        """ Get a random set of statements the length of ``count``."""
        return self.published().order_by("?")[:count]

class TagManager(models.Manager):

    def most_used(self, count=20):
        """
        Return a list of the most-used tags (limited by the ``limit`` 
        argument).
        """
        qs = self.get_query_set().annotate(
            times_used=Count('statement')).order_by('times_used').reverse()
        return qs[:count]
