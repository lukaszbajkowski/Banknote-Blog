from allauth.socialaccount.models import *
from django import forms

from blog.forms.base_form import DeleteForm

COMMON_WIDGETS = {
    'class': 'form-control',
}


# Formularz do edycji aplikacji społecznościowych
class SocialAppForm(forms.ModelForm):
    class Meta:
        model = SocialApp
        fields = ['provider', 'provider_id', 'name', 'client_id', 'secret', 'key', 'settings', 'sites']

        widgets = {
            'provider': forms.Select(attrs=COMMON_WIDGETS),
            'provider_id': forms.TextInput(attrs=COMMON_WIDGETS),
            'name': forms.TextInput(attrs=COMMON_WIDGETS),
            'client_id': forms.TextInput(attrs=COMMON_WIDGETS),
            'secret': forms.TextInput(attrs=COMMON_WIDGETS),
            'key': forms.TextInput(attrs=COMMON_WIDGETS),
            'settings': forms.Textarea(attrs={**COMMON_WIDGETS, 'rows': 5, 'style': 'resize:none'}),
            'sites': forms.SelectMultiple(attrs=COMMON_WIDGETS),
        }

        help_texts = {
            'client_id': 'ID aplikacji lub klucz odbiorcy',
            'secret': 'Klucz prywatny API, klienta lub odbiorcy',
        }

        labels = {
            'provider': 'Dostawca usługi',
            'provider_id': 'ID dostawcy',
            'name': 'Nazwa dostawcy',
            'client_id': 'ID klienta',
            'secret': 'Klucz prywatny',
            'key': 'Klucz publiczny',
            'settings': 'Ustawienia',
            'sites': 'Strony',
        }


# Formularz do edycji tokenów społecznościowych
class SocialTokenForm(forms.ModelForm):
    class Meta:
        model = SocialToken
        fields = ['app', 'account', 'token', 'token_secret', 'expires_at']

        widgets = {
            'app': forms.Select(attrs=COMMON_WIDGETS),
            'account': forms.Select(attrs=COMMON_WIDGETS),
            'token': forms.TextInput(attrs=COMMON_WIDGETS),
            'token_secret': forms.TextInput(attrs=COMMON_WIDGETS),
            'expires_at': forms.DateTimeInput(attrs=COMMON_WIDGETS),
        }

        help_texts = {
            'token': '"oauth_token" (OAuth1) lub access token (OAuth2)',
            'token_secret': '"oauth_token_secret" (OAuth1) lub refresh token (OAuth2)',
        }

        labels = {
            'app': 'Aplikacja',
            'account': 'Konto',
            'token': 'Token',
            'token_secret': 'Token prywatny',
            'expires_at': 'Data wygaśnięcia',
        }


# Formularz do edycji kont społecznościowych
class SocialAccountForm(forms.ModelForm):
    class Meta:
        model = SocialAccount
        fields = ['user', 'provider', 'uid', 'extra_data']

        widgets = {
            'user': forms.Select(attrs=COMMON_WIDGETS),
            'provider': forms.TextInput(attrs=COMMON_WIDGETS),
            'uid': forms.TextInput(attrs=COMMON_WIDGETS),
            'extra_data': forms.Textarea(attrs={**COMMON_WIDGETS, 'rows': 5, 'style': 'resize:none'}),
        }

        labels = {
            'user': 'Użytkownik',
            'provider': 'Dostawca usługi',
            'uid': 'ID',
            'extra_data': 'Dodatkowe dane',
        }


# Formularz do edycji adresów e-mail dla użytkowników logujących się przez aplikacje
class EmailAddressForm(forms.ModelForm):
    class Meta:
        model = EmailAddress
        fields = ['user', 'email', 'verified', 'primary']

        widgets = {
            'user': forms.Select(attrs=COMMON_WIDGETS),
            'email': forms.TextInput(attrs=COMMON_WIDGETS),
            'verified': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'primary': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }

        labels = {
            'user': 'Użytkownik',
            'email': 'Adres e-mail',
            'verified': 'Potwierdzony',
            'primary': 'Pierwszy',
        }


# Formularz do usuwania aplikacji społecznościowych
class SocialAppDeleteForm(DeleteForm):
    class Meta(DeleteForm.Meta):
        model = SocialApp


# Formularz do usuwania tokenów społecznościowych
class SocialTokenDeleteForm(DeleteForm):
    class Meta(DeleteForm.Meta):
        model = SocialToken


# Formularz do usuwania kont społecznościowych
class SocialAccountDeleteForm(DeleteForm):
    class Meta(DeleteForm.Meta):
        model = SocialAccount


# Formularz do usuwania adresów e-mail dla użytkowników logujących się przez aplikacje
class EmailAddressDeleteForm(DeleteForm):
    class Meta(DeleteForm.Meta):
        model = EmailAddress
