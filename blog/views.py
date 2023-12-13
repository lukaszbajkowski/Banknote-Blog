from django.contrib import messages
from django.core.mail import send_mail
from django.core.paginator import Paginator
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


# Funkcja odpowiedzialna za przekazanie danych do funkcji wysyłającej maile do użytkowników i przekazująca dane o
# odpowiednich powiadomieniach
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
