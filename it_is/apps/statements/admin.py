from django.conf import settings
from django.core.urlresolvers import reverse
from django.conf.urls.defaults import patterns, url
from django.contrib import admin
from django.http import HttpResponseBadRequest
from django.views.decorators.http import require_POST
from django.views.generic import simple

from extract import from_csv, from_url
from forms import CSVImportForm, URLImportForm, StatementForm
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
            url(r'^import-url/$', self.admin_site.admin_view(
                self.import_url_view, 
                cacheable=True
            ), name="statements_statement_import_url"),
            url(r'^import-csv/$', self.admin_site.admin_view(
                self.import_csv_view, 
                cacheable=True
            ), name="statements_statement_import_csv"),
            url(r'^process/$', self.admin_site.admin_view(
                require_POST(self.process_view), 
                cacheable=True
            ), name="statements_statement_process")
        )
        return my_urls + urls
    
    def import_url_view(self, request):
        """
        Import and edit statements from a URL.
        """        
        records = None
        if request.method == 'POST':
            form = URLImportForm(request.POST)
            if form.is_valid():
                url = form.cleaned_data['url']
                default_tag = form.cleaned_data['default_tag']
                records = from_url(url, default_tag)
                return simple.direct_to_template(request,
                    template = 'admin/statements/statement/process.html',
                    extra_context = {
                        'title': 'Edit and import statements',
                        'records': records,
                        'type': 'url'
                    }
                )
        else:
            form = URLImportForm()
        return simple.direct_to_template(request,
            template = 'admin/statements/statement/import.html',
            extra_context = {
                'title': 'Import Statements',
                'form': form,
                'type': 'url'
            }
        )
    
    def import_csv_view(self, request):
        """
        Import and edit statements from a CSV file (uploaded).
        """
        records = None
        if request.method == 'POST':
            form = CSVImportForm(request.POST, request.FILES)
            if form.is_valid():
                dialect = form.cleaned_data['dialect']
                contents = form.cleaned_data['csv']
                records = from_csv(contents, is_excel=(dialect == 'excel'))
                return simple.direct_to_template(request,
                    template = 'admin/statements/statement/process.html',
                    extra_context = {
                        'title': 'Edit and import statements',
                        'records': records,
                        'type': 'csv'
                    }
                )
        else:
            form = CSVImportForm()
        return simple.direct_to_template(request,
            template = 'admin/statements/statement/import.html',
            extra_context = {
                'title': 'Import Statements',
                'form': form,
                'type': 'csv'
            }
        )        
    
    def process_view(self, request):
        """
        Create a set of statements in bulk, based on CSV upload or URL lookup.
        """
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
            return simple.redirect_to(request, url)                      

class TagAdmin(admin.ModelAdmin):
    date_hierarchy = 'date_created'
    list_display = ('tag_name', 'date_created')
    
     
admin.site.register(Statement, StatementAdmin)
admin.site.register(Tag, TagAdmin)