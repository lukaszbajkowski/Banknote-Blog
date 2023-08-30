import ckeditor.widgets
from django import forms
from .models import *
from ckeditor.widgets import CKEditorWidget
from django.contrib.admin.widgets import FilteredSelectMultiple
from phonenumber_field.formfields import PhoneNumberField
from captcha.fields import ReCaptchaField
from captcha.widgets import ReCaptchaV2Checkbox
from django.utils.translation import gettext_lazy as _
from django.core.validators import MinLengthValidator, MaxLengthValidator, RegexValidator
from django.contrib.auth import get_user_model
from django.contrib.auth.validators import UnicodeUsernameValidator
from allauth.socialaccount.models import *
from allauth.account.models import *


# Funkcja do walidacji adresu e-mail, sprawdzająca czy adres już istnieje
def validate_email(value):
    if User.objects.filter(email=value).exists():
        raise ValidationError(f" Adres {value} jest zajęty.", params={'value': value})


# Bazowa klasa formularza do dodawania biuletynów
class AddEmailForm(forms.ModelForm):
    title = forms.CharField(
        label='Tytuł',
        widget=forms.TextInput(attrs={'class': 'form-control'}),
    )

    class Meta:
        abstract = True
        fields = ['title', 'text', 'status_field']
        labels = {
            'status_field': 'Status',
        }
        widgets = {
            'status_field': forms.Select(attrs={'class': 'form-select'}),
            'text': CKEditorWidget(),
        }

    def clean_title(self):
        title = self.cleaned_data.get('title')
        return title

    def clean_content(self):
        content = self.cleaned_data.get('content')
        return content


# Bazowa klasa formularza do usuwania
class DeleteEmailForm(forms.ModelForm):
    is_active = forms.BooleanField(
        label='Regulamin serwisu i polityka prywatności',
        required=True,
        initial=False,
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'})
    )

    class Meta:
        abstract = True
        fields = ['is_active']

    def clean_is_active(self):
        is_active = self.cleaned_data.get('is_active')
        return is_active


# Formularz do kontaktu
class ContactForm(forms.Form):
    name = forms.CharField(label='Imię', max_length=128)
    email = forms.EmailField(label='E-mail', max_length=128)
    message = forms.CharField(label='Wiadomość', widget=forms.Textarea)
    captcha = ReCaptchaField(
        widget=ReCaptchaV2Checkbox(),
        error_messages={
            'required': _('reCaptacha jest wymagana.'),
            'invalid': _('Niepoprawna reCaptacha.')
        },
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['name'].widget.attrs.update({'class': 'form-control'})
        self.fields['email'].widget.attrs.update({'class': 'form-control'})
        self.fields['message'].widget.attrs.update({'class': 'form-control', 'rows': 5, 'style': 'resize:none'})


# Formularz do rejestracji użytkowników do subskrypcji newslettera
class NewsletterUserSignUpForm(forms.ModelForm):
    email = forms.EmailField(
        label='Wprowadź e-mail',
        widget=forms.EmailInput(attrs={'class': 'form-control form-subscribe bg-body-tertiary border-0 me-4',
                                       'placeholder': 'Wprowadź e-mail'}),
    )

    class Meta:
        model = NewsletterUser
        fields = ['email']

    def clean_email(self):
        email = self.cleaned_data.get('email')
        return email


# Formularz do tworzenia nowego newslettera
class NewsletterCreationForm(forms.ModelForm):
    title = forms.CharField(
        label='Tytuł',
        widget=forms.TextInput(attrs={'class': 'form-control'}),
    )

    class Meta:
        model = Newsletter
        fields = ['title', 'text', 'email', 'status_field']
        labels = {
            'status_field': 'Status',
        }
        widgets = {
            'email': forms.SelectMultiple(attrs={'class': 'form-select'}),
            'status_field': forms.Select(attrs={'class': 'form-select'}),
            'text': CKEditorWidget(),
        }

    def clean_title(self):
        title = self.cleaned_data.get('title')
        return title

    def clean_content(self):
        content = self.cleaned_data.get('content')
        return content


# Formularz do dodawania użytkowników do subskrypcji newslettera
class NewsletterAddUserForm(forms.ModelForm):
    email = forms.EmailField(
        label='E-mail',
        widget=forms.EmailInput(attrs={'class': 'form-control'}),
    )

    class Meta:
        model = NewsletterUser
        fields = ['email']

    def clean_email(self):
        email = self.cleaned_data.get('email')
        return email


# Formularz do usuwania newslettera
class NewsletterDeleteForm(DeleteEmailForm):
    class Meta(DeleteEmailForm.Meta):
        model = Newsletter


# Formularz do usuwania subskrybenta z listy newslettera
class NewsletterUserDeleteForm(DeleteEmailForm):
    class Meta(DeleteEmailForm.Meta):
        model = NewsletterUser


# Formularz do tworzenia profilu autora
class AuthorCreateForm(forms.ModelForm):
    bio = forms.CharField(
        label='O autorze',
        max_length=512,
        required=True,
        widget=forms.Textarea(attrs={'rows': 5, 'class': 'form-control', 'style': 'resize:none'}),
        help_text="Krótka informacja o autorze, maksymalnie 512 znaków",
    )
    profile_pic = forms.ImageField(
        label='Zdjęcie profilowe dla autora',
        required=True,
        widget=forms.FileInput(attrs={'class': 'form-control align-middle'}),
    )
    author_quote = forms.CharField(
        label='Cytat autora',
        max_length=128,
        required=True,
        widget=forms.Textarea(attrs={'rows': 3, 'class': 'form-control', 'style': 'resize:none'}),
        help_text="Krótkie motto autora, maksymalnie 128 znaków",
    )
    author_function = forms.CharField(
        label='Funkcja autora',
        max_length=128,
        required=True,
        widget=forms.TextInput(attrs={'class': 'form-control', 'style': 'resize:none'}),
        help_text="Nazwa funkcji jaką pełni autor",
    )
    author_url = forms.URLField(
        label='URL do strony autora',
        required=False,
        widget=forms.URLInput(attrs={'class': 'form-control'}),
    )
    pinterest_url = forms.URLField(
        label='URL do Pinteresta',
        required=False,
        widget=forms.URLInput(attrs={'class': 'form-control'})
    )
    facebook_url = forms.URLField(
        label='URL do Facebooka',
        required=False,
        widget=forms.URLInput(attrs={'class': 'form-control'})
    )
    twitter_url = forms.URLField(
        label='URL do Twittera',
        required=False,
        widget=forms.URLInput(attrs={'class': 'form-control'})
    )
    instagram_url = forms.URLField(
        label='URL do Instagrama',
        required=False,
        widget=forms.URLInput(attrs={'class': 'form-control'})
    )

    class Meta:
        model = Author
        fields = "__all__"

        label = {
            'user': 'Użytkownik',
        }
        widgets = {
            'user': forms.Select(attrs={'class': 'form-select'}),
        }


# Formularz do edycji profilu autora
class AuthorEditForm(forms.ModelForm):
    bio = forms.CharField(
        label='O autorze',
        max_length=512,
        required=True,
        widget=forms.Textarea(attrs={'rows': 5, 'class': 'form-control', 'style': 'resize:none'}),
        help_text="Krótka informacja o autorze, maksymalnie 512 znaków",
    )
    profile_pic = forms.ImageField(
        label='Zdjęcie profilowe dla autora',
        required=True,
        widget=forms.FileInput(attrs={'class': 'form-control align-middle'}),
    )
    author_quote = forms.CharField(
        label='Cytat autora',
        max_length=128,
        required=True,
        widget=forms.Textarea(attrs={'rows': 3, 'class': 'form-control', 'style': 'resize:none'}),
        help_text="Krótkie motto autora, maksymalnie 128 znaków",
    )
    author_function = forms.CharField(
        label='Funkcja autora',
        max_length=128,
        required=True,
        widget=forms.TextInput(attrs={'class': 'form-control', 'style': 'resize:none'}),
        help_text="Nazwa funkcji jaką pełni autor",
    )
    author_url = forms.URLField(
        label='URL do strony autora',
        required=False,
        widget=forms.URLInput(attrs={'class': 'form-control'}),
    )
    pinterest_url = forms.URLField(
        label='URL do Pinteresta',
        required=False,
        widget=forms.URLInput(attrs={'class': 'form-control'})
    )
    facebook_url = forms.URLField(
        label='URL do Facebooka',
        required=False,
        widget=forms.URLInput(attrs={'class': 'form-control'})
    )
    twitter_url = forms.URLField(
        label='URL do Twittera',
        required=False,
        widget=forms.URLInput(attrs={'class': 'form-control'})
    )
    instagram_url = forms.URLField(
        label='URL do Instagrama',
        required=False,
        widget=forms.URLInput(attrs={'class': 'form-control'})
    )

    class Meta:
        model = Author
        fields = ['bio', 'profile_pic', 'author_quote', 'author_url', 'author_function', 'facebook_url', 'twitter_url',
                  'instagram_url', 'pinterest_url']


# Formularz do usuwania profilu autora
class AuthorDeleteForm(DeleteEmailForm):
    class Meta(DeleteEmailForm.Meta):
        model = Author


# Formularz do tworzenia kategorii
class CategoryCreateForm(forms.ModelForm):
    name = forms.CharField(
        label='Kategoria',
        required=True,
        widget=forms.TextInput(attrs={'class': 'form-control'}),
    )
    description = forms.CharField(
        label='Opis',
        max_length=256,
        required=True,
        widget=forms.Textarea(attrs={'rows': 5, 'class': 'form-control', 'style': 'resize:none'}),
        help_text="Opis kategorii, maksymalnie 256 znaków",
    )

    class Meta:
        model = Category
        fields = "__all__"


# Formularz do usuwania kategorii
class CategoryDeleteForm(DeleteEmailForm):
    class Meta(DeleteEmailForm.Meta):
        model = Category


# Formularz do tworzenia wpisu na blogu
class PostCreateForm(forms.ModelForm):
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
    favorite = forms.BooleanField(
        label='Czy wyróżnić post?',
        required=False,
        initial=False,
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'})
    )
    publiction_status = forms.BooleanField(
        label='Czy opublikować post?',
        initial=False,
        required=False,
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'})
    )

    class Meta:
        model = Blog
        fields = "__all__"

        labels = {
            'content': 'Treść',
            'author': 'Autor',
        }
        widgets = {
            'content': CKEditorWidget(),
            'author': forms.Select(attrs={'class': 'form-select'}),
        }


# Formularz do usuwania wpisu na blogu
class PostDeleteForm(DeleteEmailForm):
    class Meta(DeleteEmailForm.Meta):
        model = Blog


# Formularz do tworzenia komentarza z panelu adminstracyjnego
class CommentCreateForm(forms.ModelForm):
    content = forms.CharField(
        label='Treść',
        required=True,
        widget=forms.Textarea(attrs={'rows': 3, 'class': 'form-control', 'style': 'resize:none'}),
        help_text="Treść komentarza, maksymalnie 256 znaków",
    )

    class Meta:
        model = Comment
        fields = "__all__"

        widgets = {
            'author': forms.Select(attrs={'class': 'form-select'}),
            'blog': forms.Select(attrs={'class': 'form-select'}),
        }


# Formularz do usuwania komentarza
class CommentDeleteForm(DeleteEmailForm):
    class Meta(DeleteEmailForm.Meta):
        model = Blog


# Formularz do tworzenia komentarza do postu
class CommentForm(forms.ModelForm):
    content = forms.CharField(
        max_length=256,
        label='Treść',
        required=True,
        widget=forms.Textarea(
            attrs={'rows': 5, 'class': 'form-control', 'id': 'comment-content', 'style': 'resize:none'}),
        help_text="Treść komentarza, maksymalnie 256 znaków",
    )

    class Meta:
        model = Comment
        fields = ['content']


# Formularz do tworzenia wiadomości o spotkaniach
class Meetups_newsCreationForm(AddEmailForm):
    class Meta(AddEmailForm.Meta):
        model = Meetups_news


# Formularz do usuwania wiadomości o spotkaniach
class Meetups_newsDeleteForm(DeleteEmailForm):
    class Meta(DeleteEmailForm.Meta):
        model = Meetups_news


# Formularz do tworzenia okazji aukcyjnych
class AuctionOpportunitiesCreationForm(AddEmailForm):
    class Meta(AddEmailForm.Meta):
        model = AuctionOpportunities


# Formularz do usuwania okazji aukcyjnych
class AuctionOpportunitiesDeleteEmailForm(DeleteEmailForm):
    class Meta(DeleteEmailForm.Meta):
        model = AuctionOpportunities


# Formularz do tworzenia wiadomości firmowych
class CompanyNewsCreationForm(AddEmailForm):
    class Meta(AddEmailForm.Meta):
        model = CompanyNews


# Formularz do usuwania wiadomości firmowych
class CompanyNewsDeleteEmailForm(DeleteEmailForm):
    class Meta(DeleteEmailForm.Meta):
        model = CompanyNews


# Formularz do tworzenia wiadomości "Shot wydarzeń"
class ReplayNewsCreationForm(AddEmailForm):
    class Meta(AddEmailForm.Meta):
        model = ReplayNews


# Formularz do usuwania wiadomości "Shot wydarzeń"
class ReplayNewsDeleteEmailForm(DeleteEmailForm):
    class Meta(DeleteEmailForm.Meta):
        model = ReplayNews


# Formularz do tworzenia wiadomości o rozwoju
class DevelopmentNewsCreationForm(AddEmailForm):
    class Meta(AddEmailForm.Meta):
        model = DevelopmentNews


# Formularz do usuwania wiadomości o rozwoju
class DevelopmentNewsDeleteEmailForm(DeleteEmailForm):
    class Meta(DeleteEmailForm.Meta):
        model = DevelopmentNews


# Formularz do usuwania użytkowników
class UsersDeleteEmailForm(DeleteEmailForm):
    class Meta(DeleteEmailForm.Meta):
        model = User


# Formularz do usuwania aplikacji społecznościowych
class SocialAppDeleteEmailForm(DeleteEmailForm):
    class Meta(DeleteEmailForm.Meta):
        model = SocialApp


# Formularz do usuwania tokenów społecznościowych
class SocialTokenDeleteEmailForm(DeleteEmailForm):
    class Meta(DeleteEmailForm.Meta):
        model = SocialToken


# Formularz do usuwania kont społecznościowych
class SocialAccountDeleteEmailForm(DeleteEmailForm):
    class Meta(DeleteEmailForm.Meta):
        model = SocialAccount


# Formularz do usuwania adresów e-mail dla użytkowników logujących się przez aplikacje
class EmailAddressDeleteForm(DeleteEmailForm):
    class Meta(DeleteEmailForm.Meta):
        model = EmailAddress


# Formularz do zarządzania wiadomościami o spotkaniah i wydarzeniach dla użytkowników
class UserMeetups_newsForm(forms.ModelForm):
    meetups_news = forms.BooleanField(
        label='Spotkania i wydarzenia',
        help_text='Otrzymuj e-mail, gdy w pobliżu Twojej lokalizacji pojawi się spotkanie bądź aukcja.',
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        required=False,
    )

    class Meta:
        model = User
        fields = ['meetups_news']


# Formularz do zarządzania powiadomieniami o pominiętych artykułąch dla użytkowników
class UserMissNewsForm(forms.ModelForm):
    miss_news = forms.BooleanField(
        label='Pominięte artykuły',
        help_text='Otrzymuj ważne powiadomienia o aktywnościach, które Cię ominęły.',
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        required=False,
    )

    class Meta:
        model = User
        fields = ['miss_news']


# Formularz do zarządzania okazjami aukcyjnymi dla użytkowników
class UserAuctionOpportunitiesForm(forms.ModelForm):
    opportunities_news = forms.BooleanField(
        label='Okazje z rynku aukcyjnego',
        help_text='Otrzymuj e-mail z niepowtarzalnymi okazjami na zakupy z rynku aukcyjnego.',
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        required=False,
    )

    class Meta:
        model = User
        fields = ['opportunities_news']


# Formularz do zarządzania wiadomościami firmowymi dla użytkowników
class UserCompanyNewsForm(forms.ModelForm):
    company_news = forms.BooleanField(
        label='Wiadomości od Banknoty',
        help_text='Otrzymuj nowości od nas, komunikaty i informacje na temat nowości dotyczących produktów.',
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        required=False,
    )

    class Meta:
        model = User
        fields = ['company_news']


# Formularz do zarządzania wiadomościami "Shot wydarzeń" przez użytkownika
class UserReplayNewsForm(forms.ModelForm):
    replay_news = forms.BooleanField(
        label='Shot wydzarzeń od Banknoty',
        help_text='Wysyłana od czasu do czasu wiadomość zawierająca najpopularniejsze shoty.',
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        required=False,
    )

    class Meta:
        model = User
        fields = ['replay_news']


# Formularz do zarządzania wiadomościami o rozwoju przez użytkownika
class UserDevelopmentNewsForm(forms.ModelForm):
    development_news = forms.BooleanField(
        label='Informacje o rozwoju i zmianach na Banknoty',
        help_text='Wiadomoś od nas zawierająca informacje o rozwoju i zmianach na Banknoty.',
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        required=False,
    )

    class Meta:
        model = User
        fields = ['development_news']


# Formularz do edycji aplikacji społecznościowych
class SocialAppForm(forms.ModelForm):
    class Meta:
        model = SocialApp
        fields = ['provider', 'provider_id', 'name',  'client_id', 'secret', 'key', 'settings', 'sites']

        widgets = {
            'provider': forms.Select(attrs={'class': 'form-select'}),
            'provider_id': forms.TextInput(attrs={'class': 'form-control'}),
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'client_id': forms.TextInput(attrs={'class': 'form-control'}),
            'secret': forms.TextInput(attrs={'class': 'form-control'}),
            'key': forms.TextInput(attrs={'class': 'form-control'}),
            'settings': forms.Textarea(attrs={'class': 'form-control', 'rows': 5, 'style': 'resize:none'}),
            'sites': forms.SelectMultiple(attrs={'class': 'form-control'}),
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
            'app': forms.Select(attrs={'class': 'form-select'}),
            'account': forms.Select(attrs={'class': 'form-select'}),
            'token': forms.TextInput(attrs={'class': 'form-control'}),
            'token_secret': forms.TextInput(attrs={'class': 'form-control'}),
            'expires_at': forms.DateTimeInput(attrs={'class': 'form-control'}),
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
            'user': forms.Select(attrs={'class': 'form-select'}),
            'provider': forms.TextInput(attrs={'class': 'form-control'}),
            'uid': forms.TextInput(attrs={'class': 'form-control'}),
            'extra_data': forms.Textarea(attrs={'class': 'form-control', 'rows': 5, 'style': 'resize:none'}),
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
            'user': forms.Select(attrs={'class': 'form-select'}),
            'email': forms.TextInput(attrs={'class': 'form-control'}),
            'verified': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'primary': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }

        labels = {
            'user': 'Użytkownik',
            'email': 'Adres e-mail',
            'verified': 'Potwierdzony',
            'primary': 'Pierwszy',
        }