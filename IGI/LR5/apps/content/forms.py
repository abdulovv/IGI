from django import forms
from .models import Review

class ReviewForm(forms.ModelForm):
    rating = forms.IntegerField(
        label='Оценка',
        min_value=1,
        max_value=5,
        widget=forms.NumberInput(attrs={'type': 'number', 'class': 'form-control', 'placeholder': 'От 1 до 5'})
    )
    text = forms.CharField(
        label='Ваш отзыв',
        widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 4, 'placeholder': 'Напишите здесь ваш отзыв...'})
    )

    class Meta:
        model = Review
        fields = ['text', 'rating'] 