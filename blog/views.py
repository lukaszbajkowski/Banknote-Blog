from django.contrib import messages
from django.contrib.auth.decorators import user_passes_test
from django.core.mail import send_mail
from django.core.paginator import Paginator
from django.db.models import Count
from django.http import JsonResponse
from django.shortcuts import render, get_object_or_404, redirect
from django.template.loader import render_to_string
from django.utils import timezone

from .form import *


def send_newsletter_signup_email(email):
    subject = 'Dziękujemy za rejestrację do biuletynu.'
    from_email = settings.EMAIL_HOST_USER
    to_email = [email]
    msg_plain = render_to_string('newsletter/newsletter_singup_mail.txt', {'mail': email})
    msg_html = render_to_string('newsletter/newsletter_singup_mail.html',
                                {'mail': str(email),
                                 'image_url': 'http://127.0.0.1:8000/static/images/logo-no-background.png'})
    send_mail(subject, msg_plain, from_email, to_email, html_message=msg_html, fail_silently=False)


def HomeView(request):
    blog_first = Blog.objects.all().filter(publiction_status=True).order_by('-date_posted')[:1]
    blog = Blog.objects.all().filter(publiction_status=True).order_by('-date_posted')[1:]
    category = Category.objects.all()
    paginator = Paginator(blog, 12)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    favorite_blogs = Blog.objects.filter(publiction_status=True, favorite=True).order_by('?')
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
        'blog_first': blog_first,
        'blog': blog,
        'category': category,
        'page_obj': page_obj,
        'favorite_blogs': favorite_blogs,
        'form': newsletter_form,
    }
    return render(request, 'home.html', context)


def ArticleDetailView(request, pk=None):
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
            user = request.user.user  # Pobranie instancji modelu User
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
            instance = newsletter_form.save(commit=False)
            if NewsletterUser.objects.filter(email=instance.email).exists():
                return JsonResponse({'success': False})
            else:
                instance.save()
                send_newsletter_signup_email(instance.email)
                return JsonResponse({'success': True})

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
    return render(request, 'article_details.html', context)


def ArticleListView(request):
    blog_data = Blog.objects.all().filter(publiction_status=True)
    paginator = Paginator(blog_data, 15)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    blog = Blog.objects.all().filter(publiction_status=True).order_by('-date_posted')[1:]
    category = Category.objects.all()
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
    }
    return render(request, 'article_list.html', context)


def ContactView(request):
    blog = Blog.objects.all().filter(publiction_status=True).order_by('-date_posted')[1:]
    category = Category.objects.all()

    if request.method == 'POST':
        form = ContactForm(request.POST)
        if form.is_valid():
            name = form.cleaned_data['name']
            email = form.cleaned_data['email']
            message = form.cleaned_data['message']

            subject = 'Wiadomość z forumularza kontaktowego'
            msg_plain = render_to_string('contact/contact_mail_to_admin.txt', {
                'name': str(name),
                'mail': str(email),
                'message': str(message)})
            msg_html = render_to_string('contact/contact_mail_to_admin.html',
                                        {'name': str(name),
                                         'mail': str(email),
                                         'message': str(message),
                                         'image_url': 'http://127.0.0.1:8000/static/images/logo-no-background.png'})

            subject_user = 'Potwierdzenie wiadomości z forumularza kontaktowego'
            msg_plain_user = render_to_string('contact/contact_mail_to_user.txt', {
                'name': str(name),
                'mail': str(email),
                'message': str(message)})
            msg_html_user = render_to_string('contact/contact_mail_to_user.html',
                                             {'name': str(name),
                                              'mail': str(email),
                                              'message': str(message),
                                              'image_url': 'http://127.0.0.1:8000/static/images/logo-no-background.png'})

            send_mail(
                subject,
                msg_plain,
                email,
                [settings.EMAIL_HOST_USER],
                html_message=msg_html,
                fail_silently=False
            )

            send_mail(
                subject_user,
                msg_plain_user,
                settings.EMAIL_HOST_USER,
                [email],
                html_message=msg_html_user,
                fail_silently=False
            )
            return JsonResponse({'success': True})

        else:
            return JsonResponse({'success': False, 'error': 'Formularz zawiera nieprawidłowe dane.'})

    else:
        form = ContactForm()

    context = {
        'form': form,
        'blog': blog,
        'category': category,
    }
    return render(request, 'contact/contact_form.html', context)


def profile_view(request, pk):
    user_account = Author.objects.get(id=pk)
    posts = Blog.objects.filter(author_id=pk).filter(publiction_status=True).order_by('-date_posted')
    paginator = Paginator(posts, 5)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    category = Category.objects.all()
    blog = Blog.objects.all().filter(publiction_status=True).order_by('-date_posted')[1:]
    return render(request, 'profile_view.html', {'posts': posts,
                                                 'user_account': user_account,
                                                 'page_obj': page_obj,
                                                 'category': category,
                                                 'blog': blog})


def CategoryView(request, cats):
    category_posts = Blog.objects.filter(category=cats, publiction_status=True)
    blog_data = Blog.objects.all().filter(publiction_status=True)
    a = Category.objects.all()
    category_name = Category.objects.filter(id=cats)
    paginator = Paginator(category_posts, 5)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    category_description = Category.objects.get(id=cats).description
    blog = Blog.objects.all().filter(publiction_status=True).order_by('-date_posted')[1:]

    context = {
        'cats': cats,
        'category_posts': category_posts,
        'posts': blog_data,
        'page_obj': page_obj,
        'a': a,
        'category': a,
        'category_name': category_name,
        'category_description': category_description,
        'blog': blog
    }
    return render(request, 'categories_detail.html', context)


def CategoryListView(request):
    categories = Category.objects.all()
    blog = Blog.objects.all().filter(publiction_status=True).order_by('-date_posted')[1:]
    category = Category.objects.all()
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
        'categories': categories,
        'posts': blog,
        'form': newsletter_form,
        'blog': blog,
        'category': category,
    }
    return render(request, 'category_list.html', context)


def ProfileListView(request):
    newsletter_form = NewsletterUserSignUpForm(request.POST or None)
    author = Author.objects.all()
    category = Category.objects.all()
    blog = Blog.objects.all().filter(publiction_status=True).order_by('-date_posted')[1:]

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
        'author': author,
        'category': category,
        'blog': blog,
        'form': newsletter_form,
    }
    return render(request, 'author_list.html', context)


def TermsConditionsView(request):
    category = Category.objects.all()
    blog = Blog.objects.all().filter(publiction_status=True).order_by('-date_posted')[1:]

    context = {
        'category': category,
        'blog': blog,
    }
    return render(request, 'terms_conditions.html', context)


def PrivacyPolicyView(request):
    category = Category.objects.all()
    blog = Blog.objects.all().filter(publiction_status=True).order_by('-date_posted')[1:]

    context = {
        'category': category,
        'blog': blog,
    }
    return render(request, 'pricacy_policy.html', context)


def AboutPageView(request):
    category = Category.objects.all()
    blog = Blog.objects.all().filter(publiction_status=True).order_by('-date_posted')[1:]

    context = {
        'category': category,
        'blog': blog,
    }
    return render(request, 'about_page.html', context)


def newsletter_signup_view(request):
    form = NewsletterUserSignUpForm(request.POST or None)
    if form.is_valid():
        instance = form.save(commit=False)
        if NewsletterUser.objects.filter(email=instance.email).exists():
            messages.warning(request,
                             'Przepraszamy, ten e-mail już istnieje.',
                             "alert alert-warning alert-dismissible fade show")
        else:
            instance.save()
            messages.success(request,
                             'Dziękujemy za rejestrację do biuletynu.',
                             "alert alert-success alert-dismissible fade show")
            subject = 'Dziękujemy za rejestrację do biuletynu.'
            from_email = settings.EMAIL_HOST_USER
            to_email = [instance.email]
            msg_plain = render_to_string('newsletter/newsletter_singup_mail.txt',
                                         {'mail': instance.email})
            msg_html = render_to_string('newsletter/newsletter_singup_mail.html',
                                        {'mail': str(instance.email),
                                         'image_url': 'http://127.0.0.1:8000/static/images/logo-no-background.png'})
            send_mail(
                subject,
                msg_plain,
                from_email,
                to_email,
                html_message=msg_html,
                fail_silently=False
            )

    category = Category.objects.all()
    blog = Blog.objects.all().filter(publiction_status=True).order_by('-date_posted')[1:]
    context = {
        'form': form,
        'category': category,
        'blog': blog
    }
    return render(request, 'newsletter/newsletter_signup.html', context)


def newsletter_unsubscribe_view(request):
    form = NewsletterUserSignUpForm(request.POST or None)
    if form.is_valid():
        instance = form.save(commit=False)
        if NewsletterUser.objects.filter(email=instance.email).exists():
            NewsletterUser.objects.filter(email=instance.email).delete()
            messages.success(request,
                             'Rezygnacja z biuletynu powiodła się',
                             "alert alert-success alert-dismissible fade show")
            subject = 'Rezygnacja z biuletynu.'
            from_email = settings.EMAIL_HOST_USER
            to_email = [instance.email]
            msg_plain = render_to_string('newsletter/newsletter_unsubscribe_mail.txt',
                                         {'mail': instance.email})
            msg_html = render_to_string('newsletter/newsletter_unsubscribe_mail.html',
                                        {'mail': str(instance.email),
                                         'image_url': 'http://127.0.0.1:8000/static/images/logo-no-background.png'})
            send_mail(
                subject,
                msg_plain,
                from_email,
                to_email,
                html_message=msg_html,
                fail_silently=False
            )
        else:
            messages.warning(request,
                             'Przepraszamy, ten e-mail nie istnieje',
                             "alert alert-danger alert-dismissible fade show")
    category = Category.objects.all()
    blog = Blog.objects.all().filter(publiction_status=True).order_by('-date_posted')[1:]
    context = {
        'form': form,
        'category': category,
        'blog': blog
    }
    return render(request, 'newsletter/newsletter_unsubscribe.html', context)


@user_passes_test(
        lambda u: u.is_authenticated and u.is_superuser,
        login_url='home'
    )
def newsletter_creation_view(request):
    form = NewsletterCreationForm(request.POST or None)
    if form.is_valid():
        instance = form.save()
        newsletter = Newsletter.objects.get(id=instance.id)
        if newsletter.status_field == "Published":
            for email in newsletter.email.all():
                msg_plain = render_to_string('newsletter/admin_panel/newsletter_mail.txt',
                                             {'mail': email,
                                              'text': newsletter.text})
                msg_html = render_to_string('newsletter/admin_panel/newsletter_mail.html',
                                            {'mail': email,
                                             'text': newsletter.text,
                                             'image_url': 'http://127.0.0.1:8000/static/images/logo-no-background.png'})
                send_mail(
                    subject=newsletter.title,
                    from_email=settings.EMAIL_HOST_USER,
                    recipient_list=[email],
                    message=msg_plain,
                    html_message=msg_html,
                    fail_silently=False,
                )
            messages.success(request,
                             'Biuletyn został wysłany',
                             "alert alert-success alert-dismissible fade show mt-3")
        messages.success(request,
                         'Biuletyn został utworzony',
                         "alert alert-success alert-dismissible fade show mt-3")
        redirect('newsletter_creation')

    context = {
        'form': form,
    }
    return render(request, 'newsletter/admin_panel/newsletter_addpost_admin_panel.html', context)


@user_passes_test(
        lambda u: u.is_authenticated and u.is_superuser,
        login_url='home'
    )
def newsletter_add_user_view(request):
    form = NewsletterAddUserForm(request.POST or None)
    if form.is_valid():
        instance = form.save(commit=False)
        if NewsletterUser.objects.filter(email=instance.email).exists():
            messages.warning(request,
                             'Przepraszamy, ten e-mail już istnieje.',
                             "alert alert-warning alert-dismissible fade show mt-3")
        else:
            instance.save()
            messages.success(request,
                             'Dziękujemy za rejestrację do biuletynu.',
                             "alert alert-success alert-dismissible fade show mt-3")
            subject = 'Dziękujemy za rejestrację do biuletynu.'
            from_email = settings.EMAIL_HOST_USER
            to_email = [instance.email]
            msg_plain = render_to_string('newsletter/newsletter_singup_mail.txt',
                                         {'mail': instance.email})
            msg_html = render_to_string('newsletter/newsletter_singup_mail.html',
                                        {'mail': str(instance.email),
                                         'image_url': 'http://127.0.0.1:8000/static/images/logo-no-background.png'})
            send_mail(
                subject,
                msg_plain,
                from_email,
                to_email,
                html_message=msg_html,
                fail_silently=False
            )
    context = {
        'form': form,
    }
    return render(request, 'newsletter/admin_panel/newsletter_singup_admin_panel.html', context)


@user_passes_test(
        lambda u: u.is_authenticated and u.is_superuser,
        login_url='home'
    )
def newsletter_remove_user_view(request):
    form = NewsletterAddUserForm(request.POST or None)
    if form.is_valid():
        instance = form.save(commit=False)
        if NewsletterUser.objects.filter(email=instance.email).exists():
            NewsletterUser.objects.filter(email=instance.email).delete()
            messages.success(request,
                             'Rezygnacja z biuletynu powiodła się',
                             "alert alert-success alert-dismissible fade show mt-3")
            subject = 'Rezygnacja z biuletynu.'
            from_email = settings.EMAIL_HOST_USER
            to_email = [instance.email]
            msg_plain = render_to_string('newsletter/newsletter_unsubscribe_mail.txt',
                                         {'mail': instance.email})
            msg_html = render_to_string('newsletter/newsletter_unsubscribe_mail.html',
                                        {'mail': str(instance.email),
                                         'image_url': 'http://127.0.0.1:8000/static/images/logo-no-background.png'})
            send_mail(
                subject,
                msg_plain,
                from_email,
                to_email,
                html_message=msg_html,
                fail_silently=False
            )
        else:
            messages.warning(request,
                             'Przepraszamy, ten e-mail nie istnieje',
                             "alert alert-danger alert-dismissible fade show mt-3")
    context = {
        'form': form,
    }
    return render(request, 'newsletter/admin_panel/newsletter_unsubscribe_admin_panel.html', context)


@user_passes_test(
        lambda u: u.is_authenticated and u.is_superuser,
        login_url='home'
    )
def newsletter_manage_admin_panel_view(request):
    newsletter = Newsletter.objects.all()
    paginator = Paginator(newsletter, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    context = {
        'page_obj': page_obj,
    }
    return render(request, 'newsletter/admin_panel/newsletter_manage_admin_panel.html', context)


@user_passes_test(
        lambda u: u.is_authenticated and u.is_superuser,
        login_url='home'
    )
def newsletter_detail_admin_panel_view(request, pk):
    newsletter = get_object_or_404(Newsletter, pk=pk)
    context = {
        'newsletter': newsletter,
    }
    return render(request, 'newsletter/admin_panel/newsletter_detail_admin_panel.html', context)


@user_passes_test(
        lambda u: u.is_authenticated and u.is_superuser,
        login_url='home'
    )
def newsletter_edit_admin_panel_view(request, pk):
    newsletter = get_object_or_404(Newsletter, pk=pk)
    if request.method == "POST":
        form = NewsletterCreationForm(request.POST, instance=newsletter)
        if form.is_valid():
            newsletter = form.save()
            if newsletter.status_field == "Published":
                for email in newsletter.email.all():
                    msg_plain = render_to_string('newsletter/admin_panel/newsletter_mail.txt',
                                                 {'mail': email,
                                                  'text': newsletter.text})
                    msg_html = render_to_string('newsletter/admin_panel/newsletter_mail.html',
                                                {'mail': email,
                                                 'text': newsletter.text,
                                                 'image_url': 'http://127.0.0.1:8000/static/images/logo-no-background.png'})
                    send_mail(
                        subject=newsletter.title,
                        from_email=settings.EMAIL_HOST_USER,
                        recipient_list=[email],
                        message=msg_plain,
                        html_message=msg_html,
                        fail_silently=False,
                    )
                messages.success(request,
                                 'Biuletyn został wysłany',
                                 "alert alert-success alert-dismissible fade show mt-3")
            messages.success(request,
                             'Biuletyn został edytowany',
                             "alert alert-success alert-dismissible fade show mt-3")
            return redirect('newsletter_admin_panel')
    else:
        form = NewsletterCreationForm(instance=newsletter)
    context = {
        'form': form,
    }
    return render(request, 'newsletter/admin_panel/newsletter_edit_admin_panel.html', context)


@user_passes_test(
        lambda u: u.is_authenticated and u.is_superuser,
        login_url='home'
    )
def newsletter_delete_admin_panel_view(request, pk):
    newsletter = get_object_or_404(Newsletter, pk=pk)
    news = get_object_or_404(Newsletter, pk=pk)
    if request.method == "POST":
        form = NewsletterDeleteForm(request.POST, instance=newsletter)
        if form.is_valid():
            newsletter.delete()
            messages.success(request,
                             'Biuletyn został usunięty',
                             "alert alert-success alert-dismissible fade show mt-3")
            return redirect('newsletter_admin_panel')
    else:
        form = NewsletterDeleteForm(instance=newsletter)
    context = {
        'form': form,
        'news': news,
    }
    return render(request, 'newsletter/admin_panel/newsletter_delete_admin_panel.html', context)


@user_passes_test(
        lambda u: u.is_authenticated and u.is_superuser,
        login_url='home'
    )
def newsletter_user_manage_admin_panel_view(request):
    newsletter = NewsletterUser.objects.all()
    paginator = Paginator(newsletter, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    context = {
        'page_obj': page_obj,
    }
    return render(request, 'newsletter/admin_panel/newsletter_user_manage_admin_panel.html', context)


@user_passes_test(
        lambda u: u.is_authenticated and u.is_superuser,
        login_url='home'
    )
def newsletter_user_detail_admin_panel_view(request, pk):
    newsletter = get_object_or_404(NewsletterUser, pk=pk)
    context = {
        'newsletter': newsletter,
    }
    return render(request, 'newsletter/admin_panel/newsletter_user_detail_admin_panel.html', context)


@user_passes_test(
        lambda u: u.is_authenticated and u.is_superuser,
        login_url='home'
    )
def newsletter_user_delete_admin_panel_view(request, pk):
    newsletter_user = get_object_or_404(NewsletterUser, pk=pk)
    news = get_object_or_404(NewsletterUser, pk=pk)
    if request.method == "POST":
        form = NewsletterUserDeleteForm(request.POST, instance=newsletter_user)
        if form.is_valid():
            newsletter_user.delete()
            messages.success(request,
                             'Użytownik został usunięty',
                             "alert alert-success alert-dismissible fade show mt-3")
            return redirect('newsletter_user_admin_panel')
    else:
        form = NewsletterDeleteForm(instance=newsletter_user)
    context = {
        'form': form,
        'news': news,
    }
    return render(request, 'newsletter/admin_panel/newsletter_user_delete_admin_panel.html', context)


@user_passes_test(
        lambda u: u.is_authenticated and u.is_superuser,
        login_url='home'
    )
def admin_panel_view(request):
    return render(request, 'admin/admin_panel.html')


@user_passes_test(
        lambda u: u.is_authenticated and u.is_superuser,
        login_url='home'
    )
def newsletters_admin_panel_view(request):
    return render(request, 'admin/newsletters_admin_panel.html')


@user_passes_test(
        lambda u: u.is_authenticated and u.is_superuser,
        login_url='home'
    )
def users_admin_panel_view(request):
    return render(request, 'admin/users_admin_panel.html')


@user_passes_test(
        lambda u: u.is_authenticated and u.is_superuser,
        login_url='home'
    )
def posts_admin_panel_view(request):
    return render(request, 'admin/posts_admin_panel.html')


@user_passes_test(
        lambda u: u.is_authenticated and u.is_superuser,
        login_url='home'
    )
def author_add_view(request):
    if request.method == 'POST':
        form = AuthorCreateForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect('admin')
    else:
        form = AuthorCreateForm()
    context = {
        'form': form,
    }
    return render(request, 'author/author_add.html', context)


@user_passes_test(
        lambda u: u.is_authenticated and u.is_superuser,
        login_url='home'
    )
def author_manage_admin_panel_view(request):
    author = Author.objects.all().order_by('user_id')
    paginator = Paginator(author, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    context = {
        'page_obj': page_obj,
    }
    return render(request, 'author/author_admin_panel.html', context)


@user_passes_test(
        lambda u: u.is_authenticated and u.is_superuser,
        login_url='home'
    )
def author_detail_admin_panel_view(request, pk):
    author = get_object_or_404(Author, pk=pk)
    context = {
        'author': author,
    }
    return render(request, 'author/author_detail_admin_panel.html', context)


@user_passes_test(
        lambda u: u.is_authenticated and u.is_superuser,
        login_url='home'
    )
def author_edit_admin_panel_view(request, pk):
    author = get_object_or_404(Author, pk=pk)
    author_name = get_object_or_404(Author, pk=pk)
    if request.method == "POST":
        form = AuthorEditForm(request.POST, request.FILES, instance=author)
        if form.is_valid():
            author = form.save()
            messages.success(request,
                             'Autor został edytowany',
                             "alert alert-success alert-dismissible fade show mt-3")
            return redirect('author_admin_panel')
    else:
        form = AuthorEditForm(instance=author)
    context = {
        'form': form,
        'author_name': author_name,
    }
    return render(request, 'author/author_edit_admin_panel.html', context)


@user_passes_test(
        lambda u: u.is_authenticated and u.is_superuser,
        login_url='home'
    )
def author_delete_admin_panel_view(request, pk):
    author = get_object_or_404(Author, pk=pk)
    news = get_object_or_404(Author, pk=pk)

    if request.method == "POST":
        form = AuthorDeleteForm(request.POST, instance=author)
        if form.is_valid():
            # Delete associated ArticleAuthor instances
            ArticleAuthor.objects.filter(email=author.user.email).delete()

            # Delete the author
            author.delete()

            messages.success(request,
                             'Autor został usunięty',
                             "alert alert-success alert-dismissible fade show mt-3")
            return redirect('author_admin_panel')
    else:
        form = AuthorDeleteForm(instance=author)

    context = {
        'form': form,
        'news': news,
    }

    return render(request, 'author/author_delete_admin_panel.html', context)


@user_passes_test(
        lambda u: u.is_authenticated and u.is_superuser,
        login_url='home'
    )
def category_add_view(request):
    if request.method == 'POST':
        form = CategoryCreateForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('admin')
    else:
        form = CategoryCreateForm()
    context = {
        'form': form,
    }
    return render(request, 'category/category_add.html', context)


@user_passes_test(
        lambda u: u.is_authenticated and u.is_superuser,
        login_url='home'
    )
def category_manage_admin_panel_view(request):
    category = Category.objects.all().order_by('name')
    paginator = Paginator(category, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    context = {
        'page_obj': page_obj,
    }
    return render(request, 'category/category_admin_panel.html', context)


@user_passes_test(
        lambda u: u.is_authenticated and u.is_superuser,
        login_url='home'
    )
def category_detail_admin_panel_view(request, pk):
    category = get_object_or_404(Category, pk=pk)
    categories = category.blog_set.count()
    context = {
        'category': category,
        'categories': categories
    }
    return render(request, 'category/category_detail_admin_panel.html', context)


@user_passes_test(
        lambda u: u.is_authenticated and u.is_superuser,
        login_url='home'
    )
def category_edit_admin_panel_view(request, pk):
    category = get_object_or_404(Category, pk=pk)
    categories = category.blog_set.count()
    if request.method == "POST":
        form = CategoryCreateForm(request.POST, instance=category)
        if form.is_valid():
            category = form.save()
            messages.success(request,
                             'Kategoria została edytowana',
                             "alert alert-success alert-dismissible fade show mt-3")
            return redirect('category_admin_panel')
    else:
        form = CategoryCreateForm(instance=category)
    context = {
        'form': form,
        'categories': categories
    }
    return render(request, 'category/category_edit_admin_panel.html', context)


@user_passes_test(
        lambda u: u.is_authenticated and u.is_superuser,
        login_url='home'
    )
def category_delete_admin_panel_view(request, pk):
    category = get_object_or_404(Category, pk=pk)
    news = get_object_or_404(Category, pk=pk)
    if request.method == "POST":
        form = CategoryDeleteForm(request.POST, instance=category)
        if form.is_valid():
            category.delete()
            messages.success(request,
                             'Kategoria została usunięta',
                             "alert alert-success alert-dismissible fade show mt-3")
            return redirect('category_admin_panel')
    else:
        form = CategoryDeleteForm(instance=category)
    context = {
        'form': form,
        'news': news,
    }
    return render(request, 'category/category_delete_admin_panel.html', context)


@user_passes_test(
        lambda u: u.is_authenticated and u.is_superuser,
        login_url='home'
    )
def category_post_in_category_panel_admin_panel_view(request):
    category = Category.objects.all().order_by('name')
    paginator = Paginator(category, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    context = {
        'page_obj': page_obj,
    }
    return render(request, 'category/category_post_in_category_panel_admin_panel.html', context)


@user_passes_test(
        lambda u: u.is_authenticated and u.is_superuser,
        login_url='home'
    )
def category_post_in_category_panel_detail_admin_panel_view(request, pk):
    category = get_object_or_404(Category, pk=pk)
    posts = category.blog_set.all()
    context = {
        'category': category,
        'posts': posts,
    }
    return render(request, 'category/category_post_in_category_panel_detail_admin_panel.html', context)


@user_passes_test(
        lambda u: u.is_authenticated and u.is_superuser,
        login_url='home'
    )
def post_add_view(request):
    if request.method == 'POST':
        form = PostCreateForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect('admin')
    else:
        form = PostCreateForm()
    context = {
        'form': form,
    }
    return render(request, 'post/post_add.html', context)


@user_passes_test(
        lambda u: u.is_authenticated and u.is_superuser,
        login_url='home'
    )
def post_manage_admin_panel_view(request):
    post = Blog.objects.all().order_by('title')
    paginator = Paginator(post, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    context = {
        'page_obj': page_obj,
    }
    return render(request, 'post/post_admin_panel.html', context)


@user_passes_test(
        lambda u: u.is_authenticated and u.is_superuser,
        login_url='home'
    )
def post_detail_admin_panel_view(request, pk):
    post = get_object_or_404(Blog, pk=pk)
    comments = post.comment_set.all().order_by('date_posted')
    context = {
        'post': post,
        'comments': comments,
    }
    return render(request, 'post/post_detail_admin_panel.html', context)


@user_passes_test(
        lambda u: u.is_authenticated and u.is_superuser,
        login_url='home'
    )
def post_edit_admin_panel_view(request, pk):
    post = get_object_or_404(Blog, pk=pk)
    if request.method == "POST":
        form = PostCreateForm(request.POST, request.FILES, instance=post)
        if form.is_valid():
            post = form.save()
            messages.success(request,
                             'Post został edytowany',
                             "alert alert-success alert-dismissible fade show mt-3")
            return redirect('post_admin_panel')
    else:
        form = PostCreateForm(instance=post)
    context = {
        'form': form,
    }
    return render(request, 'post/post_edit_admin_panel.html', context)


@user_passes_test(
        lambda u: u.is_authenticated and u.is_superuser,
        login_url='home'
    )
def post_delete_admin_panel_view(request, pk):
    post = get_object_or_404(Blog, pk=pk)
    news = get_object_or_404(Blog, pk=pk)
    if request.method == "POST":
        form = PostDeleteForm(request.POST, instance=post)
        if form.is_valid():
            post.delete()
            messages.success(request,
                             'Post został usunięty',
                             "alert alert-success alert-dismissible fade show mt-3")
            return redirect('post_admin_panel')
    else:
        form = PostDeleteForm(instance=post)
    context = {
        'form': form,
        'news': news,
    }
    return render(request, 'post/post_delete_admin_panel.html', context)


@user_passes_test(
        lambda u: u.is_authenticated and u.is_superuser,
        login_url='home'
    )
def post_publication_admin_panel_view(request):
    if request.method == 'POST':
        blog_id = request.POST.get('blog_id')
        publication_status = request.POST.get('publication_status')
        blog = Blog.objects.get(pk=blog_id)
        blog.publiction_status = (publication_status == 'approve')
        blog.save()

    post = Blog.objects.all().order_by('title')
    paginator = Paginator(post, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    context = {
        'page_obj': page_obj,
    }
    return render(request, 'post/post_publication.html', context)


@user_passes_test(
        lambda u: u.is_authenticated and u.is_superuser,
        login_url='home'
    )
def comment_add_view(request):
    if request.method == 'POST':
        form = CommentCreateForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('admin')
    else:
        form = CommentCreateForm()
    context = {
        'form': form,
    }
    return render(request, 'comment/comment_add.html', context)


@user_passes_test(
        lambda u: u.is_authenticated and u.is_superuser,
        login_url='home'
    )
def comment_manage_admin_panel_view(request):
    comment = Comment.objects.all().order_by('-date_posted')
    paginator = Paginator(comment, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    context = {
        'page_obj': page_obj,
    }
    return render(request, 'comment/comment_admin_panel.html', context)


@user_passes_test(
        lambda u: u.is_authenticated and u.is_superuser,
        login_url='home'
    )
def comment_detail_admin_panel_view(request, pk):
    comment = get_object_or_404(Comment, pk=pk)
    context = {
        'comment': comment,
    }
    return render(request, 'comment/comment_detail_admin_panel.html', context)


@user_passes_test(
        lambda u: u.is_authenticated and u.is_superuser,
        login_url='home'
    )
def comment_edit_admin_panel_view(request, pk):
    comment = get_object_or_404(Comment, pk=pk)
    if request.method == "POST":
        form = CommentCreateForm(request.POST, instance=comment)
        if form.is_valid():
            comment = form.save()
            messages.success(request,
                             'Komentarz został edytowany',
                             "alert alert-success alert-dismissible fade show mt-3")
            return redirect('comment_admin_panel')
    else:
        form = CommentCreateForm(instance=comment)
    context = {
        'form': form,
    }
    return render(request, 'comment/comment_edit_admin_panel.html', context)


@user_passes_test(
        lambda u: u.is_authenticated and u.is_superuser,
        login_url='home'
    )
def comment_delete_admin_panel_view(request, pk):
    comment = get_object_or_404(Comment, pk=pk)
    news = get_object_or_404(Comment, pk=pk)
    if request.method == "POST":
        form = CommentDeleteForm(request.POST, instance=comment)
        if form.is_valid():
            comment.delete()
            messages.success(request,
                             'Komentarz został usunięty',
                             "alert alert-success alert-dismissible fade show mt-3")
            return redirect('comment_admin_panel')
    else:
        form = CommentDeleteForm(instance=comment)
    context = {
        'form': form,
        'news': news,
    }
    return render(request, 'comment/comment_delete_admin_panel.html', context)


@user_passes_test(
        lambda u: u.is_authenticated and u.is_superuser,
        login_url='home'
    )
def comment_in_post_admin_panel_view(request):
    posts = Blog.objects.all().order_by('title')
    paginator = Paginator(posts, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    context = {
        'page_obj': page_obj,
    }
    return render(request, 'comment/comment_in_post_admin_panel.html', context)


@user_passes_test(
        lambda u: u.is_authenticated and u.is_superuser,
        login_url='home'
    )
def comment_in_post_detail_admin_panel_view(request, pk):
    posts = get_object_or_404(Blog, pk=pk)
    comments = posts.comment_set.all().order_by('-date_posted')
    context = {
        'posts': posts,
        'comments': comments,
    }
    return render(request, 'comment/comment_in_post_detail_admin_panel.html', context)


@user_passes_test(
        lambda u: u.is_authenticated and u.is_superuser,
        login_url='home'
    )
def comment_users_admin_panel_view(request):
    users = User.objects.annotate(comment_count=Count('user__comment'))
    paginator = Paginator(users, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    context = {
        'page_obj': page_obj
    }
    return render(request, 'comment/comment_users_admin_panel.html', context)


@user_passes_test(
        lambda u: u.is_authenticated and u.is_superuser,
        login_url='home'
    )
def comment_users_detail_admin_panel_view(request, pk):
    user = get_object_or_404(User, id=pk)
    comments = Comment.objects.filter(author=user.user).order_by('-date_posted')
    context = {
        'users': user,
        'comments': comments
    }
    return render(request, 'comment/comment_users_detail_admin_panel.html', context)


@user_passes_test(
        lambda u: u.is_authenticated and u.is_superuser,
        login_url='home'
    )
def meetups_news_add_view(request):
    form = Meetups_newsCreationForm(request.POST or None)
    if form.is_valid():
        meetups_news_instance = form.save()
        if meetups_news_instance.status_field == 'Published':
            users_with_meetups_news = User.objects.filter(meetups_news=True)
            for user in users_with_meetups_news:
                msg_plain = render_to_string('meetups_news/meetups_news_mail.txt',
                                             {'mail': user.user,
                                              'text': meetups_news_instance.text})
                msg_html = render_to_string('meetups_news/meetups_news_mail.html',
                                            {'mail': user.user,
                                             'text': meetups_news_instance.text,
                                             'image_url': 'http://127.0.0.1:8000/static/images/logo-no-background.png'})

                send_mail(
                    'Nadchodzące spotkania i wydarzenia',
                    from_email=settings.EMAIL_HOST_USER,
                    recipient_list=[user.user.email],
                    message=msg_plain,
                    html_message=msg_html,
                    fail_silently=False,
                )
            messages.success(request, 'Mail o spotkaniach i wydarzeniach został wysłany',
                             "alert alert-success alert-dismissible fade show mt-3")
        messages.success(request, 'Mail o spotkaniach i wydarzeniach został utworzony',
                         "alert alert-success alert-dismissible fade show mt-3")
        return redirect('meetups_news_add')

    context = {
        'form': form,
    }
    return render(request, 'meetups_news/meetups_news_add.html', context)


@user_passes_test(
        lambda u: u.is_authenticated and u.is_superuser,
        login_url='home'
    )
def meetups_news_manage_admin_panel_view(request):
    meetups_news = Meetups_news.objects.all().order_by('title')
    paginator = Paginator(meetups_news, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    context = {
        'page_obj': page_obj,
    }
    return render(request, 'meetups_news/meetups_news_admin_panel.html', context)


@user_passes_test(
        lambda u: u.is_authenticated and u.is_superuser,
        login_url='home'
    )
def meetups_news_detail_admin_panel_view(request, pk):
    meetups_news = get_object_or_404(Meetups_news, pk=pk)
    context = {
        'meetups_news': meetups_news,
    }
    return render(request, 'meetups_news/meetups_news_detail_admin_panel.html', context)


@user_passes_test(
        lambda u: u.is_authenticated and u.is_superuser,
        login_url='home'
    )
def meetups_news_edit_admin_panel_view(request, pk):
    meetups_news = get_object_or_404(Meetups_news, pk=pk)
    if request.method == "POST":
        form = Meetups_newsCreationForm(request.POST, instance=meetups_news)
        if form.is_valid():
            meetups_news = form.save()
            if meetups_news.status_field == "Published":
                users_with_meetups_news = User.objects.filter(meetups_news=True)
                for user in users_with_meetups_news:
                    msg_plain = render_to_string('meetups_news/meetups_news_mail.txt',
                                                 {'mail': user.user,
                                                  'text': meetups_news.text})
                    msg_html = render_to_string('meetups_news/meetups_news_mail.html',
                                                {'mail': user.user,
                                                 'text': meetups_news.text,
                                                 'image_url': 'http://127.0.0.1:8000/static/images/logo-no-background.png'})

                    send_mail(
                        subject='Nadchodzące spotkania i wydarzenia',
                        from_email=settings.EMAIL_HOST_USER,
                        recipient_list=[user.user.email],
                        message=msg_plain,
                        html_message=msg_html,
                        fail_silently=False,
                    )
                messages.success(request,
                                 'Mail o spotkaniach i wydarzeniach został wysłany',
                                 "alert alert-success alert-dismissible fade show mt-3")
            messages.success(request,
                             'Mail o spotkaniach i wydarzeniach został edytowany',
                             "alert alert-success alert-dismissible fade show mt-3")
            return redirect('meetups_news_admin_panel')
    else:
        form = Meetups_newsCreationForm(instance=meetups_news)

    context = {
        'form': form,
    }
    return render(request, 'meetups_news/meetups_news_edit_admin_panel.html', context)


@user_passes_test(
        lambda u: u.is_authenticated and u.is_superuser,
        login_url='home'
    )
def meetups_news_delete_admin_panel_view(request, pk):
    meetups_news = get_object_or_404(Meetups_news, pk=pk)
    news = get_object_or_404(Meetups_news, pk=pk)
    if request.method == "POST":
        form = Meetups_newsCreationForm(request.POST, instance=meetups_news)
        if form.is_valid():
            meetups_news.delete()
            messages.success(request,
                             'Mail o spotkaniach i wydarzeniach został usunięty',
                             "alert alert-success alert-dismissible fade show mt-3")
            return redirect('meetups_news_admin_panel')
    else:
        form = Meetups_newsCreationForm(instance=meetups_news)
    context = {
        'form': form,
        'news': news,
    }
    return render(request, 'meetups_news/meetups_news_delete_admin_panel.html', context)


@user_passes_test(
        lambda u: u.is_authenticated and u.is_superuser,
        login_url='home'
    )
def meetups_news_user_manage_admin_panel_view(request):
    users = User.objects.all().order_by('user__id')
    paginator = Paginator(users, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    context = {
        'page_obj': page_obj,
    }
    return render(request, 'meetups_news/meetups_news_user_admin_panel.html', context)


@user_passes_test(
        lambda u: u.is_authenticated and u.is_superuser,
        login_url='home'
    )
def meetups_news_user_detail_admin_panel_view(request, pk):
    user = get_object_or_404(User, pk=pk)
    context = {
        'users': user,
    }
    return render(request, 'meetups_news/meetups_news_user_detail_admin_panel.html', context)


@user_passes_test(
        lambda u: u.is_authenticated and u.is_superuser,
        login_url='home'
    )
def meetups_news_user_edit_admin_panel_view(request, pk):
    user = get_object_or_404(User, id=pk)
    if request.method == "POST":
        form = UserMeetups_newsForm(request.POST, instance=user)
        if form.is_valid():
            form.save()
            messages.success(request,
                             'Ustawienia e-maila o spotkaniach i wydarzeniach zostały zaaktualizowane.',
                             "alert alert-success alert-dismissible fade show mt-3")
            return redirect('meetups_news_user_admin_panel')
    else:
        form = UserMeetups_newsForm(instance=user)

    return render(request, 'meetups_news/meetups_news_user_edit_admin_panel.html', {'form': form, 'users': user})


@user_passes_test(
    lambda u: u.is_authenticated and u.is_superuser,
    login_url='home'
)
def send_emails_view(request):
    if request.method == 'POST':
        users = User.objects.all()

        for user in users:
            if user.miss_news:
                unopened_posts = Blog.objects.filter(publiction_status=True).exclude(id__in=user.opened_posts.all())

                if unopened_posts:
                    from_email = settings.EMAIL_HOST_USER
                    msg_plain = render_to_string('skipped_posts/skipped_posts_mail.html',
                                                 {'mail': user.user,
                                                  'post_list': unopened_posts})
                    msg_html = render_to_string('skipped_posts/skipped_posts_mail.html',
                                                {'mail': user.user,
                                                 'post_list': unopened_posts,
                                                 'image_url': 'http://127.0.0.1:8000/static/images/logo-no-background.png', })
                    send_mail(
                        'Nieprzeczytane posty',
                        msg_plain,
                        from_email,
                        [user.user.email],
                        fail_silently=False,
                        html_message=msg_html
                    )

        return render(request, 'skipped_posts/skipped_posts_send_emails.html')

    return render(request, 'skipped_posts/skipped_posts_confirmation_send_emails.html')


@user_passes_test(
    lambda u: u.is_authenticated and u.is_superuser,
    login_url='home'
)
def skipped_posts_admin_panel(request):
    users = User.objects.all().order_by('user__id')

    users_with_unopened_posts = []
    for user in users:
        unopened_posts_count = Blog.objects.filter(publiction_status=True).exclude(
            id__in=user.opened_posts.all()).count()
        user.unopened_posts_count = unopened_posts_count
        users_with_unopened_posts.append(user)

    paginator = Paginator(users_with_unopened_posts, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    context = {
        'page_obj': page_obj,
    }
    return render(request, 'skipped_posts/skipped_posts_user_list.html', context)


@user_passes_test(
    lambda u: u.is_authenticated and u.is_superuser,
    login_url='home'
)
def skipped_posts_detail_admin_panel(request, pk):
    user = get_object_or_404(User, pk=pk)
    posts = Blog.objects.filter(publiction_status=True).exclude(id__in=user.opened_posts.all())
    context = {
        'posts': posts,
        'users': user
    }
    return render(request, 'skipped_posts/skipped_posts_detail_admin_panel.html', context)


@user_passes_test(
    lambda u: u.is_authenticated and u.is_superuser,
    login_url='home'
)
def skipped_posts_user_admin_panel(request):
    users = User.objects.all().order_by('user__id')
    context = {
        'users': users,
    }
    return render(request, 'skipped_posts/skipped_posts_user_admin_panel.html', context)


@user_passes_test(
    lambda u: u.is_authenticated and u.is_superuser,
    login_url='home'
)
def skipped_posts_user_edit_admin_panel(request, pk):
    user = get_object_or_404(User, id=pk)

    if request.method == 'POST':
        form = UserMissNewsForm(request.POST, instance=user)
        if form.is_valid():
            form.save()
            messages.success(request,
                             'Ustawienia pominiętych artykułów zostały zaktualizowane.',
                             "alert alert-success alert-dismissible fade show mt-3")
            return redirect('skipperd_posts_user_admin_panel')
    else:
        form = UserMissNewsForm(instance=user)

    return render(request, 'skipped_posts/skipped_posts_user_edit_admin_panel.html', {'form': form, 'users': user})


@user_passes_test(
        lambda u: u.is_authenticated and u.is_superuser,
        login_url='home'
    )
def auction_opportunities_add_view(request):
    form = AuctionOpportunitiesCreationForm(request.POST or None)
    if form.is_valid():
        auction_opportunities_instance = form.save()
        if auction_opportunities_instance.status_field == 'Published':
            users_with_auction_opportunities = User.objects.filter(opportunities_news=True)
            for user in users_with_auction_opportunities:
                msg_plain = render_to_string('auction_opportunities/auction_opportunities_mail.txt',
                                             {'mail': user.user,
                                              'text': auction_opportunities_instance.text})
                msg_html = render_to_string('auction_opportunities/auction_opportunities_mail.html',
                                            {'mail': user.user,
                                             'text': auction_opportunities_instance.text,
                                             'image_url': 'http://127.0.0.1:8000/static/images/logo-no-background.png'})

                send_mail(
                    'Okazje z rynku aukcyjnego',
                    from_email=settings.EMAIL_HOST_USER,
                    recipient_list=[user.user.email],
                    message=msg_plain,
                    html_message=msg_html,
                    fail_silently=False,
                )
            messages.success(request, 'Mail o okazjach z rynku aukcyjnego został wysłany',
                             "alert alert-success alert-dismissible fade show mt-3")
        messages.success(request, 'Mail o okazjach z rynku aukcyjnego został utworzony',
                         "alert alert-success alert-dismissible fade show mt-3")
        return redirect('auction_opportunities_add')

    context = {
        'form': form,
    }
    return render(request, 'auction_opportunities/auction_opportunities_add.html', context)


@user_passes_test(
        lambda u: u.is_authenticated and u.is_superuser,
        login_url='home'
    )
def auction_opportunities_admin_panel_view(request):
    auction_opportunities = AuctionOpportunities.objects.all().order_by('title')
    paginator = Paginator(auction_opportunities, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    context = {
        'page_obj': page_obj,
    }
    return render(request, 'auction_opportunities/auction_opportunities_admin_panel.html', context)


@user_passes_test(
        lambda u: u.is_authenticated and u.is_superuser,
        login_url='home'
    )
def auction_opportunities_detail_admin_panel_view(request, pk):
    auction_opportunities = get_object_or_404(AuctionOpportunities, pk=pk)
    context = {
        'auction_opportunities': auction_opportunities,
    }
    return render(request, 'auction_opportunities/auction_opportunities_detail_admin_panel.html', context)


@user_passes_test(
        lambda u: u.is_authenticated and u.is_superuser,
        login_url='home'
    )
def auction_opportunities_edit_admin_panel_view(request, pk):
    auction_opportunities = get_object_or_404(AuctionOpportunities, pk=pk)
    if request.method == "POST":
        form = AuctionOpportunitiesCreationForm(request.POST, instance=auction_opportunities)
        if form.is_valid():
            auction_opportunities = form.save()
            if auction_opportunities.status_field == "Published":
                users_with_auction_opportunities= User.objects.filter(opportunities_news=True)
                for user in users_with_auction_opportunities:
                    msg_plain = render_to_string('auction_opportunities/auction_opportunities_mail.txt',
                                                 {'mail': user.user,
                                                  'text': auction_opportunities.text})
                    msg_html = render_to_string('auction_opportunities/auction_opportunities_mail.html',
                                                {'mail': user.user,
                                                 'text': auction_opportunities.text,
                                                 'image_url': 'http://127.0.0.1:8000/static/images/logo-no-background.png'})

                    send_mail(
                        subject='Okazje z rynku aukcyjnego',
                        from_email=settings.EMAIL_HOST_USER,
                        recipient_list=[user.user.email],
                        message=msg_plain,
                        html_message=msg_html,
                        fail_silently=False,
                    )
                messages.success(request,
                                 'Mail o okazjach z rynku aukcyjengo został wysłany',
                                 "alert alert-success alert-dismissible fade show mt-3")
            messages.success(request,
                             'Mail o okazjach z rynku aukcyjnego został edytowany',
                             "alert alert-success alert-dismissible fade show mt-3")
            return redirect('auction_opportunities_admin_panel')
    else:
        form = AuctionOpportunitiesCreationForm(instance=auction_opportunities)

    context = {
        'form': form,
    }
    return render(request, 'auction_opportunities/auction_opportunities_edit_admin_panel.html', context)


@user_passes_test(
        lambda u: u.is_authenticated and u.is_superuser,
        login_url='home'
    )
def auction_opportunities_delete_admin_panel_view(request, pk):
    auction_opportunities = get_object_or_404(AuctionOpportunities, pk=pk)
    news = get_object_or_404(AuctionOpportunities, pk=pk)
    if request.method == "POST":
        form = AuctionOpportunitiesDeleteEmailForm(request.POST, instance=auction_opportunities)
        if form.is_valid():
            auction_opportunities.delete()
            messages.success(request,
                             'Mail o spotkaniach i wydarzeniach został usunięty',
                             "alert alert-success alert-dismissible fade show mt-3")
            return redirect('auction_opportunities_admin_panel')
    else:
        form = AuctionOpportunitiesDeleteEmailForm(instance=auction_opportunities)
    context = {
        'form': form,
        'news': news,
    }
    return render(request, 'auction_opportunities/auction_opportunities_delete_admin_panel.html', context)


@user_passes_test(
        lambda u: u.is_authenticated and u.is_superuser,
        login_url='home'
    )
def auction_opportunities_user_manage_admin_panel_view(request):
    users = User.objects.all().order_by('user__id')
    paginator = Paginator(users, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    context = {
        'page_obj': page_obj,
    }
    return render(request, 'auction_opportunities/auction_opportunities_user_admin_panel.html', context)


@user_passes_test(
        lambda u: u.is_authenticated and u.is_superuser,
        login_url='home'
    )
def auction_opportunities_user_detail_admin_panel_view(request, pk):
    user = get_object_or_404(User, pk=pk)
    context = {
        'users': user,
    }
    return render(request, 'auction_opportunities/auction_opportunities_user_detail_admin_panel.html', context)


@user_passes_test(
        lambda u: u.is_authenticated and u.is_superuser,
        login_url='home'
    )
def auction_opportunities_user_edit_admin_panel_view(request, pk):
    user = get_object_or_404(User, id=pk)
    if request.method == "POST":
        form = UserAuctionOpportunitiesForm(request.POST, instance=user)
        if form.is_valid():
            form.save()
            messages.success(request,
                             'Ustawienia e-maila o okazjach z rynku aukcyjnego zostały zaaktualizowane.',
                             "alert alert-success alert-dismissible fade show mt-3")
            return redirect('auction_opportunities_user_manage_admin_panel')
    else:
        form = UserAuctionOpportunitiesForm(instance=user)

    return render(request, 'auction_opportunities/auction_opportunities_user_edit_admin_panel.html', {'form': form, 'users': user})


@user_passes_test(
        lambda u: u.is_authenticated and u.is_superuser,
        login_url='home'
    )
def company_news_add_view(request):
    form = CompanyNewsCreationForm(request.POST or None)
    if form.is_valid():
        company_news_instance = form.save()
        if company_news_instance.status_field == 'Published':
            users_with_company_news = User.objects.filter(company_news=True)
            for user in users_with_company_news:
                msg_plain = render_to_string('company_news/company_news_mail.txt',
                                             {'mail': user.user,
                                              'text': company_news_instance.text})
                msg_html = render_to_string('company_news/company_news_mail.html',
                                            {'mail': user.user,
                                             'text': company_news_instance.text,
                                             'image_url': 'http://127.0.0.1:8000/static/images/logo-no-background.png'})

                send_mail(
                    'Wiadomość od Banknoty',
                    from_email=settings.EMAIL_HOST_USER,
                    recipient_list=[user.user.email],
                    message=msg_plain,
                    html_message=msg_html,
                    fail_silently=False,
                )
            messages.success(request, 'Mail z wiadomością od Bankonty został wysłany',
                             "alert alert-success alert-dismissible fade show mt-3")
        messages.success(request, 'Mail z wiadomością od Bankonty został utworzony',
                         "alert alert-success alert-dismissible fade show mt-3")
        return redirect('company_news_add')

    context = {
        'form': form,
    }
    return render(request, 'company_news/company_news_add.html', context)


@user_passes_test(
        lambda u: u.is_authenticated and u.is_superuser,
        login_url='home'
    )
def company_news_admin_panel_view(request):
    company_news = CompanyNews.objects.all().order_by('title')
    paginator = Paginator(company_news, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    context = {
        'page_obj': page_obj,
    }
    return render(request, 'company_news/company_news_admin_panel.html', context)


@user_passes_test(
        lambda u: u.is_authenticated and u.is_superuser,
        login_url='home'
    )
def company_news_detail_admin_panel_view(request, pk):
    company_news = get_object_or_404(CompanyNews, pk=pk)
    context = {
        'company_news': company_news,
    }
    return render(request, 'company_news/company_news_detail_admin_panel.html', context)


@user_passes_test(
        lambda u: u.is_authenticated and u.is_superuser,
        login_url='home'
    )
def company_news_edit_admin_panel_view(request, pk):
    company_news = get_object_or_404(CompanyNews, pk=pk)
    if request.method == "POST":
        form = CompanyNewsCreationForm(request.POST, instance=company_news)
        if form.is_valid():
            company_news = form.save()
            if company_news.status_field == "Published":
                users_with_company_news = User.objects.filter(opportunities_news=True)
                for user in users_with_company_news:
                    msg_plain = render_to_string('company_news/company_news_mail.txt',
                                                 {'mail': user.user,
                                                  'text': company_news.text})
                    msg_html = render_to_string('company_news/company_news_mail.html',
                                                {'mail': user.user,
                                                 'text': company_news.text,
                                                 'image_url': 'http://127.0.0.1:8000/static/images/logo-no-background.png'})

                    send_mail(
                        subject='Okazje z rynku aukcyjnego',
                        from_email=settings.EMAIL_HOST_USER,
                        recipient_list=[user.user.email],
                        message=msg_plain,
                        html_message=msg_html,
                        fail_silently=False,
                    )
                messages.success(request,
                                 'Mail z wiadomością od Bankonty został wysłany',
                                 "alert alert-success alert-dismissible fade show mt-3")
            messages.success(request,
                             'Mail z wiadomością od Bankonty został edytowany',
                             "alert alert-success alert-dismissible fade show mt-3")
            return redirect('company_news_admin_panel')
    else:
        form = CompanyNewsCreationForm(instance=company_news)

    context = {
        'form': form,
    }
    return render(request, 'company_news/company_news_edit_admin_panel.html', context)


@user_passes_test(
        lambda u: u.is_authenticated and u.is_superuser,
        login_url='home'
    )
def company_news_delete_admin_panel_view(request, pk):
    company_news = get_object_or_404(CompanyNews, pk=pk)
    news = get_object_or_404(CompanyNews, pk=pk)
    if request.method == "POST":
        form = CompanyNewsDeleteEmailForm(request.POST, instance=company_news)
        if form.is_valid():
            company_news.delete()
            messages.success(request,
                             'Mail z wiadomością od Bankonty został usunięty',
                             "alert alert-success alert-dismissible fade show mt-3")
            return redirect('company_news_admin_panel')
    else:
        form = CompanyNewsDeleteEmailForm(instance=company_news)
    context = {
        'form': form,
        'news': news,
    }
    return render(request, 'company_news/company_news_delete_admin_panel.html', context)



@user_passes_test(
        lambda u: u.is_authenticated and u.is_superuser,
        login_url='home'
    )
def company_news_user_manage_admin_panel_view(request):
    users = User.objects.all().order_by('user__id')
    paginator = Paginator(users, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    context = {
        'page_obj': page_obj,
    }
    return render(request, 'company_news/company_news_user_manage_admin_panel.html', context)


@user_passes_test(
        lambda u: u.is_authenticated and u.is_superuser,
        login_url='home'
    )
def company_news_user_detail_admin_panel_view(request, pk):
    user = get_object_or_404(User, pk=pk)
    context = {
        'users': user,
    }
    return render(request, 'company_news/company_news_user_detail_admin_panel.html', context)


@user_passes_test(
        lambda u: u.is_authenticated and u.is_superuser,
        login_url='home'
    )
def company_news_user_edit_admin_panel_view(request, pk):
    user = get_object_or_404(User, id=pk)
    if request.method == "POST":
        form = UserCompanyNewsForm(request.POST, instance=user)
        if form.is_valid():
            form.save()
            messages.success(request,
                             'Ustawienia e-maila z wiadmością od Banknoty zostały zaaktualizowane.',
                             "alert alert-success alert-dismissible fade show mt-3")
            return redirect('company_news_user_manage_admin_panel')
    else:
        form = UserCompanyNewsForm(instance=user)

    return render(request, 'company_news/company_news_user_edit_admin_panel.html', {'form': form, 'users': user})


@user_passes_test(
        lambda u: u.is_authenticated and u.is_superuser,
        login_url='home'
    )
def replay_news_add_view(request):
    form = ReplayNewsCreationForm(request.POST or None)
    if form.is_valid():
        replay_news_instance = form.save()
        if replay_news_instance.status_field == 'Published':
            users_with_replay_news = User.objects.filter(replay_news=True)
            for user in users_with_replay_news:
                msg_plain = render_to_string('replay_news/replay_news_mail.txt',
                                             {'mail': user.user,
                                              'text': replay_news_instance.text})
                msg_html = render_to_string('replay_news/replay_news_mail.html',
                                            {'mail': user.user,
                                             'text': replay_news_instance.text,
                                             'image_url': 'http://127.0.0.1:8000/static/images/logo-no-background.png'})

                send_mail(
                    'Shot wydarzeń od Banknoty',
                    from_email=settings.EMAIL_HOST_USER,
                    recipient_list=[user.user.email],
                    message=msg_plain,
                    html_message=msg_html,
                    fail_silently=False,
                )
            messages.success(request, 'Mail z shotem od Bankonty został wysłany',
                             "alert alert-success alert-dismissible fade show mt-3")
        messages.success(request, 'Mail z shotem od Bankonty został utworzony',
                         "alert alert-success alert-dismissible fade show mt-3")
        return redirect('replay_news_add')

    context = {
        'form': form,
    }
    return render(request, 'replay_news/replay_news_add.html', context)


@user_passes_test(
        lambda u: u.is_authenticated and u.is_superuser,
        login_url='home'
    )
def replay_news_admin_panel_view(request):
    replay_news = ReplayNews.objects.all().order_by('title')
    paginator = Paginator(replay_news, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    context = {
        'page_obj': page_obj,
    }
    return render(request, 'replay_news/replay_news_admin_panel.html', context)


@user_passes_test(
        lambda u: u.is_authenticated and u.is_superuser,
        login_url='home'
    )
def replay_news_detail_admin_panel_view(request, pk):
    replay_news = get_object_or_404(ReplayNews, pk=pk)
    context = {
        'replay_news': replay_news,
    }
    return render(request, 'replay_news/replay_news_detail_admin_panel.html', context)


@user_passes_test(
        lambda u: u.is_authenticated and u.is_superuser,
        login_url='home'
    )
def replay_news_edit_admin_panel_view(request, pk):
    replay_news = get_object_or_404(ReplayNews, pk=pk)
    if request.method == "POST":
        form = ReplayNewsCreationForm(request.POST, instance=replay_news)
        if form.is_valid():
            replay_news = form.save()
            if replay_news.status_field == "Published":
                users_with_replay_news = User.objects.filter(replay_news=True)
                for user in users_with_replay_news:
                    msg_plain = render_to_string('replay_news/replay_news_mail.txt',
                                                 {'mail': user.user,
                                                  'text': replay_news.text})
                    msg_html = render_to_string('replay_news/replay_news_mail.html',
                                                {'mail': user.user,
                                                 'text': replay_news.text,
                                                 'image_url': 'http://127.0.0.1:8000/static/images/logo-no-background.png'})

                    send_mail(
                        subject='Shot wydarzeń od Banknoty',
                        from_email=settings.EMAIL_HOST_USER,
                        recipient_list=[user.user.email],
                        message=msg_plain,
                        html_message=msg_html,
                        fail_silently=False,
                    )
                messages.success(request,
                                 'Mail z shotem od Bankonty został wysłany',
                                 "alert alert-success alert-dismissible fade show mt-3")
            messages.success(request,
                             'Mail z shotem od Bankonty został edytowany',
                             "alert alert-success alert-dismissible fade show mt-3")
            return redirect('replay_news_admin_panel')
    else:
        form = ReplayNewsCreationForm(instance=replay_news)

    context = {
        'form': form,
    }
    return render(request, 'replay_news/replay_news_edit_admin_panel.html', context)


@user_passes_test(
        lambda u: u.is_authenticated and u.is_superuser,
        login_url='home'
    )
def replay_news_delete_admin_panel_view(request, pk):
    replay_news = get_object_or_404(ReplayNews, pk=pk)
    news = get_object_or_404(ReplayNews, pk=pk)
    if request.method == "POST":
        form = ReplayNewsDeleteEmailForm(request.POST, instance=replay_news)
        if form.is_valid():
            replay_news.delete()
            messages.success(request,
                             'Shot z wiadomością od Bankonty został usunięty',
                             "alert alert-success alert-dismissible fade show mt-3")
            return redirect('replay_news_admin_panel')
    else:
        form = ReplayNewsDeleteEmailForm(instance=replay_news)
    context = {
        'form': form,
        'news': news,
    }
    return render(request, 'replay_news/replay_news_delete_admin_panel.html', context)


@user_passes_test(
        lambda u: u.is_authenticated and u.is_superuser,
        login_url='home'
    )
def replay_news_user_manage_admin_panel_view(request):
    users = User.objects.all().order_by('user__id')
    paginator = Paginator(users, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    context = {
        'page_obj': page_obj,
    }
    return render(request, 'replay_news/replay_news_user_manage_admin_panel.html', context)


@user_passes_test(
        lambda u: u.is_authenticated and u.is_superuser,
        login_url='home'
    )
def replay_news_user_detail_admin_panel_view(request, pk):
    user = get_object_or_404(User, pk=pk)
    context = {
        'users': user,
    }
    return render(request, 'replay_news/replay_news_user_detail_admin_panel.html', context)


@user_passes_test(
        lambda u: u.is_authenticated and u.is_superuser,
        login_url='home'
    )
def replay_news_user_edit_admin_panel_view(request, pk):
    user = get_object_or_404(User, id=pk)
    if request.method == "POST":
        form = UserReplayNewsForm(request.POST, instance=user)
        if form.is_valid():
            form.save()
            messages.success(request,
                             'Ustawienia e-maila z shotem wiadomości od Banknoty zostały zaaktualizowane.',
                             "alert alert-success alert-dismissible fade show mt-3")
            return redirect('replay_news_user_manage_admin_panel')
    else:
        form = UserReplayNewsForm(instance=user)

    context = {
        'form': form,
        'users': user
    }
    return render(request, 'replay_news/replay_news_user_edit_admin_panel.html', context)


@user_passes_test(
        lambda u: u.is_authenticated and u.is_superuser,
        login_url='home'
    )
def development_news_add_view(request):
    form = DevelopmentNewsCreationForm(request.POST or None)
    if form.is_valid():
        development_news_instance = form.save()
        if development_news_instance.status_field == 'Published':
            users_with_development_news = User.objects.filter(development_news=True)
            for user in users_with_development_news:
                msg_plain = render_to_string('development_news/development_news_mail.txt',
                                             {'mail': user.user,
                                              'text': development_news_instance.text})
                msg_html = render_to_string('development_news/development_news_mail.html',
                                            {'mail': user.user,
                                             'text': development_news_instance.text,
                                             'image_url': 'http://127.0.0.1:8000/static/images/logo-no-background.png'})

                send_mail(
                    'Informacje o rozwoju i zmianach na Banknoty',
                    from_email=settings.EMAIL_HOST_USER,
                    recipient_list=[user.user.email],
                    message=msg_plain,
                    html_message=msg_html,
                    fail_silently=False,
                )
            messages.success(request, 'Mail z informacjami o rozwoju i zmianach na Bankonty został wysłany',
                             "alert alert-success alert-dismissible fade show mt-3")
        messages.success(request, 'Mail z informacjami o rozwoju i zmianach na Bankonty został utworzony',
                         "alert alert-success alert-dismissible fade show mt-3")
        return redirect('development_news_add')

    context = {
        'form': form,
    }
    return render(request, 'development_news/development_news_add.html', context)


@user_passes_test(
        lambda u: u.is_authenticated and u.is_superuser,
        login_url='home'
    )
def development_news_admin_panel_view(request):
    development_news = DevelopmentNews.objects.all().order_by('title')
    paginator = Paginator(development_news, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    context = {
        'page_obj': page_obj,
    }
    return render(request, 'development_news/development_news_admin_panel.html', context)


@user_passes_test(
        lambda u: u.is_authenticated and u.is_superuser,
        login_url='home'
    )
def development_news_detail_admin_panel_view(request, pk):
    development_news = get_object_or_404(DevelopmentNews, pk=pk)
    context = {
        'development_news': development_news,
    }
    return render(request, 'development_news/development_news_detail_admin_panel.html', context)


@user_passes_test(
        lambda u: u.is_authenticated and u.is_superuser,
        login_url='home'
    )
def development_news_edit_admin_panel_view(request, pk):
    development_news = get_object_or_404(DevelopmentNews, pk=pk)
    if request.method == "POST":
        form = DevelopmentNewsCreationForm(request.POST, instance=development_news)
        if form.is_valid():
            development_news = form.save()
            if development_news.status_field == "Published":
                users_with_development_news = User.objects.filter(development_news=True)
                for user in users_with_development_news:
                    msg_plain = render_to_string('development_news/development_news_mail.txt',
                                                 {'mail': user.user,
                                                  'text': development_news.text})
                    msg_html = render_to_string('development_news/development_news_mail.html',
                                                {'mail': user.user,
                                                 'text': development_news.text,
                                                 'image_url': 'http://127.0.0.1:8000/static/images/logo-no-background.png'})

                    send_mail(
                        subject='Informacje o rozwoju i zmianach na Banknoty',
                        from_email=settings.EMAIL_HOST_USER,
                        recipient_list=[user.user.email],
                        message=msg_plain,
                        html_message=msg_html,
                        fail_silently=False,
                    )
                messages.success(request,
                                 'Mail z informacjami o rozwoju i zmianach na Bankonty został wysłany',
                                 "alert alert-success alert-dismissible fade show mt-3")
            messages.success(request,
                             'Mail z informacjami o rozwoju i zmianach na Bankonty został edytowany',
                             "alert alert-success alert-dismissible fade show mt-3")
            return redirect('development_news_admin_panel')
    else:
        form = DevelopmentNewsCreationForm(instance=development_news)

    context = {
        'form': form,
    }
    return render(request, 'development_news/development_news_edit_admin_panel.html', context)


@user_passes_test(
        lambda u: u.is_authenticated and u.is_superuser,
        login_url='home'
    )
def development_news_delete_admin_panel_view(request, pk):
    development_news = get_object_or_404(DevelopmentNews, pk=pk)
    news = get_object_or_404(DevelopmentNews, pk=pk)
    if request.method == "POST":
        form = DevelopmentNewsDeleteEmailForm(request.POST, instance=development_news)
        if form.is_valid():
            development_news.delete()
            messages.success(request,
                             'Mail z informacjami o rozwoju i zmianach na Bankonty został usunięty',
                             "alert alert-success alert-dismissible fade show mt-3")
            return redirect('development_news_admin_panel')
    else:
        form = DevelopmentNewsDeleteEmailForm(instance=development_news)
    context = {
        'form': form,
        'news': news,
    }
    return render(request, 'development_news/development_news_delete_admin_panel.html', context)


@user_passes_test(
        lambda u: u.is_authenticated and u.is_superuser,
        login_url='home'
    )
def development_news_user_manage_admin_panel_view(request):
    users = User.objects.all().order_by('user__id')
    paginator = Paginator(users, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    context = {
        'page_obj': page_obj,
    }
    return render(request, 'development_news/development_news_user_manage_admin_panel.html', context)


@user_passes_test(
        lambda u: u.is_authenticated and u.is_superuser,
        login_url='home'
    )
def development_news_user_detail_admin_panel_view(request, pk):
    user = get_object_or_404(User, pk=pk)
    context = {
        'users': user,
    }
    return render(request, 'development_news/development_news_user_detail_admin_panel.html', context)


@user_passes_test(
        lambda u: u.is_authenticated and u.is_superuser,
        login_url='home'
    )
def development_news_user_edit_admin_panel_view(request, pk):
    user = get_object_or_404(User, id=pk)
    if request.method == "POST":
        form = UserDevelopmentNewsForm(request.POST, instance=user)
        if form.is_valid():
            form.save()
            messages.success(request,
                             'Ustawienia e-maila z informacjami o rozwoju i zmianach na Banknoty zostały zaaktualizowane.',
                             "alert alert-success alert-dismissible fade show mt-3")
            return redirect('development_news_user_manage_admin_panel')
    else:
        form = UserDevelopmentNewsForm(instance=user)

    context = {
        'form': form,
        'users': user
    }
    return render(request, 'development_news/development_news_user_edit_admin_panel.html', context)


def create_user(request):
    if request.method == 'POST':
        user_form = UserCreationForm(request.POST)
        profile_form = UserProfileForm(request.POST, request.FILES)
        if user_form.is_valid() and profile_form.is_valid():
            user = user_form.save(commit=False)
            user.set_password(user_form.cleaned_data['password'])
            user.save()
            profile = profile_form.save(commit=False)
            profile.user = user
            profile.save()
            messages.success(request,
                             'Użytkownik został utworzony',
                             "alert alert-success alert-dismissible fade show mt-3")
            return redirect('create_user')
    else:
        user_form = UserCreationForm()
        profile_form = UserProfileForm()
    return render(request, 'create_user.html', {'user_form': user_form, 'profile_form': profile_form})

