from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect
from django.shortcuts import render

from blog.models import Blog
from blog.models import Category
from members.forms.user_data_form import PasswordChangingForm


# Widok zmiany hasła użytkownika
@login_required(login_url='home')
def user_change_password_view(request):
    category = Category.objects.all()
    blog = Blog.objects.all().filter(publiction_status=True).order_by('-date_posted')[1:]

    if request.method == 'POST':
        edit_password_form = PasswordChangingForm(user=request.user, data=request.POST)
        if edit_password_form.is_valid():
            user = edit_password_form.save()
            update_session_auth_hash(request, user)
            return redirect('edit_security_page')
    else:
        edit_password_form = PasswordChangingForm(user=request.user)

    context = {
        'category': category,
        'blog': blog,
        'edit_password_form': edit_password_form,
    }
    return render(
        request,
        'UserTemplates/UserAccount/EditPassword.html',
        context
    )
