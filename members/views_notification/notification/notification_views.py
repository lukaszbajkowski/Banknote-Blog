from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect
from django.shortcuts import render

from blog.models import Category, Blog
from blog.models import User as User_Custom
from members.forms import CommunicationSettingForm
from members.forms import NotificationSettingsForm


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
