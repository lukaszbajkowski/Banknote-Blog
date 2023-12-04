from django.contrib import messages
from django.contrib.auth import update_session_auth_hash
from django.core.mail import send_mail
from django.core.paginator import Paginator
from django.db.models import Count
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect
from django.template.loader import render_to_string

from .admin_views import *
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


# Dekorator sprawdzający uprawnienia superusera
def superuser_required(view_func):
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        if request.user.is_authenticated and request.user.is_superuser:
            return view_func(request, *args, **kwargs)
        else:
            return redirect('home')

    return _wrapped_view


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
def HomeView(request):
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


# Widok tworzenia biuletynu (dla superusera)
@superuser_required
def newsletter_creation_view(request):
    form = NewsletterCreationForm(request.POST or None)
    if form.is_valid():
        instance = form.save()
        newsletter = Newsletter.objects.get(id=instance.id)

        def send_newsletter(emails, newsletter):
            subject = newsletter.title
            text_template = 'AdminTemplates/Newsletter/Mail/NewsletterMail.txt'
            html_template = 'AdminTemplates/Newsletter/Mail/NewsletterMail.html'
            send_custom_emails(emails, subject, text_template, html_template)

        if newsletter.status_field == "Published":
            users = User.objects.filter(subscribed=True)
            emails = [user.email for user in users]
            send_newsletter(emails, newsletter)
            messages.success(request, PUBLISHED_SUCCESS_MESSAGE_EDIT,
                             "alert alert-success alert-dismissible fade show mt-3")
        else:
            messages.success(request, SUCCESS_MESSAGE_EDIT, "alert alert-success alert-dismissible fade show mt-3")
        return redirect('newsletter_creation')

    context = {
        'form': form,
    }
    return render(request, 'AdminTemplates/Newsletter/Newsletter/NewsletterAddAdmin.html', context)


# Widok dodawania użytkownika do biuletynu (dla superusera)
@superuser_required
def newsletter_add_user_view(request):
    return process_newsletter_signup(request, NewsletterAddUserForm,
                                     'AdminTemplates/Newsletter/Newsletter/NewsletterSingUpAdmin.html',
                                     'AdminTemplates/Newsletter/Newsletter/NewsletterSingUpAdmin.html')


# Widok usuwania użytkownika z biuletynu (dla superusera)
@superuser_required
def newsletter_remove_user_view(request):
    form = NewsletterAddUserForm(request.POST or None)
    if form.is_valid():
        instance = form.save(commit=False)
        email = instance.email
        if delete_newsletter_user(email):
            send_unsubscribe_mail(email)
            messages.success(request, UNSUBSCRIBE_SUCCESS_MESSAGE,
                             "alert alert-success alert-dismissible fade show mt-3")
        else:
            messages.warning(request, INVALID_EMAIL_MESSAGE, "alert alert-danger alert-dismissible fade show mt-3")

    context = {
        'form': form
    }
    return render(request, 'AdminTemplates/Newsletter/Newsletter/NewsletterUnsubscribeAdmin.html', context)


# Widok zarządzania biuletynami (dla superusera)
@superuser_required
def newsletter_manage_admin_panel_view(request):
    newsletter = Newsletter.objects.all()
    context = get_paginated_context(request, newsletter, 10)
    return render(request, 'AdminTemplates/Newsletter/Newsletter/NewsletterManageAdmin.html', context)


# Widok szczegółów biuletynu (dla superusera)
@superuser_required
def newsletter_detail_admin_panel_view(request, pk):
    newsletter = get_object_or_404(Newsletter, pk=pk)
    context = {
        'newsletter': newsletter,
    }
    return render(request, 'AdminTemplates/Newsletter/Newsletter/NewsletterDetaliAdmin.html', context)


# Widok edycji biuletynu (dla superusera)
@superuser_required
def newsletter_edit_admin_panel_view(request, pk):
    newsletter = get_object_or_404(Newsletter, pk=pk)
    if request.method == "POST":
        form = NewsletterCreationForm(request.POST, instance=newsletter)
        if form.is_valid():
            newsletter = form.save()
            if newsletter.status_field == "Published":
                send_newsletter_emails(newsletter)
                messages.success(request, PUBLISHED_SUCCESS_MESSAGE,
                                 "alert alert-success alert-dismissible fade show mt-3")
            messages.success(request, 'Biuletyn został edytowany',
                             "alert alert-success alert-dismissible fade show mt-3")
            return redirect('newsletter_admin_panel')
    else:
        form = NewsletterCreationForm(instance=newsletter)

    context = {
        'form': form
    }
    return render(request, 'AdminTemplates/Newsletter/Newsletter/NewsletterEditAdmin.html', context)


# Widok usuwania biuletynu (dla superusera)
@superuser_required
def newsletter_delete_admin_panel_view(request, pk):
    return process_delete(request, pk, Newsletter, NewsletterDeleteForm,
                          'AdminTemplates/Newsletter/Newsletter/NewsletterDeleteAdmin.html',
                          SUCCESS_DELETE_MESSAGE, 'newsletter_admin_panel')


# Widok zarządzania użytkownikami newslettera (dla superusera)
@superuser_required
def newsletter_user_manage_admin_panel_view(request):
    newsletter = NewsletterUser.objects.all()
    context = get_paginated_context(request, newsletter, 10)
    return render(request, 'AdminTemplates/Newsletter/Newsletter/NewsletterUserManageAdmin.html', context)


# Widok szczegółów użytkownika newslettera (dla superusera)
@superuser_required
def newsletter_user_detail_admin_panel_view(request, pk):
    newsletter = get_object_or_404(NewsletterUser, pk=pk)
    context = {
        'newsletter': newsletter,
    }
    return render(request, 'AdminTemplates/Newsletter/Newsletter/NewsletterUserDetailAdmin.html', context)


# Widok usuwania użytkownika newslettera (dla superusera)
@superuser_required
def newsletter_user_delete_admin_panel_view(request, pk):
    return process_delete_admin_panel_view(request, pk, NewsletterUser, NewsletterUserDeleteForm,
                                           'AdminTemplates/Newsletter/Newsletter/NewsletterUserDeleteAdmin.html',
                                           USER_SUCCESS_DELETE_MESSAGE, 'newsletter_user_admin_panel')


# Widok dodawania autora (dla superusera)
@superuser_required
def author_add_view(request):
    return process_form_submission(request, AuthorCreateForm, 'AdminTemplates/Accounts/Author/AuthorAddAdmin.html',
                                   'author_add',
                                   'Autor został utworzony')


# Widok zarządzania autorami (dla superusera)
@superuser_required
def author_manage_admin_panel_view(request):
    author = Author.objects.all().order_by('user_id')
    context = get_paginated_context(request, author, 10)
    return render(request, 'AdminTemplates/Accounts/Author/AuthorManageAdmin.html', context)


# Widok szczegółów autora (dla superusera)
@superuser_required
def author_detail_admin_panel_view(request, pk):
    author = get_object_or_404(Author, pk=pk)
    context = {
        'author': author,
    }
    return render(request, 'AdminTemplates/Accounts/Author/AuthorDetailAdmin.html', context)


# Widok edycji autora (dla superusera)
@superuser_required
def author_edit_admin_panel_view(request, pk):
    author_name = get_object_or_404(Author, pk=pk)
    extra_context = {
        'author_name': author_name,
    }

    return edit_entity_admin_panel_view(
        request,
        pk,
        model_class=Author,
        form_class=AuthorEditForm,
        template_name='AdminTemplates/Accounts/Author/AuthorEditAdmin.html',
        success_message='Autor został edytowany',
        redirect_name='author_admin_panel',
        extra_context=extra_context
    )


# Widok usuwania autora (dla superusera)
@superuser_required
def author_delete_admin_panel_view(request, pk):
    return process_delete_admin_panel_view(
        request, pk, Author, AuthorDeleteForm, 'AdminTemplates/Accounts/Author/AuthorDeleteAdmin.html',
        'Autor został usunięty', 'author_admin_panel'
    )


# Widok dodawania kategorii (dla superusera)
@superuser_required
def category_add_view(request):
    return process_form_submission(request, CategoryCreateForm, 'AdminTemplates/Content/Category/CategoryAddAdmin.html',
                                   'category_add',
                                   'Kategoria została dodana.')


# Widok zarządzania kategoriami (dla superusera)
@superuser_required
def category_manage_admin_panel_view(request):
    category = Category.objects.all().order_by('name')
    context = get_paginated_context(request, category, 10)
    return render(request, 'AdminTemplates/Content/Category/CategoryManageAdmin.html', context)


# Widok szczegółów kategorii (dla superusera)
@superuser_required
def category_detail_admin_panel_view(request, pk):
    category = get_object_or_404(Category, pk=pk)
    categories = category.blog_set.count()
    context = {
        'category': category,
        'categories': categories
    }
    return render(request, 'AdminTemplates/Content/Category/CategoryDetailAdmin.html', context)


# Widok edycji kategorii (dla superusera)
@superuser_required
def category_edit_admin_panel_view(request, pk):
    category = get_object_or_404(Category, pk=pk)
    extra_context = {
        'categories': category.blog_set.count(),
    }

    return edit_entity_admin_panel_view(
        request,
        pk,
        model_class=Category,
        form_class=CategoryCreateForm,
        template_name='AdminTemplates/Content/Category/CategoryEditAdmin.html',
        success_message='Kategoria została edytowana',
        redirect_name='category_admin_panel',
        extra_context=extra_context
    )


# Widok usuwania kategorii (dla superusera)
@superuser_required
def category_delete_admin_panel_view(request, pk):
    return process_delete_admin_panel_view(
        request, pk, Category, CategoryDeleteForm, 'AdminTemplates/Content/Category/CategoryDeleteAdmin.html',
        'Kategoria została usunięta', 'category_admin_panel'
    )


# Widok panelu administracyjnego dla postów w danej kategorii (dla superusera)
@superuser_required
def category_post_in_category_panel_admin_panel_view(request):
    category = Category.objects.all().order_by('name')
    context = get_paginated_context(request, category, 10)
    return render(request, 'AdminTemplates/Content/Category/CategoryPostInCategoryAdmin.html', context)


# Widok szczegółów postów w danej kategorii (dla superusera)
@superuser_required
def category_post_in_category_panel_detail_admin_panel_view(request, pk):
    category = get_object_or_404(Category, pk=pk)
    posts = category.blog_set.all()
    context = {
        'category': category,
        'posts': posts,
    }
    return render(request, 'AdminTemplates/Content/Category/CategoryPostInCategoryDetailAdmin.html', context)


# Widok dodawania posta (dla superusera)
@superuser_required
def post_add_view(request):
    return process_form_submission(request, PostCreateForm, 'AdminTemplates/Content/Post/PostAddAdmin.html', 'post_add',
                                   'Post został dodany')


# Widok zarządzania postami (dla superusera)
@superuser_required
def post_manage_admin_panel_view(request):
    post = Blog.objects.all().order_by('title')
    context = get_paginated_context(request, post, 10)
    return render(request, 'AdminTemplates/Content/Post/PostManageAdmin.html', context)


# Widok szczegółów posta (dla superusera)
@superuser_required
def post_detail_admin_panel_view(request, pk):
    post = get_object_or_404(Blog, pk=pk)
    comments = post.comment_set.all().order_by('date_posted')
    context = {
        'post': post,
        'comments': comments,
    }
    return render(request, 'AdminTemplates/Content/Post/PostDetailAdmin.html', context)


# Widok edycji posta (dla superusera)
@superuser_required
def post_edit_admin_panel_view(request, pk):
    return edit_entity_admin_panel_view(
        request,
        pk,
        model_class=Blog,
        form_class=PostCreateForm,
        template_name='AdminTemplates/Content/Post/PostEditAdmin.html',
        success_message='Post został edytowany',
        redirect_name='post_admin_panel',
    )


# Widok usuwania posta (dla superusera)
@superuser_required
def post_delete_admin_panel_view(request, pk):
    return process_delete_admin_panel_view(
        request, pk, Blog, PostDeleteForm, 'AdminTemplates/Content/Post/PostDeleteAdmin.html',
        'Post został usunięty', 'post_admin_panel'
    )


# Widok publikacji posta (dla superusera)
@superuser_required
def post_publication_admin_panel_view(request):
    if request.method == 'POST':
        blog_id = request.POST.get('blog_id')
        publiction_status = request.POST.get('publiction_status')
        blog = Blog.objects.get(pk=blog_id)
        blog.publiction_status = (publiction_status == 'approve')
        blog.save()

    post = Blog.objects.all().order_by('title')
    context = get_paginated_context(request, post, 10)
    return render(request, 'AdminTemplates/Content/Post/PostPublicationAdmin.html', context)


# Widok dodawania komentarza (dla superusera)
@superuser_required
def comment_add_view(request):
    return process_form_submission(request, CommentCreateForm, 'AdminTemplates/Content/Comment/CommentAdd.html',
                                   'comment_add',
                                   'Komentarz został dodany')


# Widok zarządzania komentarzami (dla superusera)
@superuser_required
def comment_manage_admin_panel_view(request):
    comment = Comment.objects.all().order_by('-date_posted')
    context = get_paginated_context(request, comment, 10)
    return render(request, 'AdminTemplates/Content/Comment/CommentMangeAdmin.html', context)


# Widok szczegółów komentarza (dla superusera)
@superuser_required
def comment_detail_admin_panel_view(request, pk):
    comment = get_object_or_404(Comment, pk=pk)
    context = {
        'comment': comment,
    }
    return render(request, 'AdminTemplates/Content/Comment/CommentDetailAdmin.html', context)


# Widok edycji komentarza (dla superusera)
@superuser_required
def comment_edit_admin_panel_view(request, pk):
    return edit_entity_admin_panel_view(
        request,
        pk,
        model_class=Comment,
        form_class=CommentCreateForm,
        template_name='AdminTemplates/Content/Comment/CommentEditAdmin.html',
        success_message='Komentarz został edytowany',
        redirect_name='comment_admin_panel',
    )


# Widok usuwania komentarza (dla superusera)
@superuser_required
def comment_delete_admin_panel_view(request, pk):
    return process_delete_admin_panel_view(
        request, pk, Comment, CommentDeleteForm, 'AdminTemplates/Content/Comment/CommentDeleteAdmin.html',
        'Komentarz został usunięty', 'comment_admin_panel'
    )


# Widok komentarzy w ramach posta (dla superusera)
@superuser_required
def comment_in_post_admin_panel_view(request):
    post = Blog.objects.all().order_by('title')
    context = get_paginated_context(request, post, 10)
    return render(request, 'AdminTemplates/Content/Comment/CommentInPostManageAdmin.html', context)


# Widok szczegółów komentarzy w ramach posta (dla superusera)
@superuser_required
def comment_in_post_detail_admin_panel_view(request, pk):
    posts = get_object_or_404(Blog, pk=pk)
    comments = posts.comment_set.all().order_by('-date_posted')
    context = {
        'posts': posts,
        'comments': comments,
    }
    return render(request, 'AdminTemplates/Content/Comment/CommentInPostDetailAdmin.html', context)


# Widok użytkowników wraz z liczbą ich komentarzy (dla superusera)
@superuser_required
def comment_users_admin_panel_view(request):
    users = User.objects.annotate(comment_count=Count('comment'))
    paginator = Paginator(users, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    context = {
        'page_obj': page_obj
    }
    return render(request, 'AdminTemplates/Content/Comment/CommentUserManageAdmin.html', context)


# Widok szczegółów użytkownika wraz z komentarzami (dla superusera)
@superuser_required
def comment_users_detail_admin_panel_view(request, pk):
    user = get_object_or_404(User, id=pk)
    comments = Comment.objects.filter(author=user).order_by('-date_posted')
    context = {
        'users': user,
        'comments': comments
    }
    return render(request, 'AdminTemplates/Content/Comment/CommentUserDetailAdmin.html', context)


# Widok dodawania newslettera spotkań i wydarzeń (dla superusera)
@superuser_required
def meetups_news_add_view(request):
    return newsletter_add_panel_view(
        request,
        'meetups_news',
        Meetups_newsCreationForm,
        'AdminTemplates/Newsletter/MeetupsNews/MeetupsNewsAddAdmin.html',
        'AdminTemplates/Newsletter/MeetupsNews/Mail/MeetupsNewsMail',
        'Nadchodzące spotkania i wydarzenia'
    )


# Widok zarządzania newsletterami spotkań i wydarzeń (dla superusera)
@superuser_required
def meetups_news_manage_admin_panel_view(request):
    meetups_news = Meetups_news.objects.all().order_by('title')
    context = get_paginated_context(request, meetups_news, 10)
    return render(request, 'AdminTemplates/Newsletter/MeetupsNews/MeetupsNewsManageAdmin.html', context)


# Widok szczegółów newslettera spotkań i wydarzeń (dla superusera)
@superuser_required
def meetups_news_detail_admin_panel_view(request, pk):
    meetups_news = get_object_or_404(Meetups_news, pk=pk)
    context = {
        'meetups_news': meetups_news,
    }
    return render(request, 'AdminTemplates/Newsletter/MeetupsNews/MeetupsNewsDetailAdmin.html', context)


# Widok edycji newslettera spotkań i wydarzeń (dla superusera)
@superuser_required
def meetups_news_edit_admin_panel_view(request, pk):
    return edit_admin_panel_view(
        request,
        pk,
        Meetups_news,
        'meetups_news',
        Meetups_newsCreationForm,
        'AdminTemplates/Newsletter/MeetupsNews/MeetupsNewsEditAdmin.html',
        'AdminTemplates/Newsletter/MeetupsNews/Mail/MeetupsNewsMail',
        'Nadchodzące spotkania i wydarzenia'
    )


# Widok usuwania newslettera spotkań i wydarzeń (dla superusera)
@superuser_required
def meetups_news_delete_admin_panel_view(request, pk):
    return process_delete_admin_panel_view(
        request, pk, Meetups_news, Meetups_newsCreationForm,
        'AdminTemplates/Newsletter/MeetupsNews/MeetupsNewsDeleteAdmin.html',
        'Mail o spotkaniach i wydarzeniach został usunięty', 'meetups_news_admin_panel'
    )


# Widok zarządzania użytkownikami w kontekście newslettera spotkań i wydarzeń (dla superusera)
@superuser_required
def meetups_news_user_manage_admin_panel_view(request):
    users = DjangoUser.objects.all().order_by('user__id')
    context = get_paginated_context(request, users, 10)
    return render(request, 'AdminTemplates/Newsletter/MeetupsNews/MeetupsNewsUserManageAdmin.html', context)


# Widok szczegółów użytkownika w kontekście newslettera spotkań i wydarzeń (dla superusera)
@superuser_required
def meetups_news_user_detail_admin_panel_view(request, pk):
    user = get_object_or_404(DjangoUser, pk=pk)
    context = {
        'users': user,
    }
    return render(request, 'AdminTemplates/Newsletter/MeetupsNews/MeetupsNewsUserDetailAdmin.html', context)


# Widok edycji ustawień użytkownika w kontekście newslettera spotkań i wydarzeń (dla superusera)
@superuser_required
def meetups_news_user_edit_admin_panel_view(request, pk):
    user = get_object_or_404(DjangoUser, id=pk)
    extra_context = {
        'users': user,
    }
    return edit_entity_admin_panel_view(
        request,
        pk,
        model_class=DjangoUser,
        form_class=UserMeetups_newsForm,
        template_name='AdminTemplates/Newsletter/MeetupsNews/MeetupsNewsUserEditAdmin.html',
        success_message='Ustawienia e-maila o spotkaniach i wydarzeniach zostały zaaktualizowane.',
        redirect_name='meetups_news_user_admin_panel',
        extra_context=extra_context
    )


# Widok wysyłania maili z przypomnieniem o nieprzeczytanych postach (dla superusera)
@superuser_required
def send_emails_view(request):
    if request.method == 'POST':
        users_with_missed_news = DjangoUser.objects.filter(miss_news=True)

        from_email = settings.EMAIL_HOST_USER
        skipped_posts_template = 'AdminTemplates/Newsletter/SkippedPosts/Mail/SkippedPostMail.txt'
        skipped_posts_html_template = 'AdminTemplates/Newsletter/SkippedPosts/Mail/skipped_posts/SkippedPostMail.html'

        for user in users_with_missed_news:
            unopened_posts = Blog.objects.filter(publiction_status=True).exclude(id__in=user.opened_posts.all())

            if unopened_posts:
                msg_plain = render_to_string(skipped_posts_template,
                                             {'mail': user.user.email,
                                              'post_list': unopened_posts})
                msg_html = render_to_string(skipped_posts_html_template,
                                            {'mail': user.user.email,
                                             'post_list': unopened_posts,
                                             'image_url': IMAGE_URL})
                send_mail(
                    'Nieprzeczytane posty',
                    msg_plain,
                    from_email,
                    [user.user.email],
                    fail_silently=False,
                    html_message=msg_html
                )

        return render(request, 'AdminTemplates/Newsletter/SkippedPosts/SkippedPostsSendEmails.html')

    return render(request, 'AdminTemplates/Newsletter/SkippedPosts/SkippedPostsConfirmation.html')


# Widok zarządzania pominiętymi postami (dla superusera)
@superuser_required
def skipped_posts_admin_panel(request):
    users = DjangoUser.objects.all().order_by('user__id')

    users_with_unopened_posts = []
    for user in users:
        unopened_posts_count = Blog.objects.filter(publiction_status=True).exclude(
            id__in=user.opened_posts.all()).count()
        user.unopened_posts_count = unopened_posts_count
        users_with_unopened_posts.append(user)

    context = get_paginated_context(request, users_with_unopened_posts, 10)
    return render(request, 'AdminTemplates/Newsletter/SkippedPosts/SkippedPostsManageAdmin.html', context)


# Widok szczegółów pominiętych postów dla konkretnego użytkownika (dla superusera)
@superuser_required
def skipped_posts_detail_admin_panel(request, pk):
    user = get_object_or_404(DjangoUser, pk=pk)
    posts = Blog.objects.filter(publiction_status=True).exclude(id__in=user.opened_posts.all())
    context = {
        'posts': posts,
        'users': user
    }
    return render(request, 'AdminTemplates/Newsletter/SkippedPosts/SkippedPostsDetailAdmin.html', context)


# Widok zarządzania użytkownikami w kontekście pominiętych postów (dla superusera)
@superuser_required
def skipped_posts_user_admin_panel(request):
    users = DjangoUser.objects.all().order_by('user__id')
    context = {
        'users': users,
    }
    return render(request, 'AdminTemplates/Newsletter/SkippedPosts/SkippedPostsUserManageAdmin.html', context)


# Widok edycji ustawień pominiętych postów dla konkretnego użytkownika (dla superusera)
@superuser_required
def skipped_posts_user_edit_admin_panel(request, pk):
    user = get_object_or_404(DjangoUser, id=pk)
    extra_context = {
        'users': user,
    }
    return edit_entity_admin_panel_view(
        request,
        pk,
        model_class=DjangoUser,
        form_class=UserMissNewsForm,
        template_name='AdminTemplates/Newsletter/SkippedPosts/SkippedPostsUserEditAdmin.html',
        success_message='Ustawienia pominiętych artykułów zostały zaktualizowane.',
        redirect_name='skipped_posts_user_admin_panel',
        extra_context=extra_context
    )


# Widok dodawania newslettera okazji z rynku aukcyjnego (dla superusera)
@superuser_required
def auction_opportunities_add_view(request):
    return newsletter_add_panel_view(
        request,
        'opportunities_news',
        AuctionOpportunitiesCreationForm,
        'AdminTemplates/Newsletter/AuctionOpportunities/AuctionOpportunitiesAddAdmin.html',
        'AdminTemplates/Newsletter/AuctionOpportunities/Mail/AuctionOpportunitiesMail',
        'Okazje z rynku aukcyjnego'
    )


# Widok edycji newslettera okazji z rynku aukcyjnego (dla superusera)
@superuser_required
def auction_opportunities_admin_panel_view(request):
    auction_opportunities = AuctionOpportunities.objects.all().order_by('title')
    context = get_paginated_context(request, auction_opportunities, 10)
    return render(request, 'AdminTemplates/Newsletter/AuctionOpportunities/AuctionOpportunitiesManageAdmin.html', context)


# Widok szczegółów okazji z rynku aukcyjnego (dla superusera)
@superuser_required
def auction_opportunities_detail_admin_panel_view(request, pk):
    auction_opportunities = get_object_or_404(AuctionOpportunities, pk=pk)
    context = {
        'auction_opportunities': auction_opportunities,
    }
    return render(request, 'AdminTemplates/Newsletter/AuctionOpportunities/AuctionOpportunitiesDetailAdmin.html', context)


# Widok edycji newslettera okazji z rynku aukcyjnego (dla superusera)
@superuser_required
def auction_opportunities_edit_admin_panel_view(request, pk):
    return edit_admin_panel_view(
        request,
        pk,
        AuctionOpportunities,
        'opportunities_news',
        AuctionOpportunitiesCreationForm,
        'AdminTemplates/Newsletter/AuctionOpportunities/AuctionOpportunitiesEditAdmin.html',
        'AdminTemplates/Newsletter/AuctionOpportunities/Mail/AuctionOpportunitiesMail',
        'Okazje z rynku aukcyjnego'
    )


# Widok usuwania newslettera okazji z rynku aukcyjnego (dla superusera)
@superuser_required
def auction_opportunities_delete_admin_panel_view(request, pk):
    return process_delete_admin_panel_view(
        request, pk, AuctionOpportunities, AuctionOpportunitiesDeleteEmailForm,
        'AdminTemplates/Newsletter/AuctionOpportunities/AuctionOpportunitiesDeleteAdmin.html',
        'Mail o okazjach z rynku aukcyjnego został usunięty', 'auction_opportunities_admin_panel'
    )


# Widok zarządzania użytkownikami w kontekście okazji z rynku aukcyjnego (dla superusera)
@superuser_required
def auction_opportunities_user_manage_admin_panel_view(request):
    users = DjangoUser.objects.all().order_by('user__id')
    context = get_paginated_context(request, users, 10)
    return render(request, 'AdminTemplates/Newsletter/AuctionOpportunities/AuctionOpportunitiesUserManageAdmin.html', context)


# Widok szczegółów użytkownika w kontekście okazji z rynku aukcyjnego (dla superusera)
@superuser_required
def auction_opportunities_user_detail_admin_panel_view(request, pk):
    user = get_object_or_404(DjangoUser, pk=pk)
    context = {
        'users': user,
    }
    return render(request, 'AdminTemplates/Newsletter/AuctionOpportunities/AuctionOpportunitiesUserDetailAdmin.html', context)


# Widok edycji ustawień e-maila o okazjach z rynku aukcyjnego dla konkretnego użytkownika (dla superusera)
@superuser_required
def auction_opportunities_user_edit_admin_panel_view(request, pk):
    user = get_object_or_404(DjangoUser, id=pk)
    extra_context = {
        'users': user,
    }
    return edit_entity_admin_panel_view(
        request,
        pk,
        model_class=DjangoUser,
        form_class=UserAuctionOpportunitiesForm,
        template_name='AdminTemplates/Newsletter/AuctionOpportunities/AuctionOpportunitiesUserEditAdmin.html',
        success_message='Ustawienia e-maila o okazjach z rynku aukcyjnego zostały zaaktualizowane.',
        redirect_name='auction_opportunities_user_manage_admin_panel',
        extra_context=extra_context
    )


# Widok dodawania newslettera od Banknoty (dla superusera)
@superuser_required
def company_news_add_view(request):
    return newsletter_add_panel_view(
        request,
        'company_news',
        CompanyNewsCreationForm,
        'company_news',
        'Wiadomość od Banknoty'
    )


# Widok edycji newslettera od Banknoty (dla superusera)
@superuser_required
def company_news_admin_panel_view(request):
    company_news = CompanyNews.objects.all().order_by('title')
    context = get_paginated_context(request, company_news, 10)
    return render(request, 'company_news/company_news_admin_panel.html', context)


# Widok szczegółów newslettera od Banknoty (dla superusera)
@superuser_required
def company_news_detail_admin_panel_view(request, pk):
    company_news = get_object_or_404(CompanyNews, pk=pk)
    context = {
        'company_news': company_news,
    }
    return render(request, 'company_news/company_news_detail_admin_panel.html', context)


# Widok edycji newslettera od Banknoty (dla superusera)
@superuser_required
def company_news_edit_admin_panel_view(request, pk):
    return edit_admin_panel_view(
        request,
        pk,
        CompanyNews,
        'company_news',
        CompanyNewsCreationForm,
        'company_news',
        'Wiadomość od banknoty'
    )


# Widok usuwania newslettera od Banknoty (dla superusera)
@superuser_required
def company_news_delete_admin_panel_view(request, pk):
    return process_delete_admin_panel_view(
        request, pk, CompanyNews, CompanyNewsDeleteEmailForm,
        'company_news/company_news_delete_admin_panel.html',
        'Mail z wiadomością od Bankonty został usunięty', 'company_news_admin_panel'
    )


# Widok zarządzania użytkownikami w kontekście newslettera od Banknoty (dla superusera)
@superuser_required
def company_news_user_manage_admin_panel_view(request):
    users = DjangoUser.objects.all().order_by('user__id')
    context = get_paginated_context(request, users, 10)
    return render(request, 'company_news/company_news_user_manage_admin_panel.html', context)


# Widok szczegółów użytkownika w kontekście newslettera od Banknoty (dla superusera)
@superuser_required
def company_news_user_detail_admin_panel_view(request, pk):
    user = get_object_or_404(DjangoUser, pk=pk)
    context = {
        'users': user,
    }
    return render(request, 'company_news/company_news_user_detail_admin_panel.html', context)


# Widok edycji ustawień e-maila z wiadomością od Banknoty dla konkretnego użytkownika (dla superusera)
@superuser_required
def company_news_user_edit_admin_panel_view(request, pk):
    user = get_object_or_404(DjangoUser, id=pk)
    extra_context = {
        'users': user,
    }
    return edit_entity_admin_panel_view(
        request,
        pk,
        model_class=DjangoUser,
        form_class=UserCompanyNewsForm,
        template_name='company_news/company_news_user_edit_admin_panel.html',
        success_message='Ustawienia e-maila z wiadmością od Banknoty zostały zaaktualizowane.',
        redirect_name='company_news_user_manage_admin_panel',
        extra_context=extra_context
    )


# Widok dodawania newslettera z shotem od Bankonty (dla superusera)
@superuser_required
def replay_news_add_view(request):
    return newsletter_add_panel_view(
        request,
        'replay_news',
        ReplayNewsCreationForm,
        'replay_news',
        'z shotem od Bankonty'
    )


# Widok edycji newslettera z shotem od Bankonty (dla superusera)
@superuser_required
def replay_news_admin_panel_view(request):
    replay_news = ReplayNews.objects.all().order_by('title')
    context = get_paginated_context(request, replay_news, 10)
    return render(request, 'replay_news/replay_news_admin_panel.html', context)


# Widok szczegółów newslettera z shotem od Bankonty (dla superusera)
@superuser_required
def replay_news_detail_admin_panel_view(request, pk):
    replay_news = get_object_or_404(ReplayNews, pk=pk)
    context = {
        'replay_news': replay_news,
    }
    return render(request, 'replay_news/replay_news_detail_admin_panel.html', context)


# Widok edycji newslettera z shotem od Bankonty (dla superusera)
@superuser_required
def replay_news_edit_admin_panel_view(request, pk):
    return edit_admin_panel_view(
        request,
        pk,
        ReplayNews,
        'replay_news',
        ReplayNewsCreationForm,
        'replay_news',
        'z shotem od Bankonty'
    )


# Widok usuwania newslettera z shotem od Bankonty (dla superusera)
@superuser_required
def replay_news_delete_admin_panel_view(request, pk):
    return process_delete_admin_panel_view(
        request, pk, ReplayNews, ReplayNewsDeleteEmailForm,
        'replay_news/replay_news_delete_admin_panel.html',
        'Mail z shotem od Bankonty został usunięty', 'replay_news_admin_panel'
    )


# Widok zarządzania użytkownikami w kontekście newslettera z shotem od Bankonty (dla superusera)
@superuser_required
def replay_news_user_manage_admin_panel_view(request):
    users = DjangoUser.objects.all().order_by('user__id')
    context = get_paginated_context(request, users, 10)
    return render(request, 'replay_news/replay_news_user_manage_admin_panel.html', context)


# Widok szczegółów użytkownika w kontekście newslettera z shotem od Bankonty (dla superusera)
@superuser_required
def replay_news_user_detail_admin_panel_view(request, pk):
    user = get_object_or_404(DjangoUser, pk=pk)
    context = {
        'users': user,
    }
    return render(request, 'replay_news/replay_news_user_detail_admin_panel.html', context)


# Widok edycji ustawień e-maila z shotem wiadomości od Banknoty dla konkretnego użytkownika (dla superusera)
@superuser_required
def replay_news_user_edit_admin_panel_view(request, pk):
    user = get_object_or_404(DjangoUser, id=pk)
    extra_context = {
        'users': user,
    }
    return edit_entity_admin_panel_view(
        request,
        pk,
        model_class=DjangoUser,
        form_class=UserReplayNewsForm,
        template_name='replay_news/replay_news_user_edit_admin_panel.html',
        success_message='Ustawienia e-maila z shotem wiadomości od Banknoty zostały zaaktualizowane.',
        redirect_name='replay_news_user_manage_admin_panel',
        extra_context=extra_context
    )


# Widok dodawania newslettera z informacjami o rozwoju i zmianach na Bankonty (dla superusera)
@superuser_required
def development_news_add_view(request):
    return newsletter_add_panel_view(
        request,
        'development_news',
        DevelopmentNewsCreationForm,
        'development_news',
        'z informacjami o rozwoju i zmianach na Bankonty'
    )


# Widok edycji newslettera z informacjami o rozwoju i zmianach na Bankonty (dla superusera)
@superuser_required
def development_news_admin_panel_view(request):
    development_news = DevelopmentNews.objects.all().order_by('title')
    context = get_paginated_context(request, development_news, 10)
    return render(request, 'development_news/development_news_admin_panel.html', context)


# Widok szczegółów newslettera z informacjami o rozwoju i zmianach na Bankonty (dla superusera)
@superuser_required
def development_news_detail_admin_panel_view(request, pk):
    development_news = get_object_or_404(DevelopmentNews, pk=pk)
    context = {
        'development_news': development_news,
    }
    return render(request, 'development_news/development_news_detail_admin_panel.html', context)


# Widok edycji newslettera z informacjami o rozwoju i zmianach na Bankonty (dla superusera)
@superuser_required
def development_news_edit_admin_panel_view(request, pk):
    return edit_admin_panel_view(
        request,
        pk,
        DevelopmentNews,
        'development_news',
        DevelopmentNewsCreationForm,
        'development_news',
        'z informacjami o rozwoju i zmianach na Bankonty'
    )


# Widok usuwania newslettera z informacjami o rozwoju i zmianach na Bankonty (dla superusera)
@superuser_required
def development_news_delete_admin_panel_view(request, pk):
    return process_delete_admin_panel_view(
        request, pk, DevelopmentNews, DevelopmentNewsDeleteEmailForm,
        'development_news/development_news_delete_admin_panel.html',
        'Mail z informacjami o rozwoju i zmianach na Bankonty został usunięty',
        'development_news_admin_panel'
    )


# Widok zarządzania użytkownikami w kontekście newslettera z informacjami o rozwoju i zmianach na Bankonty (dla superusera)
@superuser_required
def development_news_user_manage_admin_panel_view(request):
    users = DjangoUser.objects.all().order_by('user__id')
    context = get_paginated_context(request, users, 10)
    return render(request, 'development_news/development_news_user_manage_admin_panel.html', context)


# Widok szczegółów użytkownika w kontekście newslettera z informacjami o rozwoju i zmianach na Bankonty (dla superusera)
@superuser_required
def development_news_user_detail_admin_panel_view(request, pk):
    user = get_object_or_404(DjangoUser, pk=pk)
    context = {
        'users': user,
    }
    return render(request, 'development_news/development_news_user_detail_admin_panel.html', context)


# Widok edycji ustawień e-maila z informacjami o rozwoju i zmianach na Bankonty dla konkretnego użytkownika (dla superusera)
@superuser_required
def development_news_user_edit_admin_panel_view(request, pk):
    user = get_object_or_404(DjangoUser, id=pk)
    extra_context = {
        'users': user,
    }
    return edit_entity_admin_panel_view(
        request,
        pk,
        model_class=DjangoUser,
        form_class=UserReplayNewsForm,
        template_name='development_news/development_news_user_edit_admin_panel.html',
        success_message='Ustawienia e-maila z informacjami o rozwoju i zmianach na Banknoty zostały zaaktualizowane.',
        redirect_name='development_news_user_manage_admin_panel',
        extra_context=extra_context
    )


# Widok dodawania użytkownika (dla superusera)
@superuser_required
def users_add_view(request):
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
            return redirect('users_add')
    else:
        user_form = UserCreationForm()
        profile_form = UserProfileForm()

    context = {
        'user_form': user_form,
        'profile_form': profile_form
    }
    return render(request, 'user/user_add.html', context)


# Widok zarządzania użytkownikami (dla superusera)
@superuser_required
def users_manage_admin_panel_view(request):
    users = DjangoUser.objects.select_related('user').all().order_by('-user__id')
    context = get_paginated_context(request, users, 10)
    return render(request, 'user/users_admin_panel.html', context)


# Widok szczegółów użytkownika (dla superusera)
@superuser_required
def users_detail_admin_panel_view(request, pk):
    users = get_object_or_404(DjangoUser, pk=pk)

    context = {
        'users': users,
    }
    return render(request, 'user/user_detail_admin_panel.html', context)


# Widok edycji użytkownika (dla superusera)
@superuser_required
def users_edit_main_page_admin_panel_view(request, pk):
    users = get_object_or_404(DjangoUser, pk=pk)
    django_user = users.user

    if request.method == 'POST':
        user_profile_form = UserProfileForm(request.POST, instance=users)
        user_email_form = UserEditForm(request.POST, instance=django_user)
        if user_profile_form.is_valid() and user_email_form.is_valid():
            user_profile_form.save()
            user_email_form.save()
            messages.success(request,
                             'Użytkownik został edytowany',
                             "alert alert-success alert-dismissible fade show mt-3")
            return redirect('users_admin_panel')
    else:
        user_profile_form = UserProfileForm(instance=users)
        user_email_form = UserEditForm(instance=django_user)
    return render(request, 'user/user_edit_admin_panel.html', {
        'profile_form': user_profile_form,
        'user_form': user_email_form,
        'users': users,
    })


# Widok edycji hasła użytkownika (dla superusera)
@superuser_required
def users_edit_password_admin_panel_view(request, pk):
    user = get_object_or_404(DjangoUser, pk=pk)

    if request.method == 'POST':
        edit_password_form = CustomPasswordChangingForm(data=request.POST)
        if edit_password_form.is_valid():
            user = edit_password_form.save(user.user)
            update_session_auth_hash(request, user)
            messages.success(request,
                             'Hasło użytkownika został edytowane',
                             "alert alert-success alert-dismissible fade show mt-3")
            return redirect('users_admin_panel')
    else:
        edit_password_form = CustomPasswordChangingForm()

    context = {
        'edit_password_form': edit_password_form,
        'users': user,
    }
    return render(request, 'user/user_edit_password_admin_panel.html', context)


# Widok usuwania użytkownika (dla superusera)
@superuser_required
def users_delete_admin_panel_view(request, pk):
    user = get_object_or_404(DjangoUser, pk=pk)

    if request.method == "POST":
        form = UsersDeleteEmailForm(request.POST, instance=user)
        if form.is_valid():
            user = user.user
            user.delete()
            messages.success(request,
                             'Użytkownik został usunięty',
                             "alert alert-success alert-dismissible fade show mt-3")
            return redirect('users_admin_panel')
    else:
        form = UsersDeleteEmailForm(instance=user)

    context = {
        'form': form,
        'users': user,
    }
    return render(request, 'user/user_delete_admin_panel.html', context)


# Widok dodawania aplikacji społecznej (dla superusera)
@superuser_required
def social_app_add_view(request):
    return process_form_submission(request, SocialAppForm,
                                   'social_app/social_app_add.html',
                                   'social_app_add',
                                   'Aplikacja społeczna została dodana.')


# Widok zarządzania aplikacjami społecznymi (dla superusera)
@superuser_required
def social_app_admin_panel_view(request):
    social_apps = SocialApp.objects.all().order_by('id')
    context = get_paginated_context(request, social_apps, 10)
    return render(request, 'social_app/social_app_manage_admin_panel.html', context)


# Widok szczegółów aplikacji społecznej (dla superusera)
@superuser_required
def social_app_detail_admin_panel_view(request, pk):
    social_apps = get_object_or_404(SocialApp, pk=pk)
    context = {
        'social_app': social_apps,
    }
    return render(request, 'social_app/social_app_detail_admin_panel.html', context)


# Widok edycji aplikacji społecznej (dla superusera)
@superuser_required
def social_app_edit_admin_panel_view(request, pk):
    social_apps = get_object_or_404(SocialApp, pk=pk)
    return edit_entity_admin_panel_view(
        request,
        pk,
        model_class=SocialApp,
        form_class=SocialAppForm,
        template_name='social_app/social_app_edit_admin_panel.html',
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
        'social_app/social_app_delete_admin_panel.html',
        'Aplikacja społeczna została usunięta',
        'social_app_admin_panel'
    )


# Widok dodawania tokena aplikacji społecznej (dla superusera)
@superuser_required
def social_token_add_view(request):
    return process_form_submission(request, SocialTokenForm,
                                   'social_token/social_token_add.html',
                                   'social_token_add',
                                   'Token aplikacji społecznościowej został dodany.')


# Widok zarządzania tokenami aplikacji społecznej (dla superusera)
@superuser_required
def social_token_admin_panel_view(request):
    social_tokens = SocialToken.objects.all().order_by('id')
    context = get_paginated_context(request, social_tokens, 10)
    return render(request, 'social_token/social_token_manage_admin_panel.html', context)


# Widok szczegółów tokena aplikacji społecznej (dla superusera)
@superuser_required
def social_token_detail_admin_panel_view(request, pk):
    social_tokens = get_object_or_404(SocialToken, pk=pk)
    context = {
        'social_token': social_tokens,
    }
    return render(request, 'social_token/social_token_detail_admin_panel.html', context)


# Widok edycji tokena aplikacji społecznej (dla superusera)
@superuser_required
def social_token_edit_admin_panel_view(request, pk):
    social_tokens = get_object_or_404(SocialToken, pk=pk)
    return edit_entity_admin_panel_view(
        request,
        pk,
        model_class=SocialToken,
        form_class=SocialTokenForm,
        template_name='social_token/social_token_edit_admin_panel.html',
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
        'social_token/social_token_delete_admin_panel.html',
        'Token aplikacji społecznościowej został usunięty',
        'social_token_admin_panel'
    )


# Widok dodawania konta aplikacji społecznej (dla superusera)
@superuser_required
def social_account_add_view(request):
    return process_form_submission(request, SocialAccountForm,
                                   'social_account/social_account_add.html',
                                   'social_account_add',
                                   'Konto aplikacji społecznościowej zostało dodane.')


# Widok zarządzania kontami aplikacji społecznej (dla superusera)
@superuser_required
def social_account_admin_panel_view(request):
    social_accounts = SocialAccount.objects.all().order_by('id')
    context = get_paginated_context(request, social_accounts, 10)
    return render(request, 'social_account/social_account_manage_admin_panel.html', context)


# Widok szczegółów konta aplikacji społecznej (dla superusera)
@superuser_required
def social_account_detail_admin_panel_view(request, pk):
    social_accounts = get_object_or_404(SocialAccount, pk=pk)
    context = {
        'social_account': social_accounts,
    }
    return render(request, 'social_account/social_account_detail_admin_panel.html', context)


# Widok edycji konta aplikacji społecznej (dla superusera)
@superuser_required
def social_account_edit_admin_panel_view(request, pk):
    social_accounts = get_object_or_404(SocialAccount, pk=pk)
    return edit_entity_admin_panel_view(
        request,
        pk,
        model_class=SocialAccount,
        form_class=SocialAccountForm,
        template_name='social_account/social_account_edit_admin_panel.html',
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
        'social_account/social_account_delete_admin_panel.html',
        'Konto aplikacji społecznościowej zostało usunięte',
        'social_account_admin_panel'
    )


#  Widok dodawania adresu email (dla superusera)
@superuser_required
def email_address_add_view(request):
    return process_form_submission(request, EmailAddressForm,
                                   'email_address/email_address_add.html',
                                   'email_address_add',
                                   'Adres email został dodany.')


# Widok zarządzania adresem email (dla superusera)
@superuser_required
def email_address_admin_panel_view(request):
    email_addresses = EmailAddress.objects.all().order_by('id')
    context = get_paginated_context(request, email_addresses, 10)
    return render(request, 'email_address/email_address_manage_admin_panel.html', context)


# Widok szczegółów adresu email (dla superusera)
@superuser_required
def email_address_detail_admin_panel_view(request, pk):
    email_addresses = get_object_or_404(EmailAddress, pk=pk)
    context = {
        'email_address': email_addresses,
    }
    return render(request, 'email_address/email_address_detail_admin_panel.html', context)


# Widok edycji adresu email (dla superusera)
@superuser_required
def email_address_edit_admin_panel_view(request, pk):
    email_addresses = get_object_or_404(EmailAddress, pk=pk)
    return edit_entity_admin_panel_view(
        request,
        pk,
        model_class=EmailAddress,
        form_class=EmailAddressForm,
        template_name='email_address/email_address_edit_admin_panel.html',
        success_message='Adres email został edytowany.',
        redirect_name='email_address_admin_panel',
        extra_context={
            'email_address': email_addresses,
        }
    )


# Widok usuwania adresu email (dla superusera)
@superuser_required
def email_address_delete_admin_panel_view(request, pk):
    return process_delete_admin_panel_view(
        request, pk, EmailAddress, EmailAddressDeleteForm,
        'email_address/email_address_delete_admin_panel.html',
        'Adres email został usunięty',
        'email_address_admin_panel'
    )
