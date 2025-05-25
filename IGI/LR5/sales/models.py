from django.db import models
from django.utils import timezone

class Sale(models.Model):
    client = models.ForeignKey(
        'clients.Client', on_delete=models.CASCADE, related_name='sales', verbose_name="Клиент"
    )
    product = models.ForeignKey(
        'shop.Product', on_delete=models.CASCADE, related_name='sales', verbose_name="Товар"
    )
    quantity = models.IntegerField(verbose_name="Количество")
    sale_date = models.DateTimeField(default=timezone.now, verbose_name="Дата продажи")
    total_price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Сумма продажи")

    def __str__(self):
        return f"Продажа {self.product.name} клиенту {self.client.name}"

    class Meta:
        verbose_name = "Продажа"
        verbose_name_plural = "Продажи"