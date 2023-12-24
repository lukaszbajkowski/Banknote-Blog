from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.shortcuts import get_object_or_404
from django.shortcuts import redirect
from django.shortcuts import render

from blog.decorators import redirect_if_author
from blog.models import ArticleAuthor
from blog.models import Author
from blog.models import Blog
from blog.models import Category
from members.forms.author_application_form import ArticleAuthorForm
from members.forms.author_form import CreateAuthorForm


# Widok formularza do zgłoszenia się jako autor
@login_required(login_url='home')
@redirect_if_author
def author_app_view(request):
    category = Category.objects.all()
    blog = Blog.objects.all().filter(publiction_status=True).order_by('-date_posted')[1:]
    is_blocked = False
    is_author = False
    current_user_email = request.user.email
    authors = ArticleAuthor.objects.filter(email=current_user_email).order_by('-date_added')

    if authors:
        has_rejected_submission = any(author.rejected for author in authors)
        all_submissions_pending = all(not author.approved and not author.rejected for author in authors)
        has_approved_submission = any(author.approved for author in authors)
        if all(author.rejected for author in authors):
            is_blocked = False
        elif has_rejected_submission or all_submissions_pending:
            is_blocked = True
        elif has_approved_submission:
            is_author = True
        else:
            is_blocked = False
    else:
        is_blocked = False

    if request.method == 'POST':
        form = ArticleAuthorForm(request.POST)
        if form.is_valid():
            author = form.save(commit=False)
            author.email = current_user_email
            author.save()
            return redirect('article_author_form')
    else:
        initial_data = {'email': current_user_email}
        form = ArticleAuthorForm(initial=initial_data)

    context = {
        'form': form,
        'is_blocked': is_blocked,
        'authors': authors,
        'is_author': is_author,
        'category': category,
        'blog': blog,
    }
    return render(
        request,
        'UserTemplates/UserAccount/AuthorApplication/AuthorApplication.html',
        context
    )


# Widok historii zgłoszeń na autora
@login_required(login_url='home')
@redirect_if_author
def author_app_history_view(request):
    category = Category.objects.all()
    blog = Blog.objects.all().filter(publiction_status=True).order_by('-date_posted')[1:]
    submitted_forms = ArticleAuthor.objects.filter(email=request.user.email).order_by('-date_added')

    paginator = Paginator(submitted_forms, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    context = {
        'page_obj': page_obj,
        'blog': blog,
        'category': category,
    }
    return render(
        request,
        'UserTemplates/UserAccount/AuthorApplication/AuthorApplicationHistory.html',
        context
    )


# Widok szczegółów zgłoszeń na autora
@login_required(login_url='home')
@redirect_if_author
def author_app_detail_view(request, pk):
    category = Category.objects.all()
    blog = Blog.objects.all().filter(publiction_status=True).order_by('-date_posted')[1:]
    submitted_forms = get_object_or_404(ArticleAuthor, pk=pk)

    if submitted_forms.email != request.user.email:
        return redirect('home')

    context = {
        'submitted_forms': submitted_forms,
        'blog': blog,
        'category': category,
    }
    return render(
        request,
        'UserTemplates/UserAccount/AuthorApplication/AuthorApplicationDetail.html',
        context
    )


# Widok tworzenia autora przez użytkownika, który ma do tego uprawnienia
@login_required(login_url='home')
@redirect_if_author
def author_create_view(request):
    user = request.user.user

    if user.can_be_author:
        if not hasattr(user, 'author'):
            if request.method == 'POST':
                form = CreateAuthorForm(request.POST, request.FILES)
                if form.is_valid():
                    author = Author.objects.create(
                        user=user.user,
                        bio=form.cleaned_data['bio'],
                        profile_pic=form.cleaned_data['profile_pic'],
                        author_quote=form.cleaned_data['author_quote'],
                        author_function=form.cleaned_data['author_function'],
                        author_url=form.cleaned_data['author_url'],
                        pinterest_url=form.cleaned_data['pinterest_url'],
                        facebook_url=form.cleaned_data['facebook_url'],
                        twitter_url=form.cleaned_data['twitter_url'],
                        instagram_url=form.cleaned_data['instagram_url']
                    )
                    user.can_be_author = False
                    user.save()

                    return redirect('edit_author')
            else:
                form = CreateAuthorForm()

            context = {
                'form': form,
            }
            return render(
                request,
                'UserTemplates/UserAccount/AuthorApplication/CreateAuthor.html',
                context
            )
        else:
            return redirect('edit_author')
    else:
        return redirect('article_author_form')
