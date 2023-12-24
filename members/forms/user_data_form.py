from django import forms
from django.contrib.auth.forms import PasswordChangeForm
from django.core.validators import EmailValidator
from django.core.validators import MaxLengthValidator
from django.core.validators import MinLengthValidator
from django.core.validators import RegexValidator
from django.utils.translation import gettext as _
from phonenumber_field.formfields import PhoneNumberField
from blog.models import *


# Funkcja valid unikalność adresu e-mail
def unique_email_validator(value):
    if User.objects.filter(email=value).exists():
        raise ValidationError(
            'Podany adres e-mail jest już zajęty.',
            code='email_taken',
        )


# Formularz edycji profilu użytkownika
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
        region='PL',
        # required=False,
        # widget=forms.TextInput(attrs={'class': 'form-control'}),
        help_text="Numer telefonu w formacie +48")
    gender = forms.ChoiceField(
        label='Płeć',
        choices=GENDER_CHOICES,
        required=True,
        widget=forms.Select(attrs={'class': 'form-select'}))

    phone_number.label = 'Numer telefonu'

    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'bio', 'profile_pic', 'phone_number', 'gender']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['first_name'].initial = self.instance.user.first_name
        self.fields['last_name'].initial = self.instance.user.last_name

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

        self.fields['bio'].validators.extend([
            MinLengthValidator(10),
            MaxLengthValidator(512),
        ])
        self.fields['bio'].error_messages['min_length'] = _(
            'Biogram musi zawierać przynajmniej 10 znaków (obecnie ma %(show_value)s).')
        self.fields['bio'].error_messages['max_length'] = _(
            'Biogram nie może przekracza 512 znaków (obecnie ma %(show_value)s).')


# Formularz zmiany hasła użytkownika
class PasswordChangingForm(PasswordChangeForm):
    error_messages = {
        'password_incorrect': "Obecne hasło jest niepoprawne. Proszę podać je jeszcze raz.",
        'password_mismatch': "Podane hasła nie są identyczne.",
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
        if new_password1 and new_password2 and new_password1 != new_password2:
            raise forms.ValidationError(
                self.error_messages['password_mismatch'],
                code='password_mismatch',
            )
        return new_password2

    def clean_old_password(self):
        old_password = self.cleaned_data.get('old_password')
        if not self.user.check_password(old_password):
            raise forms.ValidationError(
                self.error_messages['password_incorrect'],
                code='password_incorrect',
            )
        return old_password

    class Meta:
        model = User
        fields = ['old_password', 'new_password1', 'new_password2']


# Formularz zmiany adresu e-mail użytkownika
class EmailChangeForm(forms.Form):
    error_messages = {
        'email_mismatch': "Podane adresy e-mail nie pasują do siebie.",
        'not_changed': "Podany adres e-mail jest taki sam jak obecny.",
    }

    new_email1 = forms.EmailField(
        label="Nowy adres e-mail",
        widget=forms.EmailInput(attrs={'class': 'form-control'}),
        error_messages={
            'required': 'Adres e-mail jest wymagany.',
            'unique': 'Podany adres e-mail jest już zajęty.',
            'email_mismatch': "Podane adresy e-mail nie pasują do siebie.",
            'not_changed': "Podany adres e-mail jest taki sam jak obecny.",
        }
    )
    new_email2 = forms.EmailField(
        label="Potwierdzenie nowego adresu e-mail",
        widget=forms.EmailInput(attrs={'class': 'form-control'}),
        error_messages={
            'required': 'Potwierdzenie adresu e-mail jest wymagane.',
            'unique': 'Podany adres e-mail jest już zajęty.',
            'email_mismatch': "Podane adresy e-mail nie pasują do siebie.",
            'not_changed': "Podany adres e-mail jest taki sam jak obecny.",
        }
    )

    def __init__(self, user, *args, **kwargs):
        self.user = user
        super(EmailChangeForm, self).__init__(*args, **kwargs)

        self.fields['new_email1'].validators.append(EmailValidator(message='Nieprawidłowy format adresu e-mail.'))
        self.fields['new_email1'].validators.append(unique_email_validator)
        self.fields['new_email2'].validators.append(EmailValidator(message='Nieprawidłowy format adresu e-mail.'))
        self.fields['new_email2'].validators.append(unique_email_validator)

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
        return new_email1, new_email2

    def clean(self):
        cleaned_data = super().clean()
        new_email = cleaned_data.get('new_email1')

        if User.objects.filter(email=new_email).exclude(pk=self.user.pk).exists():
            raise ValidationError(
                self.error_messages['email_taken'],
                code='email_taken',
            )

        return cleaned_data

    def save(self, commit=True):
        email = self.cleaned_data["new_email1"]
        self.user.email = email
        if commit:
            self.user.save()
        return self.user


# Formularz do usuwania konta
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
