from django.contrib.auth.forms import UserCreationForm
from django import forms
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError


def validate_email(value):
    if User.objects.filter(email=value).exists():
        raise ValidationError(f" Adres {value} jest zajęty.", params={'value': value})


class CustomUserForm(UserCreationForm):
    email = forms.EmailField(
        label='Adres e-mail',
        widget=forms.EmailInput(attrs={'class': 'form-control'}),
        validators=[validate_email]
    )
    username = forms.CharField(
        label='Nazwa użytkownika',
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    password1 = forms.CharField(
        label='Hasło',
        widget=forms.PasswordInput(attrs={'class': 'form-control'})
    )
    password2 = forms.CharField(
        label='Potwierdzenie hasła',
        widget=forms.PasswordInput(attrs={'class': 'form-control'})
    )

    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']

