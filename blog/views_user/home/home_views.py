from django.core.paginator import Paginator
from django.http import JsonResponse
from django.shortcuts import redirect
from django.shortcuts import render

from blog.forms.newsletter_form import NewsletterUserSignUpForm
from blog.models import Blog
from blog.models import Category
from blog.models import User as DjangoUser
from blog.views import handle_newsletter_signup


# Widok strony głównej
def home_view(request):
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
            DjangoUser.objects.get(user=request.user)
        except DjangoUser.DoesNotExist:
            return redirect('edit_profile')

    if request.method == 'POST':
        response_data = handle_newsletter_signup(request, newsletter_form)
        return JsonResponse(response_data)

    context = {
        'blog_first': blog_first,
        'blog': blog,
        'category': category,
        'page_obj': page_obj,
        'favorite_blogs': favorite_blogs,
        'form': newsletter_form,
    }
    return render(
        request,
        'UserTemplates/Home/Home.html',
        context
    )
