from captcha.fields import ReCaptchaField
from captcha.widgets import ReCaptchaV2Checkbox
from django import forms
from django.utils.translation import gettext_lazy as _


# Formularz do kontaktu
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
