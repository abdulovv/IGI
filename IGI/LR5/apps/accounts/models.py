from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator
from datetime import date
from django.db.models.signals import post_save
from django.dispatch import receiver
from apps.content.models import Vacancy

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    phone = models.CharField('Телефон', max_length=15, blank=True)
    birth_date = models.DateField('Дата рождения', null=True, blank=True)
    address = models.TextField('Адрес', max_length=500, blank=True)

    class Meta:
        verbose_name = 'Профиль пользователя'
        verbose_name_plural = 'Профили пользователей'

    def __str__(self):
        return f'Профиль {self.user.username}'

    @property
    def age(self):
        if self.birth_date:
            today = date.today()
            return today.year - self.birth_date.year - ((today.month, today.day) < (self.birth_date.month, self.birth_date.day))
        return None

    def is_adult(self):
        return self.age >= 18 if self.age is not None else False

@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        UserProfile.objects.create(user=instance)

@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    if not hasattr(instance, 'profile'):
        UserProfile.objects.create(user=instance)
    instance.profile.save()

class Employee(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='employee', verbose_name='Пользователь')
    vacancy = models.ForeignKey(Vacancy, on_delete=models.SET_NULL, null=True, blank=True, related_name='employees', verbose_name='Вакансия')
    hire_date = models.DateField('Дата приема на работу', auto_now_add=True)
    salary = models.DecimalField('Зарплата', max_digits=10, decimal_places=2, validators=[MinValueValidator(0)])
    is_active = models.BooleanField('Активен', default=True)

    class Meta:
        verbose_name = 'Сотрудник'
        verbose_name_plural = 'Сотрудники'

    def __str__(self):
        vacancy_title = self.vacancy.title if self.vacancy else "Без вакансии"
        return f"{self.user.get_full_name()} - {vacancy_title}"
