from django.contrib import admin
from .models import Category, Supplier, Product, Sale, Cart, CartItem, Order, OrderItem, Promo, PromoUsage

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'description')
    search_fields = ('name',)

@admin.register(Supplier)
class SupplierAdmin(admin.ModelAdmin):
    list_display = ('name', 'email', 'phone')
    search_fields = ('name', 'email', 'phone')

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'article', 'category', 'price', 'quantity')
    list_filter = ('category', 'suppliers')
    search_fields = ('name', 'article', 'description')
    filter_horizontal = ('suppliers',)

@admin.register(Sale)
class SaleAdmin(admin.ModelAdmin):
    list_display = ('product', 'quantity', 'price_per_unit', 'total_price', 'customer', 'date')
    list_filter = ('date', 'customer')
    search_fields = ('product__name', 'customer__username')
    readonly_fields = ('total_price', 'date')

@admin.register(Cart)
class CartAdmin(admin.ModelAdmin):
    list_display = ('customer', 'total_price', 'total_items', 'created_at')
    search_fields = ('customer__username',)
    readonly_fields = ('created_at', 'updated_at')

@admin.register(CartItem)
class CartItemAdmin(admin.ModelAdmin):
    list_display = ('cart', 'product', 'quantity', 'total_price')
    search_fields = ('cart__customer__username', 'product__name')

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('id', 'customer', 'status', 'total', 'created_at')
    list_filter = ('status', 'created_at')
    search_fields = ('customer__username', 'shipping_address', 'email')
    readonly_fields = ('created_at', 'updated_at')

@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    list_display = ('order', 'product', 'quantity', 'price', 'total_price')
    search_fields = ('order__customer__username', 'product__name')

@admin.register(Promo)
class PromoAdmin(admin.ModelAdmin):
    list_display = ('code', 'discount_amount', 'valid_from', 'valid_until', 'is_active')
    list_filter = ('is_active', 'valid_from', 'valid_until')
    search_fields = ('code', 'description')

@admin.register(PromoUsage)
class PromoUsageAdmin(admin.ModelAdmin):
    list_display = ('promo', 'customer', 'used_at')
    list_filter = ('used_at',)
    search_fields = ('promo__code', 'customer__username')
