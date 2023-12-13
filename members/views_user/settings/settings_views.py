from django.contrib.auth import logout
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect
from django.shortcuts import render

from blog.models import Blog
from blog.models import Category
from blog.models import User as User_Custom
from members.forms import DeleteAccountForm
from members.forms import EditUserForm
from members.forms import UserForm


# Widok edycji profilu użytkownika
@login_required(login_url='home')
def user_edit_view(request):
    category = Category.objects.all()
    blog = Blog.objects.all().filter(publiction_status=True).order_by('-date_posted')[1:]
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
    return render(
        request,
        'my_account/edit_profile.html',
        context
    )


# Widok do przekierowania do zmiany e-mail lub hasła
@login_required(login_url='home')
def user_change_main_page_view(request):
    category = Category.objects.all()
    blog = Blog.objects.all().filter(publiction_status=True).order_by('-date_posted')[1:]

    context = {
        'category': category,
        'blog': blog,
    }
    return render(
        request,
        'my_account/edit_security_page.html',
        context
    )