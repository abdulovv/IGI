from django.contrib import admin
from .models import News, CompanyInfo, FAQ, Review, Vacancy, Promotion, Employee

@admin.register(News)
class NewsAdmin(admin.ModelAdmin):
    list_display = ('title', 'created_at', 'updated_at', 'is_published')
    list_filter = ('is_published', 'created_at')
    search_fields = ('title', 'content')
    readonly_fields = ('created_at', 'updated_at')

@admin.register(CompanyInfo)
class CompanyInfoAdmin(admin.ModelAdmin):
    list_display = ('title',)
    search_fields = ('title', 'content')

@admin.register(FAQ)
class FAQAdmin(admin.ModelAdmin):
    list_display = ('question', 'created_at', 'is_published')
    list_filter = ('is_published', 'created_at')
    search_fields = ('question', 'answer')
    readonly_fields = ('created_at',)

@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ('user', 'rating', 'created_at', 'is_published')
    list_filter = ('rating', 'is_published', 'created_at')
    search_fields = ('user__username', 'text')
    readonly_fields = ('created_at',)

@admin.register(Vacancy)
class VacancyAdmin(admin.ModelAdmin):
    list_display = ('title', 'is_active', 'created_at')
    list_filter = ('is_active', 'created_at')
    search_fields = ('title', 'description')
    readonly_fields = ('created_at',)
    search_fields = ['title']

@admin.register(Promotion)
class PromotionAdmin(admin.ModelAdmin):
    list_display = [
        'title', 'promo_code', 'promo_discount_display',
        'is_active', 'valid_from_display', 'valid_until_display'
    ]
    list_filter = ['is_active']
    search_fields = ['title', 'description', 'promo__code']
    readonly_fields = ['created_at']

    def promo_code(self, obj):
        return obj.promo.code if obj.promo else 'N/A'
    promo_code.short_description = 'Промокод'

    def promo_discount_display(self, obj):
        return obj.discount_display
    promo_discount_display.short_description = 'Скидка'

    def valid_from_display(self, obj):
        return obj.promo.valid_from if obj.promo else 'N/A'
    valid_from_display.short_description = 'Действует с'

    def valid_until_display(self, obj):
        return obj.promo.valid_until if obj.promo else 'N/A'
    valid_until_display.short_description = 'Действует до'

@admin.register(Employee)
class EmployeeAdmin(admin.ModelAdmin):
    list_display = ('full_name', 'position', 'phone', 'is_active')
    search_fields = ('first_name', 'last_name', 'phone', 'vacancy__title')
    list_filter = ('vacancy', 'is_active')
    autocomplete_fields = ['vacancy']

    fieldsets = (
        (None, {
            'fields': ('first_name', 'last_name', 'vacancy', 'phone', 'photo', 'description', 'is_active')
        }),
    )

    def get_full_name(self, obj):
        return obj.user.get_full_name() or obj.user.username
    get_full_name.short_description = 'ФИО'
    get_full_name.admin_order_field = 'user__last_name'

    def get_email(self, obj):
        return obj.user.email
    get_email.short_description = 'Email'
    get_email.admin_order_field = 'user__email'
