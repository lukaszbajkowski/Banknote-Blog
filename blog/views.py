from django.views.generic import ListView, DetailView
from .models import Blog


class HomeView(ListView):
    model = Blog
    template_name = 'home.html'


class ArticleDetailView(DetailView):
    model = Blog
    template_name = 'article_details.html'
