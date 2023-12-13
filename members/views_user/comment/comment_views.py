from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.http import JsonResponse
from django.shortcuts import render

from blog.form import NewsletterUserSignUpForm
from blog.models import Blog
from blog.models import Category
from blog.models import Comment
from blog.views import handle_newsletter_signup


# Widok listy komentarzy użytkownika
@login_required(login_url='home')
def comment_list_view(request):
    user = request.user
    user_comments = Comment.objects.filter(author=user).order_by('-date_posted')
    paginator = Paginator(user_comments, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    category = Category.objects.all()
    blog = Blog.objects.all().filter(publiction_status=True).order_by('-date_posted')[1:]
    newsletter_form = NewsletterUserSignUpForm(request.POST or None)

    if request.method == 'POST':
        response_data = handle_newsletter_signup(request, newsletter_form)
        return JsonResponse(response_data)

    context = {
        'page_obj': page_obj,
        'form': newsletter_form,
        'blog': blog,
        'category': category,
        'user_comments': user_comments,
        'user_gender': user.user.gender,
    }
    return render(
        request,
        'UserTemplates/UserAccount/comments.html',
        context
    )
