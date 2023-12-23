from django import forms

from blog.forms.base_form import AddEmailForm
from blog.forms.base_form import DeleteForm
from blog.models import ReplayNews
from blog.models import User


# Formularz do tworzenia i edycji wiadomości "Shot wydarzeń"
class ReplayNewsCreationForm(AddEmailForm):
    class Meta(AddEmailForm.Meta):
        model = ReplayNews


# Formularz do usuwania wiadomości "Shot wydarzeń"
class ReplayNewsDeleteForm(DeleteForm):
    class Meta(DeleteForm.Meta):
        model = ReplayNews


# Formularz do zarządzania wiadomościami "Shot wydarzeń" przez użytkownika
class UserReplayNewsForm(forms.ModelForm):
    replay_news = forms.BooleanField(
        label='Shot wydarzeń od Banknoty',
        help_text='Wysyłana od czasu do czasu wiadomość zawierająca najpopularniejsze shoty.',
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        required=False,
    )

    class Meta:
        model = User
        fields = ['replay_news']
