from django.shortcuts import get_object_or_404
from django.shortcuts import render

from blog.decorators import superuser_required
from blog.forms.company_news_form import CompanyNewsCreationForm
from blog.forms.company_news_form import CompanyNewsDeleteForm
from blog.forms.company_news_form import UserCompanyNewsForm
from blog.models import CompanyNews
from blog.models import User as DjangoUser
from blog.views import edit_admin_panel_view
from blog.views import edit_entity_admin_panel_view
from blog.views import get_paginated_context
from blog.views import newsletter_add_panel_view
from blog.views import process_delete_admin_panel_view


# Widok dodawania newslettera od Banknoty (dla superusera)
@superuser_required
def company_news_add_view(request):
    return newsletter_add_panel_view(
        request,
        'company_news',
        CompanyNewsCreationForm,
        'AdminTemplates/Newsletter/CompanyNews/CompanyNewsAddAdmin.html',
        'AdminTemplates/Newsletter/CompanyNews/Mail/CompanyNewsMail',
        'Wiadomość od Banknoty'
    )


# Widok edycji newslettera od Banknoty (dla superusera)
@superuser_required
def company_news_admin_panel_view(request):
    company_news = CompanyNews.objects.all().order_by('title')

    context = get_paginated_context(request, company_news, 10)
    return render(
        request,
        'AdminTemplates/Newsletter/CompanyNews/CompanyNewsManageAdmin.html',
        context
    )


# Widok szczegółów newslettera od Banknoty (dla superusera)
@superuser_required
def company_news_detail_admin_panel_view(request, pk):
    company_news = get_object_or_404(CompanyNews, pk=pk)

    context = {
        'company_news': company_news,
    }
    return render(
        request,
        'AdminTemplates/Newsletter/CompanyNews/CompanyNewsDetailAdmin.html',
        context
    )


# Widok edycji newslettera od Banknoty (dla superusera)
@superuser_required
def company_news_edit_admin_panel_view(request, pk):
    return edit_admin_panel_view(
        request,
        pk,
        CompanyNews,
        'company_news',
        CompanyNewsCreationForm,
        'AdminTemplates/Newsletter/CompanyNews/CompanyNewsEditAdmin.html',
        'AdminTemplates/Newsletter/CompanyNews/Mail/CompanyNewsMail',
        'Wiadomość od banknoty'
    )


# Widok usuwania newslettera od Banknoty (dla superusera)
@superuser_required
def company_news_delete_admin_panel_view(request, pk):
    return process_delete_admin_panel_view(
        request,
        pk,
        CompanyNews,
        CompanyNewsDeleteForm,
        'AdminTemplates/Newsletter/CompanyNews/CompanyNewsDeleteAdmin.html',
        'Mail z wiadomością od Banknoty został usunięty',
        'company_news_admin_panel'
    )


# Widok zarządzania użytkownikami w kontekście newslettera od Banknoty (dla superusera)
@superuser_required
def company_news_user_manage_admin_panel_view(request):
    users = DjangoUser.objects.all().order_by('user__id')

    context = get_paginated_context(request, users, 10)
    return render(
        request,
        'AdminTemplates/Newsletter/CompanyNews/CompanyNewsUserManageAdmin.html',
        context
    )


# Widok szczegółów użytkownika w kontekście newslettera od Banknoty (dla superusera)
@superuser_required
def company_news_user_detail_admin_panel_view(request, pk):
    user = get_object_or_404(DjangoUser, pk=pk)

    context = {
        'users': user,
    }
    return render(
        request,
        'AdminTemplates/Newsletter/CompanyNews/CompanyNewsUserDetailAdmin.html',
        context
    )


# Widok edycji ustawień e-maila z wiadomością od Banknoty dla konkretnego użytkownika (dla superusera)
@superuser_required
def company_news_user_edit_admin_panel_view(request, pk):
    user = get_object_or_404(DjangoUser, id=pk)

    extra_context = {
        'users': user,
    }
    return edit_entity_admin_panel_view(
        request,
        pk,
        DjangoUser,
        UserCompanyNewsForm,
        'AdminTemplates/Newsletter/CompanyNews/CompanyNewsUserEditAdmin.html',
        'Ustawienia e-maila z wiadomością od Banknoty zostały zaktualizowane.',
        'company_news_user_manage_admin_panel',
        extra_context
    )
