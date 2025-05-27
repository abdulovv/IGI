from django.contrib import admin
from .models import Supplier, Product, Purchase, PriceChange, Category

admin.site.register(Supplier)
admin.site.register(Product)
admin.site.register(Purchase)
admin.site.register(PriceChange)
admin.site.register(Category)
