from django.urls import path
from . import views

app_name = 'sales'

urlpatterns = [
    path('', views.sale_list, name='sale_list'),
    path('sale/<int:id>/', views.sale_detail, name='sale_detail'),
    path('create/', views.sale_create, name='sale_create'),
    path('update/<int:id>/', views.sale_update, name='sale_update'),
    path('delete/<int:id>/', views.sale_delete, name='sale_delete'),
]