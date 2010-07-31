import re

from django.db import models
from django.utils.safestring import mark_safe
from django.utils.translation import ugettext_lazy as _

from managers import StatementManager, TagManager
from color import ColorField

_STATEMENT_STATUS = (
    ('p', 'published'),
    ('u', 'unpublished'),    
)

_PUNCTUATION_MATCH = re.compile('[,.:;]{1,3}$')

class Statement(models.Model):
    """ A model of a statement. """
    text = models.TextField(_("Statement"), 
        db_index = True,
        unique = True
    )
    tag = models.ForeignKey("Tag")
    status = models.CharField(_("Status"), 
        choices = _STATEMENT_STATUS,
        db_index = True,
        default = 'p',
        max_length = 1,
    )
    date_created = models.DateTimeField(_("Date created"),
        auto_now_add = True
    )
    author = models.CharField(_("Author"), 
        blank=True,
        max_length = 100
    )
    title = models.CharField(_("Title"),
        blank=True,
        max_length = 100
    )
    
    objects = StatementManager()
    
    class Meta:
        ordering = ['-date_created', 'text']
        get_latest_by = 'date_created'
    
    def __unicode__(self):
        """
        Show the first 12 words, then an ellipsis for the rest if necessary.
        """
        max_words = 12
        words = self.text.split(" ")
        preview = " ".join(words[0:max_words])
        
        if len(words) > max_words:
            preview = _PUNCTUATION_MATCH.sub('', preview)
            preview += "... "
        return preview
    
    def published(self):
        return self.status == 'p'
    published.boolean = True

# We're using the class_prepared signal to ensure that a CSV file is generated 
# once on startup. The reason this has to go here is subtle: attaching a signal
# to the Tag model requires that it be conneced before the model class is 
# actually declared. We need to ensure that the Tag *and* Statement models are
# prepared becuase they are both needed to generate the CSV. Thus the only 
# place this can go is between the two model classes.
def export_csv_callback(sender, **kwargs):
    """ Export a CSV file when the Tag model is prepared."""
    if sender._meta.object_name == 'Tag':
        print "Registering"
        Statement.objects.export_csv()

from django.db.models.signals import class_prepared
#class_prepared.connect(export_csv_callback)


class Tag(models.Model):
    slug = models.SlugField(_("Slug"),
        help_text = "Used to generate URL.",
        unique = True
    )
    tag = models.CharField(_("Tag"),
        max_length= 100,
        unique = True
    )
    color = ColorField()
    date_created = models.DateTimeField(_("Date created"),
        auto_now_add = True
    )
    objects = TagManager()
    
    class Meta:
        ordering = ['tag']
    
    def __unicode__(self):
        return self.tag
    
    def tag_name(self):
        html = (
            '<div style="background-color: #%s; width: 12px; '
            'height: 12px; float: left;"></div>'
        ) % self.color
        html += '&nbsp;' + self.__unicode__()
        return html
        
    tag_name.allow_tags = True
