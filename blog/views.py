from django.contrib import messages
from django.core.mail import send_mail
from django.core.paginator import Paginator
from django.db.models import Count
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.template.loader import render_to_string

from blog.views_admin.admin_panel.admin_views import *
from .decorators import *
from .form import *
from .form_users import *
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


# Funkcja obsługująca proces rejestracji do biuletynu
def process_newsletter_signup(request, form_class, template, admin_panel_template):
    category = Category.objects.all()
    blog = Blog.objects.filter(publiction_status=True).order_by('-date_posted')[1:]
    form = form_class(request.POST or None)

    if form.is_valid():
        instance = form.save(commit=False)
        email = instance.email
        # if delete_newsletter_user(email):
        if NewsletterUser.objects.filter(email=email).exists():
            messages.warning(request, DUPLICATE_EMAIL_MESSAGE, "alert alert-warning alert-dismissible fade show")
        else:
            instance.save()
            messages.success(request, SUCCESS_MESSAGE, "alert alert-success alert-dismissible fade show")
            send_signup_mail(email)

    context = {
        'form': form,
        'category': category,
        'blog': blog
    }

    if admin_panel_template:
        return render(request, admin_panel_template, context)
    else:
        return render(request, template, context)


# Funkcja obsługująca proces rejestracji do biuletynu w sekcji bloga
def process_newsletter_in_blog_signup(request, form_class):
    if request.method == 'POST':
        form = form_class(request.POST)
        if form.is_valid():
            instance = form.save(commit=False)
            if NewsletterUser.objects.filter(email=instance.email).exists():
                return JsonResponse({'success': False})
            else:
                instance.save()
                send_newsletter_signup_email(instance.email)
                return JsonResponse({'success': True})
        else:
            return JsonResponse({'success': False})
    return None


# Funkcja obsługująca proces usuwania rekordu
def process_delete(request, pk, model_class, form_class, template, success_message, redirect_url):
    instance = get_object_or_404(model_class, pk=pk)
    if request.method == "POST":
        form = form_class(request.POST, instance=instance)
        if form.is_valid():
            instance.delete()
            messages.success(request, success_message, "alert alert-success alert-dismissible fade show mt-3")
            return redirect(redirect_url)
    else:
        form = form_class(instance=instance)

    context = {
        'form': form,
        'news': instance
    }
    return render(request, template, context)


# Funkcja obsługująca proces zapisu formularza
def process_form_submission(request, form_class, template, redirect_view_name, message_text=None):
    if request.method == 'POST':
        form = form_class(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, message_text, "alert alert-success alert-dismissible fade show mt-3")
            return redirect(redirect_view_name)
    else:
        form = form_class()
    context = {
        'form': form
    }
    return render(request, template, context)


# Widok edycji encji w panelu administratora
def edit_entity_admin_panel_view(request, pk, model_class, form_class, template_name, success_message, redirect_name,
                                 extra_context=None):
    instance = get_object_or_404(model_class, pk=pk)

    if request.method == "POST":
        form = form_class(request.POST, request.FILES, instance=instance)
        if form.is_valid():
            entity = form.save()
            messages.success(request, success_message, "alert alert-success alert-dismissible fade show mt-3")
            return redirect(redirect_name)
    else:
        form = form_class(instance=instance)

    context = {
        'form': form,
    }

    if extra_context:
        context.update(extra_context)

    return render(request, template_name, context)


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
    return render(request, template, context)


# Funkcja wysyłająca e-maile z biuletynami
def send_newsletter_emails(newsletter):
    for email in newsletter.email.all():
        msg_plain = render_to_string('AdminTemplates/Newsletter/Mail/NewsletterMail.txt',
                                     {'mail': email, 'text': newsletter.text})
        msg_html = render_to_string('AdminTemplates/Newsletter/Mail/NewsletterMail.html',
                                    {'mail': email, 'text': newsletter.text, 'image_url': IMAGE_URL})
        send_mail(subject=newsletter.title,
                  from_email=settings.EMAIL_HOST_USER,
                  recipient_list=[email],
                  message=msg_plain,
                  html_message=msg_html,
                  fail_silently=False)


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
    msg_plain = render_to_string('AdminTemplates/Newsletter/Mail/NewsletterUnsubscribeMail.txt', {'mail': email})
    msg_html = render_to_string('AdminTemplates/Newsletter/Mail/NewsletterUnsubscribeMail.html',
                                {'mail': str(email), 'image_url': IMAGE_URL})
    send_mail(subject, msg_plain, from_email, to_email, html_message=msg_html, fail_silently=False)


# Funkcja wysyłająca e-mail potwierdzający rejestrację do biuletynu
def send_signup_mail(email):
    subject = 'Dziękujemy za rejestrację do biuletynu.'
    from_email = settings.EMAIL_HOST_USER
    to_email = [email]
    msg_plain = render_to_string('AdminTemplates/Newsletter/Mail/NewsletterSingUpMail.txt', {'mail': email})
    msg_html = render_to_string('AdminTemplates/Newsletter/Mail/NewsletterSingUpMail.html',
                                {'mail': str(email),
                                 'image_url': IMAGE_URL})
    send_mail(subject, msg_plain, from_email, to_email, html_message=msg_html, fail_silently=False)


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


# Widok edycji treści w panelu administratora
def edit_admin_panel_view(request, pk, model_class, userfield, form_class, content_template, mail, mail_subject):
    instance = get_object_or_404(model_class, pk=pk)
    if request.method == "POST":
        form = form_class(request.POST, instance=instance)
        if form.is_valid():
            instance = form.save()
            if instance.status_field == "Published":
                users_with_news = DjangoUser.objects.filter(**{userfield: True})
                for user in users_with_news:
                    mail_context = {
                        'mail': user.user,
                        'text': instance.text,
                        'image_url': IMAGE_URL,
                    }
                    send_newsletters_mail(mail_subject, user, mail, mail_context)
                messages.success(request,
                                 f'Mail {mail_subject.lower()} został wysłany',
                                 "alert alert-success alert-dismissible fade show mt-3")
            messages.success(request,
                             f'Mail {mail_subject.lower()} został edytowany',
                             "alert alert-success alert-dismissible fade show mt-3")
            return redirect(userfield + '_admin_panel')
    else:
        form = form_class(instance=instance)

    context = {
        'form': form,
    }
    return render(request, content_template, context)


# Widok dodawania treści w panelu administratora
def newsletter_add_panel_view(request, userfield, form_class, content_template, mail, mail_subject):
    form = form_class(request.POST or None)
    if form.is_valid():
        instance = form.save()
        if instance.status_field == 'Published':
            users_with_news = DjangoUser.objects.filter(**{userfield: True})
            for user in users_with_news:
                mail_context = {
                    'mail': user.user,
                    'text': instance.text,
                    'image_url': IMAGE_URL,
                }
                send_newsletters_mail(mail_subject, user, mail, mail_context)
            messages.success(request,
                             f'Mail {mail_subject.lower()} został wysłany',
                             "alert alert-success alert-dismissible fade show mt-3")
        messages.success(request,
                         f'Mail {mail_subject.lower()} został utworzony',
                         "alert alert-success alert-dismissible fade show mt-3")
        return redirect(userfield + '_add')

    context = {
        'form': form,
    }
    return render(request, content_template, context)


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
            user_extension = DjangoUser.objects.get(user=request.user)
        except DjangoUser.DoesNotExist:
            return redirect('edit_profile')

    if request.method == 'POST':
        if newsletter_form.is_valid():
            instance = newsletter_form.save(commit=False)
            if NewsletterUser.objects.filter(email=instance.email).exists():
                return JsonResponse({'success': False})
            else:
                instance.save()
                send_signup_mail(instance.email)
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
    return render(request, 'UserTemplates/Home/Home.html', context)


# Widok artykułu
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
            instance = newsletter_form.save(commit=False)
            if NewsletterUser.objects.filter(email=instance.email).exists():
                return JsonResponse({'success': False})
            else:
                instance.save()
                send_signup_mail(instance.email)
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
    return render(request, 'UserTemplates/Article/Article.html', context)


# Widok listy artykułów
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
                send_signup_mail(instance.email)
                return JsonResponse({'success': True})
        else:
            return JsonResponse({'success': False})

    context = {
        'page_obj': page_obj,
        'form': newsletter_form,
        'blog': blog,
        'category': category,
    }
    return render(request, 'UserTemplates/ArticlesList/ArticlesList.html', context)


# Widok formularza kontaktowego
def ContactView(request):
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
    return render(request, 'Contact/ContactPage.html', context)


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
    return render(request, 'UserTemplates/Author/Author.html', context)


# Widok kategorii
def CategoryView(request, pk):
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

    return render(request, 'UserTemplates/SingleCategory/Category.html', context)


# Widok listy kategorii
def CategoryListView(request):
    categories = Category.objects.all()
    blog = Blog.objects.filter(publiction_status=True).order_by('-date_posted')[1:]
    newsletter_form = NewsletterUserSignUpForm(request.POST or None)

    if request.method == 'POST':
        if newsletter_form.is_valid():
            instance = newsletter_form.save(commit=False)
            if NewsletterUser.objects.filter(email=instance.email).exists():
                return JsonResponse({'success': False})
            else:
                instance.save()
                send_signup_mail(instance.email)
                return JsonResponse({'success': True})
        else:
            return JsonResponse({'success': False})

    context = {
        'categories': categories,
        'posts': blog,
        'form': newsletter_form,
        'blog': blog,
        'category': categories,
    }
    return render(request, 'UserTemplates/CategoriesList/CategoriesList.html', context)


# Widok listy profili użytkowników
def ProfileListView(request):
    author = Author.objects.all()
    category = Category.objects.all()
    blog = Blog.objects.filter(publiction_status=True).order_by('-date_posted')[1:]
    newsletter_form = NewsletterUserSignUpForm(request.POST or None)

    if request.method == 'POST':
        if newsletter_form.is_valid():
            instance = newsletter_form.save(commit=False)
            if NewsletterUser.objects.filter(email=instance.email).exists():
                return JsonResponse({'success': False})
            else:
                instance.save()
                send_signup_mail(instance.email)
                return JsonResponse({'success': True})
        else:
            return JsonResponse({'success': False})

    context = {
        'author': author,
        'category': category,
        'blog': blog,
        'form': newsletter_form,
    }
    return render(request, 'UserTemplates/Authors/Authors.html', context)


# Widok regulaminu
def TermsConditionsView(request):
    category = Category.objects.all()
    blog = Blog.objects.all().filter(publiction_status=True).order_by('-date_posted')[1:]

    context = {
        'category': category,
        'blog': blog,
    }
    return render(request, 'UserTemplates/TermsConditions/TermsConditions.html', context)


# Widok polityki prywatności
def PrivacyPolicyView(request):
    category = Category.objects.all()
    blog = Blog.objects.all().filter(publiction_status=True).order_by('-date_posted')[1:]

    context = {
        'category': category,
        'blog': blog,
    }
    return render(request, 'UserTemplates/PrivacyPolicy/PrivacyPolicy.html', context)


# Widok strony "O Nas"
def AboutPageView(request):
    category = Category.objects.all()
    blog = Blog.objects.all().filter(publiction_status=True).order_by('-date_posted')[1:]

    context = {
        'category': category,
        'blog': blog,
    }
    return render(request, 'UserTemplates/About/About.html', context)


# Widok rejestracji do biuletynu
def newsletter_signup_view(request):
    return process_newsletter_signup(request, NewsletterUserSignUpForm,
                                     'UserTemplates/NewsletterRegister/NewsletterSingUp.html', None)


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
            messages.success(request, UNSUBSCRIBE_SUCCESS_MESSAGE, "alert alert-success alert-dismissible fade show")
        else:
            messages.warning(request, INVALID_EMAIL_MESSAGE, "alert alert-danger alert-dismissible fade show")

    context = {
        'form': form,
        'category': category,
        'blog': blog
    }
    return render(request, 'UserTemplates/NewsletterDelete/NewsletterDelete.html', context)


# Widok dodawania aplikacji społecznej (dla superusera)
@superuser_required
def social_app_add_view(request):
    return process_form_submission(request, SocialAppForm,
                                   'AdminTemplates/SocialmediaAccounts/SocialApp/SocialAppAddAdmin.html',
                                   'social_app_add',
                                   'Aplikacja społeczna została dodana.')


# Widok zarządzania aplikacjami społecznymi (dla superusera)
@superuser_required
def social_app_admin_panel_view(request):
    social_apps = SocialApp.objects.all().order_by('id')
    context = get_paginated_context(request, social_apps, 10)
    return render(request, 'AdminTemplates/SocialmediaAccounts/SocialApp/SocialAppManageAdmin.html', context)


# Widok szczegółów aplikacji społecznej (dla superusera)
@superuser_required
def social_app_detail_admin_panel_view(request, pk):
    social_apps = get_object_or_404(SocialApp, pk=pk)
    context = {
        'social_app': social_apps,
    }
    return render(request, 'AdminTemplates/SocialmediaAccounts/SocialApp/SocialAppDetailAdmin.html', context)


# Widok edycji aplikacji społecznej (dla superusera)
@superuser_required
def social_app_edit_admin_panel_view(request, pk):
    social_apps = get_object_or_404(SocialApp, pk=pk)
    return edit_entity_admin_panel_view(
        request,
        pk,
        model_class=SocialApp,
        form_class=SocialAppForm,
        template_name='AdminTemplates/SocialmediaAccounts/SocialApp/SocialAppEditAdmin.html',
        success_message='Aplikacja społeczna została edytowana.',
        redirect_name='social_app_admin_panel',
        extra_context={
            'social_app': social_apps,
        }
    )


# Widok usuwania aplikacji społecznej (dla superusera)
@superuser_required
def social_app_delete_admin_panel_view(request, pk):
    return process_delete_admin_panel_view(
        request, pk, SocialApp, SocialAppDeleteEmailForm,
        'AdminTemplates/SocialmediaAccounts/SocialApp/SocialAppDeleteAdmin.html',
        'Aplikacja społeczna została usunięta',
        'social_app_admin_panel'
    )


# Widok dodawania tokena aplikacji społecznej (dla superusera)
@superuser_required
def social_token_add_view(request):
    return process_form_submission(request, SocialTokenForm,
                                   'AdminTemplates/SocialmediaAccounts/SocialToken/SocialTokenAddAdmin.html',
                                   'social_token_add',
                                   'Token aplikacji społecznościowej został dodany.')


# Widok zarządzania tokenami aplikacji społecznej (dla superusera)
@superuser_required
def social_token_admin_panel_view(request):
    social_tokens = SocialToken.objects.all().order_by('id')
    context = get_paginated_context(request, social_tokens, 10)
    return render(request, 'AdminTemplates/SocialmediaAccounts/SocialToken/SocialTokenManageAdmin.html', context)


# Widok szczegółów tokena aplikacji społecznej (dla superusera)
@superuser_required
def social_token_detail_admin_panel_view(request, pk):
    social_tokens = get_object_or_404(SocialToken, pk=pk)
    context = {
        'social_token': social_tokens,
    }
    return render(request, 'AdminTemplates/SocialmediaAccounts/SocialToken/SocialTokenDetailAdmin.html', context)


# Widok edycji tokena aplikacji społecznej (dla superusera)
@superuser_required
def social_token_edit_admin_panel_view(request, pk):
    social_tokens = get_object_or_404(SocialToken, pk=pk)
    return edit_entity_admin_panel_view(
        request,
        pk,
        model_class=SocialToken,
        form_class=SocialTokenForm,
        template_name='AdminTemplates/SocialmediaAccounts/SocialToken/SocialTokenEditAdmin.html',
        success_message='Token aplikacji społecznościowej został edytowany.',
        redirect_name='social_token_admin_panel',
        extra_context={
            'social_token': social_tokens,
        }
    )


# Widok usuwania tokena aplikacji społecznej (dla superusera)
@superuser_required
def social_token_delete_admin_panel_view(request, pk):
    return process_delete_admin_panel_view(
        request, pk, SocialToken, SocialTokenDeleteEmailForm,
        'AdminTemplates/SocialmediaAccounts/SocialToken/SocialTokenDeleteAdmin.html',
        'Token aplikacji społecznościowej został usunięty',
        'social_token_admin_panel'
    )


# Widok dodawania konta aplikacji społecznej (dla superusera)
@superuser_required
def social_account_add_view(request):
    return process_form_submission(request, SocialAccountForm,
                                   'AdminTemplates/SocialmediaAccounts/SocialAccount/SocialAccountAddAdmin.html',
                                   'social_account_add',
                                   'Konto aplikacji społecznościowej zostało dodane.')


# Widok zarządzania kontami aplikacji społecznej (dla superusera)
@superuser_required
def social_account_admin_panel_view(request):
    social_accounts = SocialAccount.objects.all().order_by('id')
    context = get_paginated_context(request, social_accounts, 10)
    return render(request, 'AdminTemplates/SocialmediaAccounts/SocialAccount/SocialAccountManageAdmin.html', context)


# Widok szczegółów konta aplikacji społecznej (dla superusera)
@superuser_required
def social_account_detail_admin_panel_view(request, pk):
    social_accounts = get_object_or_404(SocialAccount, pk=pk)
    context = {
        'social_account': social_accounts,
    }
    return render(request, 'AdminTemplates/SocialmediaAccounts/SocialAccount/SocialAccountDetailAdmin.html', context)


# Widok edycji konta aplikacji społecznej (dla superusera)
@superuser_required
def social_account_edit_admin_panel_view(request, pk):
    social_accounts = get_object_or_404(SocialAccount, pk=pk)
    return edit_entity_admin_panel_view(
        request,
        pk,
        model_class=SocialAccount,
        form_class=SocialAccountForm,
        template_name='AdminTemplates/SocialmediaAccounts/SocialAccount/SocialAccountEditAdmin.html',
        success_message='Konto aplikacji społecznościowej zostało edytowane.',
        redirect_name='social_account_admin_panel',
        extra_context={
            'social_account': social_accounts,
        }
    )


# Widok usuwania konta aplikacji społecznej (dla superusera)
@superuser_required
def social_account_delete_admin_panel_view(request, pk):
    return process_delete_admin_panel_view(
        request, pk, SocialAccount, SocialAccountDeleteEmailForm,
        'AdminTemplates/SocialmediaAccounts/SocialAccount/SocialAccountDeleteAdmin.html',
        'Konto aplikacji społecznościowej zostało usunięte',
        'social_account_admin_panel'
    )
