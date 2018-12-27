from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('apps.home.urls')),
    path('items/', include('apps.items.urls')),
    path('sales/', include('apps.sales.urls')),
]
