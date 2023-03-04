from django.contrib import messages
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.models import User
from django.shortcuts import render, redirect
from django.contrib.auth.forms import UserCreationForm
from .forms import CustomUserForm


def register_page(request):
    if request.method != 'POST':
        form = CustomUserForm()
    else:
        form = CustomUserForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('/')

    context = {'form': form}

    return render(request, 'registration/registration.html', context)


def login_page(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        try:
            user = User.objects.get(username=username)
            user = authenticate(username=username, password=password)

            if user is not None:
                login(request, user)
                return redirect('home')
            else:
                messages.error(request, 'Username or Password is incorrect')
        except:
            messages.error(request, 'User does not exist.')

    context = {}

    return render(request, 'registration/login.html', context)

def logout_page(request):
    logout(request)
    return redirect('/')
