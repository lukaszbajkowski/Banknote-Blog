from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.decorators import user_passes_test
from django.core.paginator import Paginator
from django.shortcuts import get_object_or_404
from django.shortcuts import redirect
from django.shortcuts import render

from blog.form import PostDeleteForm
from blog.models import Author
from blog.models import Blog
from blog.models import Category
from members.decorators import is_author
from members.forms import AuthorForm
from members.forms import PostAddForm
from members.forms import PostEditForm


# Widok tworzenia profilu autora
@login_required(login_url='home')
@user_passes_test(is_author, login_url='home')
def author_view(request):
    category = Category.objects.all()
    blog = Blog.objects.all().filter(publiction_status=True).order_by('-date_posted')[1:]

    author = Author.objects.get(user=request.user)
    if request.method == 'POST':
        form = AuthorForm(request.POST, request.FILES, instance=author)
        if form.is_valid():
            form.save()
            return redirect(
                'edit_author')
    else:
        form = AuthorForm(instance=author)

    context = {
        'category': category,
        'blog': blog,
        'form': form,
    }
    return render(
        request,
        'UserTemplates/UserAccount/Author/EditAuthorPage.html',
        context
    )


# Widok tworzenia nowego postu przez autora
@login_required(login_url='home')
@user_passes_test(is_author, login_url='home')
def author_post_create_view(request):
    category = Category.objects.all()
    blog = Blog.objects.all().filter(publiction_status=True).order_by('-date_posted')[1:]

    if request.method == 'POST':
        form = PostAddForm(request.POST, request.FILES)
        if form.is_valid():
            blog = form.save(commit=False)
            blog.author = request.user.author
            blog.save()
            form.save_m2m()
            return redirect('my_posts')
    else:
        form = PostAddForm()

    context = {
        'form': form,
        'category': category,
        'blog': blog,
    }
    return render(
        request,
        'UserTemplates/UserAccount/author/my_posts_add.html',
        context
    )


# Widok wyświetlania postów przez autora
@login_required(login_url='home')
@user_passes_test(is_author, login_url='home')
def author_post_view(request):
    author = request.user.author
    category = Category.objects.all()
    blog = Blog.objects.all().filter(publiction_status=True).order_by('-date_posted')[1:]
    published_posts = Blog.objects.filter(author=author, publiction_status=True).order_by('-date_posted')
    unpublished_posts = Blog.objects.filter(author=author, publiction_status=False).order_by('-date_posted')

    show_published = True

    if 'unpublished' in request.GET:
        show_published = False

    if show_published:
        posts = published_posts
        paginator = Paginator(posts, 10)
        page_number = request.GET.get('page')
        page_obj = paginator.get_page(page_number)
    else:
        posts = unpublished_posts
        paginator = Paginator(posts, 10)
        page_number = request.GET.get('page')
        page_obj = paginator.get_page(page_number)

    context = {
        'category': category,
        'posts': posts,
        'page_obj': page_obj,
        'show_published': show_published,
        'blog': blog,
    }
    return render(
        request,
        'UserTemplates/UserAccount/author/my_posts.html',
        context
    )


# Widok szczegółów postu przez autora
@login_required(login_url='home')
@user_passes_test(is_author, login_url='home')
def author_post_detail_view(request, pk):
    post = get_object_or_404(Blog, pk=pk)
    comments = post.comment_set.all().order_by('date_posted')
    category = Category.objects.all()
    blog = Blog.objects.all().filter(publiction_status=True).order_by('-date_posted')[1:]

    context = {
        'post': post,
        'comments': comments,
        'category': category,
        'blog': blog,
    }
    return render(
        request,
        'UserTemplates/UserAccount/author/my_posts_detail.html',
        context
    )


# Widok edycji postu przez autora
@login_required(login_url='home')
@user_passes_test(is_author, login_url='home')
def author_post_edit_view(request, pk):
    post = get_object_or_404(Blog, pk=pk)
    category = Category.objects.all()
    blog = Blog.objects.all().filter(publiction_status=True).order_by('-date_posted')[1:]

    if request.method == "POST":
        form = PostEditForm(request.POST, request.FILES, instance=post)
        if form.is_valid():
            form.save()
            messages.success(
                request,
                'Post został edytowany',
                "alert alert-success alert-dismissible fade show mt-3"
            )
            return redirect('my_posts')

    else:
        form = PostEditForm(instance=post)

    context = {
        'form': form,
        'category': category,
        'blog': blog,
    }
    return render(
        request,
        'UserTemplates/UserAccount/author/my_posts_edit.html',
        context
    )


# Widok usuwania postu przez autora
@login_required(login_url='home')
@user_passes_test(is_author, login_url='home')
def author_post_delete_view(request, pk):
    post = get_object_or_404(Blog, pk=pk)
    news = get_object_or_404(Blog, pk=pk)
    category = Category.objects.all()
    blog = Blog.objects.all().filter(publiction_status=True).order_by('-date_posted')[1:]

    if request.method == "POST":
        form = PostDeleteForm(request.POST, instance=post)
        if form.is_valid():
            post.delete()
            messages.success(
                request,
                'Post został usunięty',
                "alert alert-success alert-dismissible fade show mt-3"
            )
            return redirect('my_posts')
    else:
        form = PostDeleteForm(instance=post)

    context = {
        'form': form,
        'news': news,
        'category': category,
        'blog': blog,
    }
    return render(
        request,
        'UserTemplates/UserAccount/author/my_posts_delete.html',
        context
    )
