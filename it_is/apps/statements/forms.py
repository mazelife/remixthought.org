import math 

from django.core.exceptions import ImproperlyConfigured
from django.core.mail import send_mail
from django import forms
from django.utils.translation import ugettext_lazy as _

from models import Statement, Tag
from recaptcha_django import ReCaptchaField, ReCaptchaWidget

class StatementForm(forms.ModelForm):
    """
    A form to handle admin-submitted statements.
    """
    tag = forms.CharField(max_length=100)
    
    def clean_tag(self):
        tag = self.cleaned_data['tag']
        obj, created = Tag.objects.get_or_create_from_tag(tag)
        return obj
    
    def clean_text(self):
        """Remove initial capitalization."""
        text = self.cleaned_data['text']
        return text[0].lower() + text[1:]
        
    class Meta:
        model = Statement
        fields = ('text', 'tag')

class StatementFormWithCaptcha(StatementForm):
    """
    A form to handle user-submitted statements.
    """
    captcha = ReCaptchaField(widget=ReCaptchaWidget(attrs={'theme':'clean'}))


class URLImportForm(forms.Form):
    url = forms.URLField(
        help_text =_("Works best with a plain-text URL."),
        label=_("URL"))
    default_tag = forms.CharField(
        label=_("Default tag"), 
        max_length=200, 
        required="False"
    )
    
class CSVImportForm(forms.Form):
    csv = forms.FileField(label=_("CSV File"))
    dialect = forms.ChoiceField(label=_("Export Type"), choices=(
        ('excel', 'MS Excel CSV Export'),
        ('plain', 'Pure CSV')        
    ))

    def clean_csv(self):
        """Ensure the CSV is not too large."""
        csv_fileobj = self.cleaned_data['csv']
        size = int(math.ceil(csv_fileobj.size/1024.0))
        if size > 200:
            raise forms.ValidationError((
                "File must be less than 200k. This file is %d kilobytes."
            ) % size)
        return csv_fileobj

class StatementSuggestionForm(forms.Form):
    """Allows a user to suggest a statement source."""
    url = forms.URLField(
        label =_("URL of source"),
        required=False
    )
    other_source = forms.CharField(
        label=_("Other source"),
        max_length=200,
        widget= forms.Textarea,
        required=False        
    )
    comments = forms.CharField(
        label=_("Comments about your source (optional)"),
        max_length=200,
        widget= forms.Textarea,
        required=False    
    )
    email = forms.EmailField(
        label=_("Your email (optional)"),
        required=False        
    )
    captcha = ReCaptchaField(widget=ReCaptchaWidget(attrs={'theme':'clean'}))
    
    def clean(self):
        url = self.cleaned_data['url']
        other_source = self.cleaned_data['other_source']
        if not url and not other_source:
            raise forms.ValidationError, \
                "Either URL of source or Other source field must be filled."
        return self.cleaned_data
    
    def send(self):
        """
        Emails form data to addresses in SOURCE_SUGGESTION_EMAIL_LIST setting.
        """
        from django.conf import settings
        if hasattr(settings, 'SOURCE_SUGGESTION_EMAIL_LIST'):
            to = settings.SOURCE_SUGGESTION_EMAIL_LIST
        else:
            raise ImproperlyConfigured, \
                "SOURCE_SUGGESTION_EMAIL_LIST setting is not present."
        message = (
            "URL: %(url)s \n Other source: %(other_source)s \n"
            "Comments: %(comments)s \n Email: %(email)s"
        )
        send_mail(
            subject = "It Is Source Suggestion",
            message = message,
            from_email = 'source_suggest@remixthought.org',
            recipient_list = to
        )