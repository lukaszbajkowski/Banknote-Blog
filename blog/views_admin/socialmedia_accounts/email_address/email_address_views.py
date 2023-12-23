from allauth.account.models import EmailAddress
from django.shortcuts import get_object_or_404
from django.shortcuts import render

from blog.decorators import superuser_required
from blog.forms.socialapp_form import EmailAddressDeleteForm
from blog.forms.socialapp_form import EmailAddressForm
from blog.views import edit_entity_admin_panel_view
from blog.views import get_paginated_context
from blog.views import process_delete_admin_panel_view
from blog.views import process_form_submission


#  Widok dodawania adresu email (dla superusera)
@superuser_required
def email_address_add_view(request):
    return process_form_submission(
        request,
        EmailAddressForm,
        'AdminTemplates/SocialmediaAccounts/EmailAddress/EmailAddressAddAdmin.html',
        'email_address_add',
        'Adres email został dodany.'
    )


# Widok zarządzania adresem email (dla superusera)
@superuser_required
def email_address_admin_panel_view(request):
    email_addresses = EmailAddress.objects.all().order_by('id')

    context = get_paginated_context(request, email_addresses, 10)
    return render(
        request,
        'AdminTemplates/SocialmediaAccounts/EmailAddress/EmailAddressManageAdmin.html',
        context
    )


# Widok szczegółów adresu email (dla superusera)
@superuser_required
def email_address_detail_admin_panel_view(request, pk):
    email_addresses = get_object_or_404(EmailAddress, pk=pk)

    context = {
        'email_address': email_addresses,
    }
    return render(
        request,
        'AdminTemplates/SocialmediaAccounts/EmailAddress/EmailAddressDetailAdmin.html',
        context
    )


# Widok edycji adresu email (dla superusera)
@superuser_required
def email_address_edit_admin_panel_view(request, pk):
    email_addresses = get_object_or_404(EmailAddress, pk=pk)

    context = {
        'email_address': email_addresses,
    }
    return edit_entity_admin_panel_view(
        request,
        pk,
        EmailAddress,
        EmailAddressForm,
        'AdminTemplates/SocialmediaAccounts/EmailAddress/EmailAddressEditAdmin.html',
        'Adres email został edytowany.',
        'email_address_admin_panel',
        context
    )


# Widok usuwania adresu email (dla superusera)
@superuser_required
def email_address_delete_admin_panel_view(request, pk):
    return process_delete_admin_panel_view(
        request,
        pk,
        EmailAddress,
        EmailAddressDeleteForm,
        'AdminTemplates/SocialmediaAccounts/EmailAddress/EmailAddressDeleteAdmin.html',
        'Adres email został usunięty',
        'email_address_admin_panel'
    )
