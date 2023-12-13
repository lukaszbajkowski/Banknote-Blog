from django.contrib.auth import views as auth_views
from django.urls import path

from . import views
from .views_author.author.author_views import *
from .views_author.author_app.author_app_views import *
from .views_confirmation.confirmation.confirmation_views import *
from .views_login.login.login_views import *
from .views_notification.notification.notification_views import *
from .views_register.register.register_views import *
from .views_user.comment.comment_views import *
from .views_user.email.email_views import *
from .views_user.password.password_views import *
from .views_user.settings.settings_views import *

urlpatterns = [
    path('register/', register_view, name='register'),
    path(r'^login/$', login_view, name='login'),

    path('mycomments/', comment_list_view, name='comments'),

    path('myprofile/', user_edit_view, name='edit_profile'),
    path('myprofile/security/', user_change_main_page_view, name='edit_security_page'),
    path('myprofile/change_password/', user_change_password_view, name='edit_security'),
    path('myprofile/change_email/', user_change_email_view, name='edit_email'),

    path('myprofile/notifications/', user_notification_view, name='notifications'),

    path('myprofile/posts/', author_post_view, name='my_posts'),
    path('myprofile/posts/create/', author_post_create_view, name='my_posts_create'),
    path('myprofile/posts/detail/<int:pk>', author_post_detail_view, name='my_posts_detail'),
    path('myprofile/posts/edit/<int:pk>', author_post_edit_view, name='my_posts_edit'),
    path('myprofile/posts/delete/<int:pk>', author_post_delete_view, name='my_posts_delete'),

    path('myprofile/author/', author_view, name='edit_author'),
    path('myprofile/author/create/', author_create_view, name='create_author'),

    path('myprofile/author_application/', author_app_view, name='article_author_form'),
    path('myprofile/author_application/history/', author_app_history_view, name='article_author_history'),
    path('myprofile/author_application/detail/<int:pk>', author_app_detail_view, name='article_author_detail'),

    path('confirmation/', confirmation_page_view, name='confirmation'),
    path('confirm/<str:uidb64>/<str:token>/', confirm_email_view, name='confirm_email'),
    path('confirmed/', registration_confirmed_view, name='registration_confirmed'),
    path('confirmation-error/', confirmation_error_view, name='confirmation_error'),

    path('reset_password/', views.CustomPasswordResetView.as_view(
        template_name='Registration/ResetPassword/PasswordResetForm.html',
        html_email_template_name='registration/ResetPassword/PasswordResetEmail.html',
        subject_template_name='registration/ResetPassword/PasswordResetSubject.txt',
    ), name='reset_password'),
    path('reset_password_sent/', auth_views.PasswordResetDoneView.as_view(
        template_name='Registration/ResetPassword/PasswordResetDone.html'
    ), name='password_reset_done'),
    path('reset/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(
        template_name='Registration/PasswordResetConfirm.html'
    ), name='password_reset_confirm'),
    path('reset_password_complete/', auth_views.PasswordResetCompleteView.as_view(
        template_name='Registration/ResetPassword/PasswordResetComplete.html'
    ), name='password_reset_complete'),

]
