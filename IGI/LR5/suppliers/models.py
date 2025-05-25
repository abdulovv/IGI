from django.db import models

class Supplier(models.Model):
    name = models.CharField(max_length=200, verbose_name="Название поставщика")
    address = models.TextField(verbose_name="Адрес")
    phone = models.CharField(max_length=20, verbose_name="Телефон")

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Поставщик"
        verbose_name_plural = "Поставщики"