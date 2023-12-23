from django.core.paginator import Paginator
from django.db.models import Count
from django.shortcuts import render, get_object_or_404

from blog.decorators import superuser_required
from blog.forms.comment_form import CommentCreateForm
from blog.forms.comment_form import CommentDeleteForm
from blog.models import Blog
from blog.models import Comment
from blog.models import User
from blog.views import edit_entity_admin_panel_view
from blog.views import get_paginated_context
from blog.views import process_delete_admin_panel_view
from blog.views import process_form_submission


# Widok dodawania komentarza (dla superusera)
@superuser_required
def comment_add_view(request):
    return process_form_submission(
        request,
        CommentCreateForm,
        'AdminTemplates/Content/Comment/CommentAdd.html',
        'comment_add',
        'Komentarz został dodany'
    )


# Widok zarządzania komentarzami (dla superusera)
@superuser_required
def comment_manage_admin_panel_view(request):
    comment = Comment.objects.all().order_by('-date_posted')

    context = get_paginated_context(request, comment, 10)
    return render(
        request,
        'AdminTemplates/Content/Comment/CommentMangeAdmin.html',
        context
    )


# Widok szczegółów komentarza (dla superusera)
@superuser_required
def comment_detail_admin_panel_view(request, pk):
    comment = get_object_or_404(Comment, pk=pk)

    context = {
        'comment': comment,
    }
    return render(
        request,
        'AdminTemplates/Content/Comment/CommentDetailAdmin.html',
        context
    )


# Widok edycji komentarza (dla superusera)
@superuser_required
def comment_edit_admin_panel_view(request, pk):
    return edit_entity_admin_panel_view(
        request,
        pk,
        Comment,
        CommentCreateForm,
        'AdminTemplates/Content/Comment/CommentEditAdmin.html',
        'Komentarz został edytowany',
        'comment_admin_panel',
    )


# Widok usuwania komentarza (dla superusera)
@superuser_required
def comment_delete_admin_panel_view(request, pk):
    return process_delete_admin_panel_view(
        request,
        pk,
        Comment,
        CommentDeleteForm,
        'AdminTemplates/Content/Comment/CommentDeleteAdmin.html',
        'Komentarz został usunięty',
        'comment_admin_panel'
    )


# Widok komentarzy w ramach posta (dla superusera)
@superuser_required
def comment_in_post_admin_panel_view(request):
    post = Blog.objects.all().order_by('title')

    context = get_paginated_context(request, post, 10)
    return render(
        request,
        'AdminTemplates/Content/Comment/CommentInPostManageAdmin.html',
        context
    )


# Widok szczegółów komentarzy w ramach posta (dla superusera)
@superuser_required
def comment_in_post_detail_admin_panel_view(request, pk):
    posts = get_object_or_404(Blog, pk=pk)
    comments = posts.comment_set.all().order_by('-date_posted')

    context = {
        'posts': posts,
        'comments': comments,
    }
    return render(
        request,
        'AdminTemplates/Content/Comment/CommentInPostDetailAdmin.html',
        context
    )


# Widok użytkowników wraz z liczbą ich komentarzy (dla superusera)
@superuser_required
def comment_users_admin_panel_view(request):
    users = User.objects.annotate(comment_count=Count('comment'))
    paginator = Paginator(users, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'page_obj': page_obj
    }
    return render(
        request,
        'AdminTemplates/Content/Comment/CommentUserManageAdmin.html',
        context
    )


# Widok szczegółów użytkownika wraz z komentarzami (dla superusera)
@superuser_required
def comment_users_detail_admin_panel_view(request, pk):
    user = get_object_or_404(User, id=pk)
    comments = Comment.objects.filter(author=user).order_by('-date_posted')

    context = {
        'users': user,
        'comments': comments
    }
    return render(
        request,
        'AdminTemplates/Content/Comment/CommentUserDetailAdmin.html',
        context
    )
