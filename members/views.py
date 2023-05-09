from django.contrib import messages
from django.contrib.auth import login, authenticate, logout, update_session_auth_hash
from django.contrib.auth.models import User
from django.shortcuts import render, redirect
from django.contrib.auth.forms import UserCreationForm, UserChangeForm, PasswordChangeForm
from .forms import *
from blog.models import *
from django.views import generic
from django.urls import reverse_lazy
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.core.validators import EmailValidator
from django.db import IntegrityError


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
            User.objects.get(username=username)
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


@login_required
def UserEditView(request):
    category = Category.objects.all()
    blog = Blog.objects.all().order_by('-date_posted')[1:]
    user = request.user
    user_custom, created = User_Custom.objects.get_or_create(user=user)
    delete_form = DeleteAccountForm(request.POST or None)
    if request.method == 'POST':
        user_form = UserForm(request.POST, request.FILES, instance=user_custom)
        edit_user_form = EditUserForm(request.POST, instance=user)
        if user_form.is_valid() and edit_user_form.is_valid():
            user_form.save()
            edit_user_form.save()
            return redirect('edit_profile')
    else:
        user_form = UserForm(instance=user_custom)
        edit_user_form = EditUserForm(instance=user)

    if delete_form.is_valid() and delete_form.cleaned_data['confirm_deletion']:
        user.delete()
        logout(request)
        return redirect('home')

    context = {
        'category': category,
        'blog': blog,
        'user_form': user_form,
        'edit_user_form': edit_user_form,
        'delete_form': delete_form,
    }
    return render(request, 'registration/edit_profile.html', context)


@login_required
def UserChangePasswordView(request):
    category = Category.objects.all()
    blog = Blog.objects.all().order_by('-date_posted')[1:]

    if request.method == 'POST':
        edit_password_form = PasswordChangingForm(user=request.user, data=request.POST)
        if edit_password_form.is_valid():
            user = edit_password_form.save()
            update_session_auth_hash(request, user)  # Important! Refresh the session
        return redirect('edit_security_page')
    else:
        edit_password_form = PasswordChangingForm(user=request.user)

    context = {
        'category': category,
        'blog': blog,
        'edit_password_form': edit_password_form,
    }
    return render(request, 'registration/edit_security.html', context)


@login_required
def UserChangePageView(request):
    category = Category.objects.all()
    blog = Blog.objects.all().order_by('-date_posted')[1:]
    context = {
        'category': category,
        'blog': blog,
    }
    return render(request, 'registration/edit_security_page.html', context)


@login_required
def UserChangeEmailView(request):
    if request.method == 'POST':
        form = EmailChangeForm(user=request.user, data=request.POST)
        if form.is_valid():
            form.save()
            return redirect('edit_security_page')
    else:
        form = EmailChangeForm(user=request.user)

    category = Category.objects.all()
    blog = Blog.objects.all().order_by('-date_posted')[1:]
    context = {
        'category': category,
        'blog': blog,
        'edit_email_form': form,
    }
    return render(request, "registration/edit_email.html", context)
