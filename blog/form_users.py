import ckeditor.widgets
from django import forms
from .models import User as User_extended
from django.contrib.auth.models import User
from ckeditor.widgets import CKEditorWidget
from django.contrib.admin.widgets import FilteredSelectMultiple
from phonenumber_field.formfields import PhoneNumberField
from django.utils.translation import gettext_lazy as _
from django.core.validators import MinLengthValidator, MaxLengthValidator, RegexValidator
from django.contrib.auth import get_user_model
from django.contrib.auth.validators import UnicodeUsernameValidator


def validate_email(value):
    if User.objects.filter(email=value).exists():
        raise ValidationError(f" Adres {value} jest zajęty.", params={'value': value})


class UserProfileForm(forms.ModelForm):
    GENDER_CHOICES = (
        ('M', 'Mężczyzna'),
        ('K', 'Kobieta'),
        ('I', 'Inna'),
    )
    bio = forms.CharField(
        label='Biogram',
        widget=forms.Textarea(attrs={'rows': 5, 'class': 'form-control', 'style': 'resize:none'}),
        help_text="Krótki opis o Tobie - przynajmniej 10 znaków lecz nie więcej niż 512.",
        max_length=512,
        validators=[MinLengthValidator(10), MaxLengthValidator(512)],)
    profile_pic = forms.ImageField(
        required=False,
        widget=forms.FileInput(attrs={'class': 'form-control align-middle'}),
        label='Zdjęcie profilowe')
    gender = forms.ChoiceField(
        label='Płeć',
        choices=GENDER_CHOICES,
        required=True,
        widget=forms.Select(attrs={'class': 'form-select'}))
    newsletter = forms.BooleanField(
        label='Biuletyn',
        help_text='Raz w tygodniu wyślemy Ci przyjemną wiadomość. Bez zbędnego spamu.',
        required=False,
        initial=False,
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'}),
    )
    miss_news = forms.BooleanField(
        label='Pominięte artykuły',
        help_text='Otrzymuj ważne powiadomienia o aktywnościach, które Cię ominęły.',
        required=False,
        initial=False,
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'}),
    )
    meetups_news = forms.BooleanField(
        label='Spotkania i wydarzenia',
        help_text='Otrzymuj e-mail, gdy w pobliżu Twojej lokalizacji pojawi się spotkanie bądź aukcja.',
        required=False,
        initial=True,
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'}),
    )
    opportunities_news = forms.BooleanField(
        label='Okazje z rynku aukcyjnego',
        help_text='Otrzymuj e-mail z niepowtarzalnymi okazjami na zakupy z rynku aukcyjnego.',
        required=False,
        initial=False,
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'}),
    )
    company_news = forms.BooleanField(
        label='Wiadomości od Banknoty',
        help_text='Otrzymuj nowości od nas, komunikaty i informacje na temat nowości dotyczących produktów.',
        required=False,
        initial=True,
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'}),
    )
    replay_news = forms.BooleanField(
        label='Shot wydzarzeń od Banknoty',
        help_text='Wysyłana od czasu do czasu wiadomość zawierająca najpopularniejsze shoty.',
        required=False,
        initial=False,
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'}),
    )
    development_news = forms.BooleanField(
        label='Informacje o rozwoju i zmianach na Banknoty',
        help_text='Wiadomoś od nas zawierająca informacje o rozwoju i zmianach na Banknoty.',
        required=False,
        initial=False,
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'}),
    )
    can_be_author = forms.BooleanField(
        label='Czy może być autorem?',
        help_text='Czy wniosek na autora został rozpatrzony pozytywnie.',
        required=False,
        initial=False,
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'}),
    )

    class Meta:
        model = User_extended
        fields = (
            'bio',  'profile_pic', 'gender', 'newsletter', 'miss_news', 'meetups_news', 'opportunities_news',
            'company_news', 'replay_news', 'development_news', 'can_be_author')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['bio'].validators.extend([
            MinLengthValidator(10),
            MaxLengthValidator(512),
        ])
        self.fields['bio'].error_messages['min_length'] = _(
            'Biogram musi zawierać przynajminej 10 znaków (obecnie ma %(show_value)s).')
        self.fields['bio'].error_messages['max_length'] = _(
            'Biogram nie może przekracza 512 znaków (obecnie ma %(show_value)s).')


class UserEditForm(forms.ModelForm):
    email = forms.EmailField(
        label=_('Adres e-mail'),
        widget=forms.EmailInput(attrs={'class': 'form-control'}),
    )
    first_name = forms.CharField(
        label='Imię',
        max_length=100,
        widget=forms.TextInput(attrs={'class': 'form-control'}),
        help_text="Imię nie może skałada się z cyfr i musi zawira przynajmniej dwa znaki.",
        required=True,
    )
    last_name = forms.CharField(
        label='Nazwisko',
        max_length=100,
        widget=forms.TextInput(attrs={'class': 'form-control'}),
        help_text="Nazwisko nie może skałada się z cyfr i musi zawira przynajmniej dwa znaki.",
        required=True,
    )

    class Meta:
        model = User
        fields = ('email', 'first_name', 'last_name')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields['email'].error_messages['required'] = _(
            'Adres e-mail jest wymagana.')

        self.fields['first_name'].validators.extend([
            MinLengthValidator(2),
            RegexValidator(
                regex=r'^\D*$',
                message=_('Imię nie może zawierać cyfr.'),
                code='invalid_first_name'
            )
        ])
        self.fields['first_name'].error_messages['min_length'] = _(
            'Imię musi zawierać przynajminej 2 znaki (obecnie ma %(show_value)s).')
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
            'Nazwisko musi zawierać przynajminej 2 znaki (obecnie ma %(show_value)s).')
        self.fields['last_name'].error_messages['required'] = _(
            'Nazwisko jest wymagane.')

    def clean_email(self):
        new_email = self.cleaned_data.get('email')
        existing_user = User.objects.filter(email=new_email).exclude(id=self.instance.id).first()

        if existing_user:
            raise forms.ValidationError("This email address is already in use.")

        return new_email


class UserCreationForm(forms.ModelForm):
    username = forms.CharField(
        label=_('Nazwa użytkownika'),
        widget=forms.TextInput(attrs={'class': 'form-control'}),
        validators=[
            UnicodeUsernameValidator(),
            MinLengthValidator(2),
            MaxLengthValidator(64)
        ],
        help_text="Wprowadź prawidłową nazwę użytkownika. Nazwa użytkownika może zawierać tylko litery, cyfry i znaki @/./+/-/_ oraz musi zawiera przynajmniej dwa znaki",
        required=True
    )
    email = forms.EmailField(
        label=_('Adres e-mail'),
        widget=forms.EmailInput(attrs={'class': 'form-control'}),
    )
    first_name = forms.CharField(
        label='Imię',
        max_length=100,
        widget=forms.TextInput(attrs={'class': 'form-control'}),
        help_text="Imię nie może skałada się z cyfr i musi zawira przynajmniej dwa znaki.",
        required=True,
    )
    last_name = forms.CharField(
        label='Nazwisko',
        max_length=100,
        widget=forms.TextInput(attrs={'class': 'form-control'}),
        help_text="Nazwisko nie może skałada się z cyfr i musi zawira przynajmniej dwa znaki.",
        required=True,
    )
    password = forms.CharField(
        label='Hasło',
        widget=forms.PasswordInput(attrs={'class': 'form-control'}),
    )

    class Meta:
        model = User
        fields = ('username', 'email', 'first_name', 'last_name', 'password')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['username'].error_messages['required'] = _(
            'Nazwa użytkownika jest wymagana.')
        self.fields['email'].error_messages['required'] = _(
            'Adres e-mail jest wymagana.')
        self.fields['password'].error_messages['required'] = _(
            'Hasło jest wymagane.')

        self.fields['first_name'].validators.extend([
            MinLengthValidator(2),
            RegexValidator(
                regex=r'^\D*$',
                message=_('Imię nie może zawierać cyfr.'),
                code='invalid_first_name'
            )
        ])
        self.fields['first_name'].error_messages['min_length'] = _(
            'Imię musi zawierać przynajminej 2 znaki (obecnie ma %(show_value)s).')
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
            'Nazwisko musi zawierać przynajminej 2 znaki (obecnie ma %(show_value)s).')
        self.fields['last_name'].error_messages['required'] = _(
            'Nazwisko jest wymagane.')

    def clean_email(self):
        new_email = self.cleaned_data.get('email')
        existing_user = User.objects.filter(email=new_email).exclude(id=self.instance.id).first()

        if existing_user:
            raise forms.ValidationError("This email address is already in use.")

        return new_email


class CustomPasswordChangingForm(forms.Form):
    error_messages = {
        'password_mismatch': "Podane hasła nie są identyczne.",
    }

    widgets = {
        'new_password1': forms.PasswordInput(attrs={'class': 'form-control', 'required': True}),
        'new_password2': forms.PasswordInput(attrs={'class': 'form-control', 'required': True}),
    }

    new_password1 = forms.CharField(label="Nowe hasło", widget=forms.PasswordInput(attrs={'class': 'form-control', 'required': True}))
    new_password2 = forms.CharField(label="Powtórz nowe hasło", widget=forms.PasswordInput(attrs={'class': 'form-control', 'required': True}))

    def clean(self):
        cleaned_data = super().clean()
        password1 = cleaned_data.get("new_password1")
        password2 = cleaned_data.get("new_password2")
        if password1 and password2 and password1 != password2:
            raise forms.ValidationError(
                self.error_messages['password_mismatch'],
                code='password_mismatch',
            )

    def save(self, user, commit=True):
        new_password = self.cleaned_data["new_password1"]
        user.set_password(new_password)
        if commit:
            user.save()
        return user