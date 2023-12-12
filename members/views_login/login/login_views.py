from django.contrib import messages
from django.contrib.auth import authenticate
from django.contrib.auth import login
from django.contrib.auth import logout
from django.contrib.auth.models import User
from django.shortcuts import redirect
from django.shortcuts import render

from members.forms import LoginForm


# Widok logowania użytkownika
def login_view(request):
    if request.method == 'POST':
        form = LoginForm(request.POST)

        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            user = authenticate(request, username=username, password=password)
            if user is not None:
                login(request, user)
                try:
                    User.objects.get(id=user.id)
                    return redirect('home')
                except User.DoesNotExist:
                    return redirect('edit_profile')
            else:
                messages.error(
                    request,
                    'Nieprawidłowa nazwa użytkownika lub hasło.'
                )
    else:
        form = LoginForm()

    context = {
        'form': form,
    }

    return render(
        request,
        'Registration/Login.html',
        context
    )


# Widok wylogowania użytkownika
def logout_page(request):
    logout(request)
    return redirect('/')
