from functools import wraps
from django.shortcuts import redirect

from blog.models import Author


# Dekorator sprawdzający uprawnienia superusera
def superuser_required(view_func):
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        if request.user.is_authenticated and request.user.is_superuser:
            return view_func(request, *args, **kwargs)
        else:
            return redirect('home')

    return _wrapped_view


# Dekorator sprawdzający, czy użytkownik jest autorem
def redirect_if_author(view_func):
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        if Author.objects.filter(user=request.user).exists():
            return redirect('home')
        return view_func(request, *args, **kwargs)

    return _wrapped_view
