from django.conf.urls.static import static
from django.urls import include
from django.urls import path

from . import views
from .views import *
from .views_admin.accounts.author.author_views import *
from .views_admin.accounts.author_application.author_application_views import *
from .views_admin.accounts.user.user_views import *
from .views_admin.content.category.category_views import *
from .views_admin.content.comment.comment_views import *
from .views_admin.content.post.post_views import *
from .views_admin.newsletter.auction_opportunities.auction_opportunities_views import *
from .views_admin.newsletter.company_news.company_news_views import *
from .views_admin.newsletter.development_news.development_news_views import *
from .views_admin.newsletter.meetups_news.meetups_news_views import *
from .views_admin.newsletter.newsletter.newsletter_views import newsletter_creation_view

urlpatterns = [
                  path('i18n/', include('django.conf.urls.i18n')),

                  path('', home_view, name='home'),  # Strona główna
                  path('article/<int:pk>', ArticleDetailView, name="article-detail"),  # Szczegóły artykułu
                  path('article/all/', ArticleListView, name="article-all"),  # Lista wszystkich artykułów
                  path('author/<int:pk>', views.profile_view, name="author-detail"),  # Szczegóły autora
                  path('category/<str:pk>/', CategoryView, name='category-detail'),  # Widok kategorii
                  path('category/', CategoryListView, name='category-all'),  # Lista wszystkich kategorii
                  path('author/all/', ProfileListView, name='author-all'),  # Lista wszystkich autorów

                  path('contact/', ContactView, name='contact'),  # Widok kontaktu

                  path('terms_and_conditions/', TermsConditionsView, name='terms_and_conditions'),  # Regulamin
                  path('privacy_policy/', PrivacyPolicyView, name='privacy_policy'),  # Polityka prywatności
                  path('about/', AboutPageView, name='about_page'),  # Strona informacyjna "O nas"

                  # Widoki związane z obsługą newslettera
                  path('newsletter/sign_up/', newsletter_signup_view, name='newsletter_signup'),
                  path('newsletter/unsubscribe/', newsletter_unsubscribe_view, name='newsletter_unsubscribe'),
                  path('newsletter/', newsletter_creation_view, name='newsletter_creation'),
                  path('newsletter/add_user/', newsletter_add_user_view, name='newsletter_add_user'),
                  path('newsletter/remove_user/', newsletter_remove_user_view, name='newsletter_remove_user'),
                  path('newsletter/AdminPanel/', newsletter_manage_admin_panel_view, name='newsletter_admin_panel'),
                  path('newsletter/<int:pk>/', newsletter_detail_admin_panel_view,
                       name='newsletter_detail_admin_panel'),
                  path('newsletter/edit/<int:pk>/', newsletter_edit_admin_panel_view,
                       name='newsletter_edit_admin_panel'),
                  path('newsletter/delete/<int:pk>/', newsletter_delete_admin_panel_view,
                       name='newsletter_delete_admin_panel'),
                  path('newsletter/user/AdminPanel/', newsletter_user_manage_admin_panel_view,
                       name='newsletter_user_admin_panel'),
                  path('newsletter/user/<int:pk>/', newsletter_user_detail_admin_panel_view,
                       name='newsletter_user_detail_admin_panel'),
                  path('newsletter/user/delete/<int:pk>/', newsletter_user_delete_admin_panel_view,
                       name='newsletter_user_delete_admin_panel'),

                  # Pozostałe widoki admina
                  path('admin/', admin_panel_view, name='admin'),
                  path('admin/newsletters/', newsletters_admin_panel_view, name='newsletters_admin'),
                  path('admin/users/', users_admin_panel_view, name='users_admin'),
                  path('admin/posts/', posts_admin_panel_view, name='posts_admin'),
                  path('admin/social/', social_media_admin_panel_view, name='social_admin'),

                  # Widoki związane z autorem
                  path('author/add_author/', author_add_view, name='author_add'),
                  path('author/AdminPanel/', author_manage_admin_panel_view, name='author_admin_panel'),
                  path('author/<int:pk>/', author_detail_admin_panel_view, name='author_detail_admin_panel'),
                  path('author/edit/<int:pk>', author_edit_admin_panel_view, name='author_edit_admin_panel'),
                  path('author/delete/<int:pk>', author_delete_admin_panel_view, name='author_delete_admin_panel'),

                  # Widoki związane z kategorią
                  path('cateogry/add_category/', category_add_view, name='category_add'),
                  path('category/manage/AdminPanel/', category_manage_admin_panel_view, name='category_admin_panel'),
                  path('category/detail/<int:pk>', category_detail_admin_panel_view,
                       name='category_detail_admin_panel'),
                  path('category/edit/<int:pk>', category_edit_admin_panel_view, name='category_edit_admin_panel'),
                  path('category/delete/<int:pk>', category_delete_admin_panel_view,
                       name='category_delete_admin_panel'),
                  path('category/manage/AdminPanel/posts/', category_post_in_category_panel_admin_panel_view,
                       name='category_posts_in_category_panel_admin_panel'),
                  path('category/manage/AdminPanel/posts/<int:pk>',
                       category_post_in_category_panel_detail_admin_panel_view,
                       name='category_post_in_category_panel_detail_admin_panel'),

                  # Widoki związane z artykułami
                  path('article/add_article/', post_add_view, name='post_add'),
                  path('article/AdminPanel/', post_manage_admin_panel_view, name='post_admin_panel'),
                  path('article/detail/<int:pk>', post_detail_admin_panel_view, name='post_detail_admin_panel'),
                  path('article/edit/<int:pk>', post_edit_admin_panel_view, name='post_edit_admin_panel'),
                  path('article/delete/<int:pk>', post_delete_admin_panel_view, name='post_delete_admin_panel'),
                  path('article/publication/', post_publication_admin_panel_view, name='post_publication_admin_panel'),

                  # Widoki związane z komentarzami
                  path('comment/add_comment/', comment_add_view, name='comment_add'),
                  path('comment/AdminPanel/', comment_manage_admin_panel_view, name='comment_admin_panel'),
                  path('comment/detail/<int:pk>', comment_detail_admin_panel_view, name='comment_detail_admin_panel'),
                  path('comment/edit/<int:pk>', comment_edit_admin_panel_view, name='comment_edit_admin_panel'),
                  path('comment/delete/<int:pk>', comment_delete_admin_panel_view, name='comment_delete_admin_panel'),
                  path('comment/post/', comment_in_post_admin_panel_view, name='comment_in_post_admin_panel'),
                  path('comment/post/<int:pk>', comment_in_post_detail_admin_panel_view,
                       name='comment_in_post_detail_admin_panel'),
                  path('comment/user/AdminPanel/', comment_users_admin_panel_view, name='comment_users_admin_panel'),
                  path('comment/user/<int:pk>', comment_users_detail_admin_panel_view,
                       name='comment_users_detail_admin_panel'),

                  # Widoki związane z wiadomościami spotkaniach
                  path('meetups_news/', meetups_news_add_view, name='meetups_news_add'),
                  path('meetups_news/AdminPanel/', meetups_news_manage_admin_panel_view,
                       name='meetups_news_admin_panel'),
                  path('meetups_news/detail/<int:pk>', meetups_news_detail_admin_panel_view,
                       name='meetups_news_detail_admin_panel'),
                  path('meetups_news/edit/<int:pk>', meetups_news_edit_admin_panel_view,
                       name='meetups_news_edit_admin_panel'),
                  path('meetups_news/delete/<int:pk>', meetups_news_delete_admin_panel_view,
                       name='meetups_news_delete_admin_panel'),
                  path('meetups_news/user/AdminPanel/', meetups_news_user_manage_admin_panel_view,
                       name='meetups_news_user_admin_panel'),
                  path('meetups_news/user/detail/<int:pk>', meetups_news_user_detail_admin_panel_view,
                       name='meetups_news_user_detail_admin_panel'),
                  path('meetups_news/user/edit/<int:pk>', meetups_news_user_edit_admin_panel_view,
                       name='meetups_news_user_edit_admin_panel'),

                  # Widoki związane z wiadomościami o okazjach aukcyjnych
                  path('auction_opportunities/', auction_opportunities_add_view, name='auction_opportunities_add'),
                  path('auction_opportunities/AdminPanel/', auction_opportunities_admin_panel_view,
                       name='auction_opportunities_admin_panel'),
                  path('auction_opportunities/detail/<int:pk>', auction_opportunities_detail_admin_panel_view,
                       name='auction_opportunities_detail_admin_panel'),
                  path('auction_opportunities/edit/<int:pk>', auction_opportunities_edit_admin_panel_view,
                       name='auction_opportunities_edit_admin_panel'),
                  path('auction_opportunities/delete/<int:pk>', auction_opportunities_delete_admin_panel_view,
                       name='auction_opportunities_delete_admin_panel'),
                  path('auction_opportunities/user/AdminPanel/', auction_opportunities_user_manage_admin_panel_view,
                       name='auction_opportunities_user_manage_admin_panel'),
                  path('auction_opportunities/user/detail/<int:pk>', auction_opportunities_user_detail_admin_panel_view,
                       name='auction_opportunities_user_detail_admin_panel'),
                  path('auction_opportunities/user/edit/<int:pk>', auction_opportunities_user_edit_admin_panel_view,
                       name='auction_opportunities_user_edit_admin_panel'),

                  # Widoki związane z wiadomościami o firmie
                  path('company_news/', company_news_add_view, name='company_news_add'),
                  path('company_news/AdminPanel/', company_news_admin_panel_view, name='company_news_admin_panel'),
                  path('company_news/detail/<int:pk>', company_news_detail_admin_panel_view,
                       name='company_news_detail_admin_panel'),
                  path('company_news/edit/<int:pk>', company_news_edit_admin_panel_view,
                       name='company_news_edit_admin_panel'),
                  path('company_news/delete/<int:pk>', company_news_delete_admin_panel_view,
                       name='company_news_delete_admin_panel'),
                  path('company_news/user/AdminPanel/', company_news_user_manage_admin_panel_view,
                       name='company_news_user_manage_admin_panel'),
                  path('company_news/user/detail/<int:pk>', company_news_user_detail_admin_panel_view,
                       name='company_news_user_detail_admin_panel'),
                  path('company_news/user/edit/<int:pk>', company_news_user_edit_admin_panel_view,
                       name='company_news_user_edit_admin_panel'),

                  # Widoki związane z wiadomościami "Shot wydarzeń"
                  path('replay_news/', replay_news_add_view, name='replay_news_add'),
                  path('replay_news/AdminPanel/', replay_news_admin_panel_view, name='replay_news_admin_panel'),
                  path('replay_news/detail/<int:pk>', replay_news_detail_admin_panel_view,
                       name='replay_news_detail_admin_panel'),
                  path('replay_news/edit/<int:pk>', replay_news_edit_admin_panel_view,
                       name='repaly_news_edit_admin_panel'),
                  path('replay_news/delete/<int:pk>', replay_news_delete_admin_panel_view,
                       name='replay_news_delete_admin_panel'),
                  path('replay_news/user/AdminPanel', replay_news_user_manage_admin_panel_view,
                       name='replay_news_user_manage_admin_panel'),
                  path('replay_news/user/detail/<int:pk>', replay_news_user_detail_admin_panel_view,
                       name='replay_news_user_detail_admin_panel'),
                  path('replay_news/user/edit/<int:pk>', replay_news_user_edit_admin_panel_view,
                       name='replay_news_user_edit_admin_panel'),

                  # Widoki związane z wiadomościami o rozwoju i zmianach na stronie
                  path('development_news/', development_news_add_view, name='development_news_add'),
                  path('development_news/AdminPanel/', development_news_admin_panel_view,
                       name='development_news_admin_panel'),
                  path('development_news/detail/<int:pk>', development_news_detail_admin_panel_view,
                       name='development_news_detail_admin_panel'),
                  path('development_news/edit/<int:pk>', development_news_edit_admin_panel_view,
                       name='development_news_edit_admin_panel'),
                  path('development_news/delete/<int:pk>', development_news_delete_admin_panel_view,
                       name='development_news_delete_admin_panel'),
                  path('development_news/user/AdminPanel', development_news_user_manage_admin_panel_view,
                       name='development_news_user_manage_admin_panel'),
                  path('development_news/user/detail/<int:pk>', development_news_user_detail_admin_panel_view,
                       name='development_news_user_detail_admin_panel'),
                  path('development_news/user/edit/<int:pk>', development_news_user_edit_admin_panel_view,
                       name='development_news_user_edit_admin_panel'),

                  # Widoki związane z pominiętymi artykułami
                  path('send_emails/', views.send_emails_view, name='send_emails'),
                  path('skipped_posts/AdminPanel/', views.skipped_posts_admin_panel, name='skipped_posts_admin_panel'),
                  path('skipped_posts/detail/<int:pk>', views.skipped_posts_detail_admin_panel,
                       name='skipped_posts_detail_admin_panel'),
                  path('skipped_posts/user/AdminPanel/', views.skipped_posts_user_admin_panel,
                       name='skipped_posts_user_admin_panel'),
                  path('skipped_posts/user/edit/<int:pk>', views.skipped_posts_user_edit_admin_panel,
                       name='skipped_posts_user_edit_admin_panel'),

                  # Widoki związane z użytkownikiem
                  path('users/', users_add_view, name='users_add'),
                  path('users/AdminPanel/', users_manage_admin_panel_view, name='users_admin_panel'),
                  path('users/detail/<int:pk>', users_detail_admin_panel_view, name='users_detail_admin_panel'),
                  path('users/edit/<int:pk>', users_edit_main_page_admin_panel_view, name='users_edit_admin_panel'),
                  path('users/edit/password/<int:pk>', users_edit_password_admin_panel_view,
                       name='users_edit_password_admin_panel'),
                  path('users/delete/<int:pk>', users_delete_admin_panel_view, name='users_delete_admin_panel'),

                  # Widoki związane z aplikacją na autora
                  path('decision_maker/AdminPanel/', decision_maker_admin_panel,
                       name='decision_maker_admin_panel'),
                  path('decision_maker/detail/<int:pk>', decision_maker_detail_admin_panel_view,
                       name='decision_maker_detail_admin_panel_view'),

                  # Widoki związane z aplikacjami społecznościowymi
                  path('social_app/', social_app_add_view, name='social_app_add'),
                  path('social_app/AdminPanel/', social_app_admin_panel_view, name='social_app_admin_panel'),
                  path('social_app/detail/<int:pk>', social_app_detail_admin_panel_view,
                       name='social_app_detail_admin_panel'),
                  path('social_app/edit/<int:pk>', social_app_edit_admin_panel_view,
                       name='social_app_edit_admin_panel'),
                  path('social_app/delete/<int:pk>', social_app_delete_admin_panel_view,
                       name='social_app_delete_admin_panel'),

                  # Widoki związane z tokenami społecznościowymi
                  path('social_token/', social_token_add_view, name='social_token_add'),
                  path('social_token/AdminPanel/', social_token_admin_panel_view, name='social_token_admin_panel'),
                  path('social_token/detail/<int:pk>', social_token_detail_admin_panel_view,
                       name='social_token_detail_admin_panel'),
                  path('social_token/edit/<int:pk>', social_token_edit_admin_panel_view,
                       name='social_token_edit_admin_panel'),
                  path('social_token/delete/<int:pk>', social_token_delete_admin_panel_view,
                       name='social_token_delete_admin_panel'),

                  # Widoki związane z kontami społecznościowymi
                  path('social_account/', social_account_add_view, name='social_account_add'),
                  path('social_account/AdminPanel/', social_account_admin_panel_view,
                       name='social_account_admin_panel'),
                  path('social_account/detail/<int:pk>', social_account_detail_admin_panel_view,
                       name='social_account_detail_admin_panel'),
                  path('social_account/edit/<int:pk>', social_account_edit_admin_panel_view,
                       name='social_account_edit_admin_panel'),
                  path('social_account/delete/<int:pk>', social_account_delete_admin_panel_view,
                       name='social_account_delete_admin_panel'),

                  # Widoki związane z adresem email dla kont społecznościowych
                  path('email_address/', email_address_add_view, name='email_address_add'),
                  path('email_address/AdminPanel/', email_address_admin_panel_view, name='email_address_admin_panel'),
                  path('email_address/detail/<int:pk>', email_address_detail_admin_panel_view,
                       name='email_address_detail_admin_panel'),
                  path('email_address/edit/<int:pk>', email_address_edit_admin_panel_view,
                       name='email_address_edit_admin_panel'),
                  path('email_address/delete/<int:pk>', email_address_delete_admin_panel_view,
                       name='email_address_delete_admin_panel'),

              ] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
