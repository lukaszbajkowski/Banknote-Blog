from django.contrib.auth.forms import (
    UserCreationForm, UserChangeForm, PasswordChangeForm, PasswordResetForm
)
from django import forms
from django.core.exceptions import ValidationError
from blog.models import *
from blog.models import User as User_Custom
from django.contrib.auth.models import User as User
from phonenumber_field.formfields import PhoneNumberField
from django.core.validators import (
    EmailValidator, MinLengthValidator, MaxLengthValidator, RegexValidator
)
from django.utils.translation import gettext as _
from ckeditor.widgets import CKEditorWidget
from urllib.parse import urlparse
from django.contrib.auth import (
    get_user_model, authenticate, login, logout
)
from django.contrib.auth.validators import UnicodeUsernameValidator
from captcha.fields import ReCaptchaField
from captcha.widgets import ReCaptchaV2Checkbox
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import EmailMultiAlternatives
from django.template import loader


# Rozszerzenie formularza resetowania hasła
class CustomPasswordResetForm(PasswordResetForm):
    email = forms.EmailField(
        label=_("Eeeeeeeemail"),
        max_length=254,
        widget=forms.EmailInput(attrs={"autocomplete": "email"}),
    )

    def send_mail(self, subject_template_name, email_template_name, context, from_email, to_email, html_email_template_name=None):
        subject = loader.render_to_string(subject_template_name, context)
        subject = ''.join(subject.splitlines())
        body = loader.render_to_string(email_template_name, context)

        email_message = EmailMultiAlternatives(subject, body, from_email, [to_email])
        if html_email_template_name is not None:
            html_email = loader.render_to_string(html_email_template_name, context)
            email_message.attach_alternative(html_email, "text/html")

        email_message.send()


# Funkcja walidująca unikalność adresu e-mail
def unique_email_validator(value):
    if User.objects.filter(email=value).exists():
        raise ValidationError(
            'Podany adres e-mail jest już zajęty.',
            code='email_taken',
        )


# Funkcja walidująca czy adres  e-mail jest zajety
def validate_email(value):
    if User.objects.filter(email=value).exists():
        raise ValidationError(f" Adres {value} jest zajęty.", params={'value': value})


# Funkcja walidująca nazwę użytkownika
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
            'Nazwa użytkownika musi zawierać przynajminej 1 znaki (obecnie ma %(show_value)s).')
        self.fields['username'].error_messages['max_length'] = _(
            'Nazwa użytkownika może zawierać maksymalnie 64 znaki (obecnie ma %(show_value)s).')
        self.fields['username'].error_messages['required'] = _(
            'Nazwa użytkownika jest wymagana.')
        self.fields['username'].error_messages['unique'] = _(
            'Użytkownik o tej nazwie użytkownika już istnieje.')

        self.fields['email'].validators.extend([
            validate_email
        ])
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
                message=_('Wprowadź prawidłową nazwę użytkownika. Nazwa użytkownika może składaś się tylko liter, '
                          'cyfr i znaków @/./+/-/_.')
            )
        ])
        self.fields['username'].error_messages['min_length'] = _(
            'Nazwa użytkownika musi zawierać przynajminej 1 znaki (obecnie ma %(show_value)s).')
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


# Formularz edycji profilu użytkownika
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

        self.fields['bio'].validators.extend([
            MinLengthValidator(10),
            # MaxLengthValidator(512),
        ])
        self.fields['bio'].error_messages['min_length'] = _(
            'Biogram musi zawierać przynajminej 10 znaków (obecnie ma %(show_value)s).')
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


# Formularz ustawień subskrybcji newsletterów
class NotificationSettingsForm(forms.ModelForm):
    newsletter = forms.BooleanField(
        label='Biuletyn',
        required=False,
        initial=False,
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        help_text="Raz w tygodniu wyślemy Ci przyjemną wiadomość. Bez zbędnego spamu."
    )
    miss_news = forms.BooleanField(
        label='Pominięte artykuły',
        required=False,
        initial=False,
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        help_text="Otrzymuj ważne powiadomienia o aktywnościach, które Cię ominęły."
    )
    meetups_news = forms.BooleanField(
        label='Spotkania i wydarzenia',
        required=False,
        initial=False,
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        help_text="Otrzymuj e-mail, gdy w pobliżu Twojej lokalizacji pojawi się spotkanie bądź aukcja."
    )
    opportunities_news = forms.BooleanField(
        label='Okazje z rynku aukcyjnego',
        required=False,
        initial=False,
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        help_text="Otrzymuj e-mail z niepowtarzalnymi okazjami na zakupy z rynku aukcyjnego."
    )

    class Meta:
        model = User
        fields = ['newsletter', 'miss_news', 'meetups_news', 'opportunities_news']


# Formularz ustawień komunikacji od Banknoty
class CommunicationSettingForm(forms.ModelForm):
    company_news = forms.BooleanField(
        label='Wiadomości od Banknoty',
        required=False,
        initial=False,
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        help_text="Otrzymuj nowości od nas, komunikaty i informacje na temat nowości dotyczących produktów."
    )
    replay_news = forms.BooleanField(
        label='Shot wydzarzeń od Banknoty',
        required=False,
        initial=False,
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        help_text="Wysyłana od czasu do czasu wiadomość zawierająca najpopularniejsze shoty."
    )
    development_news = forms.BooleanField(
        label='Informacje o rozwoju i zmianach na Banknoty',
        required=False,
        initial=False,
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        help_text="Wiadomoś od nas zawierająca informacje o rozwoju i zmianach na Banknoty."
    )

    class Meta:
        model = User
        fields = ['company_news', 'replay_news', 'development_news']


# Formularz zgłoszeniowy na autora
class ArticleAuthorForm(forms.ModelForm):
    phone_number = PhoneNumberField(
        label='Numer telefonu',
        region='PL',
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control'}),
        help_text="Numer telefonu w formacie +48")
    accept_terms = forms.BooleanField(
        label='Akceptuję regulamin',
        required=True,
        initial=False,
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        error_messages={'required': 'Musisz zaakceptować regulamin.'}
    )

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

        self.fields['experience'].validators.append(MaxLengthValidator(500))
        self.fields['experience'].validators.append(MinLengthValidator(10))
        self.fields['experience'].error_messages['min_length'] = _(
            'Doświadczenie musi zawierać przynajminej 10 znaków (obecnie ma %(show_value)s).')
        self.fields['experience'].error_messages['max_length'] = _(
            'Doświadczenie nie może przekraczać 500 znaków. (obecnie ma %(show_value)s)')
        self.fields['experience'].error_messages['required'] = _(
            'Doświadczenie jest wymagane.')

        self.fields['sample_article'].validators.append(MaxLengthValidator(5000))
        self.fields['sample_article'].validators.append(MinLengthValidator(100))
        self.fields['sample_article'].error_messages['min_length'] = _(
            'Próbny artykuł musi zawierać przynajminej 100 znaków (obecnie ma %(show_value)s).')
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


# Klasy walidatorów
# Walidator na maksymalną liczbę słów
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


# Walidator na maksymalną liczbę kategorii
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


# Formularz dodawania postÓw
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


# Formularz edycji autora
class AuthorForm(forms.ModelForm):
    class Meta:
        model = Author
        fields = ['bio', 'profile_pic', 'author_quote', 'author_function', 'author_url', 'pinterest_url',
                  'facebook_url', 'twitter_url', 'instagram_url']
        widgets = {
            'bio': forms.Textarea(attrs={'class': 'form-control', 'rows': 5, 'cols': 50, 'maxlength': 512,
                                         'style': 'resize: none', 'required': True}),
            'profile_pic': forms.ClearableFileInput(attrs={'class': 'form-control', 'accept': 'image/*',
                                                           'required': True}),
            'author_quote': forms.Textarea(attrs={'class': 'form-control', 'rows': 2, 'cols': 30,
                                                  'maxlength': 128, 'style': 'resize: none', 'required': True}),
            'author_function': forms.TextInput(attrs={'class': 'form-control', 'maxlength': 150, 'required': True}),
            'author_url': forms.URLInput(attrs={'class': 'form-control', 'required': False}),
            'pinterest_url': forms.URLInput(attrs={'class': 'form-control', 'required': False}),
            'facebook_url': forms.URLInput(attrs={'class': 'form-control', 'required': False}),
            'twitter_url': forms.URLInput(attrs={'class': 'form-control', 'required': False}),
            'instagram_url': forms.URLInput(attrs={'class': 'form-control', 'required': False}),
        }

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
        self.fields['bio'].error_messages['required'] = _(
            'Biogram jest wymagany.')

        self.fields['author_quote'].validators.extend([
            MinLengthValidator(2),
            MaxLengthValidator(128)
        ])
        self.fields['author_quote'].error_messages['min_length'] = _(
            'Cytat musi zawierać przynajmniej 2 znaki (obecnie ma %(show_value)s).')
        self.fields['author_quote'].error_messages['max_length'] = _(
            'Cytat nie może przekraczać 128 znakÓw (obecnie ma %(show_value)s).')
        self.fields['author_quote'].error_messages['required'] = _(
            'Cytat jest wymagany.')

        self.fields['author_function'].validators.extend([
            MinLengthValidator(2),
            MaxLengthValidator(150)
        ])
        self.fields['author_function'].error_messages['min_length'] = _(
            'Funkcja musi zawierać przynajmniej 2 znaki (obecnie ma %(show_value)s).')
        self.fields['author_function'].error_messages['max_length'] = _(
            'Funkcja nie może przekraczać 150 znakÓw (obecnie ma %(show_value)s).')
        self.fields['author_function'].error_messages['required'] = _(
            'Funkcja jest wymagana.')

        self.fields['author_url'].validators.append(RegexValidator(
            regex=r'^https?://(www\.)?.+$',
            message='Wprowadť prawidłowy adres URL.',
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
            message='Wprowadť prawidłowy adres URL Instagram.',
            code='invalid_instagram_url'
        ))

    def clean_author_function(self):
        author_function = self.cleaned_data['author_function']
        word_count = len(author_function.split())

        if word_count > 5:
            raise ValidationError('Stanowisko autora powinna składać się z co najwyżej 5 słów.')

        return author_function


# Formularz tworzenia autora
class CreateAuthorForm(forms.Form):
    bio = forms.CharField(
        widget=forms.Textarea(
            attrs={'class': 'form-control', 'rows': 5, 'cols': 50, 'maxlength': 512, 'style': 'resize: none',
                   'required': True}),
    )
    profile_pic = forms.ImageField(
        widget=forms.ClearableFileInput(attrs={'class': 'form-control', 'accept': 'image/*', 'required': True})
    )
    author_quote = forms.CharField(
        widget=forms.Textarea(
            attrs={'class': 'form-control', 'rows': 2, 'cols': 30, 'maxlength': 128, 'style': 'resize: none',
                   'required': True}),
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
        self.fields['bio'].error_messages['required'] = _(
            'Biogram jest wymagany.')

        self.fields['author_quote'].validators.extend([
            MinLengthValidator(2),
            MaxLengthValidator(128)
        ])
        self.fields['author_quote'].error_messages['min_length'] = _(
            'Cytat musi zawierać przynajmniej 2 znaki (obecnie ma %(show_value)s).')
        self.fields['author_quote'].error_messages['max_length'] = _(
            'Cytat nie może przekraczać 128 znakÓw (obecnie ma %(show_value)s).')
        self.fields['author_quote'].error_messages['required'] = _(
            'Cytat jest wymagany.')

        self.fields['author_function'].validators.extend([
            MinLengthValidator(2),
            MaxLengthValidator(150)
        ])
        self.fields['author_function'].error_messages['min_length'] = _(
            'Funkcja musi zawierać przynajmniej 2 znaki (obecnie ma %(show_value)s).')
        self.fields['author_function'].error_messages['max_length'] = _(
            'Funkcja nie może przekraczać 150 znakÓw (obecnie ma %(show_value)s).')
        self.fields['author_function'].error_messages['required'] = _(
            'Funkcja jest wymagana.')

        self.fields['author_url'].validators.append(RegexValidator(
            regex=r'^https?://(www\.)?.+$',
            message='Wprowadť prawidłowy adres URL.',
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
            raise ValidationError('Stanowisko autora powinna składać się z co najwyżej 5 słów.')

        return author_function
