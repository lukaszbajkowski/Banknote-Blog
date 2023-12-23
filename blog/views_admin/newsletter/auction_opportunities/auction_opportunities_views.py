from django.shortcuts import get_object_or_404
from django.shortcuts import render

from blog.decorators import superuser_required
from blog.forms.auction_opportunities_form import AuctionOpportunitiesCreationForm
from blog.forms.auction_opportunities_form import AuctionOpportunitiesDeleteForm
from blog.forms.auction_opportunities_form import UserAuctionOpportunitiesForm
from blog.models import AuctionOpportunities
from blog.models import User as DjangoUser
from blog.views import edit_admin_panel_view
from blog.views import edit_entity_admin_panel_view
from blog.views import get_paginated_context
from blog.views import newsletter_add_panel_view
from blog.views import process_delete_admin_panel_view


# Widok dodawania newslettera okazji z rynku aukcyjnego (dla superusera)
@superuser_required
def auction_opportunities_add_view(request):
    return newsletter_add_panel_view(
        request,
        'opportunities_news',
        AuctionOpportunitiesCreationForm,
        'AdminTemplates/Newsletter/AuctionOpportunities/AuctionOpportunitiesAddAdmin.html',
        'AdminTemplates/Newsletter/AuctionOpportunities/Mail/AuctionOpportunitiesMail',
        'Okazje z rynku aukcyjnego'
    )


# Widok edycji newslettera okazji z rynku aukcyjnego (dla superusera)
@superuser_required
def auction_opportunities_admin_panel_view(request):
    auction_opportunities = AuctionOpportunities.objects.all().order_by('title')

    context = get_paginated_context(request, auction_opportunities, 10)
    return render(
        request,
        'AdminTemplates/Newsletter/AuctionOpportunities/AuctionOpportunitiesManageAdmin.html',
        context
    )


# Widok szczegółów okazji z rynku aukcyjnego (dla superusera)
@superuser_required
def auction_opportunities_detail_admin_panel_view(request, pk):
    auction_opportunities = get_object_or_404(AuctionOpportunities, pk=pk)

    context = {
        'auction_opportunities': auction_opportunities,
    }
    return render(
        request,
        'AdminTemplates/Newsletter/AuctionOpportunities/AuctionOpportunitiesDetailAdmin.html',
        context
    )


# Widok edycji newslettera okazji z rynku aukcyjnego (dla superusera)
@superuser_required
def auction_opportunities_edit_admin_panel_view(request, pk):
    return edit_admin_panel_view(
        request,
        pk,
        AuctionOpportunities,
        'opportunities_news',
        AuctionOpportunitiesCreationForm,
        'AdminTemplates/Newsletter/AuctionOpportunities/AuctionOpportunitiesEditAdmin.html',
        'AdminTemplates/Newsletter/AuctionOpportunities/Mail/AuctionOpportunitiesMail',
        'Okazje z rynku aukcyjnego'
    )


# Widok usuwania newslettera okazji z rynku aukcyjnego (dla superusera)
@superuser_required
def auction_opportunities_delete_admin_panel_view(request, pk):
    return process_delete_admin_panel_view(
        request,
        pk,
        AuctionOpportunities,
        AuctionOpportunitiesDeleteForm,
        'AdminTemplates/Newsletter/AuctionOpportunities/AuctionOpportunitiesDeleteAdmin.html',
        'Mail o okazjach z rynku aukcyjnego został usunięty',
        'auction_opportunities_admin_panel'
    )


# Widok zarządzania użytkownikami w kontekście okazji z rynku aukcyjnego (dla superusera)
@superuser_required
def auction_opportunities_user_manage_admin_panel_view(request):
    users = DjangoUser.objects.all().order_by('user__id')

    context = get_paginated_context(request, users, 10)
    return render(
        request,
        'AdminTemplates/Newsletter/AuctionOpportunities/AuctionOpportunitiesUserManageAdmin.html',
        context
    )


# Widok szczegółów użytkownika w kontekście okazji z rynku aukcyjnego (dla superusera)
@superuser_required
def auction_opportunities_user_detail_admin_panel_view(request, pk):
    user = get_object_or_404(DjangoUser, pk=pk)

    context = {
        'users': user,
    }
    return render(
        request,
        'AdminTemplates/Newsletter/AuctionOpportunities/AuctionOpportunitiesUserDetailAdmin.html',
        context
    )


# Widok edycji ustawień e-maila o okazjach z rynku aukcyjnego dla konkretnego użytkownika (dla superusera)
@superuser_required
def auction_opportunities_user_edit_admin_panel_view(request, pk):
    user = get_object_or_404(DjangoUser, id=pk)

    extra_context = {
        'users': user,
    }
    return edit_entity_admin_panel_view(
        request,
        pk,
        DjangoUser,
        UserAuctionOpportunitiesForm,
        'AdminTemplates/Newsletter/AuctionOpportunities/AuctionOpportunitiesUserEditAdmin.html',
        'Ustawienia e-maila o okazjach z rynku aukcyjnego zostały zaktualizowane.',
        'auction_opportunities_user_manage_admin_panel',
        extra_context
    )
