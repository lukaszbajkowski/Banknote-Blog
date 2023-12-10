from django.shortcuts import get_object_or_404
from django.shortcuts import render

from blog.decorators import superuser_required
from blog.form import ReplayNewsCreationForm
from blog.form import ReplayNewsDeleteEmailForm
from blog.form import UserReplayNewsForm
from blog.models import ReplayNews
from blog.models import User as DjangoUser
from blog.views import edit_admin_panel_view
from blog.views import edit_entity_admin_panel_view
from blog.views import get_paginated_context
from blog.views import newsletter_add_panel_view
from blog.views import process_delete_admin_panel_view


# Widok dodawania newslettera z shotem od Banknoty (dla superusera)
@superuser_required
def replay_news_add_view(request):
    return newsletter_add_panel_view(
        request,
        'replay_news',
        ReplayNewsCreationForm,
        'AdminTemplates/Newsletter/ReplayNews/ReplayNewsAddAdmin.html',
        'AdminTemplates/Newsletter/ReplayNews/Mail/ReplayNewsMail',
        'z shotem od Banknoty'
    )


# Widok edycji newslettera z shotem od Banknoty (dla superusera)
@superuser_required
def replay_news_admin_panel_view(request):
    replay_news = ReplayNews.objects.all().order_by('title')

    context = get_paginated_context(request, replay_news, 10)
    return render(
        request,
        'AdminTemplates/Newsletter/ReplayNews/ReplayNewsManageAdmin.html',
        context
    )


# Widok szczegółów newslettera z shotem od Banknoty (dla superusera)
@superuser_required
def replay_news_detail_admin_panel_view(request, pk):
    replay_news = get_object_or_404(ReplayNews, pk=pk)

    context = {
        'replay_news': replay_news,
    }
    return render(
        request,
        'AdminTemplates/Newsletter/ReplayNews/ReplayNewsDetailAdmin.html',
        context
    )


# Widok edycji newslettera z shotem od Banknoty (dla superusera)
@superuser_required
def replay_news_edit_admin_panel_view(request, pk):
    return edit_admin_panel_view(
        request,
        pk,
        ReplayNews,
        'replay_news',
        ReplayNewsCreationForm,
        'AdminTemplates/Newsletter/ReplayNews/ReplayNewsEditAdmin.html',
        'AdminTemplates/Newsletter/ReplayNews/Mail/ReplayNewsMail',
        'z shotem od Banknoty'
    )


# Widok usuwania newslettera z shotem od Banknoty (dla superusera)
@superuser_required
def replay_news_delete_admin_panel_view(request, pk):
    return process_delete_admin_panel_view(
        request,
        pk,
        ReplayNews,
        ReplayNewsDeleteEmailForm,
        'AdminTemplates/Newsletter/ReplayNews/ReplayNewsDeleteAdmin.html',
        'Mail z shotem od Banknoty został usunięty',
        'replay_news_admin_panel'
    )


# Widok zarządzania użytkownikami w kontekście newslettera z shotem od Banknoty (dla superusera)
@superuser_required
def replay_news_user_manage_admin_panel_view(request):
    users = DjangoUser.objects.all().order_by('user__id')

    context = get_paginated_context(request, users, 10)
    return render(
        request,
        'AdminTemplates/Newsletter/ReplayNews/ReplayNewsUserManageAdmin.html',
        context
    )


# Widok szczegółów użytkownika w kontekście newslettera z shotem od Bankonty (dla superusera)
@superuser_required
def replay_news_user_detail_admin_panel_view(request, pk):
    user = get_object_or_404(DjangoUser, pk=pk)

    context = {
        'users': user,
    }
    return render(
        request,
        'AdminTemplates/Newsletter/ReplayNews/ReplayNewsUserDetailAdmin.html',
        context
    )


# Widok edycji ustawień e-maila z shotem wiadomości od Banknoty dla konkretnego użytkownika (dla superusera)
@superuser_required
def replay_news_user_edit_admin_panel_view(request, pk):
    user = get_object_or_404(DjangoUser, id=pk)

    extra_context = {
        'users': user,
    }
    return edit_entity_admin_panel_view(
        request,
        pk,
        DjangoUser,
        UserReplayNewsForm,
        'AdminTemplates/Newsletter/ReplayNews/ReplayNewsUserEditAdmin.html',
        'Ustawienia e-maila z shotem wiadomości od Banknoty zostały zaaktualizowane.',
        'replay_news_user_manage_admin_panel',
        extra_context
    )
