from django import forms
from django.contrib.auth.models import User as User


# Formularz ustawień subskrypcji newsletterów
class NotificationSettingsForm(forms.ModelForm):
    newsletter = forms.BooleanField(
        label='Biuletyn',
        required=False,
        initial=False,
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        help_text="Raz w tygodniu wyślemy Ci przyjemną wiadomość. Bez zbędnego spamu."
    )
    miss_news = forms.BooleanField(
        label='Pominięte artykuły',
        required=False,
        initial=False,
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        help_text="Otrzymuj ważne powiadomienia o aktywnościach, które Cię ominęły."
    )
    meetups_news = forms.BooleanField(
        label='Spotkania i wydarzenia',
        required=False,
        initial=False,
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        help_text="Otrzymuj e-mail, gdy w pobliżu Twojej lokalizacji pojawi się spotkanie bądź aukcja."
    )
    opportunities_news = forms.BooleanField(
        label='Okazje z rynku aukcyjnego',
        required=False,
        initial=False,
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        help_text="Otrzymuj e-mail z niepowtarzalnymi okazjami na zakupy z rynku aukcyjnego."
    )

    class Meta:
        model = User
        fields = ['newsletter', 'miss_news', 'meetups_news', 'opportunities_news']


# Formularz ustawień komunikacji od Banknoty
class CommunicationSettingForm(forms.ModelForm):
    company_news = forms.BooleanField(
        label='Wiadomości od Banknoty',
        required=False,
        initial=False,
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        help_text="Otrzymuj nowości od nas, komunikaty i informacje na temat nowości dotyczących produktów."
    )
    replay_news = forms.BooleanField(
        label='Shot wydarzeń od Banknoty',
        required=False,
        initial=False,
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        help_text="Wysyłana od czasu do czasu wiadomość zawierająca najpopularniejsze shoty."
    )
    development_news = forms.BooleanField(
        label='Informacje o rozwoju i zmianach na Banknoty',
        required=False,
        initial=False,
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        help_text="Wiadomość od nas zawierająca informacje o rozwoju i zmianach na Banknoty."
    )

    class Meta:
        model = User
        fields = ['company_news', 'replay_news', 'development_news']
