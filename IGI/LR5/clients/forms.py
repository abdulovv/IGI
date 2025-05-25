from django import forms
from .models import Client

class ClientForm(forms.ModelForm):
    class Meta:
        model = Client
        fields = ['name', 'phone', 'email', 'address']
        labels = {
            'name': 'ФИО клиента',
            'phone': 'Телефон',
            'email': 'Email',
            'address': 'Адрес',
        }
        widgets = {
            'address': forms.Textarea(attrs={'rows': 3}),
        }