from captcha.fields import ReCaptchaField
from captcha.widgets import ReCaptchaV2Checkbox
from django import forms
from django.contrib.auth import authenticate
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User as User
from django.contrib.auth.validators import UnicodeUsernameValidator
from django.core.exceptions import ValidationError
from django.core.validators import MaxLengthValidator
from django.core.validators import MinLengthValidator
from django.utils.translation import gettext as _


# Funkcja valid czy adres e-mail jest zajęty
def validate_email(value):
    if User.objects.filter(email=value).exists():
        raise ValidationError(f" Adres {value} jest zajęty.", params={'value': value})


# Funkcja valid nazwę użytkownika
def validate_username(value):
    if User.objects.filter(username=value).exists():
        raise forms.ValidationError(_('Nazwa użytkownika jest już zajęta.'))


# Formularz rejestracji użytkownika
class CustomUserForm(UserCreationForm):
    email = forms.EmailField(
        label=_('Adres e-mail'),
        widget=forms.EmailInput(attrs={'class': 'form-control'}),
    )
    username = forms.CharField(
        label=_('Nazwa użytkownika'),
        widget=forms.TextInput(attrs={'class': 'form-control'}),
        required=True
    )
    password1 = forms.CharField(
        label=_('Hasło'),
        widget=forms.PasswordInput(attrs={'class': 'form-control'})
    )
    password2 = forms.CharField(
        label=_('Potwierdzenie hasła'),
        widget=forms.PasswordInput(attrs={'class': 'form-control'})
    )
    is_active = forms.BooleanField(
        label=_('Regulamin serwisu i polityka prywatności'),
        required=False,
        initial=False,
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'})
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['username'].validators.extend([
            MinLengthValidator(1),
            MaxLengthValidator(64),
            UnicodeUsernameValidator(
                message=_('Wprowadź prawidłową nazwę użytkownika. Nazwa użytkownika może składać się tylko liter, '
                          'cyfr i znaków @/./+/-/_.')
            )
        ])
        self.fields['username'].error_messages['min_length'] = _(
            'Nazwa użytkownika musi zawierać przynajmniej 1 znaki (obecnie ma %(show_value)s).')
        self.fields['username'].error_messages['max_length'] = _(
            'Nazwa użytkownika może zawierać maksymalnie 64 znaki (obecnie ma %(show_value)s).')
        self.fields['username'].error_messages['required'] = _(
            'Nazwa użytkownika jest wymagana.')
        self.fields['username'].error_messages['unique'] = _(
            'Użytkownik o tej nazwie użytkownika już istnieje.')

        self.fields['email'].validators.extend([validate_email])
        self.fields['email'].error_messages['required'] = _(
            'Adres e-mail jest wymagany.')
        self.fields['email'].error_messages['invalid'] = _(
            'Wprowadź prawidłowy adres e-mail.')

        self.fields['password1'].error_messages['required'] = _(
            'Hasło jest wymagane.')

        self.fields['password2'].error_messages['required'] = _(
            'Potwierdzenie hasła jest wymagane.')

    def clean_is_active(self):
        is_active = self.cleaned_data.get('is_active')
        if not is_active:
            raise forms.ValidationError(_('Akceptacja regulaminu serwisu i polityki prywatności jest wymagana.'))
        return is_active

    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2', 'is_active']


# Formularz logowania użytkownika
class LoginForm(forms.Form):
    username = forms.CharField(
        label=_('Nazwa użytkownika'),
        widget=forms.TextInput(attrs={'class': 'form-control'}),
        required=True,
    )
    password = forms.CharField(
        label='Hasło',
        widget=forms.PasswordInput(attrs={'class': 'form-control'}),
    )
    captcha = ReCaptchaField(
        widget=ReCaptchaV2Checkbox(),
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['username'].validators.extend([
            MinLengthValidator(1),
            MaxLengthValidator(64),
            UnicodeUsernameValidator(
                message=_('Wprowadź prawidłową nazwę użytkownika. Nazwa użytkownika może składać się tylko liter, '
                          'cyfr i znaków @/./+/-/_.')
            )
        ])
        self.fields['username'].error_messages['min_length'] = _(
            'Nazwa użytkownika musi zawierać przynajmniej 1 znaki (obecnie ma %(show_value)s).')
        self.fields['username'].error_messages['max_length'] = _(
            'Nazwa użytkownika może zawierać maksymalnie 64 znaki (obecnie ma %(show_value)s).')
        self.fields['username'].error_messages['required'] = _(
            'Nazwa użytkownika jest wymagana.')

        self.fields['password'].error_messages['required'] = _(
            'Hasło jest wymagane.')
        self.fields['password'].error_messages['invalid'] = _(
            'Niepoprawne hasło.')

        self.fields['captcha'].error_messages['required'] = _(
            'reCaptacha jest wymagana.')
        self.fields['captcha'].error_messages['invalid'] = _(
            'Niepoprawna reCaptacha.')

    def clean(self, *args, **kwargs):
        username = self.cleaned_data.get('username')
        password = self.cleaned_data.get('password')
        if username and password:
            user = authenticate(username=username, password=password)
            if not user:
                raise forms.ValidationError(_('Nieprawidłowa nazwa użytkownika lub hasło.'))
        return super().clean(*args, **kwargs)
