from django.core.paginator import Paginator
from django.http import JsonResponse
from django.shortcuts import render

from blog.forms.newsletter_form import NewsletterUserSignUpForm
from blog.models import Author
from blog.models import Blog
from blog.models import Category
from blog.views import handle_newsletter_signup


# Widok listy profili użytkowników
def profile_list_view(request):
    author = Author.objects.all()
    category = Category.objects.all()
    blog = Blog.objects.filter(publiction_status=True).order_by('-date_posted')[1:]
    newsletter_form = NewsletterUserSignUpForm(request.POST or None)

    if request.method == 'POST':
        response_data = handle_newsletter_signup(request, newsletter_form)
        return JsonResponse(response_data)

    context = {
        'author': author,
        'category': category,
        'blog': blog,
        'form': newsletter_form,
    }
    return render(
        request,
        'UserTemplates/Authors/Authors.html',
        context
    )


# Widok profilu użytkownika
def profile_view(request, pk):
    user_account = Author.objects.get(id=pk)
    posts = Blog.objects.filter(author_id=pk).filter(publiction_status=True).order_by('-date_posted')
    paginator = Paginator(posts, 5)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    category = Category.objects.all()
    blog = Blog.objects.all().filter(publiction_status=True).order_by('-date_posted')[1:]

    context = {
        'posts': posts,
        'user_account': user_account,
        'page_obj': page_obj,
        'category': category,
        'blog': blog
    }
    return render(
        request,
        'UserTemplates/Author/Author.html',
        context
    )
