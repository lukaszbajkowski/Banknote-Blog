import ssl

from django.contrib import messages
from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.contrib.auth.decorators import user_passes_test
from django.contrib.auth.views import PasswordResetView
from django.contrib.sites.shortcuts import get_current_site
from django.core.mail import send_mail
from django.core.paginator import Paginator
from django.http import JsonResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.template.loader import render_to_string
from django.utils.encoding import force_bytes
from django.utils.encoding import force_str
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode

from blog.form import PostDeleteForm, NewsletterUserSignUpForm
from .decorators import is_author
from .forms import *

ssl._create_default_https_context = ssl._create_unverified_context


# Widok do obsługi resetowania hasła z dostosowanym formularzem
class CustomPasswordResetView(PasswordResetView):
    form_class = CustomPasswordResetForm


# Widok tworzenia profilu autora
@login_required(login_url='home')
@user_passes_test(is_author, login_url='home')
def UserAuthorView(request):
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
        'my_account/author/edit_author_page.html',
        context
    )


# Widok tworzenia nowego postu przez autora
@login_required(login_url='home')
@user_passes_test(is_author, login_url='home')
def my_posts_create(request):
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
        'my_account/author/my_posts_add.html',
        context
    )


# Widok wyświetlania postów przez autora
@login_required(login_url='home')
@user_passes_test(is_author, login_url='home')
def my_posts(request):
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
        'my_account/author/my_posts.html',
        context
    )


# Widok szczegółów postu przez autora
@login_required(login_url='home')
@user_passes_test(is_author, login_url='home')
def my_posts_detail(request, pk):
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
        'my_account/author/my_posts_detail.html',
        context
    )


# Widok edycji postu przez autora
@login_required(login_url='home')
@user_passes_test(is_author, login_url='home')
def my_posts_edit(request, pk):
    post = get_object_or_404(Blog, pk=pk)
    category = Category.objects.all()
    blog = Blog.objects.all().filter(publiction_status=True).order_by('-date_posted')[1:]

    if request.method == "POST":
        form = PostEditForm(request.POST, request.FILES, instance=post)
        if form.is_valid():
            post = form.save()
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
        'my_account/author/my_posts_edit.html',
        context
    )


# Widok usuwania postu przez autora
@login_required(login_url='home')
@user_passes_test(is_author, login_url='home')
def my_posts_delete(request, pk):
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
        'my_account/author/my_posts_delete.html',
        context
    )


# Widok listy komentarzy użytkownika
@login_required(login_url='home')
def CommentListView(request):
    user = request.user
    user_comments = Comment.objects.filter(author=user).order_by('-date_posted')
    paginator = Paginator(user_comments, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    category = Category.objects.all()
    blog = Blog.objects.all().filter(publiction_status=True).order_by('-date_posted')[1:]
    newsletter_form = NewsletterUserSignUpForm(request.POST or None)

    if request.method == 'POST':
        if newsletter_form.is_valid():
            instance = newsletter_form.save(commit=False)
            if NewsletterUser.objects.filter(email=instance.email).exists():
                return JsonResponse({'success': False})
            else:
                instance.save()
                send_newsletter_signup_email(instance.email)
                return JsonResponse({'success': True})
        else:
            return JsonResponse({'success': False})

    context = {
        'page_obj': page_obj,
        'form': newsletter_form,
        'blog': blog,
        'category': category,
        'user_comments': user_comments,
        'user_gender': user.user.gender,
    }
    return render(
        request,
        'my_account/comments.html',
        context
    )
