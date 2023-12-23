from django.shortcuts import get_object_or_404
from django.shortcuts import render

from blog.decorators import superuser_required
from blog.forms.author_form import AuthorCreateForm
from blog.forms.author_form import AuthorDeleteForm
from blog.forms.author_form import AuthorEditForm
from blog.models import Author
from blog.views import edit_entity_admin_panel_view
from blog.views import get_paginated_context
from blog.views import process_delete_admin_panel_view
from blog.views import process_form_submission


# Widok dodawania autora (dla superusera)
@superuser_required
def author_add_view(request):
    return process_form_submission(
        request,
        AuthorCreateForm,
        'AdminTemplates/Accounts/Author/AuthorAddAdmin.html',
        'author_add',
        'Autor został utworzony'
    )


# Widok zarządzania autorami (dla superusera)
@superuser_required
def author_manage_admin_panel_view(request):
    author = Author.objects.all().order_by('user_id')

    context = get_paginated_context(request, author, 10)
    return render(
        request,
        'AdminTemplates/Accounts/Author/AuthorManageAdmin.html',
        context
    )


# Widok szczegółów autora (dla superusera)
@superuser_required
def author_detail_admin_panel_view(request, pk):
    author = get_object_or_404(Author, pk=pk)

    context = {
        'author': author,
    }
    return render(
        request,
        'AdminTemplates/Accounts/Author/AuthorDetailAdmin.html',
        context
    )


# Widok edycji autora (dla superusera)
@superuser_required
def author_edit_admin_panel_view(request, pk):
    author_name = get_object_or_404(Author, pk=pk)

    extra_context = {
        'author_name': author_name,
    }
    return edit_entity_admin_panel_view(
        request,
        pk,
        model_class=Author,
        form_class=AuthorEditForm,
        template_name='AdminTemplates/Accounts/Author/AuthorEditAdmin.html',
        success_message='Autor został edytowany',
        redirect_name='author_admin_panel',
        extra_context=extra_context
    )


# Widok usuwania autora (dla superusera)
@superuser_required
def author_delete_admin_panel_view(request, pk):
    return process_delete_admin_panel_view(
        request,
        pk,
        Author,
        AuthorDeleteForm,
        'AdminTemplates/Accounts/Author/AuthorDeleteAdmin.html',
        'Autor został usunięty',
        'author_admin_panel'
    )
