from django.contrib import messages
from django.contrib.auth import login, authenticate, logout, update_session_auth_hash
from django.contrib.auth.models import User
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.forms import UserCreationForm, UserChangeForm, PasswordChangeForm
from .forms import *
from blog.form import PostCreateForm, PostDeleteForm, NewsletterUserSignUpForm
from blog.models import *
from django.views import generic
from django.urls import reverse_lazy
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.core.validators import EmailValidator
from django.db import IntegrityError
from django.core.paginator import Paginator
from django.contrib.auth.decorators import user_passes_test
from django.core.mail import send_mail, EmailMultiAlternatives, EmailMessage
from django.template.loader import get_template, render_to_string
from django.contrib.sites.shortcuts import get_current_site
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from django.contrib.auth.tokens import default_token_generator
from django.utils.html import strip_tags
from django.contrib.auth.forms import PasswordResetForm
from django.contrib.auth.views import PasswordResetConfirmView
from django.contrib.auth.forms import SetPasswordForm
import time
import ssl

ssl._create_default_https_context = ssl._create_unverified_context


def register_page(request):
    if request.method != 'POST':
        form = CustomUserForm()
    else:
        form = CustomUserForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.is_active = False
            user.save()

            current_site = get_current_site(request)
            mail_subject = 'Potwierdź swój adres e-mail'
            message = render_to_string('registration/confirmation_email.html', {
                'user': user,
                'domain': current_site.domain,
                'uid': urlsafe_base64_encode(force_bytes(user.pk)),
                'token': default_token_generator.make_token(user),
                'image_url': 'http://127.0.0.1:8000/static/images/logo-no-background.png',
            })
            from_email = settings.EMAIL_HOST_USER
            to_email = form.cleaned_data.get('email')
            send_mail(
                mail_subject,
                message,
                from_email,
                [to_email],
                html_message=message,
                fail_silently=False
            )

            return redirect('confirmation')  # Przekierowanie na stronę potwierdzenia rejestracji

    context = {'form': form}
    return render(request, 'registration/registration.html', context)


def confirm_email(request, uidb64, token):
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = get_user_model().objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, get_user_model().DoesNotExist):
        user = None

    if user is not None and default_token_generator.check_token(user, token):
        user.is_active = True
        user.save()
        return redirect('registration_confirmed')  # Przekierowanie na stronę potwierdzenia rejestracji
    else:
        return redirect('confirmation_error')  # Przekierowanie na stronę błędu potwierdzenia rejestracji


def registration_confirmed(request):
    return render(request, 'registration/confirmed.html')


def confirmation_error(request):
    return render(request, 'registration/confirmation_error.html')


def confirmation_page(request):
    return render(request, 'registration/confirmation.html')


# def login_page(request):
#     if request.method == 'POST':
#         form = LoginForm(request.POST)
#
#         if form.is_valid():
#             username = form.cleaned_data['username']
#             password = form.cleaned_data['password']
#             user = authenticate(request, username=username, password=password)
#             if user is not None:
#                 login(request, user)
#                 return redirect('home')
#             else:
#                 messages.error(request, 'Nieprawidłowa nazwa użytkownika lub hasło.')
#     else:
#         form = LoginForm()
#
#     context = {
#         'form': form,
#     }
#
#     return render(request, 'registration/login.html', context)


def login_page(request):
    if request.method == 'POST':
        form = LoginForm(request.POST)

        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            user = authenticate(request, username=username, password=password)
            if user is not None:
                login(request, user)
                try:
                    user_extension = User.objects.get(user_id=user)
                    return redirect('home')
                except User.DoesNotExist:
                    return redirect('edit_profile')
            else:
                messages.error(request, 'Nieprawidłowa nazwa użytkownika lub hasło.')
    else:
        form = LoginForm()

    context = {
        'form': form,
    }

    return render(request, 'registration/login.html', context)



def logout_page(request):
    logout(request)
    return redirect('/')


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
    return render(request, 'my_account/edit_profile.html', context)


@login_required(login_url='home')
def UserChangePasswordView(request):
    category = Category.objects.all()
    blog = Blog.objects.all().filter(publiction_status=True).order_by('-date_posted')[1:]

    if request.method == 'POST':
        edit_password_form = PasswordChangingForm(user=request.user, data=request.POST)
        if edit_password_form.is_valid():
            user = edit_password_form.save()
            update_session_auth_hash(request, user)  # Important! Refresh the session
            return redirect('edit_security_page')
    else:
        edit_password_form = PasswordChangingForm(user=request.user)

    context = {
        'category': category,
        'blog': blog,
        'edit_password_form': edit_password_form,
    }
    return render(request, 'my_account/edit_security.html', context)


@login_required(login_url='home')
def UserChangePageView(request):
    category = Category.objects.all()
    blog = Blog.objects.all().filter(publiction_status=True).order_by('-date_posted')[1:]
    context = {
        'category': category,
        'blog': blog,
    }
    return render(request, 'my_account/edit_security_page.html', context)


@login_required(login_url='home')
def UserChangeEmailView(request):
    if request.method == 'POST':
        form = EmailChangeForm(user=request.user, data=request.POST)
        if form.is_valid():
            new_email = form.cleaned_data['new_email1']
            form.save()
            messages.success(request,
                             'Dziękujemy za rejestrację do biuletynu.',
                             "alert alert-success alert-dismissible fade show")
            subject = 'Zmiana adresu e-mail'
            from_email = settings.EMAIL_HOST_USER
            to_email = [new_email]
            msg_plain = render_to_string('my_account/edit_email_confirmation.txt',
                                         {'mail': new_email})
            msg_html = render_to_string('my_account/edit_email_confirmation.html',
                                        {'mail': new_email,
                                         'image_url': 'http://127.0.0.1:8000/static/images/logo-no-background.png'})
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

    category = Category.objects.all()
    blog = Blog.objects.all().filter(publiction_status=True).order_by('-date_posted')[1:]
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


@login_required(login_url='home')
def UserNotificationView(request):
    try:
        settings = User.objects.get(user=request.user)
    except User.DoesNotExist:
        settings = User(user=request.user)

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

    category = Category.objects.all()
    blog = Blog.objects.all().filter(publiction_status=True).order_by('-date_posted')[1:]
    context = {
        'category': category,
        'blog': blog,
        'form': form,
        'communication_form': communication_form,
    }
    return render(request, 'my_account/notification.html', context)


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
    return render(request, 'my_account/author/edit_author_page.html', context)


@login_required(login_url='home')
@user_passes_test(is_author, login_url='home')
def my_posts_create(request):
    if request.method == 'POST':
        form = PostAddForm(request.POST, request.FILES)
        if form.is_valid():
            blog = form.save(commit=False)
            blog.author = request.user.author
            blog.save()
            form.save_m2m()  # Zapisuje powiązane kategorie
            return redirect('my_posts')
    else:
        form = PostAddForm()
    category = Category.objects.all()
    blog = Blog.objects.all().filter(publiction_status=True).order_by('-date_posted')[1:]
    context = {
        'form': form,
        'category': category,
        'blog': blog,
    }
    return render(request, 'my_account/author/my_posts_add.html', context)


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
    return render(request, 'my_account/author/my_posts.html', context)


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
    return render(request, 'my_account/author/my_posts_detail.html', context)


@login_required(login_url='home')
@user_passes_test(is_author, login_url='home')
def my_posts_edit(request, pk):
    post = get_object_or_404(Blog, pk=pk)
    if request.method == "POST":
        form = PostEditForm(request.POST, request.FILES, instance=post)
        if form.is_valid():
            post = form.save()
            messages.success(request,
                             'Post został edytowany',
                             "alert alert-success alert-dismissible fade show mt-3")
            return redirect('my_posts')

    else:
        form = PostEditForm(instance=post)

    category = Category.objects.all()
    blog = Blog.objects.all().filter(publiction_status=True).order_by('-date_posted')[1:]
    context = {
        'form': form,
        'category': category,
        'blog': blog,
    }
    return render(request, 'my_account/author/my_posts_edit.html', context)


@login_required(login_url='home')
@user_passes_test(is_author, login_url='home')
def my_posts_delete(request, pk):
    post = get_object_or_404(Blog, pk=pk)
    news = get_object_or_404(Blog, pk=pk)
    if request.method == "POST":
        form = PostDeleteForm(request.POST, instance=post)
        if form.is_valid():
            post.delete()
            messages.success(request,
                             'Post został usunięty',
                             "alert alert-success alert-dismissible fade show mt-3")
            return redirect('my_posts')
    else:
        form = PostDeleteForm(instance=post)

    category = Category.objects.all()
    blog = Blog.objects.all().filter(publiction_status=True).order_by('-date_posted')[1:]
    context = {
        'form': form,
        'news': news,
        'category': category,
        'blog': blog,
    }
    return render(request, 'my_account/author/my_posts_delete.html', context)


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
    return render(request, 'my_account/author_application/author_application.html', context)


@user_passes_test(
    lambda u: u.is_authenticated and u.is_superuser,
    login_url='home'
)
def decision_maker_admin_panel(request):
    if request.method == 'POST':
        form_id = request.POST.get('form_id')
        decision = request.POST.get('decision')
        if form_id and decision:
            form = ArticleAuthor.objects.get(id=form_id)
            if not form.approved and not form.rejected:
                if decision == 'approve':
                    form.approved = True
                    form.rejected = False

                    # Update User's can_be_author field based on email
                    users = User.objects.all()
                    for user in users:
                        if user.user.email == form.email:
                            user.can_be_author = True
                            user.save()
                elif decision == 'reject':
                    form.approved = False
                    form.rejected = True
                form.save()
            return redirect('decision_maker_admin_panel')
    else:
        submitted_forms = ArticleAuthor.objects.all().order_by('-date_added')
        paginator = Paginator(submitted_forms, 10)
        page_number = request.GET.get('page')
        page_obj = paginator.get_page(page_number)
        context = {
            'page_obj': page_obj,
        }
        return render(request, 'author_application/decision_maker_admin_panel.html', context)


@user_passes_test(
    lambda u: u.is_authenticated and u.is_superuser,
    login_url='home'
)
def decision_maker_detail_admin_panel_view(request, pk):
    submitted_forms = get_object_or_404(ArticleAuthor, pk=pk)
    context = {
        'submitted_forms': submitted_forms,
    }
    return render(request, 'author_application/decision_maker_detail_admin_panel.html', context)


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
    return render(request, 'my_account/author_application/author_application_history.html', context)


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
    return render(request, 'my_account/author_application/author_application_detail.html', context)


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

            return render(request, 'my_account/author_application/create_author.html', {'form': form})
        else:
            return redirect('edit_author')
    else:
        return redirect('article_author_form')


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
    return render(request, 'my_account/comments.html', context)
