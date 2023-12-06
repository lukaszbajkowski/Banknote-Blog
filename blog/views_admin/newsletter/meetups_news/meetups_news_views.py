from django.shortcuts import get_object_or_404
from django.shortcuts import render

from blog.decorators import superuser_required
from blog.form import Meetups_newsCreationForm
from blog.form import UserMeetups_newsForm
from blog.models import Meetups_news
from blog.models import User as DjangoUser
from blog.views import edit_admin_panel_view
from blog.views import edit_entity_admin_panel_view
from blog.views import get_paginated_context
from blog.views import newsletter_add_panel_view
from blog.views import process_delete_admin_panel_view


# Widok dodawania newslettera spotkań i wydarzeń (dla superusera)
@superuser_required
def meetups_news_add_view(request):
    return newsletter_add_panel_view(
        request,
        'meetups_news',
        Meetups_newsCreationForm,
        'AdminTemplates/Newsletter/MeetupsNews/MeetupsNewsAddAdmin.html',
        'AdminTemplates/Newsletter/MeetupsNews/Mail/MeetupsNewsMail',
        'Nadchodzące spotkania i wydarzenia'
    )


# Widok zarządzania newsletterami spotkań i wydarzeń (dla superusera)
@superuser_required
def meetups_news_manage_admin_panel_view(request):
    meetups_news = Meetups_news.objects.all().order_by('title')

    context = get_paginated_context(request, meetups_news, 10)
    return render(
        request,
        'AdminTemplates/Newsletter/MeetupsNews/MeetupsNewsManageAdmin.html',
        context
    )


# Widok szczegółów newslettera spotkań i wydarzeń (dla superusera)
@superuser_required
def meetups_news_detail_admin_panel_view(request, pk):
    meetups_news = get_object_or_404(Meetups_news, pk=pk)

    context = {
        'meetups_news': meetups_news,
    }
    return render(
        request,
        'AdminTemplates/Newsletter/MeetupsNews/MeetupsNewsDetailAdmin.html',
        context
    )


# Widok edycji newslettera spotkań i wydarzeń (dla superusera)
@superuser_required
def meetups_news_edit_admin_panel_view(request, pk):
    return edit_admin_panel_view(
        request,
        pk,
        Meetups_news,
        'meetups_news',
        Meetups_newsCreationForm,
        'AdminTemplates/Newsletter/MeetupsNews/MeetupsNewsEditAdmin.html',
        'AdminTemplates/Newsletter/MeetupsNews/Mail/MeetupsNewsMail',
        'Nadchodzące spotkania i wydarzenia'
    )


# Widok usuwania newslettera spotkań i wydarzeń (dla superusera)
@superuser_required
def meetups_news_delete_admin_panel_view(request, pk):
    return process_delete_admin_panel_view(
        request,
        pk,
        Meetups_news,
        Meetups_newsCreationForm,
        'AdminTemplates/Newsletter/MeetupsNews/MeetupsNewsDeleteAdmin.html',
        'Mail o spotkaniach i wydarzeniach został usunięty',
        'meetups_news_admin_panel'
    )


# Widok zarządzania użytkownikami w kontekście newslettera spotkań i wydarzeń (dla superusera)
@superuser_required
def meetups_news_user_manage_admin_panel_view(request):
    users = DjangoUser.objects.all().order_by('user__id')

    context = get_paginated_context(request, users, 10)
    return render(
        request,
        'AdminTemplates/Newsletter/MeetupsNews/MeetupsNewsUserManageAdmin.html',
        context
    )


# Widok szczegółów użytkownika w kontekście newslettera spotkań i wydarzeń (dla superusera)
@superuser_required
def meetups_news_user_detail_admin_panel_view(request, pk):
    user = get_object_or_404(DjangoUser, pk=pk)

    context = {
        'users': user,
    }
    return render(
        request,
        'AdminTemplates/Newsletter/MeetupsNews/MeetupsNewsUserDetailAdmin.html',
        context
    )


# Widok edycji ustawień użytkownika w kontekście newslettera spotkań i wydarzeń (dla superusera)
@superuser_required
def meetups_news_user_edit_admin_panel_view(request, pk):
    user = get_object_or_404(DjangoUser, id=pk)

    extra_context = {
        'users': user,
    }
    return edit_entity_admin_panel_view(
        request,
        pk,
        DjangoUser,
        UserMeetups_newsForm,
        'AdminTemplates/Newsletter/MeetupsNews/MeetupsNewsUserEditAdmin.html',
        'Ustawienia e-maila o spotkaniach i wydarzeniach zostały zaaktualizowane.',
        'meetups_news_user_admin_panel',
        extra_context
    )
