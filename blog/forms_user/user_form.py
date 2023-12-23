from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.validators import UnicodeUsernameValidator
from django.core.validators import MaxLengthValidator
from django.core.validators import MinLengthValidator
from django.core.validators import RegexValidator
from django.utils.translation import gettext_lazy as _

from blog.forms.base_form import DeleteForm
from blog.models import User as User_extended


# Funkcja do tworzenia pola checkbox.
def create_checkbox_field(label, help_text, initial=False):
    return forms.BooleanField(
        label=label,
        help_text=help_text,
        required=False,
        initial=initial,
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'}),
    )


# Formularz dla informacji o profilu użytkownika z modelu User, który rozszerza wbudowany model User.
class UserProfileForm(forms.ModelForm):
    GENDER_CHOICES = (
        ('M', 'Mężczyzna'),
        ('K', 'Kobieta'),
        ('I', 'Inna'),
    )
    bio = forms.CharField(
        label='Biogram',
        widget=forms.Textarea(
            attrs={
                'rows': 5,
                'class': 'form-control',
                'style': 'resize:none'
            }
        ),
        help_text="Krótki opis o Tobie - przynajmniej 10 znaków lecz nie więcej niż 512.",
        max_length=512,
        validators=[
            MinLengthValidator(10),
            MaxLengthValidator(512)
        ],
    )
    profile_pic = forms.ImageField(
        required=False,
        widget=forms.FileInput(
            attrs={
                'class': 'form-control align-middle'}
        ),
        label='Zdjęcie profilowe'
    )
    gender = forms.ChoiceField(
        label='Płeć',
        choices=GENDER_CHOICES,
        required=True,
        widget=forms.Select(
            attrs={
                'class': 'form-select'
            }
        )
    )
    newsletter = create_checkbox_field(
        'Biuletyn',
        'Raz w tygodniu wyślemy Ci przyjemną wiadomość. Bez zbędnego spamu.'
    )
    miss_news = create_checkbox_field(
        'Pominięte artykuły',
        'Otrzymuj ważne powiadomienia o aktywnościach, które Cię ominęły.'
    )
    meetups_news = create_checkbox_field(
        'Spotkania i wydarzenia',
        'Otrzymuj e-mail, gdy w pobliżu pojawi się spotkanie bądź aukcja.',
        initial=True
    )
    opportunities_news = create_checkbox_field(
        'Okazje z rynku aukcyjnego',
        'Otrzymuj e-mail z niepowtarzalnymi okazjami na zakupy z rynku aukcyjnego.',
    )
    company_news = create_checkbox_field(
        'Wiadomości od Banknoty',
        'Otrzymuj nowości od nas, komunikaty i informacje na temat nowości dotyczących produktów.',
    )
    replay_news = create_checkbox_field(
        'Shot wydarzeń od Banknoty',
        'Wysyłana od czasu do czasu wiadomość zawierająca najpopularniejsze shoty.',
    )
    development_news = create_checkbox_field(
        'Informacje o rozwoju i zmianach na Banknoty',
        'Wiadomość od nas zawierająca informacje o rozwoju i zmianach na Banknoty.',
    )
    can_be_author = create_checkbox_field(
        'Czy może być autorem?',
        'Czy wniosek na autora został rozpatrzony pozytywnie.',
    )

    class Meta:
        model = User_extended
        fields = (
            'bio',
            'profile_pic',
            'gender',
            'newsletter',
            'miss_news',
            'meetups_news',
            'opportunities_news',
            'company_news',
            'replay_news',
            'development_news',
            'can_be_author'
        )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['bio'].validators.extend([
            MinLengthValidator(10),
            MaxLengthValidator(512),
        ])
        self.fields['bio'].error_messages['min_length'] = _(
            'Biogram musi zawierać przynajmniej 10 znaków (obecnie ma %(show_value)s).'
        )
        self.fields['bio'].error_messages['max_length'] = _(
            'Biogram nie może przekracza 512 znaków (obecnie ma %(show_value)s).'
        )


class BaseUserForm(forms.ModelForm):
    email = forms.EmailField(
        label=_('Adres e-mail'),
        widget=forms.EmailInput(attrs={'class': 'form-control'}),
    )
    first_name = forms.CharField(
        label='Imię',
        max_length=100,
        widget=forms.TextInput(attrs={'class': 'form-control'}),
        help_text="Imię nie może składać się z cyfr i musi zawierać przynajmniej dwa znaki.",
        required=True,
    )
    last_name = forms.CharField(
        label='Nazwisko',
        max_length=100,
        widget=forms.TextInput(attrs={'class': 'form-control'}),
        help_text="Nazwisko nie może składać się z cyfr i musi zawierać przynajmniej dwa znaki.",
        required=True,
    )

    class Meta:
        abstract = True
        model = User
        fields = ('email', 'first_name', 'last_name')

    def clean_email(self):
        new_email = self.cleaned_data.get('email')
        existing_user = User.objects.filter(email=new_email).exclude(id=self.instance.id).first()

        if existing_user:
            raise forms.ValidationError("This email address is already in use.")

        return new_email

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['email'].error_messages['required'] = _('Adres e-mail jest wymagany.')

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
        self.fields['first_name'].error_messages['required'] = _('Imię jest wymagane.')

        self.fields['last_name'].validators.extend([
            MinLengthValidator(2),
            RegexValidator(
                regex=r"^\D*$",
                message=_('Nazwisko nie może zawierać cyfr.'),
                code='invalid_last_name'
            )
        ])
        self.fields['last_name'].error_messages['min_length'] = _(
            'Nazwisko musi zawierać przynajmniej 2 znaki (obecnie ma %(show_value)s).')
        self.fields['last_name'].error_messages['required'] = _('Nazwisko jest wymagane.')


# Formularz do edycji informacji o użytkowniku z modelu wbudowanego User.
class UserEditForm(BaseUserForm):
    class Meta(BaseUserForm.Meta):
        fields = ('email', 'first_name', 'last_name')


# Formularz do utworzenia użytkownika przez administratora.
class UserCreationForm(BaseUserForm):
    username = forms.CharField(
        label=_('Nazwa użytkownika'),
        widget=forms.TextInput(attrs={'class': 'form-control'}),
        validators=[
            UnicodeUsernameValidator(),
            MinLengthValidator(2),
            MaxLengthValidator(64)
        ],
        help_text="Wprowadź prawidłową nazwę użytkownika. Nazwa użytkownika może zawierać tylko litery, cyfry i znaki "
                  "@/./+/-/_ oraz musi zawierać przynajmniej dwa znaki",
        required=True
    )
    password = forms.CharField(
        label='Hasło',
        widget=forms.PasswordInput(attrs={'class': 'form-control'}),
    )

    class Meta(BaseUserForm.Meta):
        fields = ('username', 'email', 'first_name', 'last_name', 'password')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['username'].error_messages['required'] = _('Nazwa użytkownika jest wymagana.')
        self.fields['email'].error_messages['required'] = _('Adres e-mail jest wymagany.')
        self.fields['password'].error_messages['required'] = _('Hasło jest wymagane.')


# Formularz do usuwania użytkowników
class UsersDeleteForm(DeleteForm):
    class Meta(DeleteForm.Meta):
        model = User
