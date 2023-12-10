from django.core.mail import send_mail
from django.shortcuts import render, get_object_or_404
from django.template.loader import render_to_string

from blog.decorators import superuser_required
from blog.form import UserMissNewsForm
from blog.models import Blog
from blog.models import User as DjangoUser
from blog.views import IMAGE_URL
from blog.views import edit_entity_admin_panel_view
from blog.views import get_paginated_context
from pm_blog import settings


# Widok wysyłania maili z przypomnieniem o nieprzeczytanych postach (dla superusera)
@superuser_required
def send_emails_view(request):
    if request.method == 'POST':
        users_with_missed_news = DjangoUser.objects.filter(miss_news=True)

        from_email = settings.EMAIL_HOST_USER
        skipped_posts_template = 'AdminTemplates/Newsletter/SkippedPosts/Mail/SkippedPostMail.txt'
        skipped_posts_html_template = 'AdminTemplates/Newsletter/SkippedPosts/Mail/SkippedPostMail.html'

        for user in users_with_missed_news:
            unopened_posts = Blog.objects.filter(publiction_status=True).exclude(id__in=user.opened_posts.all())

            if unopened_posts:
                msg_plain = render_to_string(
                    skipped_posts_template,
                    {
                        'mail': user.user.email,
                        'post_list': unopened_posts
                    }
                )
                msg_html = render_to_string(
                    skipped_posts_html_template,
                    {
                        'mail': user.user.email,
                        'post_list': unopened_posts,
                        'image_url': IMAGE_URL
                    }
                )
                send_mail(
                    'Nieprzeczytane posty',
                    msg_plain,
                    from_email,
                    [user.user.email],
                    fail_silently=False,
                    html_message=msg_html
                )

        return render(
            request,
            'AdminTemplates/Newsletter/SkippedPosts/SkippedPostsSendEmails.html'
        )

    return render(
        request,
        'AdminTemplates/Newsletter/SkippedPosts/SkippedPostsConfirmation.html'
    )


# Widok zarządzania pominiętymi postami (dla superusera)
@superuser_required
def skipped_posts_admin_panel(request):
    users = DjangoUser.objects.all().order_by('user__id')

    users_with_unopened_posts = []
    for user in users:
        unopened_posts_count = Blog.objects.filter(publiction_status=True).exclude(
            id__in=user.opened_posts.all()).count()
        user.unopened_posts_count = unopened_posts_count
        users_with_unopened_posts.append(user)

    context = get_paginated_context(request, users_with_unopened_posts, 10)
    return render(
        request,
        'AdminTemplates/Newsletter/SkippedPosts/SkippedPostsManageAdmin.html',
        context
    )


# Widok szczegółów pominiętych postów dla konkretnego użytkownika (dla superusera)
@superuser_required
def skipped_posts_detail_admin_panel(request, pk):
    user = get_object_or_404(DjangoUser, pk=pk)
    posts = Blog.objects.filter(publiction_status=True).exclude(id__in=user.opened_posts.all())

    context = {
        'posts': posts,
        'users': user
    }
    return render(
        request,
        'AdminTemplates/Newsletter/SkippedPosts/SkippedPostsDetailAdmin.html',
        context
    )


# Widok zarządzania użytkownikami w kontekście pominiętych postów (dla superusera)
@superuser_required
def skipped_posts_user_admin_panel(request):
    users = DjangoUser.objects.all().order_by('user__id')

    context = {
        'users': users,
    }
    return render(
        request,
        'AdminTemplates/Newsletter/SkippedPosts/SkippedPostsUserManageAdmin.html',
        context
    )


# Widok edycji ustawień pominiętych postów dla konkretnego użytkownika (dla superusera)
@superuser_required
def skipped_posts_user_edit_admin_panel(request, pk):
    user = get_object_or_404(DjangoUser, id=pk)

    extra_context = {
        'users': user,
    }
    return edit_entity_admin_panel_view(
        request,
        pk,
        DjangoUser,
        UserMissNewsForm,
        'AdminTemplates/Newsletter/SkippedPosts/SkippedPostsUserEditAdmin.html',
        'Ustawienia pominiętych artykułów zostały zaktualizowane.',
        'skipped_posts_user_admin_panel',
        extra_context
    )
