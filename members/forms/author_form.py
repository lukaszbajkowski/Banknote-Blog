from django import forms
from django.core.validators import MaxLengthValidator, MinLengthValidator, RegexValidator
from django.utils.translation import gettext as _
from django.core.exceptions import ValidationError
from blog.models import Author

class BaseAuthorForm(forms.ModelForm):
    bio = forms.CharField(
        widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 5, 'cols': 50, 'maxlength': 512, 'style': 'resize: none', 'required': True}),
    )
    profile_pic = forms.ImageField(
        widget=forms.ClearableFileInput(attrs={'class': 'form-control', 'accept': 'image/*', 'required': True})
    )
    author_quote = forms.CharField(
        widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 2, 'cols': 30, 'maxlength': 128, 'style': 'resize: none', 'required': True}),
    )
    author_function = forms.CharField(
        widget=forms.TextInput(attrs={'class': 'form-control', 'maxlength': 150, 'required': True}),
    )
    author_url = forms.URLField(
        widget=forms.URLInput(attrs={'class': 'form-control', 'required': False}), required=False
    )
    pinterest_url = forms.URLField(
        widget=forms.URLInput(attrs={'class': 'form-control', 'required': False}), required=False
    )
    facebook_url = forms.URLField(
        widget=forms.URLInput(attrs={'class': 'form-control', 'required': False}), required=False
    )
    twitter_url = forms.URLField(
        widget=forms.URLInput(attrs={'class': 'form-control', 'required': False}), required=False
    )
    instagram_url = forms.URLField(
        widget=forms.URLInput(attrs={'class': 'form-control', 'required': False}), required=False
    )

    class Meta:
        abstract = True
        model = Author
        fields = ['bio', 'profile_pic', 'author_quote', 'author_function', 'author_url', 'pinterest_url',
                  'facebook_url', 'twitter_url', 'instagram_url']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields['bio'].validators.extend([
            MinLengthValidator(10),
            MaxLengthValidator(512),
        ])
        self.fields['bio'].error_messages['min_length'] = _('Biogram musi zawierać przynajmniej 10 znaków (obecnie ma %(show_value)s).')
        self.fields['bio'].error_messages['max_length'] = _('Biogram nie może przekraczać 512 znaków (obecnie ma %(show_value)s).')
        self.fields['bio'].error_messages['required'] = _('Biogram jest wymagany.')

        self.fields['author_quote'].validators.extend([
            MinLengthValidator(2),
            MaxLengthValidator(128)
        ])
        self.fields['author_quote'].error_messages['min_length'] = _('Cytat musi zawierać przynajmniej 2 znaki (obecnie ma %(show_value)s).')
        self.fields['author_quote'].error_messages['max_length'] = _('Cytat nie może przekraczać 128 znaków (obecnie ma %(show_value)s).')
        self.fields['author_quote'].error_messages['required'] = _('Cytat jest wymagany.')

        self.fields['author_function'].validators.extend([
            MinLengthValidator(2),
            MaxLengthValidator(150)
        ])
        self.fields['author_function'].error_messages['min_length'] = _('Funkcja musi zawierać przynajmniej 2 znaki (obecnie ma %(show_value)s).')
        self.fields['author_function'].error_messages['max_length'] = _('Funkcja nie może przekraczać 150 znaków (obecnie ma %(show_value)s).')
        self.fields['author_function'].error_messages['required'] = _('Funkcja jest wymagana.')

        self.fields['author_url'].validators.append(RegexValidator(
            regex=r'^https?://(www\.)?.+$',
            message='Wprowadź prawidłowy adres URL.',
            code='invalid_author_url'
        ))

        self.fields['pinterest_url'].validators.append(RegexValidator(
            regex=r'^https?://(www\.)?pinterest\.co.uk/.+$',
            message='Wprowadź prawidłowy adres URL Pinterest.',
            code='invalid_pinterest_url'
        ))

        self.fields['facebook_url'].validators.append(RegexValidator(
            regex=r'^https?://(www\.)?facebook\.com/.+$',
            message='Wprowadź prawidłowy adres URL Facebook.',
            code='invalid_facebook_url'
        ))

        self.fields['twitter_url'].validators.append(RegexValidator(
            regex=r'^https?://(www\.)?twitter\.com/.+$',
            message='Wprowadź prawidłowy adres URL Twitter.',
            code='invalid_twitter_url'
        ))

        self.fields['instagram_url'].validators.append(RegexValidator(
            regex=r'^https?://(www\.)?instagram\.com/.+$',
            message='Wprowadź prawidłowy adres URL Instagram.',
            code='invalid_instagram_url'
        ))

    def clean_author_function(self):
        author_function = self.cleaned_data['author_function']
        word_count = len(author_function.split())

        if word_count > 5:
            raise ValidationError('Stanowisko autora powinno składać się z co najwyżej 5 słów.')

        return author_function


# Formularz edycji autora
class AuthorForm(BaseAuthorForm):
    pass


# Formularz tworzenia autora
class CreateAuthorForm(BaseAuthorForm, forms.Form):
    pass
