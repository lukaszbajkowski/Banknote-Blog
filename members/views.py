import ssl

from django.contrib.auth.views import PasswordResetView

from members.forms.reset_password_form import CustomPasswordResetForm

ssl._create_default_https_context = ssl._create_unverified_context


# Widok do obsługi resetowania hasła z dostosowanym formularzem
class CustomPasswordResetView(PasswordResetView):
    form_class = CustomPasswordResetForm
