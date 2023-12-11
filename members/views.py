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
from .forms import *

ssl._create_default_https_context = ssl._create_unverified_context


# Widok do obsługi resetowania hasła z dostosowanym formularzem
class CustomPasswordResetView(PasswordResetView):
    form_class = CustomPasswordResetForm


# Widok edycji profilu użytkownika
@login_required(login_url='home')
def UserEditView(request):
    category = Category.objects.all()
    blog = Blog.objects.all().filter(publiction_status=True).order_by('-date_posted')[1:]
    user = request.user
    user_custom, created = User_Custom.objects.get_or_create(user=user)
    delete_form = DeleteAccountForm(request.POST or None)
    if request.method == 'POST':
        user_form = UserForm(request.POST, request.FILES, instance=user_custom)
        edit_user_form = EditUserForm(request.POST, instance=user)
        if user_form.is_valid() and edit_user_form.is_valid():
            user_form.save()
            edit_user_form.save()
            return redirect('edit_profile')
    else:
        user_form = UserForm(instance=user_custom)
        edit_user_form = EditUserForm(instance=user)

    if delete_form.is_valid() and delete_form.cleaned_data['confirm_deletion']:
        user.delete()
        logout(request)
        return redirect('home')

    context = {
        'category': category,
        'blog': blog,
        'user_form': user_form,
        'edit_user_form': edit_user_form,
        'delete_form': delete_form,
    }
    return render(
        request,
        'my_account/edit_profile.html',
        context
    )


# Widok zmiany hasła użytkownika
@login_required(login_url='home')
def UserChangePasswordView(request):
    category = Category.objects.all()
    blog = Blog.objects.all().filter(publiction_status=True).order_by('-date_posted')[1:]

    if request.method == 'POST':
        edit_password_form = PasswordChangingForm(user=request.user, data=request.POST)
        if edit_password_form.is_valid():
            user = edit_password_form.save()
            update_session_auth_hash(request, user)
            return redirect('edit_security_page')
    else:
        edit_password_form = PasswordChangingForm(user=request.user)

    context = {
        'category': category,
        'blog': blog,
        'edit_password_form': edit_password_form,
    }
    return render(
        request,
        'my_account/edit_security.html',
        context
    )


# Widok do przekierowania do zmiany e-mail lub hasła
@login_required(login_url='home')
def UserChangePageView(request):
    category = Category.objects.all()
    blog = Blog.objects.all().filter(publiction_status=True).order_by('-date_posted')[1:]
    context = {
        'category': category,
        'blog': blog,
    }
    return render(
        request,
        'my_account/edit_security_page.html',
        context
    )


# Widok zmiany e-maila użytkownika
@login_required(login_url='home')
def UserChangeEmailView(request):
    category = Category.objects.all()
    blog = Blog.objects.all().filter(publiction_status=True).order_by('-date_posted')[1:]

    if request.method == 'POST':
        form = EmailChangeForm(user=request.user, data=request.POST)
        if form.is_valid():
            new_email = form.cleaned_data['new_email1']
            form.save()
            messages.success(
                request,
                'Dziękujemy za rejestrację do biuletynu.',
                "alert alert-success alert-dismissible fade show"
            )
            subject = 'Zmiana adresu e-mail'
            from_email = settings.EMAIL_HOST_USER
            to_email = [new_email]
            msg_plain = render_to_string(
                'my_account/edit_email_confirmation.txt',
                {
                    'mail': new_email
                }
            )
            msg_html = render_to_string(
                'my_account/edit_email_confirmation.html',
                {
                    'mail': new_email,
                    'image_url': 'http://127.0.0.1:8000/static/images/logo-no-background.png'
                }
            )
            send_mail(
                subject,
                msg_plain,
                from_email,
                to_email,
                html_message=msg_html,
                fail_silently=False
            )
            return redirect('edit_security_page')
    else:
        form = EmailChangeForm(user=request.user)

    context = {
        'category': category,
        'blog': blog,
        'edit_email_form': form,
    }
    return render(request, "my_account/edit_email.html", context)


def is_author(user):
    try:
        Author.objects.get(user=user)
        return True
    except Author.DoesNotExist:
        return False


# Widok zarządzania ustawieniami powiadomień użytkownika
@login_required(login_url='home')
def user_notification_view(request):
    category = Category.objects.all()
    blog = Blog.objects.filter(publiction_status=True).order_by('-date_posted')[1:]
    settings = User_Custom.objects.get(user=request.user)

    if request.method == 'POST':
        form = NotificationSettingsForm(request.POST, instance=settings)
        communication_form = CommunicationSettingForm(request.POST, instance=settings)
        if form.is_valid() and communication_form.is_valid():
            form.save()
            communication_form.save()
            return redirect('notifications')
    else:
        form = NotificationSettingsForm(instance=settings)
        communication_form = CommunicationSettingForm(instance=settings)

    context = {
        'category': category,
        'blog': blog,
        'form': form,
        'communication_form': communication_form,
    }
    return render(
        request,
        'my_account/notification.html',
        context
    )


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


# Widok formularza do zgłoszenia się jako autor
@login_required(login_url='home')
def article_author_form(request):
    category = Category.objects.all()
    blog = Blog.objects.all().filter(publiction_status=True).order_by('-date_posted')[1:]
    is_blocked = False
    is_author = False
    current_user_email = request.user.email
    authors = ArticleAuthor.objects.filter(email=current_user_email).order_by('-date_added')

    if Author.objects.filter(user=request.user).exists():
        return redirect('home')

    if authors:
        has_rejected_submission = any(author.rejected for author in authors)
        all_submissions_pending = all(not author.approved and not author.rejected for author in authors)
        has_approved_submission = any(author.approved for author in authors)
        if all(author.rejected for author in authors):
            is_blocked = False
        elif has_rejected_submission or all_submissions_pending:
            is_blocked = True
        elif has_approved_submission:
            is_author = True
        else:
            is_blocked = False
    else:
        is_blocked = False

    if request.method == 'POST':
        form = ArticleAuthorForm(request.POST)
        if form.is_valid():
            author = form.save(commit=False)
            author.email = current_user_email
            author.save()
            return redirect('article_author_form')
    else:
        initial_data = {'email': current_user_email}
        form = ArticleAuthorForm(initial=initial_data)

    context = {
        'form': form,
        'is_blocked': is_blocked,
        'authors': authors,
        'is_author': is_author,
        'category': category,
        'blog': blog,
    }
    return render(
        request,
        'my_account/author_application/author_application.html',
        context
    )


# Widok historii zgłoszeń na autora
@login_required(login_url='home')
def article_author_history(request):
    category = Category.objects.all()
    blog = Blog.objects.all().filter(publiction_status=True).order_by('-date_posted')[1:]

    if Author.objects.filter(user=request.user).exists():
        return redirect('home')

    submitted_forms = ArticleAuthor.objects.filter(email=request.user.email).order_by('-date_added')

    paginator = Paginator(submitted_forms, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    context = {
        'page_obj': page_obj,
        'blog': blog,
        'category': category,
    }
    return render(
        request,
        'my_account/author_application/author_application_history.html',
        context
    )


# Widok szczegółów zgłoszeń na autora
@login_required(login_url='home')
def article_author_detail(request, pk):
    if Author.objects.filter(user=request.user).exists():
        return redirect('home')

    category = Category.objects.all()
    blog = Blog.objects.all().filter(publiction_status=True).order_by('-date_posted')[1:]
    submitted_forms = get_object_or_404(ArticleAuthor, pk=pk)

    if submitted_forms.email != request.user.email:
        return redirect('home')

    context = {
        'submitted_forms': submitted_forms,
        'blog': blog,
        'category': category,
    }
    return render(
        request,
        'my_account/author_application/author_application_detail.html',
        context
    )


# Widok tworzenia autora przez użytkownika, który ma do tego uprawnienia
@login_required(login_url='home')
def create_author(request):
    user = request.user.user

    if user.can_be_author:
        if not hasattr(user, 'author'):
            if request.method == 'POST':
                form = CreateAuthorForm(request.POST, request.FILES)
                if form.is_valid():
                    author = Author.objects.create(
                        user=user.user,
                        bio=form.cleaned_data['bio'],
                        profile_pic=form.cleaned_data['profile_pic'],
                        author_quote=form.cleaned_data['author_quote'],
                        author_function=form.cleaned_data['author_function'],
                        author_url=form.cleaned_data['author_url'],
                        pinterest_url=form.cleaned_data['pinterest_url'],
                        facebook_url=form.cleaned_data['facebook_url'],
                        twitter_url=form.cleaned_data['twitter_url'],
                        instagram_url=form.cleaned_data['instagram_url']
                    )
                    user.can_be_author = False
                    user.save()

                    return redirect('edit_author')
            else:
                form = CreateAuthorForm()

            context = {
                'form': form,
            }
            return render(
                request,
                'my_account/author_application/create_author.html',
                context
            )
        else:
            return redirect('edit_author')
    else:
        return redirect('article_author_form')


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
