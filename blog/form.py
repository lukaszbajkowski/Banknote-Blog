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
        model = User
        fields = (
            'bio',  'profile_pic', 'phone_number', 'gender', 'newsletter', 'miss_news', 'meetups_news', 'opportunities_news',
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


User = get_user_model()


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
        validators=[validate_email]
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
        label=_('Hasło'),
        widget=forms.PasswordInput(attrs={'class': 'form-control'})
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

    def clean_is_active(self):
        is_active = self.cleaned_data.get('is_active')
        if not is_active:
            raise forms.ValidationError(_('Akceptacja regulaminu serwisu i polityki prywatności jest wymagana.'))
        return is_active


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


class NewsletterDeleteForm(DeleteEmailForm):
    class Meta(DeleteEmailForm.Meta):
        model = Newsletter


class NewsletterUserDeleteForm(DeleteEmailForm):
    class Meta(DeleteEmailForm.Meta):
        model = NewsletterUser


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


class AuthorDeleteForm(DeleteEmailForm):
    class Meta(DeleteEmailForm.Meta):
        model = Author


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


class CategoryDeleteForm(DeleteEmailForm):
    class Meta(DeleteEmailForm.Meta):
        model = Category


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


class PostDeleteForm(DeleteEmailForm):
    class Meta(DeleteEmailForm.Meta):
        model = Blog


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


class CommentDeleteForm(DeleteEmailForm):
    class Meta(DeleteEmailForm.Meta):
        model = Blog


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


class Meetups_newsCreationForm(AddEmailForm):
    class Meta(AddEmailForm.Meta):
        model = Meetups_news


class Meetups_newsDeleteForm(DeleteEmailForm):
    class Meta(DeleteEmailForm.Meta):
        model = Meetups_news


class AuctionOpportunitiesCreationForm(AddEmailForm):
    class Meta(AddEmailForm.Meta):
        model = AuctionOpportunities


class AuctionOpportunitiesDeleteEmailForm(DeleteEmailForm):
    class Meta(DeleteEmailForm.Meta):
        model = AuctionOpportunities


class CompanyNewsCreationForm(AddEmailForm):
    class Meta(AddEmailForm.Meta):
        model = CompanyNews


class CompanyNewsDeleteEmailForm(DeleteEmailForm):
    class Meta(DeleteEmailForm.Meta):
        model = CompanyNews


class ReplayNewsCreationForm(AddEmailForm):
    class Meta(AddEmailForm.Meta):
        model = ReplayNews


class ReplayNewsDeleteEmailForm(DeleteEmailForm):
    class Meta(DeleteEmailForm.Meta):
        model = ReplayNews


class DevelopmentNewsCreationForm(AddEmailForm):
    class Meta(AddEmailForm.Meta):
        model = DevelopmentNews


class DevelopmentNewsDeleteEmailForm(DeleteEmailForm):
    class Meta(DeleteEmailForm.Meta):
        model = DevelopmentNews


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
