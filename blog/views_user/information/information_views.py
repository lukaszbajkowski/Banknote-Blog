from django.shortcuts import render

from blog.models import Blog
from blog.models import Category


# Widok regulaminu
def terms_conditions_view(request):
    category = Category.objects.all()
    blog = Blog.objects.all().filter(publiction_status=True).order_by('-date_posted')[1:]

    context = {
        'category': category,
        'blog': blog,
    }
    return render(
        request,
        'UserTemplates/TermsConditions/TermsConditions.html',
        context
    )


# Widok polityki prywatności
def privacy_policy_view(request):
    category = Category.objects.all()
    blog = Blog.objects.all().filter(publiction_status=True).order_by('-date_posted')[1:]

    context = {
        'category': category,
        'blog': blog,
    }
    return render(
        request,
        'UserTemplates/PrivacyPolicy/PrivacyPolicy.html',
        context
    )


# Widok strony "O Nas"
def about_page_view(request):
    category = Category.objects.all()
    blog = Blog.objects.all().filter(publiction_status=True).order_by('-date_posted')[1:]

    context = {
        'category': category,
        'blog': blog,
    }
    return render(
        request,
        'UserTemplates/About/About.html',
        context
    )
