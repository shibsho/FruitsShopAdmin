from django.contrib import admin
from .models import Item


class ItemAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'price', 'created_at', 'updated_at')
    list_display_links = ('id', 'name')


admin.site.register(Item, ItemAdmin)
