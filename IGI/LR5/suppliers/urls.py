from django.urls import path
from . import views

app_name = 'suppliers'

urlpatterns = [
    path('', views.supplier_list, name='supplier_list'),
    path('supplier/<int:id>/', views.supplier_detail, name='supplier_detail'),
    path('create/', views.supplier_create, name='supplier_create'),
    path('update/<int:id>/', views.supplier_update, name='supplier_update'),
    path('delete/<int:id>/', views.supplier_delete, name='supplier_delete'),
]