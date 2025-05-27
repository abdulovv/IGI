from django.urls import path
from . import views
from django.utils.text import slugify

urlpatterns = [
    path('', views.index, name='index'),
    path('catalog/', views.catalog_view, name='catalog'),
    path('catalog/<slug:category_slug>/', views.product_list_by_category, name='product_list_by_category'),
]
