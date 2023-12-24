from ckeditor.widgets import CKEditorWidget
from django import forms
from django.core.validators import MaxLengthValidator
from django.core.validators import MinLengthValidator
from django.utils.translation import gettext as _

from blog.models import *


# Valid na maksymalną liczbę słów
class MaxWordsValidator:
    def __init__(self, max_words):
        self.max_words = max_words

    def __call__(self, value):
        words = value.split()
        if len(words) > self.max_words:
            raise forms.ValidationError(
                _('Wstęp może zawierać maksymalnie %(max_words)d słów (obecnie zawiera %(num_words)d).'),
                code='max_words',
                params={'max_words': self.max_words, 'num_words': len(words)},
            )


# Valid na maksymalną liczbę kategorii
class MaxSelectedCategoriesValidator:
    def __init__(self, max_selected):
        self.max_selected = max_selected

    def __call__(self, value):
        if len(value) > self.max_selected:
            raise forms.ValidationError(
                _('Możesz wybrać maksymalnie %(max_selected)d kategorie (obecnie wybrałeś %(num_selected)d).'),
                code='max_selected',
                params={'max_selected': self.max_selected, 'num_selected': len(value)},
            )


# Formularz edycji postów
class PostEditForm(forms.ModelForm):
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

    class Meta:
        model = Blog
        fields = ['title', 'introduction', 'background', 'category', 'content']

        labels = {
            'content': 'Treść',
            'author': 'Autor',
        }
        widgets = {
            'content': CKEditorWidget(),
            'author': forms.Select(attrs={'class': 'form-select'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields['title'].validators.extend([
            MinLengthValidator(2),
            MaxLengthValidator(100),
        ])
        self.fields['title'].error_messages['min_length'] = _(
            'Tytuł musi zawierać przynajmniej 2 znaki (obecnie ma %(show_value)s).'
        )
        self.fields['title'].error_messages['max_length'] = _(
            'Tytuł nie może przekraczać 100 znaków (obecnie ma %(show_value)s).'
        )
        self.fields['title'].error_messages['required'] = _(
            'Tytuł jest wymagany.'
        )

        self.fields['introduction'].validators.extend([
            MinLengthValidator(10),
            MaxLengthValidator(512),
            MaxWordsValidator(50),
        ])
        self.fields['introduction'].error_messages['min_length'] = _(
            'Wstęp musi zawierać przynajmniej 10 znaków (obecnie ma %(show_value)s).'
        )
        self.fields['introduction'].error_messages['max_length'] = _(
            'Wstęp nie może przekraczać 512 znaków (obecnie ma %(show_value)s).'
        )
        self.fields['introduction'].error_messages['required'] = _(
            'Wstęp jest wymagany.'
        )

        self.fields['content'].validators.extend([
            MinLengthValidator(512),
            MaxLengthValidator(16384),
        ])
        self.fields['content'].error_messages['min_length'] = _(
            'Treść musi zawierać przynajmniej 512 znaków (obecnie ma %(show_value)s).'
        )
        self.fields['content'].error_messages['max_length'] = _(
            'Treść nie może przekraczać 16384 znaków (obecnie ma %(show_value)s).'
        )
        self.fields['content'].error_messages['required'] = _(
            'Treść jest wymagana.'
        )

        self.fields['background'].error_messages['required'] = _(
            'Tło wpisu jest wymagane.'
        )

        self.fields['category'].validators.extend([
            MaxSelectedCategoriesValidator(3),
        ])
        self.fields['category'].error_messages['required'] = _(
            'Kategorie są wymagane.'
        )


# Formularz dodawania postów
class PostAddForm(forms.ModelForm):
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

    class Meta:
        model = Blog
        fields = ['title', 'introduction', 'background', 'category', 'content']

        labels = {
            'content': 'Treść',
        }
        widgets = {
            'content': CKEditorWidget(),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields['title'].validators.extend([
            MinLengthValidator(2),
            MaxLengthValidator(100),
        ])
        self.fields['title'].error_messages['min_length'] = _(
            'Tytuł musi zawierać przynajmniej 2 znaki (obecnie ma %(show_value)s).'
        )
        self.fields['title'].error_messages['max_length'] = _(
            'Tytuł nie może przekraczać 100 znaków (obecnie ma %(show_value)s).'
        )
        self.fields['title'].error_messages['required'] = _(
            'Tytuł jest wymagany.'
        )

        self.fields['introduction'].validators.extend([
            MinLengthValidator(10),
            MaxLengthValidator(512),
            MaxWordsValidator(50),
        ])
        self.fields['introduction'].error_messages['min_length'] = _(
            'Wstęp musi zawierać przynajmniej 10 znaków (obecnie ma %(show_value)s).'
        )
        self.fields['introduction'].error_messages['max_length'] = _(
            'Wstęp nie może przekraczać 512 znaków (obecnie ma %(show_value)s).'
        )
        self.fields['introduction'].error_messages['required'] = _(
            'Wstęp jest wymagany.'
        )

        self.fields['content'].validators.extend([
            MinLengthValidator(512),
            MaxLengthValidator(16384),
        ])
        self.fields['content'].error_messages['min_length'] = _(
            'Treść musi zawierać przynajmniej 512 znaków (obecnie ma %(show_value)s).'
        )
        self.fields['content'].error_messages['max_length'] = _(
            'Treść nie może przekraczać 16384 znaków (obecnie ma %(show_value)s).'
        )
        self.fields['content'].error_messages['required'] = _(
            'Treść jest wymagana.'
        )

        self.fields['background'].error_messages['required'] = _(
            'Tło wpisu jest wymagane.'
        )

        self.fields['category'].validators.extend([
            MaxSelectedCategoriesValidator(3),
        ])
        self.fields['category'].error_messages['required'] = _(
            'Kategorie są wymagane.'
        )
