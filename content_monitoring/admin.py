from django.contrib import admin

from .models import ContentItem, Flag, Keyword

admin.site.register(Keyword)
admin.site.register(ContentItem)
admin.site.register(Flag)
