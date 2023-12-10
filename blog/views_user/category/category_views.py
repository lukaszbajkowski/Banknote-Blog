from django.core.paginator import Paginator
from django.http import JsonResponse
from django.shortcuts import render

from blog.form import NewsletterUserSignUpForm
from blog.models import Blog
from blog.models import Category
from blog.views import handle_newsletter_signup


# Widok kategorii
def category_view(request, pk):
    category_posts = Blog.objects.filter(category=pk)
    blog_data = Blog.objects.filter(publiction_status=True).order_by('-date_posted')[1:]
    a = Category.objects.all()
    category_name = Category.objects.filter(id=pk)
    paginator = Paginator(category_posts, 5)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'cats': pk,
        'category_posts': category_posts,
        'posts': blog_data,
        'page_obj': page_obj,
        'category_name': category_name,
        'category': a,
        'blog': blog_data,
    }

    return render(
        request,
        'UserTemplates/SingleCategory/Category.html',
        context
    )


# Widok listy kategorii
def category_list_view(request):
    categories = Category.objects.all()
    blog = Blog.objects.filter(publiction_status=True).order_by('-date_posted')[1:]
    newsletter_form = NewsletterUserSignUpForm(request.POST or None)

    if request.method == 'POST':
        response_data = handle_newsletter_signup(request, newsletter_form)
        return JsonResponse(response_data)

    context = {
        'categories': categories,
        'posts': blog,
        'form': newsletter_form,
        'blog': blog,
        'category': categories,
    }
    return render(
        request,
        'UserTemplates/CategoriesList/CategoriesList.html',
        context
    )
