from django import forms

from blog.forms.base_form import DeleteForm, AddEmailForm
from blog.models import *


# Formularz do tworzenia i edycji okazji aukcyjnych
class AuctionOpportunitiesCreationForm(AddEmailForm):
    class Meta(AddEmailForm.Meta):
        model = AuctionOpportunities


# Formularz do usuwania okazji aukcyjnych
class AuctionOpportunitiesDeleteForm(DeleteForm):
    class Meta(DeleteForm.Meta):
        model = AuctionOpportunities


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
