from django import forms

from blog.models import *


# Formularz do zarządzania powiadomieniami o pominiętych artykułach dla użytkowników
class UserMissNewsForm(forms.ModelForm):
    miss_news = forms.BooleanField(
        label='Pominięte artykuły',
        help_text='Otrzymuj ważne powiadomienia o aktywnościach, które Cię ominęły.',
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        required=False,
    )

    class Meta:
        model = User
        fields = ['miss_news']
