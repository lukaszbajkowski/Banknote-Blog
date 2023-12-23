from django import forms

from blog.forms.base_form import DeleteForm
from blog.models import *


# Formularz do tworzenia i edycji kategorii
class CategoryCreateForm(forms.ModelForm):
    name = forms.CharField(
        label='Kategoria',
        required=True,
        widget=forms.TextInput(attrs={'class': 'form-control'}),
    )
    description = forms.CharField(
        label='Opis',
        max_length=256,
        required=True,
        widget=forms.Textarea(attrs={'rows': 5, 'class': 'form-control', 'style': 'resize:none'}),
        help_text="Opis kategorii, maksymalnie 256 znaków",
    )

    class Meta:
        model = Category
        fields = "__all__"


# Formularz do usuwania kategorii
class CategoryDeleteForm(DeleteForm):
    class Meta(DeleteForm.Meta):
        model = Category
