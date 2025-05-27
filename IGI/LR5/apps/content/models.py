from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils import timezone
from datetime import timedelta

class News(models.Model):
    title = models.CharField('Заголовок', max_length=200)
    content = models.TextField('Содержание')
    image = models.ImageField('Изображение', upload_to='news/', blank=True, null=True)
    created_at = models.DateTimeField('Дата создания', auto_now_add=True)
    updated_at = models.DateTimeField('Дата обновления', auto_now=True)
    is_published = models.BooleanField('Опубликовано', default=True)

    class Meta:
        verbose_name = 'Новость'
        verbose_name_plural = 'Новости'
        ordering = ['-created_at']

    def __str__(self):
        return self.title

class CompanyInfo(models.Model):
    title = models.CharField('Название', max_length=100)
    content = models.TextField('Содержание')
    logo = models.ImageField('Логотип', upload_to='company/', blank=True, null=True)

    class Meta:
        verbose_name = 'Информация о компании'
        verbose_name_plural = 'Информация о компании'
        ordering = ['id']

    def __str__(self):
        return self.title

class FAQ(models.Model):
    question = models.CharField('Вопрос', max_length=255)
    answer = models.TextField('Ответ')
    created_at = models.DateTimeField('Дата добавления', auto_now_add=True)
    is_published = models.BooleanField('Опубликовано', default=True)

    class Meta:
        verbose_name = 'Вопрос-Ответ'
        verbose_name_plural = 'Вопросы-Ответы'
        ordering = ['created_at']

    def __str__(self):
        return self.question

class Review(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='reviews', verbose_name='Пользователь')
    text = models.TextField('Текст отзыва')
    rating = models.PositiveSmallIntegerField(
        'Оценка',
        validators=[MinValueValidator(1), MaxValueValidator(5)]
    )
    # image = models.ImageField('Изображение к отзыву', upload_to='reviews/', blank=True, null=True) # Поле image закомментировано/удалено
    created_at = models.DateTimeField('Дата создания', auto_now_add=True)
    is_published = models.BooleanField('Опубликовано', default=True)

    class Meta:
        verbose_name = 'Отзыв'
        verbose_name_plural = 'Отзывы'
        ordering = ['-created_at']

    def __str__(self):
        return f"Отзыв от {self.user.username}"

class Vacancy(models.Model):
    title = models.CharField('Название вакансии', max_length=100)
    description = models.TextField('Описание')
    is_active = models.BooleanField('Активна', default=True)
    created_at = models.DateTimeField('Дата создания', auto_now_add=True)

    class Meta:
        verbose_name = 'Вакансия'
        verbose_name_plural = 'Вакансии'
        ordering = ['-created_at']

    def __str__(self):
        return self.title

class Promotion(models.Model):
    title = models.CharField('Название акции', max_length=100, default="Новая акция")
    description = models.TextField('Описание', default="", blank=True)
    promo = models.OneToOneField(
        'core.Promo',
        on_delete=models.CASCADE,
        related_name='promotion',
        verbose_name='Промокод',
        null=True,
        blank=True
    )
    image = models.ImageField('Изображение', upload_to='promotions/', blank=True, null=True)
    is_active = models.BooleanField('Активна', default=True)
    created_at = models.DateTimeField('Дата создания', auto_now_add=True)

    class Meta:
        verbose_name = 'Акция'
        verbose_name_plural = 'Акции'
        ordering = ['-created_at']

    def __str__(self):
        if self.promo:
            return f"{self.title} ({self.promo.code})"
        return self.title

    @property
    def discount_display(self):
        if not self.promo:
            return "Нет скидки"
        # Since discount_type is removed, all discounts are fixed amounts
        return f"{self.promo.discount_amount} руб."

    @property
    def period_display(self):
        if not self.promo:
            return "Период не указан"
        
        start_str = self.promo.valid_from.strftime('%d.%m.%Y %H:%M') if self.promo.valid_from else 'N/A'
        end_str = self.promo.valid_until.strftime('%d.%m.%Y %H:%M') if self.promo.valid_until else 'N/A'
        
        if self.promo.valid_from and self.promo.valid_until:
            return f"Действует с {start_str} по {end_str}"
        elif self.promo.valid_from:
            return f"Действует с {start_str}"
        elif self.promo.valid_until:
            return f"Действует до {end_str}"
        return "Период не указан"

class Employee(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, verbose_name='Пользователь системы', related_name='content_profile')
    position = models.CharField('Должность', max_length=100)
    photo = models.ImageField('Фото', upload_to='employees/', blank=True, null=True)
    phone = models.CharField('Рабочий телефон', max_length=20, blank=True)
    description = models.TextField('Описание/Обязанности', blank=True)
    is_active = models.BooleanField('Активен (работает)', default=True)
    created_at = models.DateTimeField('Дата добавления записи', auto_now_add=True)
    updated_at = models.DateTimeField('Дата обновления записи', auto_now=True)

    class Meta:
        verbose_name = 'Сотрудник'
        verbose_name_plural = 'Сотрудники'
        ordering = ['user__last_name', 'user__first_name']

    def __str__(self):
        return f"{self.user.get_full_name() or self.user.username} - {self.position}"

    @property
    def full_name(self):
        return self.user.get_full_name() or self.user.username
    
    @property
    def email(self):
        return self.user.email
