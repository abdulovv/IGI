from django import forms
from .models import SupplierPurchase, Supplier

class ProductQuantityUpdateForm(forms.Form):
    quantity = forms.IntegerField(label="Новое количество", min_value=0)

class SupplierPurchaseForm(forms.ModelForm):
    supplier = forms.ModelChoiceField(
        queryset=None,  # Будет установлено в __init__
        label='Поставщик',
        empty_label='Выберите поставщика'
    )

    class Meta:
        model = SupplierPurchase
        fields = ['supplier', 'quantity', 'price_per_unit']
        labels = {
            'quantity': 'Количество',
            'price_per_unit': 'Цена за единицу'
        }
        widgets = {
            'quantity': forms.NumberInput(attrs={'min': 1}),
            'price_per_unit': forms.NumberInput(attrs={'min': 0, 'step': '0.01'})
        }

    def __init__(self, product=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if product:
            self.fields['supplier'].queryset = product.suppliers.all() 