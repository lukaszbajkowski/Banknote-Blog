from urllib import request
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.core.validators import URLValidator
from django.db import models
from ckeditor.fields import RichTextField
from django.utils.translation import gettext as _


def validate_bio(value):
    if len(value) > 512:
        raise ValidationError('O autorze może zawierać maksymalnie 512 znaków.')


def validate_content(value):
    if len(value) > 256:
        raise ValidationError('Komentarz może zawierać maksymalnie 256 znaków.')


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
    if len(value) > 256:
        raise ValidationError('Kategoria może zawierać maksymalnie 256 znaków.')


def validate_category_description(value):
    if len(value) > 512:
        raise ValidationError('Opis kategori może zawierać maksymalnie 512 znaków.')


class Category(models.Model):
    name = models.CharField(max_length=256, blank=False, validators=[validate_category], verbose_name="Kategorie")
    description = models.TextField(blank=False, validators=[validate_category_description], verbose_name='Opis')

    def __str__(self):
        return self.name


# Model dla wpisu
class Blog(models.Model):
    title = models.CharField(max_length=122, verbose_name="Tytuł")
    content = RichTextField(verbose_name="Treść")
    introduction = models.TextField(validators=[validate_introduction], verbose_name="Wstęp", null=True)
    background = models.ImageField(
        null=False, blank=False,
        upload_to="images/post/",
        verbose_name="Tło wpisu")
    date_posted = models.DateTimeField(auto_now_add=True, verbose_name="Data publikacji")
    date_edited = models.DateTimeField(auto_now=True, verbose_name="Data ostatniej edycji")
    author = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="Autor")
    favorite = models.BooleanField(null=False, blank=False, default=False, verbose_name='Czy wyróżnić post?')
    category = models.ManyToManyField(Category, max_length=256, blank=False, verbose_name="Kategorie", help_text="Wyświetlą się maksymalnie trzy kategorie.<br/> <br/>")

    def __str__(self):
        if str(self.author.first_name) and str(self.author.last_name):
            return self.title + " | " + str(self.author.first_name) + " " + str(self.author.last_name)
        else:
            return self.title + " | " + str(self.author).capitalize()

    def is_backgroud(self):
        if self.background:
            return True
        else:
            return False

    is_backgroud.boolean = True
    is_backgroud.short_description = 'Background picture'


# Model dla komentarzy
class Comment(models.Model):
    blog = models.ForeignKey(Blog, on_delete=models.CASCADE, verbose_name='Wpis')
    content = models.TextField(validators=[validate_content], verbose_name="Komentarz")
    date_posted = models.DateTimeField(auto_now_add=True, verbose_name="Data publikacji")
    author = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="Autor")

    def __str__(self):
        if str(self.author.first_name) and str(self.author.last_name):
            return str(self.content)[:15].capitalize() + "... | " + \
                   str(self.author.first_name) + " " + str(self.author.last_name)
        else:
            return str(self.content)[:15].capitalize() + "... | " + str(self.author).capitalize()


# Model dla autora
class Author(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, verbose_name="Użytkownik")
    bio = models.TextField(
        validators=[validate_bio],
        verbose_name="O autorze", help_text="Krótka informacja o autorze, maksymalnie 512 znaków.")
    profile_pic = models.ImageField(
        null=True, blank=True,
        upload_to="images/profile/",
        verbose_name="Zdjęcie profilowe")
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

# 1. Model postu blogowego:
# - Tytuł postu
# - Autor
# - Data publikacji
# - Treść postu
# - Kategoria
# - Tagi
# - Komentarze
