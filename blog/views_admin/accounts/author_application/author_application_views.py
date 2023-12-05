from django.core.paginator import Paginator

from django.shortcuts import redirect
from django.shortcuts import render
from django.shortcuts import get_object_or_404

from blog.decorators import superuser_required

from blog.models import ArticleAuthor
from blog.models import User


# Widok panelu administracyjnego do decydowania o aplikacjach na autora
@superuser_required
def decision_maker_admin_panel(request):
    if request.method == 'POST':
        form_id = request.POST.get('form_id')
        decision = request.POST.get('decision')
        if form_id and decision:
            form = ArticleAuthor.objects.get(id=form_id)
            if not form.approved and not form.rejected:
                if decision == 'approve':
                    form.approved = True
                    form.rejected = False
                    users = User.objects.all()
                    for user in users:
                        if user.user.email == form.email:
                            user.can_be_author = True
                            user.save()
                elif decision == 'reject':
                    form.approved = False
                    form.rejected = True
                form.save()
            return redirect('decision_maker_admin_panel')
    else:
        submitted_forms = ArticleAuthor.objects.all().order_by('-date_added')
        paginator = Paginator(submitted_forms, 10)
        page_number = request.GET.get('page')
        page_obj = paginator.get_page(page_number)

        context = {
            'page_obj': page_obj,
        }
        return render(
            request,
            'AdminTemplates/Accounts/AuthorApplication/AuthorApplicationManageAdmin.html',
            context
        )


# Widok panelu administracyjnego ze szczegółami do decydowania o aplikacjach na autora
@superuser_required
def decision_maker_detail_admin_panel_view(request, pk):
    submitted_forms = get_object_or_404(ArticleAuthor, pk=pk)

    context = {
        'submitted_forms': submitted_forms,
    }
    return render(
        request,
        'AdminTemplates/Accounts/AuthorApplication/AuthorApplicationDetailAdmin.html',
        context
    )
