# Widok dodawania konta aplikacji społecznej (dla superusera)
from allauth.socialaccount.models import SocialAccount
from django.shortcuts import get_object_or_404
from django.shortcuts import render

from blog.decorators import superuser_required
from blog.form import SocialAccountDeleteEmailForm
from blog.form import SocialAccountForm
from blog.views import edit_entity_admin_panel_view
from blog.views import get_paginated_context
from blog.views import process_delete_admin_panel_view
from blog.views import process_form_submission


@superuser_required
def social_account_add_view(request):
    return process_form_submission(
        request,
        SocialAccountForm,
        'AdminTemplates/SocialmediaAccounts/SocialAccount/SocialAccountAddAdmin.html',
        'social_account_add',
        'Konto aplikacji społecznościowej zostało dodane.'
    )


# Widok zarządzania kontami aplikacji społecznej (dla superusera)
@superuser_required
def social_account_admin_panel_view(request):
    social_accounts = SocialAccount.objects.all().order_by('id')

    context = get_paginated_context(request, social_accounts, 10)
    return render(
        request,
        'AdminTemplates/SocialmediaAccounts/SocialAccount/SocialAccountManageAdmin.html',
        context
    )


# Widok szczegółów konta aplikacji społecznej (dla superusera)
@superuser_required
def social_account_detail_admin_panel_view(request, pk):
    social_accounts = get_object_or_404(SocialAccount, pk=pk)

    context = {
        'social_account': social_accounts,
    }
    return render(
        request,
        'AdminTemplates/SocialmediaAccounts/SocialAccount/SocialAccountDetailAdmin.html',
        context
    )


# Widok edycji konta aplikacji społecznej (dla superusera)
@superuser_required
def social_account_edit_admin_panel_view(request, pk):
    social_accounts = get_object_or_404(SocialAccount, pk=pk)

    extra_context = {
        'social_account': social_accounts,
    }
    return edit_entity_admin_panel_view(
        request,
        pk,
        SocialAccount,
        SocialAccountForm,
        'AdminTemplates / SocialmediaAccounts / SocialAccount / SocialAccountEditAdmin.html',
        'Konto aplikacji społecznościowej zostało edytowane.',
        'social_account_admin_panel',
        extra_context
    )


# Widok usuwania konta aplikacji społecznej (dla superusera)
@superuser_required
def social_account_delete_admin_panel_view(request, pk):
    return process_delete_admin_panel_view(
        request,
        pk,
        SocialAccount,
        SocialAccountDeleteEmailForm,
        'AdminTemplates/SocialmediaAccounts/SocialAccount/SocialAccountDeleteAdmin.html',
        'Konto aplikacji społecznościowej zostało usunięte',
        'social_account_admin_panel'
    )
