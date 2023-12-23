from django.core.mail import send_mail
from django.http import JsonResponse
from django.shortcuts import render
from django.template.loader import render_to_string

from blog.forms.contact_form import ContactForm
from blog.models import Blog
from blog.models import Category
from blog.views import IMAGE_URL
from pm_blog import settings


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
            msg_plain = render_to_string(
                'Contact/Mail/ContactMailToAdmin.txt',
                context
            )
            msg_html = render_to_string(
                'Contact/Mail/ContactMailToAdmin.html',
                context
            )

            msg_plain_user = render_to_string(
                'Contact/Mail/ContactMailToUser.txt',
                context
            )
            msg_html_user = render_to_string(
                'Contact/Mail/ContactMailToUser.html',
                context
            )

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

            return JsonResponse(
                {
                    'success': True
                }
            )
        else:
            return JsonResponse(
                {
                    'success': False,
                    'error': 'Formularz zawiera nieprawidłowe dane.'
                }
            )
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
