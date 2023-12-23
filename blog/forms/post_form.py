from ckeditor.widgets import CKEditorWidget
from django import forms

from blog.forms.base_form import DeleteForm
from blog.models import *


# Formularz do tworzenia i edycji wpisu na blogu
class PostCreateForm(forms.ModelForm):
    title = forms.CharField(
        label='Tytuł',
        required=True,
        widget=forms.TextInput(attrs={'class': 'form-control'}),
    )
    introduction = forms.CharField(
        label='Wstęp',
        required=True,
        widget=forms.Textarea(attrs={'rows': 5, 'class': 'form-control', 'style': 'resize:none'}),
        help_text="Wstęp do postu na maksymalnie 50 słów",
    )
    background = forms.ImageField(
        label='Tło wpisu',
        required=True,
        widget=forms.FileInput(attrs={'class': 'form-control align-middle'}),
    )
    category = forms.ModelMultipleChoiceField(
        label='Kategorie',
        queryset=Category.objects.all(),
        required=True,
        widget=forms.SelectMultiple(attrs={'class': 'form-control'}),
        help_text="Wyświetlą się maksymalnie trzy kategorie",
    )
    favorite = forms.BooleanField(
        label='Czy wyróżnić post?',
        required=False,
        initial=False,
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'})
    )
    publiction_status = forms.BooleanField(
        label='Czy opublikować post?',
        initial=False,
        required=False,
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'})
    )

    class Meta:
        model = Blog
        fields = "__all__"

        labels = {
            'content': 'Treść',
            'author': 'Autor',
        }
        widgets = {
            'content': CKEditorWidget(),
            'author': forms.Select(attrs={'class': 'form-select'}),
        }


# Formularz do usuwania wpisu na blogu
class PostDeleteForm(DeleteForm):
    class Meta(DeleteForm.Meta):
        model = Blog
