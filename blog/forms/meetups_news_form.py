from django import forms

from blog.forms.base_form import DeleteForm, AddEmailForm
from blog.models import *


# Formularz do tworzenia i edycji wiadomości o spotkaniach
class MeetupsNewsCreationForm(AddEmailForm):
    class Meta(AddEmailForm.Meta):
        model = Meetups_news


# Formularz do usuwania wiadomości o spotkaniach
class MeetupsNewsDeleteForm(DeleteForm):
    class Meta(DeleteForm.Meta):
        model = Meetups_news


# Formularz do zarządzania wiadomościami o spotkaniach i wydarzeniach dla użytkowników
class UserMeetupsNewsForm(forms.ModelForm):
    meetups_news = forms.BooleanField(
        label='Spotkania i wydarzenia',
        help_text='Otrzymuj e-mail, gdy w pobliżu Twojej lokalizacji pojawi się spotkanie bądź aukcja.',
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        required=False,
    )

    class Meta:
        model = User
        fields = ['meetups_news']
