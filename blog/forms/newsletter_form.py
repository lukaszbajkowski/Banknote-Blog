from ckeditor.widgets import CKEditorWidget
from django import forms

from blog.forms.base_form import DeleteForm
from blog.models import *


# Formularz do rejestracji użytkowników do subskrypcji newslettera
class NewsletterUserSignUpForm(forms.ModelForm):
    email = forms.EmailField(
        label='Wprowadź e-mail',
        widget=forms.EmailInput(attrs={
            'class': 'form-control form-subscribe bg-body-tertiary border-0 me-4',
            'placeholder': 'Wprowadź e-mail'
        }
        ),
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
class NewsletterDeleteForm(DeleteForm):
    class Meta(DeleteForm.Meta):
        model = Newsletter


# Formularz do usuwania subskrybenta z listy newslettera
class NewsletterUserDeleteForm(DeleteForm):
    class Meta(DeleteForm.Meta):
        model = NewsletterUser
