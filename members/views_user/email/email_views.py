from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.mail import send_mail
from django.shortcuts import render, redirect
from django.template.loader import render_to_string

from blog.models import Blog
from blog.models import Category
from members.forms.user_data_form import EmailChangeForm
from pm_blog import settings


# Widok zmiany e-maila użytkownika
@login_required(login_url='home')
def user_change_email_view(request):
    category = Category.objects.all()
    blog = Blog.objects.all().filter(publiction_status=True).order_by('-date_posted')[1:]

    if request.method == 'POST':
        form = EmailChangeForm(user=request.user, data=request.POST)
        if form.is_valid():
            new_email = form.cleaned_data['new_email1']
            form.save()
            messages.success(
                request,
                'Dziękujemy za rejestrację do biuletynu.',
                "alert alert-success alert-dismissible fade show"
            )
            subject = 'Zmiana adresu e-mail'
            from_email = settings.EMAIL_HOST_USER
            to_email = [new_email]
            msg_plain = render_to_string(
                'UserTemplates/UserAccount/EditEmailConfirmation.txt',
                {
                    'mail': new_email
                }
            )
            msg_html = render_to_string(
                'UserTemplates/UserAccount/EditEmailConfirmation.html',
                {
                    'mail': new_email,
                    'image_url': 'http://127.0.0.1:8000/static/images/logo-no-background.png'
                }
            )
            send_mail(
                subject,
                msg_plain,
                from_email,
                to_email,
                html_message=msg_html,
                fail_silently=False
            )
            return redirect('edit_security_page')
    else:
        form = EmailChangeForm(user=request.user)

    context = {
        'category': category,
        'blog': blog,
        'edit_email_form': form,
    }
    return render(
        request,
        "UserTemplates/UserAccount/EditEmail.html",
        context
    )
