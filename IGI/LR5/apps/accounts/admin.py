from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import User
from .models import UserProfile, Employee

# Отменяем регистрацию стандартной модели User
admin.site.unregister(User)

class UserProfileInline(admin.StackedInline):
    model = UserProfile
    can_delete = False
    verbose_name_plural = 'Профиль'
    fk_name = 'user'

class EmployeeInline(admin.StackedInline):
    model = Employee
    can_delete = False
    verbose_name_plural = 'Информация о сотруднике'
    fk_name = 'user'
    fields = ('vacancy', 'salary', 'is_active')
    autocomplete_fields = ['vacancy']
    
    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == "vacancy":
            kwargs["queryset"] = db_field.related_model.objects.filter(is_active=True)
        return super().formfield_for_foreignkey(db_field, request, **kwargs)

@admin.register(User)
class CustomUserAdmin(UserAdmin):
    inlines = (UserProfileInline,)
    list_display = ('username', 'email', 'first_name', 'last_name', 'is_staff', 'get_phone', 'get_vacancy')
    list_select_related = ('profile', 'employee')
    list_editable = ('is_staff',)
    list_filter = ('is_staff', 'is_superuser', 'is_active', 'employee__vacancy__title')
    
    # Убираем поля групп из всех fieldsets
    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        ('Персональная информация', {'fields': ('first_name', 'last_name', 'email')}),
        ('Права доступа', {'fields': ('is_active', 'is_staff', 'is_superuser')}),
        ('Важные даты', {'fields': ('last_login', 'date_joined')}),
    )
    
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'password1', 'password2', 'is_staff'),
        }),
    )
    
    def get_phone(self, instance):
        return instance.profile.phone if hasattr(instance, 'profile') else '-'
    get_phone.short_description = 'Телефон'

    def get_vacancy(self, instance):
        if hasattr(instance, 'employee') and instance.employee.vacancy:
            return instance.employee.vacancy.title
        return '-'
    get_vacancy.short_description = 'Вакансия'

    def get_inline_instances(self, request, obj=None):
        if not obj:
            return []
        inlines = super().get_inline_instances(request, obj)
        if obj.is_staff:
            employee_inline = EmployeeInline(self.model, self.admin_site)
            inlines.append(employee_inline)
        return inlines

    def save_model(self, request, obj, form, change):
        is_new_staff = not change or (change and form.initial.get('is_staff', False) != obj.is_staff and obj.is_staff)
        super().save_model(request, obj, form, change)
        
        if is_new_staff and obj.is_staff and not hasattr(obj, 'employee'):
            Employee.objects.create(
                user=obj,
                salary=0
            )
