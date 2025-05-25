from django.urls import path
from . import views

app_name = 'clients'

urlpatterns = [
    path('', views.client_list, name='client_list'),
    path('client/<int:id>/', views.client_detail, name='client_detail'),
    path('create/', views.client_create, name='client_create'),
    path('update/<int:id>/', views.client_update, name='client_update'),
    path('delete/<int:id>/', views.client_delete, name='client_delete'),
]