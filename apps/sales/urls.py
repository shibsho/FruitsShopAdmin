from django.urls import path
from . import views

app_name = 'sales'

urlpatterns = [
    path('', views.index, name='index'),
    path('register/', views.register, name='register'),
    path('<int:id>/edit/', views.edit, name='edit'),
    path('<int:id>/delete/', views.delete, name='delete'),
    path('csv_upload/', views.csv_upload, name='csv_upload'),
    path('statistics/', views.statistics, name='statistics')
]
