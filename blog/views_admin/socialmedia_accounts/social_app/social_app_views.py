from allauth.socialaccount.models import SocialApp
from django.shortcuts import get_object_or_404
from django.shortcuts import render

from blog.decorators import superuser_required
from blog.form import SocialAppDeleteEmailForm
from blog.form import SocialAppForm
from blog.views import edit_entity_admin_panel_view
from blog.views import get_paginated_context
from blog.views import process_delete_admin_panel_view
from blog.views import process_form_submission


# Widok dodawania aplikacji społecznej (dla superusera)
@superuser_required
def social_app_add_view(request):
    return process_form_submission(
        request,
        SocialAppForm,
        'AdminTemplates/SocialmediaAccounts/SocialApp/SocialAppAddAdmin.html',
        'social_app_add',
        'Aplikacja społeczna została dodana.'
    )


# Widok zarządzania aplikacjami społecznymi (dla superusera)
@superuser_required
def social_app_admin_panel_view(request):
    social_apps = SocialApp.objects.all().order_by('id')

    context = get_paginated_context(request, social_apps, 10)
    return render(
        request,
        'AdminTemplates/SocialmediaAccounts/SocialApp/SocialAppManageAdmin.html',
        context
    )


# Widok szczegółów aplikacji społecznej (dla superusera)
@superuser_required
def social_app_detail_admin_panel_view(request, pk):
    social_apps = get_object_or_404(SocialApp, pk=pk)

    context = {
        'social_app': social_apps,
    }
    return render(
        request,
        'AdminTemplates/SocialmediaAccounts/SocialApp/SocialAppDetailAdmin.html',
        context
    )


# Widok edycji aplikacji społecznej (dla superusera)
@superuser_required
def social_app_edit_admin_panel_view(request, pk):
    social_apps = get_object_or_404(SocialApp, pk=pk)

    extra_context = {
        'social_app': social_apps,
    }
    return edit_entity_admin_panel_view(
        request,
        pk,
        SocialApp,
        SocialAppForm,
        'AdminTemplates/SocialmediaAccounts/SocialApp/SocialAppEditAdmin.html',
        'Aplikacja społeczna została edytowana.',
        'social_app_admin_panel',
        extra_context
    )


# Widok usuwania aplikacji społecznej (dla superusera)
@superuser_required
def social_app_delete_admin_panel_view(request, pk):
    return process_delete_admin_panel_view(
        request,
        pk,
        SocialApp,
        SocialAppDeleteEmailForm,
        'AdminTemplates/SocialmediaAccounts/SocialApp/SocialAppDeleteAdmin.html',
        'Aplikacja społeczna została usunięta',
        'social_app_admin_panel'
    )
