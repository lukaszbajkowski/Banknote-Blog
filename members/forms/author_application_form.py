from ckeditor.widgets import CKEditorWidget
from django import forms
from django.core.validators import MinLengthValidator
from django.core.validators import MaxLengthValidator
from django.core.validators import RegexValidator
from django.utils.translation import gettext as _
from phonenumber_field.formfields import PhoneNumberField

from blog.models import *


# Formularz zgłoszeniowy na autora
class ArticleAuthorForm(forms.ModelForm):
    phone_number = PhoneNumberField(
        region='PL',
        # required=False,
        # widget=forms.TextInput(attrs={'class': 'form-control'}),
        help_text="Numer telefonu w formacie +48"
    )
    accept_terms = forms.BooleanField(
        label='Akceptuję regulamin',
        required=True,
        initial=False,
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        error_messages={'required': 'Musisz zaakceptować regulamin.'}
    )

    phone_number.label = 'Numer telefonu'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields['first_name'].validators.extend([
            MinLengthValidator(2),
            RegexValidator(
                regex=r'^\D*$',
                message=_('Imię nie może zawierać cyfr.'),
                code='invalid_first_name'
            )
        ])
        self.fields['first_name'].error_messages['min_length'] = _(
            'Imię musi zawierać przynajmniej 2 znaki (obecnie ma %(show_value)s).')
        self.fields['first_name'].error_messages['required'] = _(
            'Imię jest wymagane.')

        self.fields['last_name'].validators.extend([
            MinLengthValidator(2),
            RegexValidator(
                regex=r"^\D*$",
                message=_('Nazwisko nie może zawiera cyfr.'),
                code='invalid_last_name'
            )
        ])
        self.fields['last_name'].error_messages['min_length'] = _(
            'Nazwisko musi zawierać przynajmniej 2 znaki (obecnie ma %(show_value)s).')
        self.fields['last_name'].error_messages['required'] = _(
            'Nazwisko jest wymagane.')

        self.fields['experience'].validators.append(MaxLengthValidator(500))
        self.fields['experience'].validators.append(MinLengthValidator(10))
        self.fields['experience'].error_messages['min_length'] = _(
            'Doświadczenie musi zawierać przynajmniej 10 znaków (obecnie ma %(show_value)s).')
        self.fields['experience'].error_messages['max_length'] = _(
            'Doświadczenie nie może przekraczać 500 znaków. (obecnie ma %(show_value)s)')
        self.fields['experience'].error_messages['required'] = _(
            'Doświadczenie jest wymagane.')

        self.fields['sample_article'].validators.append(MaxLengthValidator(5000))
        self.fields['sample_article'].validators.append(MinLengthValidator(100))
        self.fields['sample_article'].error_messages['min_length'] = _(
            'Próbny artykuł musi zawierać przynajmniej 100 znaków (obecnie ma %(show_value)s).')
        self.fields['sample_article'].error_messages['max_length'] = _(
            'Próbny artykuł nie może przekraczać 5000 znaków. (obecnie ma %(show_value)s)')
        self.fields['sample_article'].error_messages['required'] = _(
            'Próbny artykuł jest wymagany.')

    class Meta:
        model = ArticleAuthor
        fields = ['first_name', 'last_name', 'phone_number', 'experience', 'sample_article', 'accept_terms']

        widgets = {
            'first_name': forms.TextInput(attrs={'class': 'form-control'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control'}),
            'experience': forms.Textarea(attrs={'rows': 5, 'class': 'form-control', 'style': 'resize:none'}),
            'sample_article': CKEditorWidget(),
        }
        error_messages = {
            'required': 'To pole jest wymagane.',
            'invalid': 'Niepoprawny format danych.',
        }
