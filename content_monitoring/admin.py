from django.contrib import admin

from .models import ContentItem, FlagRecord

admin.site.register(ContentItem)
admin.site.register(FlagRecord)
