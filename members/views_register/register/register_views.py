from django.contrib.auth.tokens import default_token_generator
from django.contrib.sites.shortcuts import get_current_site
from django.core.mail import send_mail
from django.shortcuts import redirect
from django.shortcuts import render
from django.template.loader import render_to_string
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode

from members.forms import CustomUserForm
from pm_blog import settings


# Widok rejestracji użytkownika
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
            message = render_to_string('Registration/ConfirmationEmail.html', {
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

            return redirect('confirmation')

    context = {
        'form': form
    }
    return render(
        request,
        'Registration/Registration.html',
        context
    )
