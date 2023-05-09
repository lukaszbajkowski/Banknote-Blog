from django.urls import path
from .import views
from .views import UserEditView

urlpatterns = [
    path('register/', views.register_page, name='register'),
    path('login/', views.login_page, name='login'),
    path('myprofile/', views.UserEditView, name='edit_profile'),
    path('myprofile/change_password', views.UserChangePasswordView, name='edit_security'),
    path('myprofile/security', views.UserChangePageView, name='edit_security_page'),
    path('myprofile/change_email', views.UserChangeEmailView, name='edit_email'),
]
