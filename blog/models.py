from urllib import request
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.core.validators import URLValidator
from django.db import models
from ckeditor.fields import RichTextField
from django.utils.translation import gettext as _
from phonenumber_field.modelfields import PhoneNumberField
from django.conf import settings
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver


def validate_bio(value):
    if len(value) > 512:
        raise ValidationError('O autorze może zawierać maksymalnie 512 znaków.')


def validate_content(value):
    if len(value) > 256:
        raise ValidationError('Komentarz może zawierać maksymalnie 256 znaków.')


def validate_title(value):
    if len(value) > 128:
        raise ValidationError('Tytuł może zawierać maksymalnie 128 znaków.')


def validate_introduction(value):
    max_words = 50
    if len(value.split()) > max_words:
        raise ValidationError(
            _("Wstpę może zawierać maksymalnie %(max_words)s słów."),
            params={'max_words': max_words},
        )


def validate_facebook(value):
    if "facebook" not in value:
        raise ValidationError('Adres nie jest od facebooka.')


def validate_twitter(value):
    if "twitter" not in value:
        raise ValidationError('Adres nie jest od twittera.')


def validate_instagram(value):
    if "instagram" not in value:
        raise ValidationError('Adres nie jest od instagrama.')


def validate_pinterest(value):
    if "pinterest" not in value:
        raise ValidationError('Adres nie jest od pinteresta.')


def validate_category(value):
    if len(value) > 128:
        raise ValidationError('Kategoria może zawierać maksymalnie 128 znaków.')


def validate_category_description(value):
    if len(value) > 512:
        raise ValidationError('Opis kategori może zawierać maksymalnie 512 znaków.')


def validate_author_quote(value):
    if len(value) > 128:
        raise ValidationError('Cytat autora może zawierać maksymalnie 128 znaków.')


def validate_author_function(value):
    if len(value.split()) > 5:
        raise ValidationError('Nazwa stanowiska autora może zawierać maksymalnie 5 słów.')


class Category(models.Model):
    name = models.CharField(
        max_length=128,
        unique=True,
        blank=False,
        validators=[validate_category],
        error_messages={
            'unique': "Kategoria o tej nazwie już istnieje",
        },
        verbose_name="Kategoria"
    )
    description = models.TextField(
        max_length=512,
        blank=False,
        validators=[validate_category_description],
        verbose_name='Opis'
    )

    def __str__(self):
        return "Kategoria | " + str(self.name)


class Author(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, verbose_name="Użytkownik")
    bio = models.TextField(
        validators=[validate_bio],
        verbose_name="O autorze", help_text="Krótka informacja o autorze, maksymalnie 512 znaków.")
    profile_pic = models.ImageField(
        null=False, blank=False,
        upload_to="images/profile/",
        verbose_name="Zdjęcie profilowe")
    author_quote = models.TextField(null=False,
                                    blank=False,
                                    validators=[validate_author_quote],
                                    verbose_name='Cytat autora',
                                    help_text="Krótkie motto autora, maksymalnie 128 znaków.")
    author_function = models.TextField(null=False,
                                       blank=False,
                                       validators=[validate_author_function],
                                       verbose_name='Stanowisko autora',
                                       help_text="Nazwa funkcji jaką pełni autor.")
    author_url = models.URLField(null=True, blank=True, verbose_name="URL do strony użytkowanika")
    pinterest_url = models.URLField(
        validators=[validate_pinterest],
        null=True, blank=True, verbose_name="URL do Pinteresta")
    facebook_url = models.URLField(
        validators=[validate_facebook],
        null=True, blank=True, verbose_name="URL do Facebooka")
    twitter_url = models.URLField(
        validators=[validate_twitter],
        null=True, blank=True, verbose_name="URL do Twittera")
    instagram_url = models.URLField(
        validators=[validate_instagram],
        null=True, blank=True, verbose_name="URL do Instagrama")

    def __str__(self):
        if str(self.user.first_name) and str(self.user.last_name):
            return "Autor | " + str(self.user.first_name) + " " + str(self.user.last_name)
        else:
            return "Autor | " + str(self.user).capitalize()

    def is_profile_pic(self):
        if self.profile_pic:
            return True
        else:
            return False

    is_profile_pic.boolean = True
    is_profile_pic.short_description = 'Profile picture'

    def is_author_url(self):
        if self.author_url:
            return True
        else:
            return False

    is_author_url.boolean = True
    is_author_url.short_description = 'Author page'

    def is_pinterest_url(self):
        if self.pinterest_url:
            return True
        else:
            return False

    is_pinterest_url.boolean = True
    is_pinterest_url.short_description = 'Pinterest page'

    def is_twitter_url(self):
        if self.twitter_url:
            return True
        else:
            return False

    is_twitter_url.boolean = True
    is_twitter_url.short_description = 'Twitter page'

    def is_facebook_url(self):
        if self.facebook_url:
            return True
        else:
            return False

    is_facebook_url.boolean = True
    is_facebook_url.short_description = 'Facebook page'

    def is_instagram_url(self):
        if self.instagram_url:
            return True
        else:
            return False

    is_instagram_url.boolean = True
    is_instagram_url.short_description = 'Instagram page'


# Model dla wpisu
class Blog(models.Model):
    title = models.TextField(validators=[validate_title], verbose_name="Tytuł")
    content = RichTextField(verbose_name="Treść")
    introduction = models.TextField(validators=[validate_introduction], verbose_name="Wstęp", null=True)
    background = models.ImageField(
        null=False,
        blank=False,
        upload_to="images/post/",
        verbose_name="Tło wpisu")
    date_posted = models.DateTimeField(auto_now_add=True, verbose_name="Data publikacji")
    date_edited = models.DateTimeField(auto_now=True, verbose_name="Data ostatniej edycji")
    author = models.ForeignKey(Author, on_delete=models.CASCADE, verbose_name="Autor")
    favorite = models.BooleanField(null=False, blank=False, default=False, verbose_name='Czy wyróżnić post?')
    category = models.ManyToManyField(Category, max_length=256, blank=False, verbose_name="Kategorie",
                                      help_text="Wyświetlą się maksymalnie trzy kategorie")
    publiction_status = models.BooleanField(null=False, blank=False, default=False, verbose_name="Czy opublikować post?")

    def __str__(self):
        if self.author.user.first_name and self.author.user.last_name:
            return f"{self.title} | {self.author.user.first_name} {self.author.user.last_name}"
        else:
            return f"{self.title} | {str(self.author).capitalize()}"

    def is_backgroud(self):
        if self.background:
            return True
        else:
            return False

    is_backgroud.boolean = True
    is_backgroud.short_description = 'Background picture'

    def is_publiction_status(self):
        if self.publiction_status:
            return True
        else:
            return False

    is_publiction_status.boolean = True
    is_publiction_status.short_description = 'Publication status'


# Model dla komentarzy
class Comment(models.Model):
    blog = models.ForeignKey(Blog, on_delete=models.CASCADE, verbose_name='Wpis')
    content = models.TextField(validators=[validate_content], verbose_name="Komentarz")
    date_posted = models.DateTimeField(auto_now_add=True, verbose_name="Data publikacji")
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, null=True, verbose_name="Autor")

    def __str__(self):
        if str(self.author.first_name) and str(self.author.last_name):
            return str(self.content)[:15].capitalize() + "... | " + \
                   str(self.author.first_name) + " " + str(self.author.last_name)
        else:
            return str(self.content)[:15].capitalize() + "... | " + str(self.author).capitalize()


# Model dla autora


class User(models.Model):
    GENDER_CHOICES = (
        ('M', 'Mężczyzna'),
        ('K', 'Kobieta'),
        ('I', 'Inna'),
    )
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        verbose_name="Użytkownik")
    bio = models.TextField(
        null=False,
        blank=True,
        validators=[validate_bio],
        verbose_name="Bio",
        help_text="Krótka informacja o użytkowniku, maksymalnie 512 znaków.")
    profile_pic = models.ImageField(
        null=False,
        blank=False,
        default="images/profile/1.png",
        upload_to="images/user/",
        verbose_name="Zdjęcie profilowe")
    phone_number = PhoneNumberField(
        region='PL',
        null=True,
        blank=True,
        unique=True,
        verbose_name="Numer telefonu")
    gender = models.CharField(
        choices=GENDER_CHOICES,
        null=False,
        blank=False,
        default='Mężczyzna',
        verbose_name="Płeć",
        max_length=6)
    newsletter = models.BooleanField(
        default=False,
        verbose_name="Biuletyn")
    miss_news = models.BooleanField(
        default=False,
        verbose_name="Pominięte artykuły")
    meetups_news = models.BooleanField(
        default=True,
        verbose_name="Spotkania i wydarzenia")
    opportunities_news = models.BooleanField(
        default=False,
        verbose_name="Okazje z rynku aukcyjnego")
    company_news = models.BooleanField(
        default=True,
        verbose_name="Wiadomości od Banknoty")
    replay_news = models.BooleanField(
        default=False,
        verbose_name="Shot wydzarzeń na Banknoty")
    development_news = models.BooleanField(
        default=False,
        verbose_name="Informacje o rozwoju i zmianach na Banknoty")
    opened_posts = models.ManyToManyField(
        Blog,
        blank=True,
        related_name='opened_by_users',
        verbose_name="Otwarte posty"
    )
    can_be_author = models.BooleanField(
        default=False,
        verbose_name="Czy może być autorem",
        help_text='Czy wniosek na autora został rozpatrzony pozytywnie.')

    def __init__(self, *args, temp=65, **kwargs):
        self.temp = temp
        return super().__init__(*args, **kwargs)

    def __str__(self):
        return "Użytkownik | " + str(self.user).capitalize()

    def is_profile_pic(self):
        if self.profile_pic == "images/profile/1.png":
            return False
        else:
            return True

    is_profile_pic.boolean = True
    is_profile_pic.short_description = 'Zdjęcie profilowe'

    def is_bio(self):
        if self.bio:
            return True
        else:
            return False

    is_bio.boolean = True
    is_bio.short_description = 'Bio'

    def is_phone_number(self):
        if self.phone_number:
            return True
        else:
            return False

    is_phone_number.boolean = True
    is_phone_number.short_description = 'Phone number'

    def is_newsletter(self):
        if self.newsletter:
            return True
        else:
            return False

    is_newsletter.boolean = True
    is_newsletter.short_description = 'Newsletter'

    def save(self, *args, **kwargs):
        email_exists = NewsletterUser.objects.filter(email=self.user.email).exists()

        if self.newsletter:
            if not email_exists:
                NewsletterUser.objects.create(email=self.user.email)
        else:
            if email_exists:
                NewsletterUser.objects.filter(email=self.user.email).delete()

        super().save(*args, **kwargs)


class NewsletterUser(models.Model):
    email = models.EmailField(
        null=False,
        blank=False,
        verbose_name="E-mail")
    date_added = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return str(self.email)

    def save(self, *args, **kwargs):
        user_exists = User.objects.filter(user__email=self.email).exists()

        # if not user_exists:
        #     user = User.objects.create(user=AuthUser.objects.create(email=self.email), newsletter=True)
        #     user.save()

        super().save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        user = User.objects.filter(user__email=self.email).first()

        if user:
            user.newsletter = False
            user.save()

        super().delete(*args, **kwargs)


@receiver(post_save, sender=NewsletterUser)
@receiver(post_delete, sender=NewsletterUser)
def update_user_newsletter(sender, instance, **kwargs):
    user = User.objects.filter(user__email=instance.email).first()
    if user:
        user.newsletter = NewsletterUser.objects.filter(email=instance.email).exists()
        user.save()


class Newsletter(models.Model):
    EMAIL_STATUS_CHOICES = (
        ('Draft', 'Projekt'),
        ('Published', 'Opublikowany'))
    title = models.CharField(
        null=False,
        blank=False,
        max_length=250,
        verbose_name="Tytuł")
    text = RichTextField(
        null=False,
        blank=False,
        verbose_name="Treść")
    email = models.ManyToManyField(
        NewsletterUser,
        verbose_name="Subskrybujący")
    date_added = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Data dodania")
    date_modified = models.DateTimeField(
        auto_now=True,
        verbose_name="Data modyfikacji")
    status_field = models.CharField(
        choices=EMAIL_STATUS_CHOICES,
        default='Draft',
        max_length=10,
        verbose_name="Status"
    )

    def __str__(self):
        return "Biuletyn | " + str(self.title)

    def status(self):
        if self.status_field == 'Published':
            return True
        else:
            return False

    status.boolean = True
    status.short_description = 'Aktywny'


class Meetups_news(models.Model):
    EMAIL_STATUS_CHOICES = (
        ('Draft', 'Projekt'),
        ('Published', 'Opublikowany'))
    title = models.CharField(
        null=False,
        blank=False,
        max_length=250,
        verbose_name="Tytuł")
    text = RichTextField(
        null=False,
        blank=False,
        verbose_name="Treść")
    date_added = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Data dodania")
    date_modified = models.DateTimeField(
        auto_now=True,
        verbose_name="Data modyfikacji")
    status_field = models.CharField(
        choices=EMAIL_STATUS_CHOICES,
        default='Draft',
        max_length=10,
        verbose_name="Status"
    )

    def __str__(self):
        return "Spotkania i wydarzenia | " + str(self.title)

    def status(self):
        if self.status_field == 'Published':
            return True
        else:
            return False

    status.boolean = True
    status.short_description = 'Aktywny'


class AuctionOpportunities(models.Model):
    EMAIL_STATUS_CHOICES = (
        ('Draft', 'Projekt'),
        ('Published', 'Opublikowany'))
    title = models.CharField(
        null=False,
        blank=False,
        max_length=250,
        verbose_name="Tytuł")
    text = RichTextField(
        null=False,
        blank=False,
        verbose_name="Treść")
    date_added = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Data dodania")
    date_modified = models.DateTimeField(
        auto_now=True,
        verbose_name="Data modyfikacji")
    status_field = models.CharField(
        choices=EMAIL_STATUS_CHOICES,
        default='Draft',
        max_length=10,
        verbose_name="Status"
    )

    def __str__(self):
        return "Okazje aukcyjne | " + str(self.title)

    def status(self):
        if self.status_field == 'Published':
            return True
        else:
            return False

    status.boolean = True
    status.short_description = 'Aktywny'


class CompanyNews(models.Model):
    EMAIL_STATUS_CHOICES = (
        ('Draft', 'Projekt'),
        ('Published', 'Opublikowany'))
    title = models.CharField(
        null=False,
        blank=False,
        max_length=250,
        verbose_name="Tytuł")
    text = RichTextField(
        null=False,
        blank=False,
        verbose_name="Treść")
    date_added = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Data dodania")
    date_modified = models.DateTimeField(
        auto_now=True,
        verbose_name="Data modyfikacji")
    status_field = models.CharField(
        choices=EMAIL_STATUS_CHOICES,
        default='Draft',
        max_length=10,
        verbose_name="Status"
    )

    def __str__(self):
        return "Wiadomości firmowe | " + str(self.title)

    def status(self):
        if self.status_field == 'Published':
            return True
        else:
            return False

    status.boolean = True
    status.short_description = 'Aktywny'


class ReplayNews(models.Model):
    EMAIL_STATUS_CHOICES = (
        ('Draft', 'Projekt'),
        ('Published', 'Opublikowany'))
    title = models.CharField(
        null=False,
        blank=False,
        max_length=250,
        verbose_name="Tytuł")
    text = RichTextField(
        null=False,
        blank=False,
        verbose_name="Treść")
    date_added = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Data dodania")
    date_modified = models.DateTimeField(
        auto_now=True,
        verbose_name="Data modyfikacji")
    status_field = models.CharField(
        choices=EMAIL_STATUS_CHOICES,
        default='Draft',
        max_length=10,
        verbose_name="Status"
    )

    def __str__(self):
        return "Shot wydarzeń | " + str(self.title)

    def status(self):
        if self.status_field == 'Published':
            return True
        else:
            return False

    status.boolean = True
    status.short_description = 'Aktywny'


class DevelopmentNews(models.Model):
    EMAIL_STATUS_CHOICES = (
        ('Draft', 'Projekt'),
        ('Published', 'Opublikowany'))
    title = models.CharField(
        null=False,
        blank=False,
        max_length=250,
        verbose_name="Tytuł")
    text = RichTextField(
        null=False,
        blank=False,
        verbose_name="Treść")
    date_added = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Data dodania")
    date_modified = models.DateTimeField(
        auto_now=True,
        verbose_name="Data modyfikacji")
    status_field = models.CharField(
        choices=EMAIL_STATUS_CHOICES,
        default='Draft',
        max_length=10,
        verbose_name="Status"
    )

    def __str__(self):
        return "Informacje o rozwoju i zmianach | " + str(self.title)

    def status(self):
        if self.status_field == 'Published':
            return True


class ArticleAuthor(models.Model):
    first_name = models.CharField(
        null=False,
        blank=False,
        max_length=150,
        verbose_name="Imię"
    )
    last_name = models.CharField(
        null=False,
        blank=False,
        max_length=150,
        verbose_name="Nazwisko"
    )
    email = models.EmailField(
        null=False,
        blank=False,
        verbose_name="Adres e-mail"
    )
    phone_number = PhoneNumberField(
        region='PL',
        null=True,
        blank=True,
        verbose_name="Numer telefonu"
    )
    experience = models.TextField(
        null=False,
        blank=False,
        verbose_name="Doświadczenie związane z tematyką banknotów"
    )
    sample_article = RichTextField(
        null=False,
        blank=False,
        verbose_name="Próbny artykuł"
    )
    accept_terms = models.BooleanField(
        null=False,
        blank=False,
        default=False,
        verbose_name="Akceptuję regulamin"
    )
    approved = models.BooleanField(
        null=False,
        blank=False,
        default=False,
        verbose_name="Zatwierdzenie zgłoszenia"
    )
    rejected = models.BooleanField(
        null=False,
        blank=False,
        default=False,
        verbose_name="Odrzucenie zgłoszenia"
    )
    date_added = models.DateTimeField(
        null=False,
        blank=False,
        auto_now_add=True,
        verbose_name="Data utworzenia"
    )

    def __str__(self):
        return "Wniosek na autora | " + str(self.first_name) + " " + str(self.last_name)

    def is_approved(self):
        return self.approved

    is_approved.boolean = True
    is_approved.short_description = 'Zatwierdzenie zgłoszenia'

    def is_rejected(self):
        return self.rejected

    is_rejected.boolean = True
    is_rejected.short_description = 'Odrzucenie zgłoszenia'
