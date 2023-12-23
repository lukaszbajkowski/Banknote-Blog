from django.shortcuts import render, get_object_or_404

from blog.decorators import superuser_required
from blog.forms.category_form import CategoryCreateForm
from blog.forms.category_form import CategoryDeleteForm
from blog.models import Category
from blog.views import edit_entity_admin_panel_view
from blog.views import get_paginated_context
from blog.views import process_delete_admin_panel_view
from blog.views import process_form_submission


# Widok dodawania kategorii (dla superusera)
@superuser_required
def category_add_view(request):
    return process_form_submission(
        request,
        CategoryCreateForm,
        'AdminTemplates/Content/Category/CategoryAddAdmin.html',
        'category_add',
        'Kategoria została dodana.'
    )


# Widok zarządzania kategoriami (dla superusera)
@superuser_required
def category_manage_admin_panel_view(request):
    category = Category.objects.all().order_by('name')

    context = get_paginated_context(request, category, 10)
    return render(
        request,
        'AdminTemplates/Content/Category/CategoryManageAdmin.html',
        context
    )


# Widok szczegółów kategorii (dla superusera)
@superuser_required
def category_detail_admin_panel_view(request, pk):
    category = get_object_or_404(Category, pk=pk)
    categories = category.blog_set.count()

    context = {
        'category': category,
        'categories': categories
    }
    return render(
        request,
        'AdminTemplates/Content/Category/CategoryDetailAdmin.html',
        context
    )


# Widok edycji kategorii (dla superusera)
@superuser_required
def category_edit_admin_panel_view(request, pk):
    category = get_object_or_404(Category, pk=pk)

    extra_context = {
        'categories': category.blog_set.count(),
    }
    return edit_entity_admin_panel_view(
        request,
        pk,
        Category,
        CategoryCreateForm,
        'AdminTemplates/Content/Category/CategoryEditAdmin.html',
        'Kategoria została edytowana',
        'category_admin_panel',
        extra_context
    )


# Widok usuwania kategorii (dla superusera)
@superuser_required
def category_delete_admin_panel_view(request, pk):
    return process_delete_admin_panel_view(
        request,
        pk,
        Category,
        CategoryDeleteForm,
        'AdminTemplates/Content/Category/CategoryDeleteAdmin.html',
        'Kategoria została usunięta',
        'category_admin_panel'
    )


# Widok panelu administracyjnego dla postów w danej kategorii (dla superusera)
@superuser_required
def category_post_in_category_panel_admin_panel_view(request):
    category = Category.objects.all().order_by('name')

    context = get_paginated_context(request, category, 10)
    return render(
        request,
        'AdminTemplates/Content/Category/CategoryPostInCategoryAdmin.html',
        context
    )


# Widok szczegółów postów w danej kategorii (dla superusera)
@superuser_required
def category_post_in_category_panel_detail_admin_panel_view(request, pk):
    category = get_object_or_404(Category, pk=pk)
    posts = category.blog_set.all()

    context = {
        'category': category,
        'posts': posts,
    }
    return render(
        request,
        'AdminTemplates/Content/Category/CategoryPostInCategoryDetailAdmin.html',
        context
    )
