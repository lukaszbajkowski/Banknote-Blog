from django import forms

from blog.forms.base_form import DeleteForm, AuthorBaseForm
from blog.models import *


# Formularz do tworzenia profilu autora
class AuthorCreateForm(AuthorBaseForm):
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

    class Meta(AuthorBaseForm.Meta):
        fields = AuthorBaseForm.Meta.fields + ['author_url', 'facebook_url', 'twitter_url', 'instagram_url',
                                               'pinterest_url']


# Formularz do edycji profilu autora
class AuthorEditForm(AuthorBaseForm):
    class Meta(AuthorBaseForm.Meta):
        pass


# Formularz do usuwania profilu autora
class AuthorDeleteForm(DeleteForm):
    class Meta(DeleteForm.Meta):
        model = Author
