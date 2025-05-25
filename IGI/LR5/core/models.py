from django.db import models
from django.utils import timezone

class CompanyInfo(models.Model):
    about_us = models.TextField(verbose_name="О компании")
    address = models.TextField(verbose_name="Адрес")
    phone = models.CharField(max_length=20, verbose_name="Телефон")
    email = models.EmailField(verbose_name="Email")
    #  Дополнительные поля (по желанию)
    # logo = models.ImageField(upload_to='company_logos/', blank=True, null=True, verbose_name="Логотип")
    # video_url = models.URLField(blank=True, null=True, verbose_name="URL видео")

    def __str__(self):
        return "Информация о компании"

    class Meta:
        verbose_name = "Информация о компании"
        verbose_name_plural = "Информация о компании"

class NewsArticle(models.Model):
    title = models.CharField(max_length=200, verbose_name="Заголовок")
    content = models.TextField(verbose_name="Содержание")
    publication_date = models.DateTimeField(default=timezone.now, verbose_name="Дата публикации")

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = "Новость"
        verbose_name_plural = "Новости"