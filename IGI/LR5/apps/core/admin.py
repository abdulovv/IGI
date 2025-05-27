from django.contrib import admin
from .models import Category, Supplier, Product, Sale, Cart, CartItem, Order, OrderItem, ProductReview, Promo, PromoUsage

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'description')
    search_fields = ('name',)

@admin.register(Supplier)
class SupplierAdmin(admin.ModelAdmin):
    list_display = ('name', 'address', 'phone', 'email')
    search_fields = ('name', 'email')
    list_filter = ('name',)

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'article', 'category', 'price', 'quantity')
    list_filter = ('category', 'suppliers')
    search_fields = ('name', 'article')
    filter_horizontal = ('suppliers',)
    readonly_fields = ('created_at', 'updated_at')

@admin.register(Sale)
class SaleAdmin(admin.ModelAdmin):
    list_display = ('product', 'quantity', 'price_per_unit', 'total_price', 'customer', 'date')
    list_filter = ('date', 'customer')
    search_fields = ('product__name', 'customer__username')
    readonly_fields = ('total_price', 'date')

@admin.register(Cart)
class CartAdmin(admin.ModelAdmin):
    list_display = ['customer', 'total_items', 'total_price', 'created_at', 'updated_at']
    list_filter = ['created_at', 'updated_at']
    search_fields = ['customer__username']
    readonly_fields = ['total_price', 'total_items']

@admin.register(CartItem)
class CartItemAdmin(admin.ModelAdmin):
    list_display = ['cart', 'product', 'quantity', 'total_price', 'added_at']
    list_filter = ['added_at']
    search_fields = ['cart__customer__username', 'product__name']
    autocomplete_fields = ['product']
    readonly_fields = ['total_price']

class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    readonly_fields = ['total_price']
    autocomplete_fields = ['product']

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = [
        'id', 'customer', 'status', 'items_count',
        'subtotal', 'shipping_cost', 'total',
        'created_at', 'client_timezone'
    ]
    list_filter = ['status', 'created_at', 'client_timezone']
    search_fields = [
        'customer__username', 'customer__email',
        'shipping_address', 'phone', 'email'
    ]
    readonly_fields = ['subtotal', 'total', 'items_count', 'created_at', 'updated_at']
    inlines = [OrderItemInline]
    fieldsets = (
        ('Основная информация', {
            'fields': (
                'customer', 'status', 'created_at',
                'updated_at', 'client_timezone'
            )
        }),
        ('Контактная информация', {
            'fields': (
                'shipping_address', 'phone', 'email',
                'comment'
            )
        }),
        ('Финансовая информация', {
            'fields': (
                'subtotal', 'shipping_cost', 'total',
                'items_count'
            )
        }),
    )

@admin.register(ProductReview)
class ProductReviewAdmin(admin.ModelAdmin):
    list_display = [
        'product', 'customer', 'rating',
        'created_at', 'is_moderated'
    ]
    list_filter = ['rating', 'is_moderated', 'created_at']
    search_fields = [
        'product__name', 'customer__username',
        'text'
    ]
    readonly_fields = ['created_at', 'updated_at']
    actions = ['approve_reviews', 'reject_reviews']

    def approve_reviews(self, request, queryset):
        queryset.update(is_moderated=True)
    approve_reviews.short_description = "Одобрить выбранные отзывы"

    def reject_reviews(self, request, queryset):
        queryset.update(is_moderated=False)
    reject_reviews.short_description = "Отклонить выбранные отзывы"

class PromoUsageInline(admin.TabularInline):
    model = PromoUsage
    extra = 0
    readonly_fields = ['customer', 'used_at']
    can_delete = False

@admin.register(Promo)
class PromoAdmin(admin.ModelAdmin):
    list_display = [
        'code', 'discount_amount',
        'valid_from', 'valid_until',
        'min_order_amount', 'is_active'
    ]
    list_filter = [
        'is_active',
        'valid_from', 'valid_until'
    ]
    search_fields = ['code', 'description']
    inlines = [PromoUsageInline]
    fieldsets = (
        ('Основная информация', {
            'fields': (
                'code', 'description', 'is_active'
            )
        }),
        ('Настройки скидки', {
            'fields': (
                'discount_amount',
                'min_order_amount'
            )
        }),
        ('Срок действия', {
            'fields': (
                'valid_from', 'valid_until',
            )
        }),
    )

@admin.register(PromoUsage)
class PromoUsageAdmin(admin.ModelAdmin):
    list_display = ['promo', 'customer', 'used_at']
    list_filter = ['used_at', 'promo', 'customer']
    search_fields = ['promo__code', 'customer__username']
    readonly_fields = ['used_at']
    autocomplete_fields = ['promo', 'customer']
