from django.contrib import messages
from django.shortcuts import render

from blog.form import NewsletterUserSignUpForm
from blog.models import Blog
from blog.models import Category
from blog.views import INVALID_EMAIL_MESSAGE
from blog.views import UNSUBSCRIBE_SUCCESS_MESSAGE
from blog.views import delete_newsletter_user
from blog.views import process_newsletter_signup
from blog.views import send_unsubscribe_mail


# Widok rejestracji do biuletynu
def newsletter_signup_view(request):
    return process_newsletter_signup(
        request,
        NewsletterUserSignUpForm,
        'UserTemplates/NewsletterRegister/NewsletterSingUp.html',
    )


# Widok rezygnacji z biuletynu
def newsletter_unsubscribe_view(request):
    category = Category.objects.all()
    blog = Blog.objects.filter(publiction_status=True).order_by('-date_posted')[1:]
    form = NewsletterUserSignUpForm(request.POST or None)

    if form.is_valid():
        instance = form.save(commit=False)
        email = instance.email
        if delete_newsletter_user(email):
            send_unsubscribe_mail(email)
            messages.success(
                request,
                UNSUBSCRIBE_SUCCESS_MESSAGE,
                "alert alert-success alert-dismissible fade show"
            )
        else:
            messages.warning(
                request,
                INVALID_EMAIL_MESSAGE,
                "alert alert-danger alert-dismissible fade show"
            )

    context = {
        'form': form,
        'category': category,
        'blog': blog
    }
    return render(
        request,
        'UserTemplates/NewsletterDelete/NewsletterDelete.html',
        context
    )
