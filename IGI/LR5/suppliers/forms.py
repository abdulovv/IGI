from django import forms
from .models import Supplier

class SupplierForm(forms.ModelForm):
    class Meta:
        model = Supplier
        fields = ['name', 'address', 'phone']
        labels = {
            'name': 'Название поставщика',
            'address': 'Адрес',
            'phone': 'Телефон',
        }
        widgets = {
            'address': forms.Textarea(attrs={'rows': 3}),
        }