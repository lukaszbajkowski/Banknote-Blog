from django.contrib import messages
from django.contrib.auth import update_session_auth_hash

from django.shortcuts import get_object_or_404
from django.shortcuts import redirect
from django.shortcuts import render

from blog.decorators import superuser_required

from blog.form_users import UserCreationForm
from blog.form_users import UserProfileForm
from blog.form_users import UserEditForm
from blog.form_users import CustomPasswordChangingForm
from blog.form import UsersDeleteEmailForm

from blog.models import User as DjangoUser

from blog.views import get_paginated_context


# Widok dodawania użytkownika (dla superusera)
@superuser_required
def users_add_view(request):
    if request.method == 'POST':
        user_form = UserCreationForm(request.POST)
        profile_form = UserProfileForm(request.POST, request.FILES)
        if user_form.is_valid() and profile_form.is_valid():
            user = user_form.save(commit=False)
            user.set_password(user_form.cleaned_data['password'])
            user.save()
            profile = profile_form.save(commit=False)
            profile.user = user
            profile.save()
            messages.success(
                request,
                'Użytkownik został utworzony',
                "alert alert-success alert-dismissible fade show mt-3"
            )
            return redirect('users_add')
    else:
        user_form = UserCreationForm()
        profile_form = UserProfileForm()

    context = {
        'user_form': user_form,
        'profile_form': profile_form
    }
    return render(
        request,
        'AdminTemplates/Accounts/User/UserAddAdmin.html',
        context
    )


# Widok zarządzania użytkownikami (dla superusera)
@superuser_required
def users_manage_admin_panel_view(request):
    users = DjangoUser.objects.select_related('user').all()\
        .order_by('-user__id')

    context = get_paginated_context(request, users, 10)
    return render(
        request,
        'AdminTemplates/Accounts/User/UserManageAdmin.html',
        context
    )


# Widok szczegółów użytkownika (dla superusera)
@superuser_required
def users_detail_admin_panel_view(request, pk):
    users = get_object_or_404(DjangoUser, pk=pk)

    context = {
        'users': users,
    }
    return render(
        request,
        'AdminTemplates/Accounts/User/UserDetailAdmin.html',
        context
    )


# Widok edycji użytkownika (dla superusera)
@superuser_required
def users_edit_main_page_admin_panel_view(request, pk):
    users = get_object_or_404(DjangoUser, pk=pk)
    django_user = users.user

    if request.method == 'POST':
        user_profile_form = UserProfileForm(request.POST, instance=users)
        user_email_form = UserEditForm(request.POST, instance=django_user)
        if user_profile_form.is_valid() and user_email_form.is_valid():
            user_profile_form.save()
            user_email_form.save()
            messages.success(
                request,
                'Użytkownik został edytowany',
                "alert alert-success alert-dismissible fade show mt-3"
            )
            return redirect('users_admin_panel')
    else:
        user_profile_form = UserProfileForm(instance=users)
        user_email_form = UserEditForm(instance=django_user)

    context = {
        'profile_form': user_profile_form,
        'user_form': user_email_form,
        'users': users,
    }
    return render(
        request,
        'AdminTemplates/Accounts/User/UserEditAdmin.html',
        context
    )


# Widok edycji hasła użytkownika (dla superusera)
@superuser_required
def users_edit_password_admin_panel_view(request, pk):
    user = get_object_or_404(DjangoUser, pk=pk)

    if request.method == 'POST':
        edit_password_form = CustomPasswordChangingForm(data=request.POST)
        if edit_password_form.is_valid():
            user = edit_password_form.save(user.user)
            update_session_auth_hash(request, user)
            messages.success(
                request,
                'Hasło użytkownika został edytowane',
                "alert alert-success alert-dismissible fade show mt-3"
            )
            return redirect('users_admin_panel')
    else:
        edit_password_form = CustomPasswordChangingForm()

    context = {
        'edit_password_form': edit_password_form,
        'users': user,
    }
    return render(
        request,
        'AdminTemplates/Accounts/User/UserEditPasswordAdmin.html',
        context
    )


# Widok usuwania użytkownika (dla superusera)
@superuser_required
def users_delete_admin_panel_view(request, pk):
    user = get_object_or_404(DjangoUser, pk=pk)

    if request.method == "POST":
        form = UsersDeleteEmailForm(request.POST, instance=user)
        if form.is_valid():
            user = user.user
            user.delete()
            messages.success(
                request,
                'Użytkownik został usunięty',
                "alert alert-success alert-dismissible fade show mt-3"
            )
            return redirect('users_admin_panel')
    else:
        form = UsersDeleteEmailForm(instance=user)

    context = {
        'form': form,
        'users': user,
    }
    return render(
        request,
        'AdminTemplates/Accounts/User/UserDeleteAdmin.html',
        context
    )
