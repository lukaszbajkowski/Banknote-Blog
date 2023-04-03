from django.views.generic import ListView, DetailView
from .models import Blog, Author, Category
from django.core.paginator import Paginator
from django.shortcuts import render
from django.shortcuts import get_object_or_404


def HomeView(request):
    blog_first = Blog.objects.all().order_by('-date_posted')[:1]
    blog = Blog.objects.all().order_by('-date_posted')[1:]
    category = Category.objects.all()
    paginator = Paginator(blog, 2)  # Show 25 contacts per page.
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    context = {
        'blog_first': blog_first,
        'blog': blog,
        'category': category,
        'page_obj': page_obj
    }
    return render(request, 'home.html', context)


def ArticleDetailView(request, pk=None):
    blog_data = Blog.objects.all()
    blog_detail = None
    category = Category.objects.all()
    if pk:
        blog_detail = get_object_or_404(Blog, id=pk)
    context = {
        'po': blog_data,
        'posts': blog_detail,
        'category': category,
    }
    return render(request, 'article_details.html', context)


def profile_view(request, pk):
    user_account = Author.objects.get(id=pk)
    posts = Blog.objects.filter(author_id=pk).order_by('-date_posted')
    posts_num = posts.count()
    paginator = Paginator(posts, 5)  # Show 25 contacts per page.
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    category = Category.objects.all()
    return render(request, 'profile_view.html', {'posts': posts,
                                                 'posts_num': posts_num,
                                                 'user_account': user_account,
                                                 'page_obj': page_obj,
                                                 'category': category})


def CategoryView(request, cats):
    category_posts = Blog.objects.filter(category=cats)
    blog_data = Blog.objects.all()
    a = Category.objects.all()
    category_name = Category.objects.filter(id=cats)
    paginator = Paginator(category_posts, 5)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    return render(request, 'categories_detail.html', {'cats': cats,
                                                      'category_posts': category_posts,
                                                      'posts': blog_data,
                                                      'page_obj': page_obj,
                                                      'a': a,
                                                      'category_name': category_name,
                                                      })


def CategoryListView(request):
    categories = Category.objects.all()
    blog = Blog.objects.all().order_by('-date_posted')[1:]
    context = {
        'categories': categories,
        'posts': blog
    }
    return render(request, 'category_list.html', context)


def ProfileListView(request):
    author = Author.objects.all()
    category = Category.objects.all()
    blog = Blog.objects.all().order_by('-date_posted')[1:]
    context = {
        'author': author,
        'category': category,
        'blog': blog
    }
    return render(request, 'author_list.html', context)
