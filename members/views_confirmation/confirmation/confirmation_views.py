from django.contrib.auth import get_user_model
from django.contrib.auth.tokens import default_token_generator
from django.shortcuts import redirect
from django.shortcuts import render
from django.utils.encoding import force_str
from django.utils.http import urlsafe_base64_decode


# Widoki potwierdzenia e-maila po rejestracji
def confirm_email(request, uidb64, token):
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = get_user_model().objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, get_user_model().DoesNotExist):
        user = None

    if user is not None and default_token_generator.check_token(user, token):
        user.is_active = True
        user.save()
        return redirect('registration_confirmed')
    else:
        return redirect('confirmation_error')


# Widok potwierdzenia rejestracji
def registration_confirmed(request):
    return render(
        request,
        'Registration/Confirmed.html'
    )


# Widok błędu potwierdzenia e-maila po rejestracji
def confirmation_error(request):
    return render(
        request,
        'Registration/ConfirmationError.html'
    )


# Widok strony z informacją o potwierdzeniu rejestracji
def confirmation_page(request):
    return render(
        request,
        'Registration/Confirmation.html'
    )
