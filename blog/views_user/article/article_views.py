from django.core.paginator import Paginator
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.shortcuts import render
from django.utils import timezone

from blog.form import CommentForm
from blog.form import NewsletterUserSignUpForm
from blog.models import Blog
from blog.models import Category
from blog.views import handle_newsletter_signup


# Widok artykułu
def article_detail_view(request, pk=None):
    blog_data = Blog.objects.all().filter(publiction_status=True)
    blog = Blog.objects.all().filter(publiction_status=True).order_by('-date_posted')[1:]
    blog_detail = None
    comments = None
    category = Category.objects.all()
    random_posts = Blog.objects.filter(publiction_status=True).order_by('?')[:4]
    total_comments = 0

    if pk:
        blog_detail = get_object_or_404(Blog, id=pk)
        comments = blog_detail.comment_set.all().order_by('date_posted')
        for comment in comments:
            comment.days_passed = (timezone.now() - comment.date_posted).days
        total_comments = comments.count()

        if request.user.is_authenticated:
            user = request.user.user
            user.opened_posts.add(blog_detail)

    if request.method == 'POST':
        comment_form = CommentForm(request.POST)
        newsletter_form = NewsletterUserSignUpForm(request.POST)

        if comment_form.is_valid():
            comment = comment_form.save(commit=False)
            comment.blog = blog_detail
            comment.date_posted = timezone.now()
            comment.author = request.user
            comment.save()
            return JsonResponse({'success': True})
        elif newsletter_form.is_valid():
            response_data = handle_newsletter_signup(request, newsletter_form)
            return JsonResponse(response_data)

    else:
        comment_form = CommentForm()
        newsletter_form = NewsletterUserSignUpForm()

    context = {
        'form': newsletter_form,
        'blog': blog,
        'po': blog_data,
        'posts': blog_detail,
        'category': category,
        'random_posts': random_posts,
        'comments': comments,
        'total_comments': total_comments,
        'comment_form': comment_form,
    }
    return render(
        request,
        'UserTemplates/Article/Article.html',
        context
    )


# Widok listy artykułów
def article_list_view(request):
    blog_data = Blog.objects.all().filter(publiction_status=True)
    paginator = Paginator(blog_data, 15)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    blog = Blog.objects.all().filter(publiction_status=True).order_by('-date_posted')[1:]
    category = Category.objects.all()
    newsletter_form = NewsletterUserSignUpForm(request.POST or None)

    if request.method == 'POST':
        response_data = handle_newsletter_signup(request, newsletter_form)
        return JsonResponse(response_data)

    context = {
        'page_obj': page_obj,
        'form': newsletter_form,
        'blog': blog,
        'category': category,
    }
    return render(
        request,
        'UserTemplates/ArticlesList/ArticlesList.html',
        context
    )
