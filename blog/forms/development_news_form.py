from django import forms

from blog.forms.base_form import DeleteForm, AddEmailForm
from blog.models import *


# Formularz do tworzenia i edycji wiadomości o rozwoju
class DevelopmentNewsCreationForm(AddEmailForm):
    class Meta(AddEmailForm.Meta):
        model = DevelopmentNews


# Formularz do usuwania wiadomości o rozwoju
class DevelopmentNewsDeleteForm(DeleteForm):
    class Meta(DeleteForm.Meta):
        model = DevelopmentNews


# Formularz do zarządzania wiadomościami o rozwoju przez użytkownika
class UserDevelopmentNewsForm(forms.ModelForm):
    development_news = forms.BooleanField(
        label='Informacje o rozwoju i zmianach na Banknoty',
        help_text='Wiadomość od nas zawierająca informacje o rozwoju i zmianach na Banknoty.',
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        required=False,
    )

    class Meta:
        model = User
        fields = ['development_news']
