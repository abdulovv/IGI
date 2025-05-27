from django import forms
from .models import ProductReview # Import ProductReview model

class ProductQuantityUpdateForm(forms.Form):
    quantity = forms.IntegerField(label="Новое количество", min_value=0)

class ProductReviewUpdateForm(forms.ModelForm):
    class Meta:
        model = ProductReview
        fields = ['rating', 'text']
        widgets = {
            'rating': forms.Select(choices=[(i, f'{'★'*i}{'☆'*(5-i)}') for i in range(5, 0, -1)]),
            'text': forms.Textarea(attrs={'rows': 4})
        }
        labels = {
            'rating': 'Ваша оценка',
            'text': 'Ваш отзыв'
        } 