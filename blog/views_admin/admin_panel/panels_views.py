from django.shortcuts import render
from blog.decorators import superuser_required


# Widok panelu administracyjnego dla newsletterów (dla superusera)
@superuser_required
def newsletters_admin_panel_view(request):
    return render(request, 'AdminTemplates/Admin/Panels/NewslettersAdminPanel.html')


# Widok panelu administracyjnego dla użytkowników (dla superusera)
@superuser_required
def users_admin_panel_view(request):
    return render(request, 'AdminTemplates/Admin/Panels/UsersAdminPanel.html')


# Widok panelu administracyjnego dla postów (dla superusera)
@superuser_required
def posts_admin_panel_view(request):
    return render(request, 'AdminTemplates/Admin/Panels/ContentAdminPanel.html')


# Widok panelu administracyjnego dla mediów społecznościowych (dla superusera)
@superuser_required
def social_media_admin_panel_view(request):
    return render(request, 'AdminTemplates/Admin/Panels/SocialmediaAdminPanel.html')