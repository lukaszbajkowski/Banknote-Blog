from django.contrib import messages
from django.core.mail import send_mail
from django.core.paginator import Paginator
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.template.loader import render_to_string

from blog.views_admin.admin_panel.admin_views import *
from .decorators import *
from .form import *
from .models import User as DjangoUser

# Stałe komunikaty
SUCCESS_MESSAGE = 'Dziękujemy za rejestrację do biuletynu.'
DUPLICATE_EMAIL_MESSAGE = 'Przepraszamy, ten e-mail już istnieje.'
UNSUBSCRIBE_SUCCESS_MESSAGE = 'Rezygnacja z biuletynu powiodła się'
INVALID_EMAIL_MESSAGE = 'Przepraszamy, ten e-mail nie istnieje'
SUCCESS_MESSAGE_CREATE = 'Biuletyn został utworzony'
PUBLISHED_SUCCESS_MESSAGE = 'Biuletyn został wysłany'
IMAGE_URL = 'http://127.0.0.1:8000/static/images/logo-no-background.png'
SUCCESS_DELETE_MESSAGE = 'Biuletyn został usunięty'
USER_SUCCESS_DELETE_MESSAGE = 'Użytkownik został usunięty'
SUCCESS_MESSAGE_EDIT = 'Mail został edytowany i wysłany'
PUBLISHED_SUCCESS_MESSAGE_EDIT = 'Mail został edytowany i wysłany oraz opublikowany'


# Funkcja obsługująca proces rejestracji do biuletynu z alertem
def handle_newsletter_signup(request, newsletter_form):
    response_data = {'success': False}

    if newsletter_form.is_valid():
        instance = newsletter_form.save(commit=False)
        if not NewsletterUser.objects.filter(email=instance.email).exists():
            instance.save()
            send_signup_mail(instance.email)
            response_data['success'] = True

    return response_data


# Funkcja obsługująca proces rejestracji do biuletynu z formularzem zamieniającym się w alert po wysłaniu go
def process_newsletter_signup(request, form_class, template):
    category = Category.objects.all()
    blog = Blog.objects.filter(publiction_status=True).order_by('-date_posted')[1:]
    form = form_class(request.POST or None)

    if form.is_valid():
        instance = form.save(commit=False)
        email = instance.email
        if NewsletterUser.objects.filter(email=email).exists():
            messages.warning(
                request,
                DUPLICATE_EMAIL_MESSAGE,
                "alert alert-warning alert-dismissible fade show"
            )
        else:
            instance.save()
            messages.success(
                request,
                SUCCESS_MESSAGE,
                "alert alert-success alert-dismissible fade show"
            )
            send_signup_mail(email)

    context = {
        'form': form,
        'category': category,
        'blog': blog
    }
    return render(
        request,
        template,
        context
    )


# Funkcja obsługująca proces usuwania rekordu
def process_delete(request, pk, model_class, form_class, template, success_message, redirect_url):
    instance = get_object_or_404(model_class, pk=pk)
    if request.method == "POST":
        form = form_class(request.POST, instance=instance)
        if form.is_valid():
            instance.delete()
            messages.success(
                request,
                success_message,
                "alert alert-success alert-dismissible fade show mt-3"
            )
            return redirect(redirect_url)
    else:
        form = form_class(instance=instance)

    context = {
        'form': form,
        'news': instance
    }
    return render(
        request,
        template,
        context
    )


# Funkcja obsługująca proces zapisu formularza
def process_form_submission(request, form_class, template, redirect_view_name, message_text=None):
    if request.method == 'POST':
        form = form_class(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(
                request,
                message_text,
                "alert alert-success alert-dismissible fade show mt-3"
            )
            return redirect(redirect_view_name)
    else:
        form = form_class()

    context = {
        'form': form
    }
    return render(
        request,
        template,
        context
    )


# Widok edycji encji w panelu administratora
def edit_entity_admin_panel_view(request, pk, model_class, form_class, template_name, success_message, redirect_name,
                                 extra_context=None):
    instance = get_object_or_404(model_class, pk=pk)

    if request.method == "POST":
        form = form_class(
            request.POST,
            request.FILES,
            instance=instance
        )
        if form.is_valid():
            form.save()
            messages.success(
                request,
                success_message,
                "alert alert-success alert-dismissible fade show mt-3"
            )
            return redirect(redirect_name)
    else:
        form = form_class(instance=instance)

    context = {
        'form': form,
    }

    if extra_context:
        context.update(extra_context)

    return render(
        request,
        template_name,
        context
    )


# Widok usuwania encji w panelu administratora
def process_delete_admin_panel_view(request, pk, model, form_class, template, success_message, redirect_view_name):
    instance = get_object_or_404(model, pk=pk)
    news = instance

    if request.method == "POST":
        form = form_class(request.POST, instance=instance)
        if form.is_valid():
            if hasattr(instance, 'user') and instance.user.email:
                delete_newsletter_user(instance.user.email)
            instance.delete()
            messages.success(request, success_message, "alert alert-success alert-dismissible fade show mt-3")
            return redirect(redirect_view_name)
    else:
        form = form_class(instance=instance)

    context = {
        'form': form,
        'news': news
    }
    return render(
        request,
        template,
        context
    )


# Funkcja wysyłająca e-maile z biuletynami
def send_newsletter_emails(newsletter):
    for email in newsletter.email.all():
        msg_plain = render_to_string(
            'AdminTemplates/Newsletter/Newsletter/Mail/NewsletterMail.txt',
            {
                'mail': email,
                'text': newsletter.text
            }
        )
        msg_html = render_to_string(
            'AdminTemplates/Newsletter/Newsletter/Mail/NewsletterMail.html',
            {
                'mail': email,
                'text': newsletter.text,
                'image_url': IMAGE_URL
            }
        )
        send_mail(
            subject=newsletter.title,
            from_email=settings.EMAIL_HOST_USER,
            recipient_list=[email],
            message=msg_plain,
            html_message=msg_html,
            fail_silently=False
        )


# Funkcja usuwająca użytkownika z biuletynu
def delete_newsletter_user(email):
    user_exists = NewsletterUser.objects.filter(email=email).exists()
    if user_exists:
        NewsletterUser.objects.filter(email=email).delete()
    return user_exists


# Funkcja wysyłająca e-mail o rezygnacji z biuletynu
def send_unsubscribe_mail(email):
    subject = 'Rezygnacja z biuletynu.'
    from_email = settings.EMAIL_HOST_USER
    to_email = [email]
    msg_plain = render_to_string(
        'AdminTemplates/Newsletter/Newsletter/Mail/NewsletterUnsubscribeMail.txt',
        {
            'mail': email
        }
    )
    msg_html = render_to_string(
        'AdminTemplates/Newsletter/Newsletter/Mail/NewsletterUnsubscribeMail.html',
        {
            'mail': str(email),
            'image_url': IMAGE_URL
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


# Funkcja wysyłająca e-mail potwierdzający rejestrację do biuletynu
def send_signup_mail(email):
    subject = 'Dziękujemy za rejestrację do biuletynu.'
    from_email = settings.EMAIL_HOST_USER
    to_email = [email]
    msg_plain = render_to_string(
        'AdminTemplates/Newsletter/Newsletter/Mail/NewsletterSingUpMail.txt',
        {
            'mail': email
        }
    )
    msg_html = render_to_string(
        'AdminTemplates/Newsletter/Newsletter/Mail/NewsletterSingUpMail.html',
        {
            'mail': str(email),
            'image_url': IMAGE_URL
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


# Funkcja wysyłająca e-maile z newsletterami do użytkowników
def send_newsletters_mail(subject, user, mail, mail_context):
    msg_plain = render_to_string(mail + '.txt', mail_context)
    msg_html = render_to_string(mail + '.html', mail_context)

    send_mail(
        subject=subject,
        from_email=settings.EMAIL_HOST_USER,
        recipient_list=[user.user.email],
        message=msg_plain,
        html_message=msg_html,
        fail_silently=False,
    )


def content_editorial_admin_panel(request, instance, userfield, mail_subject, mail, status):
    if instance.status_field == "Published":
        users_with_news = DjangoUser.objects.filter(**{userfield: True})
        for user in users_with_news:
            mail_context = {
                'mail': user.user,
                'text': instance.text,
                'image_url': IMAGE_URL,
            }
            send_newsletters_mail(mail_subject, user, mail, mail_context)
        messages.success(
            request,
            f'Mail {mail_subject.lower()} został wysłany',
            "alert alert-success alert-dismissible fade show mt-3"
        )
    messages.success(
        request,
        f'Mail {mail_subject.lower()} został {status}',
        "alert alert-success alert-dismissible fade show mt-3"
    )


# Widok edycji treści w panelu administratora
def edit_admin_panel_view(request, pk, model_class, userfield, form_class, content_template, mail, mail_subject):
    instance = get_object_or_404(model_class, pk=pk)
    if request.method == "POST":
        form = form_class(request.POST, instance=instance)
        if form.is_valid():
            instance = form.save()
            content_editorial_admin_panel(instance, userfield, mail_subject, mail, "edytowany")
            return redirect(userfield + '_admin_panel')
    else:
        form = form_class(instance=instance)

    context = {
        'form': form,
    }
    return render(
        request,
        content_template,
        context
    )


# Widok dodawania treści w panelu administratora
def newsletter_add_panel_view(request, userfield, form_class, content_template, mail, mail_subject):
    form = form_class(request.POST or None)
    if form.is_valid():
        instance = form.save()
        content_editorial_admin_panel(instance, userfield, mail_subject, mail, "utworzony")
        return redirect(userfield + '_add')

    context = {
        'form': form,
    }
    return render(
        request,
        content_template,
        context
    )


# Funkcja generująca kontekst paginacji
def get_paginated_context(request, queryset, items_per_page=10):
    paginator = Paginator(queryset, items_per_page)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'page_obj': page_obj,
    }
    return context


# Widok strony głównej
def home_view(request):
    blog_first = Blog.objects.all().filter(publiction_status=True).order_by('-date_posted')[:1]
    blog = Blog.objects.all().filter(publiction_status=True).order_by('-date_posted')[1:]
    category = Category.objects.all()
    paginator = Paginator(blog, 12)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    favorite_blogs = Blog.objects.filter(publiction_status=True, favorite=True).order_by('?')
    newsletter_form = NewsletterUserSignUpForm(request.POST or None)

    if request.user.is_authenticated:
        try:
            DjangoUser.objects.get(user=request.user)
        except DjangoUser.DoesNotExist:
            return redirect('edit_profile')

    if request.method == 'POST':
        response_data = handle_newsletter_signup(request, newsletter_form)
        return JsonResponse(response_data)

    context = {
        'blog_first': blog_first,
        'blog': blog,
        'category': category,
        'page_obj': page_obj,
        'favorite_blogs': favorite_blogs,
        'form': newsletter_form,
    }
    return render(
        request,
        'UserTemplates/Home/Home.html',
        context
    )


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


# Widok formularza kontaktowego
def contact_view(request):
    blog = Blog.objects.filter(publiction_status=True).order_by('-date_posted')[1:]
    category = Category.objects.all()

    if request.method == 'POST':
        form = ContactForm(request.POST)
        if form.is_valid():
            name = form.cleaned_data['name']
            email = form.cleaned_data['email']
            message = form.cleaned_data['message']
            image_url = IMAGE_URL

            subject = 'Wiadomość z formularza kontaktowego'
            subject_user = 'Potwierdzenie wiadomości z formularza kontaktowego'
            context = {
                'name': name,
                'mail': email,
                'message': message,
                'image_url': image_url,
            }
            msg_plain = render_to_string('Contact/Mail/ContactMailToAdmin.txt', context)
            msg_html = render_to_string('Contact/Mail/ContactMailToAdmin.html', context)

            msg_plain_user = render_to_string('Contact/Mail/ContactMailToUser.txt', context)
            msg_html_user = render_to_string('Contact/Mail/ContactMailToUser.html', context)

            send_mail(
                subject, msg_plain, email, [settings.EMAIL_HOST_USER], html_message=msg_html, fail_silently=False
            )

            send_mail(
                subject_user, msg_plain_user, settings.EMAIL_HOST_USER, [email], html_message=msg_html_user,
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
    return render(
        request,
        'Contact/ContactPage.html',
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


# Widok regulaminu
def terms_conditions_view(request):
    category = Category.objects.all()
    blog = Blog.objects.all().filter(publiction_status=True).order_by('-date_posted')[1:]

    context = {
        'category': category,
        'blog': blog,
    }
    return render(
        request,
        'UserTemplates/TermsConditions/TermsConditions.html',
        context
    )


# Widok polityki prywatności
def privacy_policy_view(request):
    category = Category.objects.all()
    blog = Blog.objects.all().filter(publiction_status=True).order_by('-date_posted')[1:]

    context = {
        'category': category,
        'blog': blog,
    }
    return render(
        request,
        'UserTemplates/PrivacyPolicy/PrivacyPolicy.html',
        context
    )


# Widok strony "O Nas"
def about_page_view(request):
    category = Category.objects.all()
    blog = Blog.objects.all().filter(publiction_status=True).order_by('-date_posted')[1:]

    context = {
        'category': category,
        'blog': blog,
    }
    return render(
        request,
        'UserTemplates/About/About.html',
        context
    )


# Widok rejestracji do biuletynu
def newsletter_signup_view(request):
    return process_newsletter_signup(
        request,
        NewsletterUserSignUpForm,
        'UserTemplates/NewsletterRegister/NewsletterSingUp.html',
    )


# Widok rezygnacji z biuletynu
def newsletter_unsubscribe_view(request):
    category = Category.objects.all()
    blog = Blog.objects.filter(publiction_status=True).order_by('-date_posted')[1:]
    form = NewsletterUserSignUpForm(request.POST or None)

    if form.is_valid():
        instance = form.save(commit=False)
        email = instance.email
        if delete_newsletter_user(email):
            send_unsubscribe_mail(email)
            messages.success(
                request,
                UNSUBSCRIBE_SUCCESS_MESSAGE,
                "alert alert-success alert-dismissible fade show"
            )
        else:
            messages.warning(
                request,
                INVALID_EMAIL_MESSAGE,
                "alert alert-danger alert-dismissible fade show"
            )

    context = {
        'form': form,
        'category': category,
        'blog': blog
    }
    return render(request, 'UserTemplates/NewsletterDelete/NewsletterDelete.html', context)
