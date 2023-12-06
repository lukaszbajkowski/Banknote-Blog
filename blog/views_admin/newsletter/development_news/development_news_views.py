from django.shortcuts import get_object_or_404
from django.shortcuts import render

from blog.decorators import superuser_required
from blog.form import DevelopmentNewsCreationForm
from blog.form import DevelopmentNewsDeleteEmailForm
from blog.form import UserDevelopmentNewsForm
from blog.models import DevelopmentNews
from blog.models import User as DjangoUser
from blog.views import edit_admin_panel_view
from blog.views import edit_entity_admin_panel_view
from blog.views import get_paginated_context
from blog.views import newsletter_add_panel_view
from blog.views import process_delete_admin_panel_view


# Widok dodawania newslettera z informacjami o rozwoju i zmianach na Banknoty (dla superusera)
@superuser_required
def development_news_add_view(request):
    return newsletter_add_panel_view(
        request,
        'development_news',
        DevelopmentNewsCreationForm,
        'AdminTemplates/Newsletter/DevelopmentNews/DevelopmentNewsAddAdmin.html',
        'AdminTemplates/Newsletter/DevelopmentNews/Mail/DevelopmentNewsMail',
        'z informacjami o rozwoju i zmianach na Banknoty'
    )


# Widok edycji newslettera z informacjami o rozwoju i zmianach na Banknoty (dla superusera)
@superuser_required
def development_news_admin_panel_view(request):
    development_news = DevelopmentNews.objects.all().order_by('title')

    context = get_paginated_context(request, development_news, 10)
    return render(
        request,
        'AdminTemplates/Newsletter/DevelopmentNews/DevelopmentNewsManageAdmin.html',
        context
    )


# Widok szczegółów newslettera z informacjami o rozwoju i zmianach na Banknoty (dla superusera)
@superuser_required
def development_news_detail_admin_panel_view(request, pk):
    development_news = get_object_or_404(DevelopmentNews, pk=pk)

    context = {
        'development_news': development_news,
    }
    return render(
        request,
        'AdminTemplates/Newsletter/DevelopmentNews/DevelopmentNewsDetailAdmin.html',
        context
    )


# Widok edycji newslettera z informacjami o rozwoju i zmianach na Banknoty (dla superusera)
@superuser_required
def development_news_edit_admin_panel_view(request, pk):
    return edit_admin_panel_view(
        request,
        pk,
        DevelopmentNews,
        'development_news',
        DevelopmentNewsCreationForm,
        'AdminTemplates/Newsletter/DevelopmentNews/DevelopmentNewsEditAdmin.html',
        'AdminTemplates/Newsletter/DevelopmentNews/Mail/DevelopmentNewsMail',
        'Mail z informacjami o rozwoju i zmianach na Banknoty'
    )


# Widok usuwania newslettera z informacjami o rozwoju i zmianach na Banknoty (dla superusera)
@superuser_required
def development_news_delete_admin_panel_view(request, pk):
    return process_delete_admin_panel_view(
        request,
        pk,
        DevelopmentNews,
        DevelopmentNewsDeleteEmailForm,
        'AdminTemplates/Newsletter/DevelopmentNews/DevelopmentNewsDeleteAdmin.html',
        'Mail z informacjami o rozwoju i zmianach na Banknoty został usunięty',
        'development_news_admin_panel'
    )


# Widok zarządzania użytkownikami w kontekście newslettera z informacjami o rozwoju i zmianach na Banknoty (dla
# superusera)
@superuser_required
def development_news_user_manage_admin_panel_view(request):
    users = DjangoUser.objects.all().order_by('user__id')

    context = get_paginated_context(request, users, 10)
    return render(
        request,
        'AdminTemplates/Newsletter/DevelopmentNews/DevelopmentNewsUserManageAdmin.html',
        context
    )


# Widok szczegółów użytkownika w kontekście newslettera z informacjami o rozwoju i zmianach na Banknoty (dla superusera)
@superuser_required
def development_news_user_detail_admin_panel_view(request, pk):
    user = get_object_or_404(DjangoUser, pk=pk)

    context = {
        'users': user,
    }
    return render(
        request,
        'AdminTemplates/Newsletter/DevelopmentNews/DevelopmentNewsUserDetailAdmin.html',
        context
    )


# Widok edycji ustawień e-maila z informacjami o rozwoju i zmianach na Banknoty dla konkretnego użytkownika (dla
# superusera)
@superuser_required
def development_news_user_edit_admin_panel_view(request, pk):
    user = get_object_or_404(DjangoUser, id=pk)

    extra_context = {
        'users': user,
    }
    return edit_entity_admin_panel_view(
        request,
        pk,
        DjangoUser,
        UserDevelopmentNewsForm,
        'AdminTemplates/Newsletter/DevelopmentNews/DevelopmentNewsUserEditAdmin.html',
        'Ustawienia e-maila z informacjami o rozwoju i zmianach na Banknoty zostały zaktualizowane.',
        'development_news_user_manage_admin_panel',
        extra_context
    )
