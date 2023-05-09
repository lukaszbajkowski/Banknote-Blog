from django.contrib.auth.forms import UserCreationForm, UserChangeForm, PasswordChangeForm
from django import forms
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from blog.models import User as User_Custom
from phonenumber_field.formfields import PhoneNumberField
from django.core.validators import EmailValidator
from django.utils.translation import gettext as _


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
    is_active = forms.BooleanField(
        label='Regulamin serwisu i polityka prywatności',
        required=True,
        initial=False,
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'})
    )

    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2', 'is_active']


class EditUserForm(forms.ModelForm):
    first_name = forms.CharField(
        label='Imię',
        max_length=100,
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    last_name = forms.CharField(
        label='Nazwisko',
        max_length=100,
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )

    class Meta:
        model = User
        fields = ['first_name', 'last_name']


class UserForm(forms.ModelForm):
    GENDER_CHOICES = (
        ('M', 'Mężczyzna'),
        ('K', 'Kobieta'),
        ('I', 'Inna'),
    )
    first_name = forms.CharField(
        label='Imię',
        max_length=100,
        widget=forms.TextInput(attrs={'class': 'form-control'}))
    last_name = forms.CharField(
        label='Nazwisko',
        max_length=100,
        widget=forms.TextInput(attrs={'class': 'form-control'}))
    bio = forms.CharField(
        label='Biogram',
        max_length=512,
        required=False,
        widget=forms.Textarea(attrs={'rows': 5, 'class': 'form-control', 'style': 'resize:none'}),
        help_text="Krótki opis o Tobie - nie więcej niż 512 znaków")
    profile_pic = forms.ImageField(
        required=False,
        widget=forms.FileInput(attrs={'class': 'form-control align-middle'}),
        label='Zdjęcie profilowe')
    phone_number = PhoneNumberField(
        label='Numer telefonu',
        region='PL',
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control'}),
        help_text="Numer telefonu w formacie +48")
    gender = forms.ChoiceField(
        label='Płeć',
        choices=GENDER_CHOICES,
        required=True,
        widget=forms.Select(attrs={'class': 'form-select'}))

    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'bio', 'profile_pic', 'phone_number', 'gender']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['first_name'].initial = self.instance.user.first_name
        self.fields['last_name'].initial = self.instance.user.last_name


class PasswordChangingForm(PasswordChangeForm):
    error_messages = {
        "password_incorrect":
            "Podane obecne hasło jest niepoprawne. Proszę podać je jeszcze raz.",
        'email_mismatch':
            _("The two email addresses fields didn't match."),
    }
    old_password = forms.CharField(
        label='Obecne hasło',
        widget=forms.PasswordInput(attrs={'class': 'form-control'}),
    )
    new_password1 = forms.CharField(
        label='Nowe hasło',
        widget=forms.PasswordInput(attrs={'class': 'form-control'}),
    )
    new_password2 = forms.CharField(
        label='Potwierdzenie nowego hasła',
        widget=forms.PasswordInput(attrs={'class': 'form-control'}),
    )

    def clean_new_password2(self):
        new_password1 = self.cleaned_data.get('new_password1')
        new_password2 = self.cleaned_data.get('new_password2')
        if new_password1 and new_password2:
            if new_password1 != new_password2:
                raise forms.ValidationError(
                    self.error_messages['email_mismatch'],
                    code='email_mismatch',
                )
        return new_password2

    class Meta:
        model = User
        fields = ['old_password', 'new_password1', 'new_password2']


class EmailChangeForm(forms.Form):
    error_messages = {
        'email_mismatch': _("The two email addresses fields didn't match."),
        'not_changed': "Adres e-mail jest taki sam jak obecny.",
    }
    new_email1 = forms.EmailField(
        label="Nowy adres e-mail",
        widget=forms.EmailInput(attrs={'class': 'form-control'}),
    )
    new_email2 = forms.EmailField(
        label="Potwierdzenie nowego adresu e-mail",
        widget=forms.EmailInput(attrs={'class': 'form-control'}),
    )

    def __init__(self, user, *args, **kwargs):
        self.user = user
        super(EmailChangeForm, self).__init__(*args, **kwargs)

    def clean_new_email1(self):
        old_email = self.user.email
        new_email1 = self.cleaned_data.get('new_email1')
        if new_email1 and old_email:
            if new_email1 == old_email:
                raise forms.ValidationError(
                    self.error_messages['not_changed'],
                    code='not_changed',
                )
        return new_email1

    def clean_new_email2(self):
        new_email1 = self.cleaned_data.get('new_email1')
        new_email2 = self.cleaned_data.get('new_email2')
        if new_email1 and new_email2:
            if new_email1 != new_email2:
                raise forms.ValidationError(
                    self.error_messages['email_mismatch'],
                    code='email_mismatch',
                )
        return new_email2

    def save(self, commit=True):
        email = self.cleaned_data["new_email1"]
        self.user.email = email
        if commit:
            self.user.save()
        return self.user


class DeleteAccountForm(forms.Form):
    confirm_deletion = forms.BooleanField(
        label='Zdaję sobie sprawę, że to działanie jest permanentne i nie może być cofnięte.',
        required=True,
        initial=False,
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'})
    )

    def clean(self):
        cleaned_data = super().clean()
        confirm_deletion = cleaned_data.get('confirm_deletion')
        if not confirm_deletion:
            raise forms.ValidationError('You must confirm that you want to delete your account.')