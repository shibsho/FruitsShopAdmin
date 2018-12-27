from django.contrib import admin
from .models import Sale

class SaleAdmin(admin.ModelAdmin):
    list_display = ('id', 'item', 'number', 'saled_at')
    list_display_links = ('id', 'item')


admin.site.register(Sale, SaleAdmin)
