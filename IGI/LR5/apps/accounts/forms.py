from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from datetime import date
from dateutil.relativedelta import relativedelta
from .models import UserProfile
from collections import OrderedDict

class CustomUserCreationForm(UserCreationForm):
    first_name = forms.CharField(max_length=30, required=True, label='Имя')
    last_name = forms.CharField(max_length=30, required=True, label='Фамилия')
    email = forms.EmailField(required=True, label='Email')
    phone = forms.CharField(max_length=15, required=True, label='Телефон')
    birth_date = forms.DateField(required=True, label='Дата рождения', 
                               widget=forms.DateInput(attrs={'type': 'date'}))
    address = forms.CharField(widget=forms.Textarea(attrs={'rows': 3}), required=True, label='Адрес')

    class Meta:
        model = User
        fields = ('username', 'first_name', 'last_name', 'email', 'phone', 'birth_date', 
                 'address', 'password1', 'password2')

    def clean_birth_date(self):
        birth_date = self.cleaned_data.get('birth_date')
        if birth_date:
            age = relativedelta(date.today(), birth_date).years
            if age < 18:
                raise forms.ValidationError('Вы должны быть старше 18 лет для регистрации.')
        return birth_date

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        user.first_name = self.cleaned_data['first_name']
        user.last_name = self.cleaned_data['last_name']
        
        if commit:
            user.save()
            # Создаем или обновляем профиль пользователя
            profile = user.profile
            profile.phone = self.cleaned_data['phone']
            profile.birth_date = self.cleaned_data['birth_date']
            profile.address = self.cleaned_data['address']
            profile.save()
            
        return user 

class ProfileUpdateForm(forms.ModelForm):
    first_name = forms.CharField(max_length=30, required=True, label='Имя')
    last_name = forms.CharField(max_length=30, required=True, label='Фамилия')
    email = forms.EmailField(required=True, label='Email')
    phone = forms.CharField(max_length=15, required=True, label='Телефон')
    birth_date = forms.DateField(required=True, label='Дата рождения', 
                               widget=forms.DateInput(attrs={'type': 'date'}))
    address = forms.CharField(widget=forms.Textarea(attrs={'rows': 3}), required=True, label='Адрес')

    class Meta:
        model = UserProfile # Используем UserProfile, так как большинство полей из него
        fields = ['phone', 'birth_date', 'address']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Добавляем поля User в форму
        if self.instance and self.instance.user:
            self.fields['first_name'].initial = self.instance.user.first_name
            self.fields['last_name'].initial = self.instance.user.last_name
            self.fields['email'].initial = self.instance.user.email
        
        # Переупорядочиваем поля, чтобы first_name, last_name, email были в начале
        field_order = ['first_name', 'last_name', 'email', 'phone', 'birth_date', 'address']
        self.fields = OrderedDict((key, self.fields[key]) for key in field_order if key in self.fields)


    def clean_birth_date(self):
        birth_date = self.cleaned_data.get('birth_date')
        if birth_date:
            today = date.today()
            age = relativedelta(date.today(), birth_date).years
            if age < 18:
                raise forms.ValidationError('Вы должны быть старше 18 лет.')
        return birth_date

    def save(self, commit=True):
        profile = super().save(commit=False)
        user = profile.user
        
        user.first_name = self.cleaned_data['first_name']
        user.last_name = self.cleaned_data['last_name']
        user.email = self.cleaned_data['email']
        
        if commit:
            user.save()
            profile.save()
        return profile 