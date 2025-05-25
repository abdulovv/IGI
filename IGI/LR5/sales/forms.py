from django import forms
from .models import Sale
from shop.models import Product
from clients.models import Client

class SaleForm(forms.ModelForm):
    class Meta:
        model = Sale
        fields = ['client', 'product', 'quantity', 'sale_date', 'total_price']
        labels = {
            'client': 'Клиент',
            'product': 'Товар',
            'quantity': 'Количество',
            'sale_date': 'Дата продажи',
            'total_price': 'Сумма продажи',
        }
        widgets = {
            'sale_date': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
        }