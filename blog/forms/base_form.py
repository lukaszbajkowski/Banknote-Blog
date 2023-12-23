from ckeditor.widgets import CKEditorWidget
from django import forms

from blog.models import *

COMMON_HELP_TEXT = "Krótka informacja o autorze, maksymalnie 512 znaków"


# Bazowa klasa formularza do dodawania biuletynów
class AddEmailForm(forms.ModelForm):
    title = forms.CharField(
        label='Tytuł',
        widget=forms.TextInput(attrs={'class': 'form-control'}),
    )

    class Meta:
        abstract = True
        fields = ['title', 'text', 'status_field']
        labels = {
            'status_field': 'Status',
        }
        widgets = {
            'status_field': forms.Select(attrs={'class': 'form-select'}),
            'text': CKEditorWidget(),
        }

    def clean_title(self):
        title = self.cleaned_data.get('title')
        return title

    def clean_content(self):
        content = self.cleaned_data.get('content')
        return content


# Bazowa klasa formularza do usuwania
class DeleteForm(forms.ModelForm):
    is_active = forms.BooleanField(
        label='Regulamin serwisu i polityka prywatności',
        required=True,
        initial=False,
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'})
    )

    class Meta:
        abstract = True
        fields = ['is_active']

    def clean_is_active(self):
        is_active = self.cleaned_data.get('is_active')
        return is_active


# Bazowa klasa formularza dla dodawania i edycji autora
class AuthorBaseForm(forms.ModelForm):
    bio = forms.CharField(
        label='O autorze',
        max_length=512,
        required=True,
        widget=forms.Textarea(attrs={'rows': 5, 'class': 'form-control', 'style': 'resize:none'}),
        help_text=COMMON_HELP_TEXT,
    )
    profile_pic = forms.ImageField(
        label='Zdjęcie profilowe dla autora',
        required=True,
        widget=forms.FileInput(attrs={'class': 'form-control align-middle'}),
    )
    author_quote = forms.CharField(
        label='Cytat autora',
        max_length=128,
        required=True,
        widget=forms.Textarea(attrs={'rows': 3, 'class': 'form-control', 'style': 'resize:none'}),
        help_text="Krótkie motto autora, maksymalnie 128 znaków",
    )
    author_function = forms.CharField(
        label='Funkcja autora',
        max_length=128,
        required=True,
        widget=forms.TextInput(attrs={'class': 'form-control', 'style': 'resize:none'}),
        help_text="Nazwa funkcji jaką pełni autor",
    )

    class Meta:
        model = Author
        fields = ['bio', 'profile_pic', 'author_quote', 'author_function']
        labels = {
            'bio': 'O autorze',
            'profile_pic': 'Zdjęcie profilowe dla autora',
            'author_quote': 'Cytat autora',
            'author_function': 'Funkcja autora',
        }
        widgets = {
            'bio': forms.Textarea(attrs={'rows': 5, 'class': 'form-control', 'style': 'resize:none'}),
            'profile_pic': forms.FileInput(attrs={'class': 'form-control align-middle'}),
            'author_quote': forms.Textarea(attrs={'rows': 3, 'class': 'form-control', 'style': 'resize:none'}),
            'author_function': forms.TextInput(attrs={'class': 'form-control', 'style': 'resize:none'}),
        }
