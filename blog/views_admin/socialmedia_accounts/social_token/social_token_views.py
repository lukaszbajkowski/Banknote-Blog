from allauth.socialaccount.models import SocialToken
from django.shortcuts import get_object_or_404
from django.shortcuts import render

from blog.decorators import superuser_required
from blog.form import SocialTokenDeleteEmailForm
from blog.form import SocialTokenForm
from blog.views import edit_entity_admin_panel_view
from blog.views import get_paginated_context
from blog.views import process_delete_admin_panel_view
from blog.views import process_form_submission


# Widok dodawania tokena aplikacji społecznej (dla superusera)
@superuser_required
def social_token_add_view(request):
    return process_form_submission(
        request,
        SocialTokenForm,
        'AdminTemplates/SocialmediaAccounts/SocialToken/SocialTokenAddAdmin.html',
        'social_token_add',
        'Token aplikacji społecznościowej został dodany.'
    )


# Widok zarządzania tokenami aplikacji społecznej (dla superusera)
@superuser_required
def social_token_admin_panel_view(request):
    social_tokens = SocialToken.objects.all().order_by('id')

    context = get_paginated_context(request, social_tokens, 10)
    return render(
        request,
        'AdminTemplates/SocialmediaAccounts/SocialToken/SocialTokenManageAdmin.html',
        context
    )


# Widok szczegółów tokena aplikacji społecznej (dla superusera)
@superuser_required
def social_token_detail_admin_panel_view(request, pk):
    social_tokens = get_object_or_404(SocialToken, pk=pk)

    context = {
        'social_token': social_tokens,
    }
    return render(
        request,
        'AdminTemplates/SocialmediaAccounts/SocialToken/SocialTokenDetailAdmin.html',
        context
    )


# Widok edycji tokena aplikacji społecznej (dla superusera)
@superuser_required
def social_token_edit_admin_panel_view(request, pk):
    social_tokens = get_object_or_404(SocialToken, pk=pk)

    extra_context = {
        'social_token': social_tokens,
    }
    return edit_entity_admin_panel_view(
        request,
        pk,
        SocialToken,
        SocialTokenForm,
        'AdminTemplates/SocialmediaAccounts/SocialToken/SocialTokenEditAdmin.html',
        'Token aplikacji społecznościowej został edytowany.',
        'social_token_admin_panel',
        extra_context
    )


# Widok usuwania tokena aplikacji społecznej (dla superusera)
@superuser_required
def social_token_delete_admin_panel_view(request, pk):
    return process_delete_admin_panel_view(
        request,
        pk,
        SocialToken,
        SocialTokenDeleteEmailForm,
        'AdminTemplates/SocialmediaAccounts/SocialToken/SocialTokenDeleteAdmin.html',
        'Token aplikacji społecznościowej został usunięty',
        'social_token_admin_panel'
    )
