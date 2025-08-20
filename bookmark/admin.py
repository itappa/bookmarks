from django.contrib import admin

from .models import Category, Item, Tag

admin.site.register(Category)
admin.site.register(Tag)
admin.site.register(Item)
