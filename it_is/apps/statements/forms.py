from django import forms

from models import Statement, Tag
from recaptcha_django import ReCaptchaField

class StatementForm(forms.ModelForm):
    """
    A form to handle user-submitted statements.
    """
    tag = forms.CharField(max_length=100)
    captcha = ReCaptchaField()
    
    def clean_tag(self):
        tag = self.cleaned_data['tag']
        obj, created = Tag.objects.get_or_create_from_tag(tag)
        return obj
        
    class Meta:
        model = Statement
        fields = ('text', 'tag')