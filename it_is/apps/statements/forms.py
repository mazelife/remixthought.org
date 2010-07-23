import math 

from django import forms
from django.utils.translation import ugettext_lazy as _

from models import Statement, Tag
from recaptcha_django import ReCaptchaField

class StatementForm(forms.ModelForm):
    """
    A form to handle admin-submitted statements.
    """
    tag = forms.CharField(max_length=100)
    
    def clean_tag(self):
        tag = self.cleaned_data['tag']
        obj, created = Tag.objects.get_or_create_from_tag(tag)
        return obj
        
    class Meta:
        model = Statement
        fields = ('text', 'tag')

class StatementFormWithCaptcha(StatementForm):
    """
    A form to handle user-submitted statements.
    """
    captcha = ReCaptchaField()


class ImportForm(forms.Form):
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