from django.urls import path
from .views import HomeView, ArticleDetailView, profile_view, CategoryView, CategoryListView, ProfileListView
from . import views
from django.conf.urls.static import static
from django.conf import settings


urlpatterns = [
    path('', HomeView, name='home'),
    path('article/<int:pk>', ArticleDetailView, name="article-detail"),
    path('profile/<int:pk>', views.profile_view, name="author-detail"),
    path('category/<str:cats>/', CategoryView, name='category-detail'),
    path('category/', CategoryListView, name='category-all'),
    path('author/all/', ProfileListView, name='author-all'),

] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
