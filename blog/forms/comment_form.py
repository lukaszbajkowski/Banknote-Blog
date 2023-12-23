from django import forms

from blog.forms.base_form import DeleteForm
from blog.models import *


# Formularz do tworzenia i edycji komentarza z panelu administracyjnego
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
class CommentDeleteForm(DeleteForm):
    class Meta(DeleteForm.Meta):
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
