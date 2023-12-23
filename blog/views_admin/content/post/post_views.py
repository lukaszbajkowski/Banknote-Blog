from django.shortcuts import get_object_or_404
from django.shortcuts import render

from blog.decorators import superuser_required
from blog.forms.post_form import PostCreateForm
from blog.forms.post_form import PostDeleteForm
from blog.models import Blog
from blog.views import edit_entity_admin_panel_view
from blog.views import get_paginated_context
from blog.views import process_delete_admin_panel_view
from blog.views import process_form_submission


# Widok dodawania posta (dla superusera)
@superuser_required
def post_add_view(request):
    return process_form_submission(
        request,
        PostCreateForm,
        'AdminTemplates/Content/Post/PostAddAdmin.html',
        'post_add',
        'Post został dodany'
    )


# Widok zarządzania postami (dla superusera)
@superuser_required
def post_manage_admin_panel_view(request):
    post = Blog.objects.all().order_by('title')

    context = get_paginated_context(request, post, 10)
    return render(
        request,
        'AdminTemplates/Content/Post/PostManageAdmin.html',
        context
    )


# Widok szczegółów posta (dla superusera)
@superuser_required
def post_detail_admin_panel_view(request, pk):
    post = get_object_or_404(Blog, pk=pk)
    comments = post.comment_set.all().order_by('date_posted')

    context = {
        'post': post,
        'comments': comments,
    }
    return render(
        request,
        'AdminTemplates/Content/Post/PostDetailAdmin.html',
        context
    )


# Widok edycji posta (dla superusera)
@superuser_required
def post_edit_admin_panel_view(request, pk):
    return edit_entity_admin_panel_view(
        request,
        pk,
        Blog,
        PostCreateForm,
        'AdminTemplates/Content/Post/PostEditAdmin.html',
        'Post został edytowany',
        'post_admin_panel',
    )


# Widok usuwania posta (dla superusera)
@superuser_required
def post_delete_admin_panel_view(request, pk):
    return process_delete_admin_panel_view(
        request,
        pk,
        Blog,
        PostDeleteForm,
        'AdminTemplates/Content/Post/PostDeleteAdmin.html',
        'Post został usunięty',
        'post_admin_panel'
    )


# Widok publikacji posta (dla superusera)
@superuser_required
def post_publication_admin_panel_view(request):
    if request.method == 'POST':
        blog_id = request.POST.get('blog_id')
        publiction_status = request.POST.get('publiction_status')
        blog = Blog.objects.get(pk=blog_id)
        blog.publiction_status = (publiction_status == 'approve')
        blog.save()

    post = Blog.objects.all().order_by('title')

    context = get_paginated_context(request, post, 10)
    return render(
        request,
        'AdminTemplates/Content/Post/PostPublicationAdmin.html',
        context
    )
