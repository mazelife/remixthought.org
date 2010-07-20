from django.contrib import admin

from models import Statement, Tag

class StatementAdmin(admin.ModelAdmin):
    date_hierarchy = 'date_created'
    exclude = ('author', 'title')
    list_display = ('__unicode__', 'published', 'tag', 'date_created')
    list_filter = ('status', 'tag',)
    search_fields = ('text',)

class TagAdmin(admin.ModelAdmin):
    date_hierarchy = 'date_created'
    list_display = ('tag_name', 'date_created')
    
     
admin.site.register(Statement, StatementAdmin)
admin.site.register(Tag, TagAdmin)