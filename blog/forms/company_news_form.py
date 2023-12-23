from django import forms

from blog.forms.base_form import DeleteForm, AddEmailForm
from blog.models import *


# Formularz do tworzenia i edycji wiadomości firmowych
class CompanyNewsCreationForm(AddEmailForm):
    class Meta(AddEmailForm.Meta):
        model = CompanyNews


# Formularz do usuwania wiadomości firmowych
class CompanyNewsDeleteForm(DeleteForm):
    class Meta(DeleteForm.Meta):
        model = CompanyNews


# Formularz do zarządzania wiadomościami firmowymi dla użytkowników
class UserCompanyNewsForm(forms.ModelForm):
    company_news = forms.BooleanField(
        label='Wiadomości od Banknoty',
        help_text='Otrzymuj nowości od nas, komunikaty i informacje na temat nowości dotyczących produktów.',
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        required=False,
    )

    class Meta:
        model = User
        fields = ['company_news']
