from django import forms


# Formularz do zmiany hasła na panelu administracyjnym.
class CustomPasswordChangingForm(forms.Form):
    error_messages = {
        'password_mismatch': "Podane hasła nie są identyczne.",
    }

    widgets = {
        'new_password1': forms.PasswordInput(
            attrs={
                'class': 'form-control',
                'required': True
            }
        ),
        'new_password2': forms.PasswordInput(
            attrs={
                'class': 'form-control',
                'required': True
            }
        ),
    }

    new_password1 = forms.CharField(
        label="Nowe hasło",
        widget=forms.PasswordInput(
            attrs={
                'class': 'form-control',
                'required': True
            }
        )
    )
    new_password2 = forms.CharField(
        label="Powtórz nowe hasło",
        widget=forms.PasswordInput(
            attrs={
                'class': 'form-control',
                'required': True
            }
        )
    )

    def clean(self):
        cleaned_data = super().clean()
        password1 = cleaned_data.get("new_password1")
        password2 = cleaned_data.get("new_password2")
        if password1 and password2 and password1 != password2:
            raise forms.ValidationError(
                self.error_messages['password_mismatch'],
                code='password_mismatch',
            )

    def save(self, user, commit=True):
        new_password = self.cleaned_data["new_password1"]
        user.set_password(new_password)
        if commit:
            user.save()
        return user
