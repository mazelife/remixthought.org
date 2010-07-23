from django.conf import settings
from django.core.urlresolvers import reverse
from django.conf.urls.defaults import patterns, url
from django.contrib import admin
from django.http import HttpResponseBadRequest
from django.views.generic import simple

from extract import from_csv
from forms import ImportForm, StatementForm
from models import Statement, Tag

class StatementAdmin(admin.ModelAdmin):
    date_hierarchy = 'date_created'
    exclude = ('author', 'title')
    list_display = ('__unicode__', 'published', 'tag', 'date_created')
    list_filter = ('status', 'tag',)
    search_fields = ('text',)
    
    def get_urls(self):
        urls = super(StatementAdmin, self).get_urls()
        my_urls = patterns('',
            url(r'^import/$', self.admin_site.admin_view(
                self.import_view, 
                cacheable=True
            ), name="statements_statement_import")
        )
        return my_urls + urls
    
    def import_view(self, request):
        records = None
        if request.method == 'POST':
            if request.POST.get('count', None):
                count = request.POST.get('count')
                if count.isdigit():
                    count = int(count)
                else:
                    return HttpResponseBadRequest("Count is not a number.")
                for i in range(1, (count + 1)):
                    data = {
                        'text': request.POST.get("s%d" % i),
                        'tag': request.POST.get("t%d" % i)
                    }
                    form = StatementForm(data)
                    if form.is_valid():
                        form.save()
                    else:
                        err_string = ""
                        for field, errs in form.errors.items():
                            errs = ", ".join(errs)
                            err_string += "%s: %s ," % (field, errs)
                        return HttpResponseBadRequest(
                            "Validation error: %s" % err_string
                        )
                url = reverse('admin:statements_statement_changelist')
                simple.redirect_to(request, url)
            else:    
                form = ImportForm(request.POST, request.FILES)
                if form.is_valid():
                    dialect = form.cleaned_data['dialect']
                    contents = form.cleaned_data['csv']
                    records = from_csv(contents, is_excel=(dialect == 'excel'))
        else:
            form = ImportForm()
        return simple.direct_to_template(request,
            template = 'statements/admin/import.html',
            extra_context = {
                'title': 'Import Statements',
                'form': form,
                'records': records
            }
        )

class TagAdmin(admin.ModelAdmin):
    date_hierarchy = 'date_created'
    list_display = ('tag_name', 'date_created')
    
     
admin.site.register(Statement, StatementAdmin)
admin.site.register(Tag, TagAdmin)