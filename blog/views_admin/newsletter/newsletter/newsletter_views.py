from django.contrib import messages
from django.shortcuts import get_object_or_404
from django.shortcuts import redirect
from django.shortcuts import render

from blog.decorators import superuser_required
from blog.forms.newsletter_form import NewsletterAddUserForm
from blog.forms.newsletter_form import NewsletterCreationForm
from blog.forms.newsletter_form import NewsletterDeleteForm
from blog.forms.newsletter_form import NewsletterUserDeleteForm
from blog.models import Newsletter
from blog.models import NewsletterUser
from blog.views import INVALID_EMAIL_MESSAGE
from blog.views import PUBLISHED_SUCCESS_MESSAGE
from blog.views import SUCCESS_DELETE_MESSAGE
from blog.views import SUCCESS_MESSAGE_CREATE
from blog.views import UNSUBSCRIBE_SUCCESS_MESSAGE
from blog.views import USER_SUCCESS_DELETE_MESSAGE
from blog.views import delete_newsletter_user
from blog.views import get_paginated_context
from blog.views import process_delete
from blog.views import process_delete_admin_panel_view
from blog.views import process_newsletter_signup
from blog.views import send_newsletter_emails
from blog.views import send_unsubscribe_mail


# Widok tworzenia biuletynu (dla superusera)
@superuser_required
def newsletter_creation_view(request):
    form = NewsletterCreationForm(request.POST or None)
    if form.is_valid():
        instance = form.save()
        newsletter = Newsletter.objects.get(id=instance.id)
        if newsletter.status_field == "Published":
            send_newsletter_emails(newsletter)
            messages.success(
                request,
                f'{SUCCESS_MESSAGE_CREATE} i wysłany',
                "alert alert-success alert-dismissible fade show mt-3"
            )
        else:
            messages.success(
                request,
                SUCCESS_MESSAGE_CREATE,
                "alert alert-success alert-dismissible fade show mt-3")
        return redirect('newsletter_creation')

    context = {
        'form': form,
    }
    return render(
        request,
        'AdminTemplates/Newsletter/Newsletter/NewsletterAddAdmin.html',
        context
    )


# Widok dodawania użytkownika do biuletynu (dla superusera)
@superuser_required
def newsletter_add_user_view(request):
    return process_newsletter_signup(
        request,
        NewsletterAddUserForm,
        'AdminTemplates/Newsletter/Newsletter/NewsletterSingUpAdmin.html',
    )


# Widok usuwania użytkownika z biuletynu (dla superusera)
@superuser_required
def newsletter_remove_user_view(request):
    form = NewsletterAddUserForm(request.POST or None)
    if form.is_valid():
        instance = form.save(commit=False)
        email = instance.email
        if delete_newsletter_user(email):
            send_unsubscribe_mail(email)
            messages.success(
                request,
                UNSUBSCRIBE_SUCCESS_MESSAGE,
                "alert alert-success alert-dismissible fade show mt-3"
            )
        else:
            messages.warning(
                request,
                INVALID_EMAIL_MESSAGE,
                "alert alert-danger alert-dismissible fade show mt-3"
            )

    context = {
        'form': form
    }
    return render(
        request,
        'AdminTemplates/Newsletter/Newsletter/NewsletterUnsubscribeAdmin.html',
        context
    )


# Widok zarządzania biuletynami (dla superusera)
@superuser_required
def newsletter_manage_admin_panel_view(request):
    newsletter = Newsletter.objects.all()

    context = get_paginated_context(request, newsletter, 10)
    return render(
        request,
        'AdminTemplates/Newsletter/Newsletter/NewsletterManageAdmin.html',
        context
    )


# Widok szczegółów biuletynu (dla superusera)
@superuser_required
def newsletter_detail_admin_panel_view(request, pk):
    newsletter = get_object_or_404(Newsletter, pk=pk)

    context = {
        'newsletter': newsletter,
    }
    return render(
        request,
        'AdminTemplates/Newsletter/Newsletter/NewsletterDetaliAdmin.html',
        context
    )


# Widok edycji biuletynu (dla superusera)
@superuser_required
def newsletter_edit_admin_panel_view(request, pk):
    newsletter = get_object_or_404(Newsletter, pk=pk)
    if request.method == "POST":
        form = NewsletterCreationForm(request.POST, instance=newsletter)
        if form.is_valid():
            newsletter = form.save()
            if newsletter.status_field == "Published":
                send_newsletter_emails(newsletter)
                messages.success(
                    request,
                    PUBLISHED_SUCCESS_MESSAGE,
                    "alert alert-success alert-dismissible fade show mt-3"
                )
            messages.success(
                request,
                'Biuletyn został edytowany',
                "alert alert-success alert-dismissible fade show mt-3"
            )
            return redirect('newsletter_admin_panel')
    else:
        form = NewsletterCreationForm(instance=newsletter)

    context = {
        'form': form
    }
    return render(
        request,
        'AdminTemplates/Newsletter/Newsletter/NewsletterEditAdmin.html',
        context
    )


# Widok usuwania biuletynu (dla superusera)
@superuser_required
def newsletter_delete_admin_panel_view(request, pk):
    return process_delete(
        request,
        pk, Newsletter,
        NewsletterDeleteForm,
        'AdminTemplates/Newsletter/Newsletter/NewsletterDeleteAdmin.html',
        SUCCESS_DELETE_MESSAGE,
        'newsletter_admin_panel'
    )


# Widok zarządzania użytkownikami newslettera (dla superusera)
@superuser_required
def newsletter_user_manage_admin_panel_view(request):
    newsletter = NewsletterUser.objects.all()

    context = get_paginated_context(request, newsletter, 10)
    return render(
        request,
        'AdminTemplates/Newsletter/Newsletter/NewsletterUserManageAdmin.html',
        context
    )


# Widok szczegółów użytkownika newslettera (dla superusera)
@superuser_required
def newsletter_user_detail_admin_panel_view(request, pk):
    newsletter = get_object_or_404(NewsletterUser, pk=pk)

    context = {
        'newsletter': newsletter,
    }
    return render(
        request,
        'AdminTemplates/Newsletter/Newsletter/NewsletterUserDetailAdmin.html',
        context
    )


# Widok usuwania użytkownika newslettera (dla superusera)
@superuser_required
def newsletter_user_delete_admin_panel_view(request, pk):
    return process_delete_admin_panel_view(
        request,
        pk,
        NewsletterUser,
        NewsletterUserDeleteForm,
        'AdminTemplates/Newsletter/Newsletter/NewsletterUserDeleteAdmin.html',
        USER_SUCCESS_DELETE_MESSAGE,
        'newsletter_user_admin_panel'
    )
